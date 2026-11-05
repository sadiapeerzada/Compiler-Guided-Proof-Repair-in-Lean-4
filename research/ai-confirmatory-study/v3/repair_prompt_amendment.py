"""Versioned development-only diagnostic projection; same budget/clock/targets.

Only candidates skipped WITHOUT inference by the original prompt may use this
revision. No already attempted candidate receives another repair.
"""
import json,time,subprocess,signal
from common_v3 import *
from prompts_v3 import repair_prompt
from runtime_v3 import LocalPhase
from parser_v3 import repair_source,ParseError,ParserUnavailable
from pipeline_v3 import check_source
from lean_adapter import LeanVerifier,live_environment

def amendment_root():return root()/'repair_prompt_amendment'

def compact_diagnostics(verification):
    ensure(verification['failure_kind']=='compiler_error','Only real compiler failures can be projected')
    ensure(not verification.get('malformed_diagnostics'),'Malformed diagnostics cannot enable this revision')
    payload=[{key:d[key] for key in ('severity','kind','data','pos','endPos') if key in d} for d in verification['diagnostics'] if d.get('severity')=='error']
    ensure(payload,'No complete structured error diagnostics')
    return dict(failure_kind=verification['failure_kind'],diagnostics=payload)

def prepare():
    authorize('reference_repair');p=freeze_check();out=amendment_root();out.mkdir(parents=True,exist_ok=True)
    manifest=out/'protocol.json';ensure(not manifest.exists(),'Amendment already frozen')
    source=root()/'reference_repair/records.jsonl';clock=root()/'reference_repair/phase_clock.json'
    ensure(time.time()<read(clock)['started_epoch']+1800,'Original repair deadline expired')
    old=rows(source);eligible=[r['index'] for r in old if r['status']=='SKIPPED_NO_INFERENCE' and r.get('reason')=='PROMPT_OVER_CAP_NO_CALL']
    charged=[r['key']['index'] for r in rows(root()/'reference_repair/calls/budget.jsonl')]
    ensure(not set(eligible)&set(charged),'An eligible index already consumed a repair')
    initial={r['index']:r for r in rows(root()/'generation/records.jsonl')}
    prompts={str(i):repair_prompt(initial[i]['candidate'],json.dumps(compact_diagnostics(initial[i]['verification']),ensure_ascii=False)) for i in eligible}
    dump(out/'prompts.json',prompts,exclusive=True)
    dump(manifest,dict(version='V3-reference-repair-diagnostic-projection-1',scope='EXPLORATORY_DEVELOPMENT_ONLY_NOT_CDE',base_protocol_sha256=sha(HERE/'protocol_v3.json'),source_script_sha256=sha(HERE/'repair_prompt_amendment.py'),original_clock_sha256=sha(clock),original_skip_records_sha256=sha(source),prompts_sha256=sha(out/'prompts.json'),eligible_indices=eligible,pre_amendment_charged_indices=charged,shared_total_repair_call_cap=10,repairs_per_candidate=1,projection='Retain all error diagnostic data/severity/kind/positions; omit duplicated compiler stdout, harness source, warnings and accounting metadata. No error messages truncated.',authorization='Existing direct user authorization for up to10 reference repairs; no additional calls, phase window or retry per candidate'),exclusive=True)
    print('Frozen repair-prompt amendment for indices:',eligible)

def validate():
    authorize('reference_repair');freeze_check();out=amendment_root();m=read(out/'protocol.json')
    ensure(m['source_script_sha256']==sha(HERE/'repair_prompt_amendment.py'),'Amendment source changed')
    ensure(m['base_protocol_sha256']==sha(HERE/'protocol_v3.json'),'Original protocol changed')
    ensure(m['original_clock_sha256']==sha(root()/'reference_repair/phase_clock.json'),'Original repair clock changed')
    ensure(m['original_skip_records_sha256']==sha(root()/'reference_repair/records.jsonl'),'Original repair records changed')
    ensure(m['prompts_sha256']==sha(out/'prompts.json'),'Amended prompts changed')
    return m

def worker():
    m=validate();out=amendment_root();prompts=read(out/'prompts.json');initial={r['index']:r for r in rows(root()/'generation/records.jsonl')};done={r['index'] for r in rows(out/'records.jsonl')};model=None
    verifier=LeanVerifier(['Mathlib'],timeout=180);dump(out/'environment.json',live_environment(read(HERE/'protocol_v3.json')['environment']))
    try:
        for index in m['eligible_indices']:
            if index in done:continue
            ensure(index not in m['pre_amendment_charged_indices'],'Forbidden second repair')
            validate();candidate=initial[index]['candidate'];text=prompts[str(index)]
            if model is None:model=LocalPhase('reference_repair')
            entry=dict(index=index,phase='reference_repair',version=m['version'],amendment_sha256=sha(out/'protocol.json'),prompt=text,prompt_sha256=text_hash(text),status='PENDING')
            try:record,folder=model.call(index,text)
            except ValueError as error:
                if str(error)!='PROMPT_OVER_CAP_NO_CALL':raise
                entry.update(status='SKIPPED_NO_INFERENCE',reason=str(error));append(out/'records.jsonl',entry);continue
            entry.update(record=record,source_call=str(folder.relative_to(HERE)))
            if record['status']!='completed':
                entry['status']='UNKNOWN_CONSUMED_INTENT';append(out/'records.jsonl',entry);raise RuntimeError('Unavailable repair, no retry')
            entry['raw_response_sha256']=text_hash(record['content']);metadata=record['metadata']
            try:
                source=repair_source(record['content'].encode(),candidate=candidate,tokens=metadata['completion_tokens'],finish=metadata['finish_reason'],evidence=folder/'native_parser.json')
                entry.update(candidate=candidate,evaluated_source=source,evaluated_source_sha256=text_hash(source),status='STRUCTURALLY_VALID')
                entry['verification']=check_source(candidate,source,'reference_repair_amendment',folder,verifier)
            except ParseError as error:entry.update(status='STRUCTURE_REJECTED',reason=str(error))
            except ParserUnavailable as error:
                entry.update(status='PARSER_UNAVAILABLE',reason=str(error));append(out/'records.jsonl',entry);raise
            append(out/'records.jsonl',entry)
            if entry.get('verification',{}).get('success','not_checked') is None:raise RuntimeError('Unknown check, stop')
    finally:
        if model:model.close()

def watch():
    validate();remaining=read(root()/'reference_repair/phase_clock.json')['started_epoch']+1800-time.time();ensure(remaining>0,'Original repair deadline exhausted')
    out=amendment_root()
    with (out/'stdout.log').open('a') as stdout,(out/'stderr.log').open('a') as stderr:
        child=subprocess.Popen([sys.executable,str(HERE/'repair_prompt_amendment.py'),'worker'],stdout=stdout,stderr=stderr,start_new_session=True)
        try:code=child.wait(timeout=remaining);status='finished' if code==0 else 'worker_failed'
        except subprocess.TimeoutExpired:os.killpg(child.pid,signal.SIGKILL);child.wait();code=None;status='original_deadline_exhausted'
    dump(out/'status.json',dict(status=status,exit_code=code,original_deadline_preserved=True));print(status,code)

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['prepare','run','worker']);a=p.parse_args();{'prepare':prepare,'run':watch,'worker':worker}[a.mode]()
