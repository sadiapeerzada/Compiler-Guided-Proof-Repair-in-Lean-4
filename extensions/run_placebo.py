"""Genuine post-hoc DEV-only control, with new contexts and no replay of intents."""
import argparse
import datetime as dt
import gc
import hashlib
import importlib.util
import json
from pathlib import Path
import resource
import sys
import time

ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT),str(ROOT/'src')]
from analysis.common import read,category
from extensions.filename_normalization import assert_private_free,normalize_verification,feedback,NormalizationError
from extensions.donors import select_donor
from local_llm_client import LocalMLXClient
from model_client import extract_lean_block
from verify import check_lean_file_detailed,VerificationPolicy
from final_study import validate_protocol
from local_protocol import live_lean_environment

spec=importlib.util.spec_from_file_location('frozen_durable_machinery',ROOT/'scripts/run_final_study.py')
frozen=importlib.util.module_from_spec(spec);spec.loader.exec_module(frozen)


def now():return dt.datetime.now(dt.timezone.utc).isoformat()
def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def save(path,value):assert_private_free(value);frozen.atomic(path,value)
def rss_peak():return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*(1 if sys.platform=='darwin' else 1024)


class MissingGeneration(Exception):pass


def completed_step(client,p,folder,row,key,prompt,selection=None):
    context=f"{p['phase']}/{p['base_seed']}/{row['id']}/{key}";step=folder/key;step.mkdir(exist_ok=True)
    phash=hashlib.sha256(prompt.encode()).hexdigest();intent=step/'intent.json';cp=step/'completion.json';vp=step/'verification.json'
    assert_private_free(prompt)
    if cp.exists():
        c=read(cp)
        if c['context']!=context or c['prompt_sha256']!=phash:raise ValueError('Completed checkpoint input changed')
    elif intent.exists():raise MissingGeneration('Existing intent without durable completion; never replay')
    else:
        save(intent,{'context':context,'prompt_sha256':phash,'protocol_sha256':p['_sha256'],'started_at':now(),'selection':selection})
        print('post_hoc_dev_generation',row['id'],key,flush=True)
        started=time.monotonic()
        try:response=client(prompt,max_tokens=2000,temperature=.2,generation_context=context)
        except Exception as error:
            # Runtime failures, not compiler messages: do not export sensitive exception paths.
            save(step/'generation_failure.json',{'error_type':type(error).__name__,
                 'reason':'context_preflight_rejection' if 'context budget' in str(error) else 'generation_infrastructure_failure',
                 'finished_at':now(),'elapsed_seconds':time.monotonic()-started,'rss_peak_bytes':rss_peak()})
            raise MissingGeneration('Generation unavailable; intent consumed and not replayed') from None
        c={'context':context,'prompt_sha256':phash,'prompt':prompt,'raw_response':response.content,'metadata':response.metadata,
           'finished_at':now(),'model_call_wall_seconds':time.monotonic()-started,'rss_peak_bytes':rss_peak()}
        save(cp,c)
    code=extract_lean_block(c['raw_response']);assert_private_free(code)
    candidate=step/'candidate.lean'
    if candidate.exists() and candidate.read_text()!=code:raise ValueError('Durable candidate mismatch')
    if not candidate.exists():candidate.write_text(code)
    # Same independent KV / weight-release schedule as the frozen study.
    client._model=None;client._tokenizer=None;gc.collect()
    import mlx.core as mx
    mx.clear_cache()
    if vp.exists():v=read(vp)
    else:
        original=check_lean_file_detailed(code,ROOT/'lean_project','posthoc_dev_'+hashlib.sha256(context.encode()).hexdigest()[:24],
            expected_statement='open scoped BigOperators\n'+row['expected_lean_statement']+' := by sorry',policy=VerificationPolicy(timeout_seconds=180)).to_record()
        v=normalize_verification(original,ROOT)
        save(vp,v)
    if v['candidate_sha256']!=hashlib.sha256(code.encode()).hexdigest():raise ValueError('Verifier candidate binding mismatch')
    print('post_hoc_dev_verified',row['id'],key,v['success'],v['failure_kind'],flush=True)
    return {'key':key,'candidate':code,'candidate_sha256':hashlib.sha256(code.encode()).hexdigest(),'verification':v,
            'completion_path':str(cp.relative_to(ROOT)),'verification_path':str(vp.relative_to(ROOT)),
            'prompt_tokens':c['metadata']['prompt_tokens'],'completion_tokens':c['metadata']['completion_tokens'],
            'generation_seconds':c['metadata']['latency_seconds'],'selection':selection}


def trajectory(client,p,row,pool,tokenizer,root):
    folder=root/'runs'/row['id'];folder.mkdir(parents=True,exist_ok=True);mp=folder/'manifest.json'
    state=read(mp) if mp.exists() else {'kind':'post_hoc_development_only_placebo','protocol_sha256':p['_sha256'],
        'phase':p['phase'],'problem_id':row['id'],'family':row['study_eligibility']['family'],'started_at':now(),
        'status':'running','initial':None,'conditions':{}}
    if state['protocol_sha256']!=p['_sha256']:raise ValueError('Frozen extension checkpoint protocol changed')
    if state['status'] in ['completed','incomplete']:return state
    save(mp,state);streams=folder/'streams';streams.mkdir(exist_ok=True);client.trace_directory=streams
    if state['initial'] is None:
        prompt=p['prompt_text']['initial'].format(nl_statement=row['nl_statement'],theorem_statement=row['expected_lean_statement'])
        try:state['initial']=completed_step(client,p,folder,row,'shared_initial',prompt)
        except MissingGeneration:
            state.update(status='incomplete',reason='shared_initial_unavailable',finished_at=now());save(mp,state);return state
        save(mp,state)
    initial=state['initial'];v=initial['verification'];infra={'timeout','infrastructure_error','input_error','verifier_error'}
    if v['failure_kind'] in infra:
        state['conditions']={c:{'success':None,'attempts':[],'status':'initial_verifier_unavailable'} for c in ['A','B','C','C_placebo']}
        state.update(status='incomplete',finished_at=now());save(mp,state);return state
    state['conditions']['A']={'success':v['success'],'attempts':[],'status':'initial_only','initial_candidate_sha256':initial['candidate_sha256']}
    for condition,prefix in [('B','blind_repair_'),('C','real_repair_'),('C_placebo','placebo_repair_')]:
        old=state['conditions'].get(condition)
        if old and old['status']!='running':continue
        branch=old or {'success':v['success'],'attempts':[],'status':'running','initial_candidate_sha256':initial['candidate_sha256']}
        state['conditions'][condition]=branch;current=branch['attempts'][-1] if branch['attempts'] else initial
        if branch['success']:branch['status']='verified_shared_initial';save(mp,state);continue
        for index in range(len(branch['attempts'])+1,4):
            selection=None
            if condition=='B':payload='No compiler diagnostics are provided in the blind-retry condition.'
            else:
                real=feedback(current['verification'])
                if real is None:branch['status']='no_genuine_compiler_diagnostics';break
                if condition=='C':payload=real
                else:
                    n=len(tokenizer.encode(real,add_special_tokens=False));donor,selection=select_donor(pool,row['id'],row['study_eligibility']['family'],category(current['verification']),n);payload=donor['payload']
            template=p['prompt_text']['blind' if condition=='B' else 'guided']
            prompt=template.format(theorem_statement=row['expected_lean_statement'],previous_candidate=current['candidate'],feedback=payload)
            try:new=completed_step(client,p,folder,row,prefix+str(index),prompt,selection)
            except MissingGeneration:
                branch.update(success=None,status='missing_generation');break
            new['feedback_payload']=payload;new['feedback_source_candidate_sha256']=current['candidate_sha256'] if condition=='C' else None
            branch['attempts'].append(new);branch['success']=new['verification']['success'];current=new;save(mp,state)
            if branch['success']:branch['status']='verified_success';break
            if new['verification']['failure_kind'] in infra:branch.update(success=None,status='verification_unavailable');break
        if branch['status']=='running':branch['status']='repair_budget_exhausted'
        save(mp,state)
    state.update(status='incomplete' if any(c['success'] is None for c in state['conditions'].values()) else 'completed',finished_at=now());save(mp,state)
    return state


def run(execute=False):
    if not execute:raise ValueError('Use --execute-dev only for the approved new development phase')
    path=ROOT/'extensions/placebo_protocol.json';p=read(path);p['_sha256']=digest(path)
    assert p['scope']=='post_hoc_development_only' and p['heldout_execution_allowed'] is False
    assert p['phase'].startswith('post_hoc_dev_') and p['normalization_user_approved'] is True
    for name,expected in p['pinned_implementation_files'].items():
        if digest(ROOT/name)!=expected:raise ValueError('Extension implementation changed after protocol freeze')
    frozen_p=validate_protocol(ROOT/'configs/repair_experiment_local_v0.4.2.json')
    root=ROOT/p['output_root'];root.mkdir(parents=True,exist_ok=True)
    pool=read(ROOT/p['donor_pool_path']);assert digest(ROOT/p['donor_pool_path'])==p['donor_pool_sha256']
    rows=read(ROOT/'data/final_study/v1/development.json')
    assert [r['id'] for r in rows]==p['development_ids'] and len(rows)==15
    # Refuse to start until the committed protocol is exactly the working copy.
    import subprocess
    committed=subprocess.check_output(['git','show','HEAD:extensions/placebo_protocol.json'],cwd=ROOT)
    assert hashlib.sha256(committed).hexdigest()==p['_sha256']
    lock=root/'worker.lock'
    if lock.exists():raise ValueError('Another or interrupted dev worker lock exists; inspect before resuming')
    lock.open('x').close()
    try:
        env=live_lean_environment({'lean_environment':{'mathlib_revision':frozen_p['mathlib_revision']}})
        save(root/'environment.json',{'post_hoc':True,'development_only':True,'environment':env,'protocol_sha256':p['_sha256'],'started_at':now()})
        from transformers import AutoTokenizer
        snapshot=Path.home()/frozen_p['model']['snapshot_home_relative']
        tokenizer=AutoTokenizer.from_pretrained(snapshot,local_files_only=True,trust_remote_code=False)
        client=LocalMLXClient(snapshot,read(ROOT/frozen_p['model']['inventory_path']),model_id=frozen_p['model']['model_id'],seed=2027,max_context_tokens=8192)
        for index,row in enumerate(rows,1):
            state=trajectory(client,p,row,pool,tokenizer,root)
            print('post_hoc_dev',index,'/15',row['id'],state['status'],{c:v['success'] for c,v in state['conditions'].items()},flush=True)
        save(root/'execution_finished.json',{'post_hoc':True,'development_only':True,'cases':len(rows),'finished_at':now(),'protocol_sha256':p['_sha256']})
    finally:lock.unlink()


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--execute-dev',action='store_true');args=parser.parse_args()
    try:run(args.execute_dev)
    except Exception as error:
        from analysis.common import sanitize
        print('Stopped safely:',type(error).__name__,sanitize(str(error)),file=sys.stderr);raise SystemExit(1)
