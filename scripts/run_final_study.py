"""Genuine, checkpointed approved-policy MLX A/B/C study; no paid API path."""
from __future__ import annotations
from dataclasses import asdict
import datetime
import hashlib
import json
from pathlib import Path
import sys
import time
import argparse
import gc

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from final_study import BASE,read,sha,canonical,validate_protocol
from local_llm_client import LocalMLXClient
from model_client import extract_lean_block
from verify import check_lean_file_detailed,VerificationPolicy

def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def atomic(path,value):
    path.parent.mkdir(parents=True,exist_ok=True);tmp=path.with_suffix(path.suffix+'.tmp')
    with tmp.open('w') as s:
        json.dump(value,s,indent=2,ensure_ascii=False);s.write('\n');s.flush();__import__('os').fsync(s.fileno())
    tmp.replace(path)

def feedback(verification):
    if verification['diagnostic_state']!='available':return None
    ds=[d for d in verification['diagnostics'] or [] if d.get('kind')!='hasSorry']
    return json.dumps({'diagnostic_state':'available','diagnostics':ds},ensure_ascii=False,indent=2) if ds else None

class InterruptedGeneration(Exception):pass

def step(client,p,run,record,phase,seed,key,prompt):
    folder=run/key;folder.mkdir(exist_ok=True)
    context=f'{phase}/{seed}/{record["id"]}/{key}'
    prompt_hash=hashlib.sha256(prompt.encode()).hexdigest()
    intent=folder/'intent.json';completed=folder/'completion.json'
    if completed.exists():
        c=read(completed)
        if c['prompt_sha256']!=prompt_hash or c['context']!=context:raise ValueError('Checkpoint prompt/context changed')
    elif intent.exists():
        raise InterruptedGeneration('Prior generation intent has no complete durable response; never replay automatically: '+context)
    else:
        atomic(intent,{'context':context,'prompt_sha256':prompt_hash,'started_at':now(),'protocol_sha256':p['_sha256']})
        try:result=client(prompt,max_tokens=2000,temperature=0.2,generation_context=context)
        except Exception as error:
            atomic(folder/'generation_failure.json',{'context':context,'error_type':type(error).__name__,'error':str(error),'finished_at':now()})
            raise InterruptedGeneration('Generation failed without replay: '+context) from error
        c={'context':context,'prompt_sha256':prompt_hash,'prompt':prompt,'raw_response':result.content,
           'metadata':result.metadata,'finished_at':now()}
        atomic(completed,c)
    code=extract_lean_block(c['raw_response']);candidate=folder/'candidate.lean'
    candidate.write_text(code)
    # Each call already uses an independent KV cache and context-derived RNG.
    # Release the identical model between generation and the memory-heavy full
    # Mathlib import; the next call reloads and rechecks the exact same weights.
    if isinstance(client,LocalMLXClient):
        client._model=None;client._tokenizer=None;gc.collect()
        import mlx.core as mx
        mx.clear_cache()
    vpath=folder/'verification.json'
    if vpath.exists():
        v=read(vpath)
        if v['candidate_sha256']!=hashlib.sha256(code.encode()).hexdigest():raise ValueError('Checkpoint candidate changed')
    else:
        expected='open scoped BigOperators\n'+record['expected_lean_statement']+' := by sorry'
        v=check_lean_file_detailed(code,ROOT/'lean_project','study_'+hashlib.sha256(context.encode()).hexdigest()[:24],
              expected_statement=expected,policy=VerificationPolicy(timeout_seconds=p['verifier_timeout_seconds'])).to_record()
        atomic(vpath,v)
    return {'key':key,'candidate_sha256':hashlib.sha256(code.encode()).hexdigest(),'candidate':code,
        'completion_path':str(completed.relative_to(ROOT)),'completion_sha256':sha(completed),
        'verification_path':str(vpath.relative_to(ROOT)),'verification_sha256':sha(vpath),
        'verification':v,'prompt_tokens':c['metadata']['prompt_tokens'],'completion_tokens':c['metadata']['completion_tokens'],
        'generation_seconds':c['metadata']['latency_seconds']}

def trajectory(client,p,record,phase,seed,root):
    run=root/phase/str(seed)/record['id'];run.mkdir(parents=True,exist_ok=True);mp=run/'manifest.json'
    state=read(mp) if mp.exists() else {'schema_version':4,'kind':'genuine_local_paired_proof_repair',
        'phase':phase,'seed':seed,'problem_id':record['id'],'protocol_sha256':p['_sha256'],
        'dataset_sha256':p['dataset_sha256'][phase],'status':'running','started_at':now(),'conditions':{},
        'initial':None,'local_generation_confirmed':False,'supervisor_approval_provenance':'student_reported_not_independently_verified'}
    if state['protocol_sha256']!=p['_sha256'] or state['dataset_sha256']!=p['dataset_sha256'][phase]:raise ValueError('Checkpoint configuration changed')
    if state['status'] in ('completed','incomplete'):return state
    atomic(mp,state)
    trace=run/'streams';trace.mkdir(exist_ok=True);client.trace_directory=trace
    if state['initial'] is None:
        prompt=(ROOT/p['prompts']['initial']).read_text().format(nl_statement=record['nl_statement'],theorem_statement=record['expected_lean_statement'])
        try:state['initial']=step(client,p,run,record,phase,seed,'initial',prompt)
        except InterruptedGeneration as error:
            state.update(status='incomplete',incomplete_reason=str(error),finished_at=now());atomic(mp,state);return state
        state['local_generation_confirmed']=True;atomic(mp,state)
    initial=state['initial'];initial_success=initial['verification']['success']
    if initial['verification']['failure_kind'] in ['timeout','infrastructure_error','input_error','verifier_error']:
        state['conditions']={k:{'success':None,'repair_calls':0,'status':'initial_verifier_incomplete',
            'initial_candidate_sha256':initial['candidate_sha256'],'attempts':[],'milestones':{}} for k in ['A','B','C']}
        state.update(status='incomplete',finished_at=now());atomic(mp,state);return state
    state['conditions']['A']={'success':initial_success,'repair_calls':0,'initial_candidate_sha256':initial['candidate_sha256'],
        'status':'verified_success' if initial_success else 'failed','milestones':{'0':initial_success},'attempts':[]}
    for condition in ['B','C']:
        existing=state['conditions'].get(condition)
        if existing and existing['status']!='running':continue
        current=initial
        result=existing or {'success':initial_success,'repair_calls':0,'initial_candidate_sha256':initial['candidate_sha256'],
            'status':'running','milestones':{'0':initial_success},'attempts':[]}
        state['conditions'][condition]=result
        if result['attempts']:current=result['attempts'][-1]
        if result['success']:
            result['status']='verified_success';atomic(mp,state);continue
        for repair in range(len(result['attempts'])+1,4):
            if condition=='B':
                payload='No compiler diagnostics are provided in the blind-retry condition.'
            else:
                payload=feedback(current['verification'])
                if payload is None:
                    result['status']='no_genuine_compiler_diagnostics';break
            template=(ROOT/p['prompts']['blind' if condition=='B' else 'guided']).read_text()
            prompt=template.format(theorem_statement=record['expected_lean_statement'],previous_candidate=current['candidate'],feedback=payload)
            try:new=step(client,p,run,record,phase,seed,condition+str(repair),prompt)
            except InterruptedGeneration as error:
                result.update(status='incomplete_interrupted_generation',success=None,incomplete_reason=str(error));break
            new['feedback_payload']=payload
            new['feedback_source_candidate_sha256']=current['candidate_sha256'] if condition=='C' else None
            result['attempts'].append(new);result['repair_calls']=len(result['attempts']);current=new
            result['success']=new['verification']['success'];result['milestones'][str(repair)]=result['success']
            atomic(mp,state)
            if result['success']:result['status']='verified_success';break
            if new['verification']['failure_kind'] in ['timeout','infrastructure_error','input_error','verifier_error']:
                result['status']='incomplete_verification';result['success']=None;break
        if result['status']=='running':result['status']='repair_budget_exhausted'
        atomic(mp,state)
    state['status']='incomplete' if any(c['success'] is None for c in state['conditions'].values()) else 'completed'
    state['finished_at']=now();atomic(mp,state);return state

def run(protocol_path,phase):
    p=validate_protocol(protocol_path);p['_sha256']=sha(protocol_path)
    if phase=='heldout':
        pilot=read(BASE/'pilot_audit.json')
        if not pilot['controls_passed'] or pilot['protocol_sha256']!=p['_sha256']:raise ValueError('Genuine audited pilot required')
    from local_protocol import live_lean_environment
    env=live_lean_environment({'lean_environment':{'mathlib_revision':p['mathlib_revision']}})
    root=ROOT/p['output_root'];root.mkdir(parents=True,exist_ok=True)
    atomic(root/(phase+'_environment.json'),env)
    rows=read(BASE/('development.json' if phase=='development_pilot' else 'test.json'))
    if phase=='development_pilot':rows=[r for r in rows if r['id'] in p['pilot_ids']]
    inventory=read(ROOT/p['model']['inventory_path']);snapshot=Path.home()/p['model']['snapshot_home_relative']
    client=LocalMLXClient(snapshot,inventory,model_id=p['model']['model_id'],seed=2027,max_context_tokens=8192)
    for seed in p['seeds']:
        for i,r in enumerate(rows,1):
            state=trajectory(client,p,r,phase,seed,root)
            print(phase,i,'/',len(rows),r['id'],state['status'],{k:v['success'] for k,v in state['conditions'].items()},flush=True)

if __name__=='__main__':
    a=argparse.ArgumentParser(description=__doc__);a.add_argument('--protocol',type=Path,required=True);a.add_argument('--phase',choices=['development_pilot','heldout'],required=True);args=a.parse_args();run(args.protocol,args.phase)
