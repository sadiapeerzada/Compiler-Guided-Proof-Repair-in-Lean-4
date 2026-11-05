"""Finish deterministic processing of durable responses after interruption.

Never initializes a model, issues inference, changes clocks or replays verification
intents. Prospective parsing and checking rules remain frozen and unchanged.
"""
import time
from common_v3 import *
from prompts_v3 import prompt,CATEGORIES
from parser_v3 import parse,ParseError,ParserUnavailable
from pipeline_v3 import check_source,summarize
from lean_adapter import LeanVerifier,live_environment

def main():
    p=freeze_check();out=root()/'generation'
    ensure(not (out/'interruption_reconciliation.json').exists(),'Original reconciliation audit already exists; inspect it without overwriting')
    clock=read(out/'phase_clock.json')
    ensure(time.time()>=clock['started_epoch']+clock['max_runtime_seconds'],'Use ordinary checkpoint resume inside the live phase window')
    done={r['index'] for r in rows(out/'records.jsonl')}
    environment=live_environment(p['environment']);verifier=LeanVerifier(['Mathlib'],timeout=180)
    processed=[]
    for intent_path in sorted((out/'calls/calls').glob('*/intent.json')):
        intent=read(intent_path);index=intent['key']['index'];folder=intent_path.parent
        if index in done:continue
        text=prompt(index);ensure(text_hash(text)==intent['prompt_sha256'],'Frozen prompt mismatch')
        entry=dict(index=index,phase='generation',prompt=text,prompt_sha256=text_hash(text),scope='DEVELOPMENT_REFERENCE_CONSTRUCTION_NEVER_CONFIRMATORY',source_call=str(folder.relative_to(HERE)),post_interruption_offline_reconciliation=True)
        if not (folder/'completion.json').exists():
            entry.update(status='UNKNOWN_CONSUMED_INTENT',record=dict(status='unknown_consumed_intent',content=None,metadata=None))
        else:
            record=read(folder/'completion.json');ensure(record['status']=='completed','Noncompleted durable record')
            ensure((folder/'raw_response.txt').read_bytes()==record['content'].encode(),'Raw response mismatch')
            entry.update(record=record,raw_response_sha256=text_hash(record['content']))
            try:
                metadata=record['metadata']
                c=parse(record['content'].encode(),expected_id=f'v3_gen_{index:03d}',category=CATEGORIES[index],tokens=metadata['completion_tokens'],finish=metadata['finish_reason'],evidence=folder/'native_parser.json')
                c['generation_provenance']=dict(model=p['models']['generation'],seed=p['base_seed'],source_call=entry['source_call'],prompt_sha256=text_hash(text),raw_response_sha256=entry['raw_response_sha256'])
                source=c['reference_proof'];entry.update(candidate=c,evaluated_source=source,evaluated_source_sha256=text_hash(source),status='STRUCTURALLY_VALID')
                entry['verification']=check_source(c,source,'generation',folder,verifier)
            except ParseError as error:entry.update(status='STRUCTURE_REJECTED',reason=str(error))
            except ParserUnavailable as error:
                entry.update(status='PARSER_UNAVAILABLE',reason=str(error));append(out/'records.jsonl',entry);raise
        append(out/'records.jsonl',entry);processed.append(index)
    dump(out/'interruption_reconciliation.json',dict(status='GENERATION_WINDOW_EXPIRED_NO_FURTHER_INFERENCE',original_clock=clock,reconciled_indices=processed,actual_new_model_calls=0,original_missing_worker_status=not (out/'phase_status.json').exists(),cause_of_original_interruption='NOT_ESTABLISHED',environment=environment),exclusive=True)
    summarize();print('Offline reconciled indices:',processed,'; new inference:0')

if __name__=='__main__':main()
