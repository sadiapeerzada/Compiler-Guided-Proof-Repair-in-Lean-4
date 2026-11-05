"""Prospective footer correction on unconsumed slots; preserve V1 and its clock.

The first method produced no three-section responses, so its category retirements
are retained as V1 outcomes, not interpreted as mathematical capability evidence.
V2 independently retires after four unusable responses per family, inside the
same original128-call phase cap and deadline. No consumed ID is attempted again.
"""
import subprocess,signal,argparse
from sprint_common import *
import construct as base

LOCK='development_prompt_v2.json'
def prompt(topic,identifier,attempt):
    return base.prompt(topic,identifier,attempt)+'''\nFINAL OUTPUT REQUIREMENT: All THREE sections are mandatory and in this order: STATEMENT, LEAN, FAMILY. After the closing Lean code fence, write a final line starting FAMILY: that names the actual mathematical relation. Do not stop after the code fence. Do not write END BY. Your response's last line must be the FAMILY line.\n'''

class VersionedModel(Model):
    def __init__(self,*args,**kwargs):frozen(LOCK);super().__init__(*args,**kwargs)
    def call(self,text,key,seed,release=False):
        frozen(LOCK);return super().call(text,dict(key,prompt_version='v2',additional_source_freeze_sha256=sha(HERE/'freezes'/LOCK)),seed,release=release)

def worker():
    stage='development_generation';authorize(stage);frozen(LOCK);clock(stage);out=RUN/stage;plan=read(HERE/'family_schedule.json');topics=plan['development'];exposure=read(HERE/'exposure_index.json')
    records=rows(out/'records.jsonl');done={r['index'] for r in records};consumed={e['key']['key']['index'] for e in rows(out/'calls/budget.jsonl')};ensure(consumed<=done,'Reconcile outstanding consumed intents without inference first')
    parser=None;model=None;verifier=base.RigidVerifier()
    try:
        for index in range(plan['development_jobs']):
            if index in done or index in consumed:continue
            topic=topics[index%len(topics)];group=base.family(topic);prior=[r for r in records if r.get('prompt_version')=='v2' and r.get('canonical_family')==group]
            if len(prior)>=4 and not any(r.get('verification',{}).get('success') is True and not r.get('pre_review_flags') for r in prior):append(out/'skipped_jobs_v2.jsonl',dict(index=index,family=group,status='V2_FAMILY_RETIRED_AFTER_FOUR_NO_USABLE_VERIFICATIONS'));continue
            identifier=f'sprint_development_{index:04d}';text=prompt(topic,identifier,index//len(topics));entry=dict(index=index,id=identifier,canonical_family=group,prompt=text,prompt_sha256=text_hash(text),prompt_version='v2',scope='development',status='PENDING')
            if model is None:model=VersionedModel(stage,'development_construction.json')
            try:record,folder=model.call(text,dict(index=index,id=identifier),plan['seeds']['development_generation'],release=True)
            except ValueError as error:
                if str(error)!='PROMPT_OVER_CAP_NO_CALL':raise
                entry.update(status='SKIPPED_NO_INFERENCE',reason=str(error));append(out/'records.jsonl',entry);records.append(entry);continue
            consumed.add(index);entry.update(record=record,source_call=str(folder.relative_to(HERE)))
            if record['status']!='completed':entry['status']='UNKNOWN_CONSUMED_INTENT';append(out/'records.jsonl',entry);raise ValueError('New unavailable generation; no replay')
            try:
                if parser is None:parser=base.NativeParser(out/'native_parser_v2')
                m=record['metadata'];c=parser.candidate(record['content'].encode(),identifier,topic['description'],m['completion_tokens'],m['finish_reason'],folder)
                c['canonical_family']=group;c['generation_provenance']=dict(model=model.model,source_call=entry['source_call'],raw_response_sha256=text_hash(record['content']),prompt_sha256=text_hash(text),scope='development',seed=plan['seeds']['development_generation'],prompt_version='v2')
                entry.update(candidate=c,pre_review_flags=base.basic_flags(c,'development',exposure),status='STRUCTURALLY_VALID',verification=base.verify(c,verifier))
            except base.ParseError as error:entry.update(status='STRUCTURE_REJECTED',reason=str(error))
            except base.ParserUnavailable as error:entry.update(status='PARSER_UNAVAILABLE',reason=str(error));append(out/'records.jsonl',entry);raise
            append(out/'records.jsonl',entry);records.append(entry);ensure(entry.get('verification',{}).get('success','not_checked') is not None,'Unknown verification; diagnose')
    finally:
        if parser:parser.close()
        if model:model.close()
        dump(RUN/'development_verified.json',[dict(r['candidate'],reference_validation_variant='rigid_declaration_type_and_universe_v1',status='FORMALLY_VERIFIED_PENDING_AI_REVIEW') for r in rows(out/'records.jsonl') if r.get('verification',{}).get('success') is True and not r.get('pre_review_flags')])

def run():
    c=clock('development_generation');frozen(LOCK);out=RUN/'development_generation';dump(out/'status.json',dict(status='running',prompt_version='v2',original_clock_preserved=True))
    with (out/'stdout_v2.log').open('a') as stdout,(out/'stderr_v2.log').open('a') as stderr:
        child=subprocess.Popen([sys.executable,str(HERE/'construct_v2.py'),'worker'],stdout=stdout,stderr=stderr,start_new_session=True)
        try:code=child.wait(timeout=c['started_epoch']+c['max_runtime_seconds']-time.time());state='finished' if code==0 else 'worker_failed'
        except subprocess.TimeoutExpired:os.killpg(child.pid,signal.SIGKILL);child.wait();code=None;state='authorized_deadline_expired'
    dump(out/'status.json',dict(status=state,exit_code=code,prompt_version='v2',original_clock_preserved=True));print(read(out/'status.json'))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['run','worker']);a=p.parse_args();run() if a.mode=='run' else worker()
