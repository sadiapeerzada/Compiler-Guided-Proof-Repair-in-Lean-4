import argparse,subprocess,signal,time
from common_v3 import *
from parser_v3 import parse,repair_source,ParseError,ParserUnavailable
from prompts_v3 import prompt,repair_prompt,CATEGORIES
from lean_adapter import LeanVerifier,live_environment

def check_source(candidate,source,phase,folder,verifier):
    store=RunStore(root()/'formal_checks',dict(protocol_sha256=sha(HERE/'protocol_v3.json'),scope='REFERENCE_CONSTRUCTION_NOT_CDE'),dict(max_runtime_seconds=3600))
    folder=root()/'formal_checks'/content_hash([phase,candidate['id'],text_hash(source)]);folder.mkdir(parents=True,exist_ok=True)
    return store.verify_once(folder,source,candidate['expected_lean_statement'],verifier)

def execute(phase):
    from runtime_v3 import LocalPhase
    authorize(phase);p=freeze_check();out=root()/phase;out.mkdir(parents=True,exist_ok=True)
    environment=live_environment(p['environment']);dump(out/'environment.json',environment)
    verifier=LeanVerifier(['Mathlib'],timeout=180);done={r['index'] for r in rows(out/'records.jsonl')}
    if phase=='generation':jobs=[(i,None) for i in range(10)]
    else:
        jobs=[(r['index'],r) for r in rows(root()/'generation/records.jsonl') if r.get('candidate') and r.get('verification',{}).get('success') is False]
    model=None
    try:
        for index,initial in jobs:
            if index in done:continue
            candidate=initial['candidate'] if initial else None
            text=prompt(index) if phase=='generation' else repair_prompt(candidate,__import__('json').dumps(initial['verification'],ensure_ascii=False))
            if model is None:model=LocalPhase(phase)
            entry=dict(index=index,phase=phase,prompt=text,prompt_sha256=text_hash(text),scope='DEVELOPMENT_REFERENCE_CONSTRUCTION_NEVER_CONFIRMATORY',status='PENDING')
            try:record,folder=model.call(index,text)
            except ValueError as error:
                if str(error)!='PROMPT_OVER_CAP_NO_CALL':raise
                entry.update(status='SKIPPED_NO_INFERENCE',reason=str(error));append(out/'records.jsonl',entry);continue
            entry.update(record=record,source_call=str(folder.relative_to(HERE)))
            if record['status']!='completed':
                entry['status']='UNKNOWN_CONSUMED_INTENT';append(out/'records.jsonl',entry);raise RuntimeError('Unavailable generation: no replay or replacement')
            metadata=record['metadata'];entry['raw_response_sha256']=text_hash(record['content'])
            try:
                if phase=='generation':
                    candidate=parse(record['content'].encode(),expected_id=f'v3_gen_{index:03d}',category=CATEGORIES[index],tokens=metadata['completion_tokens'],finish=metadata['finish_reason'],evidence=folder/'native_parser.json')
                    candidate['generation_provenance']=dict(model=model.model,seed=p['base_seed'],source_call=entry['source_call'],prompt_sha256=text_hash(text),raw_response_sha256=entry['raw_response_sha256'])
                    source=candidate['reference_proof']
                else:
                    source=repair_source(record['content'].encode(),candidate=candidate,tokens=metadata['completion_tokens'],finish=metadata['finish_reason'],evidence=folder/'native_parser.json')
                entry.update(candidate=candidate,evaluated_source=source,evaluated_source_sha256=text_hash(source),status='STRUCTURALLY_VALID')
                entry['verification']=check_source(candidate,source,phase,folder,verifier)
            except ParseError as error:entry.update(status='STRUCTURE_REJECTED',reason=str(error))
            except ParserUnavailable as error:
                entry.update(status='PARSER_UNAVAILABLE',reason=str(error));append(out/'records.jsonl',entry);raise
            append(out/'records.jsonl',entry)
            if entry.get('verification',{}).get('success','not_checked') is None:raise RuntimeError('Unknown verification: stop, retain consumed check')
    finally:
        if model:model.close()
        summarize()

def summarize():
    out=root();out.mkdir(parents=True,exist_ok=True);all_records={s:rows(out/s/'records.jsonl') for s in ('generation','reference_repair')};metrics={};verified=[]
    for phase,records in all_records.items():
        calls=out/phase/'calls';ledger=rows(calls/'budget.jsonl');completed=[read(p) for p in (calls/'calls').glob('*/completion.json')]
        metrics[phase]=dict(charged_intents=len(ledger),durable_responses=len(completed),unknown_consumed_intents=len(ledger)-len(completed),structurally_valid=sum(r['status']=='STRUCTURALLY_VALID' for r in records),strict_verified=sum(r.get('verification',{}).get('success') is True for r in records),strict_failed=sum(r.get('verification',{}).get('success') is False for r in records),strict_unknown=sum('verification' in r and r['verification']['success'] is None for r in records),actual_input_tokens=sum(r['metadata']['prompt_tokens'] for r in completed),actual_output_tokens=sum(r['metadata']['completion_tokens'] for r in completed),generation_seconds=sum(r['metadata']['latency_seconds'] for r in completed),max_MLX_peak_memory_gb=max((r['metadata']['peak_memory_gb'] for r in completed),default=None),rejection_reasons=[dict(index=r['index'],status=r['status'],reason=r.get('reason'),failure_kind=r.get('verification',{}).get('failure_kind')) for r in records if r['status']!='STRUCTURALLY_VALID' or r.get('verification',{}).get('success') is not True])
    repairs={r['index']:r for r in all_records['reference_repair']}
    for initial in all_records['generation']:
        chosen=initial if initial.get('verification',{}).get('success') is True else repairs.get(initial['index'])
        if chosen and chosen.get('verification',{}).get('success') is True:
            c=dict(initial['candidate']);c['reference_proof']=chosen['evaluated_source'];c['proof_sha256']=text_hash(c['reference_proof']);c['status']='FORMALLY_VERIFIED_PENDING_AI_REVIEW';c['construction_path']='initial' if chosen is initial else 'one_compiler_guided_repair';c['verification_source_call']=chosen['source_call'];verified.append(c)
    dump(out/'verified_candidates.json',verified);dump(out/'metrics.json',dict(phases=metrics,unique_verified_candidates=len(verified),AI_adjudication_calls=0,CDE_calls=0,test_calls=0,unknown_compute_not_estimated=True))

def watch(phase):
    authorize(phase);freeze_check();out=root()/phase;out.mkdir(parents=True,exist_ok=True);clock=out/'phase_clock.json'
    if not clock.exists():dump(clock,dict(started_epoch=time.time(),max_runtime_seconds=1800),exclusive=True)
    remaining=read(clock)['started_epoch']+1800-time.time();ensure(remaining>0,'Phase deadline exhausted, never reset')
    with (out/'stdout.log').open('a') as stdout,(out/'stderr.log').open('a') as stderr:
        process=subprocess.Popen([sys.executable,str(HERE/'pipeline_v3.py'),'worker',phase],stdout=stdout,stderr=stderr,start_new_session=True)
        try:code=process.wait(timeout=remaining);status='finished' if code==0 else 'worker_failed'
        except subprocess.TimeoutExpired:os.killpg(process.pid,signal.SIGKILL);process.wait();code=None;status='authorized_deadline_exhausted'
    summarize();dump(out/'phase_status.json',dict(status=status,exit_code=code));print(phase,status,code)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('command',choices=['run','worker','summarize']);p.add_argument('phase',nargs='?',choices=['generation','reference_repair']);a=p.parse_args()
    if a.command=='summarize':summarize()
    elif a.command=='run':watch(a.phase)
    else:execute(a.phase)
