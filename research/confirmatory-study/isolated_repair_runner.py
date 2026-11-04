"""Gated shared-predecessor first-repair execution. Default CLI reports NO_GO."""
import argparse
import csv
import hashlib
import json
import re
from pathlib import Path
from common import HERE,content_hash,dump,read,ensure,csv_write
from isolated_repair_validation import require_go,gate
from matching import initial_prompt,matched_conditions,diagnostic_payload,donor_order,planned_orders
from checkpoint import RunStore
import importlib.util
_analysis_spec=importlib.util.spec_from_file_location('confirmatory_paired_analysis',HERE/'paired_analysis.py')
_analysis_module=importlib.util.module_from_spec(_analysis_spec);_analysis_spec.loader.exec_module(_analysis_module)
analyze=_analysis_module.analyze

ARMS=('C','D','E')

def key_for(permit,row,seed,arm):
    return dict(phase=permit['phase'],protocol_sha256=permit['protocol_sha256'],model_revision=permit['protocol']['model']['revision'],model_id=permit['protocol']['model']['model_id'],id=row['id'],seed=seed,arm=arm)

def extract(text):
    match=re.search(r'```lean\s*(.*?)```',text,re.S);return match.group(1).strip() if match else text.strip()

def new_file(path,value):
    if path.exists():ensure(read(path)==value,'Checkpoint changed: '+str(path))
    else:dump(path,value,exclusive=True)

def classify(record):
    if record.get('success') is True:return 'verified'
    kind=record.get('failure_kind')
    if record.get('success') is None:return kind or 'unavailable'
    if kind!='compiler_error':return kind or 'unclassified'
    text='\n'.join(record.get('errors') or []).lower()
    for label,tokens in [('syntax',('unexpected token','parser','expected token')),('unknown_name',('unknown identifier','unknown constant','unknown tactic')),('type_elaboration',('type mismatch','failed to synthesize')),('tactic_goals',('unsolved goals','tactic failed'))]:
        if any(t in text for t in tokens):return label
    return 'other_compiler'

def perform(store,permit,row,seed,arm,prompt,backend,verifier):
    p=permit['protocol'];key=key_for(permit,row,seed,arm);count=backend.tokenizer.count(prompt)
    ensure(count<=p['budget']['input_tokens_per_call'],'Prompt exceeds allocation; no call issued')
    completion,folder=store.call_once(key,prompt,count,p['budget']['output_tokens_per_call'],'initial' if arm=='A' else 'repair',lambda text,path:backend.generate(text,seed,'confirmatory/'+content_hash(key),path))
    if completion['status']!='completed':return dict(candidate=None,verification=dict(success=None,failure_kind='generation_unavailable'),folder=str(folder),resumed_unknown=completion.get('resumed',False))
    candidate=extract(completion['content'])
    previous_verification_intent=(folder/'verification_intent.json').exists()
    verification=store.verify_once(folder,candidate,row['expected_lean_statement'],verifier)
    ensure(verification.get('success') in (True,False,None),'Verifier returned invalid outcome')
    if verification.get('success') is not None:
        ensure(verification.get('candidate_sha256')==hashlib.sha256(candidate.encode()).hexdigest(),'Verifier checked another candidate')
    return dict(candidate=candidate,verification=verification,folder=str(folder),resumed_unknown=previous_verification_intent and verification.get('success') is None)

def collect(store,permit):
    rows=[]
    for row in permit['records']:
        for seed in permit['protocol']['seeds']:
            base=dict(unit_test_only=permit['authorization'].get('unit_test_only',False),id=row['id'],family=row['family'],seed=seed,phase=permit['phase'],model_revision=permit['protocol']['model']['revision'])
            initial=store.root/'calls'/content_hash(key_for(permit,row,seed,'A'))/'verification.json'
            iv=read(initial) if initial.exists() else dict(success=None,failure_kind='initial_unavailable')
            item=dict(**base,initial_success=iv.get('success'),initial_error=classify(iv))
            plan=store.root/'cases'/content_hash([row['id'],seed])/'matching.json'
            valid=plan.exists() and read(plan)['valid']
            if any((store.root/'calls'/content_hash(key_for(permit,row,seed,a))/'nonconforming_generation.json').exists() for a in ARMS):valid=False
            item['comparison_valid']=valid
            for arm in ('A',)+ARMS:
                folder=store.root/'calls'/content_hash(key_for(permit,row,seed,arm));vp=folder/'verification.json'
                verification=read(vp) if vp.exists() else {'success':None}
                item['strict_'+arm]=verification.get('success')
                item[arm]=verification.get('success') if valid and iv.get('success') is False else None
                item[arm+'_status']='initial_verified_not_applicable' if iv.get('success') is True else ('verified' if item[arm] is True else 'unverified' if item[arm] is False else 'unknown_or_not_started')
                reserved=any(e['key']==key_for(permit,row,seed,arm) and e['run_binding']==content_hash(store.binding) for e in store.events())
                item[arm+'_generation_status']='completed' if (folder/'completion.json').exists() else 'nonconforming' if (folder/'nonconforming_generation.json').exists() else 'unknown_consumed_intent' if reserved else 'not_issued'
                cp=folder/'completion.json';metadata=read(cp).get('metadata') if cp.exists() else (read(folder/'nonconforming_generation.json').get('metadata') if (folder/'nonconforming_generation.json').exists() else None)
                item[arm+'_input_tokens']=metadata.get('prompt_tokens') if metadata else None
                item[arm+'_output_tokens']=metadata.get('completion_tokens') if metadata else None
                item[arm+'_generation_seconds']=metadata.get('latency_seconds',metadata.get('generation_seconds')) if metadata else None
                item[arm+'_compiler_seconds']=verification.get('elapsed_seconds')
            rows.append(item)
    return rows

def export(store,permit):
    rows=collect(store,permit);version=store.root/'exports'/content_hash(rows);version.mkdir(parents=True,exist_ok=True)
    new_file(version/'rows.json',rows)
    if not (version/'isolated_repair_results.csv').exists():csv_write(version/'isolated_repair_results.csv',rows)
    report=analyze(rows,replicates=permit['protocol']['statistics']['replicates'],seed=permit['protocol']['statistics']['bootstrap_seed'],expected_keys=[(r['id'],seed) for r in permit['records'] for seed in permit['protocol']['seeds']],expected_phase=permit['phase'],expected_model_revision=permit['protocol']['model']['revision'])
    costs={}
    for arm in ('A',)+ARMS:
        inputs=[r[arm+'_input_tokens'] for r in rows if type(r[arm+'_input_tokens']) is int]
        outputs=[r[arm+'_output_tokens'] for r in rows if type(r[arm+'_output_tokens']) is int]
        costs[arm]=dict(generations_with_recorded_input=len(inputs),generations_with_recorded_output=len(outputs),actual_input_tokens_observed=sum(inputs) if inputs else None,actual_output_tokens_observed=sum(outputs) if outputs else None,unknown_consumed_intents=sum(r[arm+'_generation_status']=='unknown_consumed_intent' for r in rows),not_issued=sum(r[arm+'_generation_status']=='not_issued' for r in rows),nonconforming=sum(r[arm+'_generation_status']=='nonconforming' for r in rows))
    report['recorded_costs']=costs;report['cost_caveat']='Durable metadata only; unknown or interrupted generation cost is not estimated. Initial calls are separate shared costs in the ledger/completions.'
    new_file(version/'analysis.json',report)
    new_file(version/'reproducibility_manifest.json',dict(protocol_sha256=permit['protocol_sha256'],source_lock_sha256=permit['source_lock_sha256'],dataset_sha256=permit['manifest'][permit['phase']]['sha256'],row_content_sha256=content_hash(rows),run_binding=store.binding))
    return version

def run_core(permit,backend,verifier,root,global_root=None):
    """Dependency-injected core; tests may pass fake clients, production CLI cannot."""
    p=permit['protocol'];records=permit['records'];n=len(records)*len(p['seeds'])
    limits=dict(max_total_calls=p['budget']['max_total_calls'],max_initial_calls=p['budget']['max_initial_calls'],max_repair_calls=p['budget']['max_repair_calls'],max_input_tokens=p['budget']['input_tokens_per_call'],max_output_tokens=p['budget']['output_tokens_per_call'],max_runtime_seconds=permit['authorization']['resource_limits']['max_runtime_seconds'],max_run_calls=permit['authorization']['resource_limits']['max_calls'])
    binding=dict(protocol_sha256=permit['protocol_sha256'],source_lock_sha256=permit['source_lock_sha256'],phase=permit['phase'],dataset_sha256=permit['manifest'][permit['phase']]['sha256'],authorization_sha256=content_hash(permit['authorization']))
    store=RunStore(root,binding,limits,global_root);store.remaining_preflight(n,n*3)
    orders=planned_orders(records,p['seeds'],p['order_seed']);initials={}
    try:
        # Freeze every initial result before selecting diagnostic donors or executing any repair.
        for seed in p['seeds']:
            for row in records:
                result=perform(store,permit,row,seed,'A',initial_prompt(row),backend,verifier)
                initials[row['id'],seed]=result
                if (Path(result['folder'])/'nonconforming_generation.json').exists():raise ValueError('Nonconforming backend; execution stopped')
                if result['verification'].get('success') is None and not result.get('resumed_unknown'):raise ValueError('New infrastructure-unavailable initial call; execution stopped with checkpoint preserved')
        assignments={}
        for seed in p['seeds']:
            for row in records:
                order=donor_order(row,records,seed,p['forbidden_donor_pairs']);donor=None
                for rid in order:
                    initial=initials[rid,seed]
                    if initial['candidate']:
                        payload=diagnostic_payload(initial['verification'],initial['candidate'])
                        target=initials[row['id'],seed]
                        real=diagnostic_payload(target['verification'],target['candidate']) if target['candidate'] else None
                        if payload is not None and payload!=real:donor=rid;break
                assignments[row['id']+'/'+str(seed)]=donor
        new_file(store.root/'donor_assignment.json',dict(policy='Predeclared rank; first distinct genuine initial-failure diagnostic in eligible disjoint family; frozen before repairs',assignments=assignments))
        byid={r['id']:r for r in records}
        for seed in p['seeds']:
            for row in records:
                initial=initials[row['id'],seed]
                if initial['verification'].get('success') is not False:continue
                path=store.root/'cases'/content_hash([row['id'],seed]);path.mkdir(parents=True,exist_ok=True)
                donor_id=assignments[row['id']+'/'+str(seed)]
                if donor_id is None:match=dict(valid=False,reason='no_eligible_frozen_donor',conditions={})
                else:
                    donor=initials[donor_id,seed]
                    match=matched_conditions(row,initial['candidate'],initial['verification'],donor['verification'],donor['candidate'],backend.tokenizer,p['budget']['input_tokens_per_call'])
                match['donor_id']=donor_id;match['order']=orders[row['id'],seed]
                new_file(path/'matching.json',match)
                if not match['valid']:continue
                for arm in match['order']:
                    done=perform(store,permit,row,seed,arm,match['conditions'][arm]['prompt'],backend,verifier)
                    if (Path(done['folder'])/'nonconforming_generation.json').exists():raise ValueError('Nonconforming backend; execution stopped')
                    if done['verification'].get('success') is None and not done.get('resumed_unknown'):raise ValueError('New infrastructure-unavailable repair; checkpoint preserved')
    finally:
        export(store,permit)
    return store

def execute(bundle,phase):
    # No client/tokenizer/held-out content access before this gate.
    permit=require_go(bundle,phase)
    from lean_adapter import LeanVerifier,live_environment
    live_environment(permit['protocol'])
    from backend import LocalBackend
    backend=LocalBackend(bundle,phase)
    verifier=LeanVerifier(permit['protocol']['lean']['imports'],permit['protocol']['lean']['timeout_seconds'])
    root=HERE/'runs'/phase/content_hash([permit['protocol_sha256'],permit['manifest'][phase]['sha256'],permit['authorization']])
    return run_core(permit,backend,verifier,root,HERE/'runs')

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('command',choices=['status','run'],nargs='?',default='status');parser.add_argument('--bundle',default=str(HERE/'execution_bundle.json'));parser.add_argument('--phase',choices=['development','test'],default='test');a=parser.parse_args()
    if a.command=='status':print(json.dumps(gate(a.bundle,a.phase),indent=2))
    else:execute(a.bundle,a.phase)
