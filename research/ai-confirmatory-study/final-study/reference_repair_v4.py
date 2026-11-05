"""Prospective development-only prompt correction inside the SAME repair allocation.

No consumed candidate is called again. The base RunStore retains its original
authorization/freeze binding; each new intent additionally binds the V4 source
freeze. Both freezes are checked before model loading and every affected call.
The original phase clock and120-call total remain in force.
"""
import argparse,subprocess,signal
from study_common import *
from runtime_v2 import PhaseModelV2
from header_parser import NativeHeaderParser
from native_parser import ParseError,ParserUnavailable
from generation import verify
from rigid_verifier import RigidVerifier
from reference_construction_v2 import curate

FREEZE='reference_prompt_v4.json'

def prompt(c,result):
    errors=[{k:d[k] for k in ('severity','kind','data','pos','endPos') if k in d} for d in result['diagnostics'] if d.get('severity')=='error']
    ensure(errors,'No complete actual compiler errors')
    return '''You are supplying a Lean 4.32 reference proof. Return ONLY a Lean4 by-block. The first word must be by. Use newline indentation, not Lean3 begin/end or comma-separated commands. Keep every target binder, assumption and conclusion exactly fixed. Do not output a declaration or theorem name. No placeholders, new axioms, helper declarations, explanations or markdown. Replace the old failed proof; do not copy its obsolete syntax.
FORMAT EXAMPLE ONLY (not your target or a benchmark subject):
Input: theorem syntax_example : True
Output:
by
  trivial
END FORMAT EXAMPLE.
Use appropriate Lean4 tactics such as omega for linear natural/integer arithmetic, ring for polynomial identities, simp for library simplifications, or exact a matching library theorem. These tactics are suggestions, not proof that this target is valid. If the fixed target is ill-typed or false, report that rather than inventing a successful proof. This is the sole repair attempt for this candidate. Maximum1200 output tokens.
YOUR FIXED TARGET:
'''+c['expected_lean_statement']+'\nOLD FAILED SOURCE:\n'+c['reference_proof']+'\nACTUAL COMPLETE COMPILER ERRORS:\n'+json.dumps(errors,ensure_ascii=False)

def entry_from_record(item,record,folder,parser,verifier,version):
    c=item['candidate'];entry=dict(index=item['index'],stage='reference_repair',version=version,origin=item['origin'],source_call=str(folder.relative_to(HERE)),record=record,status='UNKNOWN_CONSUMED_INTENT')
    if record['status']!='completed':return entry
    try:
        m=record['metadata'];source=parser.repair(record['content'].encode(),c,m['completion_tokens'],m['finish_reason'],folder)
        entry.update(candidate=c,source=source,status='HEADER_COMPLETE_REPAIR',verification=verify(c,source,'reference_repair_v2',verifier))
    except ParseError as error:entry.update(status='STRUCTURE_REJECTED',reason=str(error))
    except ParserUnavailable as error:entry.update(status='PARSER_UNAVAILABLE',reason=str(error));raise
    return entry

def worker():
    spec,_=authorize('reference_repair');frozen(FREEZE);frozen('reference_construction_v3.json');clock('reference_repair')
    out=run_root()/'reference_repair';pool={r['index']:r for r in read(run_root()/'reference_candidate_pool_v2.json')};queue=read(out/'frozen_repair_queue_v2.json')
    parser=NativeHeaderParser(out/'header_parser_v4');verifier=RigidVerifier();model=None
    try:
        done={r['index'] for r in rows(out/'records.jsonl')}
        # Reconcile the interrupted old worker without a model retry. A charged
        # intent with no durable response stays unknown and is never regenerated.
        for event in rows(out/'calls/budget.jsonl'):
            index=event['key']['key']['index']
            if index in done:continue
            folder=out/'calls/calls'/content_hash(event['key']);cp=folder/'completion.json';record=read(cp) if cp.exists() else dict(status='unknown_consumed_intent',content=None,metadata=None)
            entry=entry_from_record(pool[index],record,folder,parser,verifier,'reference_prompt_v3_reconciled_without_inference')
            from generation_prompts import repair_prompt
            text=repair_prompt(pool[index]['candidate'],pool[index]['verification']);entry.update(prompt=text,prompt_sha256=text_hash(text),reconciled_without_inference=True)
            append(out/'records.jsonl',entry);append(run_root()/'reference_repair_attempts.jsonl',entry);done.add(index)
        consumed={e['key']['key']['index'] for e in rows(out/'calls/budget.jsonl')}
        for index in queue:
            if index in done or index in consumed:continue
            frozen(FREEZE);clock('reference_repair');ensure(len(rows(out/'calls/budget.jsonl'))<spec['max_calls'],'Original repair call cap exhausted')
            item=pool[index];text=prompt(item['candidate'],item['verification'])
            if model is None:model=PhaseModelV2('reference_repair','reference_construction_v3.json')
            key=dict(index=index,id=item['candidate']['id'],prompt_version='v4',additional_source_freeze_sha256=sha(HERE/'freezes'/FREEZE))
            try:record,folder=model.call(text,key,protocol()['base_seed'])
            except ValueError as error:
                if str(error)!='PROMPT_OVER_CAP_NO_CALL':raise
                append(out/'records.jsonl',dict(index=index,status='SKIPPED_NO_INFERENCE',version='reference_prompt_v4',reason=str(error),prompt=text,prompt_sha256=text_hash(text)));continue
            consumed.add(index);entry=entry_from_record(item,record,folder,parser,verifier,'reference_prompt_v4');entry.update(prompt=text,prompt_sha256=text_hash(text),additional_source_freeze_sha256=key['additional_source_freeze_sha256'])
            append(out/'records.jsonl',entry);append(run_root()/'reference_repair_attempts.jsonl',entry)
            ensure(record['status']=='completed','New unavailable V4 response; stop, no replacement')
            ensure(entry.get('verification',{}).get('success','not_checked') is not None,'New unknown V4 formal check; stop')
    finally:
        parser.close()
        if model:model.close()
        curate()

def run():
    authorize('reference_repair');frozen(FREEZE);c=clock('reference_repair');out=run_root()/'reference_repair'
    old=out/'status.json';saved=out/'status_before_prompt_v4.json'
    if old.exists() and not saved.exists():dump(saved,read(old),exclusive=True)
    remaining=c['started_epoch']+c['max_runtime_seconds']-time.time()
    with (out/'stdout_v4.log').open('a') as stdout,(out/'stderr_v4.log').open('a') as stderr:
        child=subprocess.Popen([sys.executable,str(HERE/'reference_repair_v4.py'),'worker'],stdout=stdout,stderr=stderr,start_new_session=True)
        try:code=child.wait(timeout=remaining);status='finished' if code==0 else 'worker_failed'
        except subprocess.TimeoutExpired:os.killpg(child.pid,signal.SIGKILL);child.wait();code=None;status='authorized_deadline_expired'
    dump(old,dict(status=status,exit_code=code,prompt_version='v4',original_clock_preserved=True,original_total_call_cap_preserved=True));print(read(old));ensure(status!='worker_failed','V4 worker needs diagnosis')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['run','worker']);a=p.parse_args();run() if a.mode=='run' else worker()
