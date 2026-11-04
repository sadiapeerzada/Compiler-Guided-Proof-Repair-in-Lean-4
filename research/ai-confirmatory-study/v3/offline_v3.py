"""No inference: archived replay, tokenizer check and actual Lean parser probes."""
import argparse,subprocess
from common_v3 import *
from parser_v3 import parse,split_theorem,ParseError
from prompts_v3 import prompt,CATEGORIES

def archived():
    source=next((OLD/'v2/runs').glob('*/v2_candidates.jsonl'));output=[]
    for row in rows(source):
        record=row['record'];entry=dict(index=row['index'],original_response_sha256=text_hash(record['content']),source_call=row['source_call'],scope='POSTHOC_DIAGNOSTIC_ONLY_NOT_NEW_DATA')
        try:
            parse(record['content'].encode(),expected_id=f"v2_gen_{row['index']:03d}",category='archived_V2',tokens=record['metadata']['completion_tokens'],finish=record['metadata']['finish_reason'])
            entry['status']='PARSED_POSTHOC_ONLY'
        except ParseError as error:entry.update(status='REJECTED',reason=str(error))
        output.append(entry)
    dump(HERE/'offline/archived_v2_replay.json',dict(records=output,parsed=sum(r['status']=='PARSED_POSTHOC_ONLY' for r in output),historical_outcomes_unchanged=True));print('Archived replay:',len(output),'responses')

def native():
    results=[]
    probes=[('theorem fixture : True := by\n  let x := 2\n  trivial','fixture','theorem fixture : True'),('theorem fixture : True := by\n  /- := ignored -/\n  trivial','fixture','theorem fixture : True')]
    for index,(source,name,target) in enumerate(probes):
        actual,proof=split_theorem(source,name,HERE/'offline'/f'native_probe_{index}.json');ensure(actual==target,'Wrong native assignment boundary');results.append(dict(index=index,status='PASSED'))
    for index,source in enumerate(['theorem fixture : True := by trivial\ntheorem second : True := by trivial','theorem fixture : (let n := 2; n) = 2 := by rfl']):
        try:split_theorem(source,'fixture',HERE/'offline'/f'native_reject_{index}.json');raise AssertionError('Ambiguous/unsupported source accepted')
        except ParseError as error:results.append(dict(index=index+2,status='CORRECTLY_REJECTED',reason=str(error)))
    dump(HERE/'offline/native_parser_checks.json',dict(results=results,actual_Lean_parser=True,synthetic_fixtures_not_candidates=True));print('Native Lean parser checks:',len(results),'passed')

def dry():
    p=freeze_check();authorize('generation')
    from transformers import AutoTokenizer
    model=p['models']['generation'];path=Path.home()/'.cache/huggingface/hub'/model['cache_name']/'snapshots'/model['revision']
    tok=AutoTokenizer.from_pretrained(str(path),local_files_only=True,trust_remote_code=False);entries=[]
    for i in range(10):
        text=prompt(i);rendered=tok.apply_chat_template([{'role':'user','content':text}],tokenize=False,add_generation_prompt=True);count=len(tok.encode(rendered,add_special_tokens=False));ensure(count<=4096,'Prompt over allocation')
        entries.append(dict(index=i,category=CATEGORIES[i],prompt=text,prompt_sha256=text_hash(text),input_tokens=count))
    dump(HERE/'offline/dry_run.json',dict(prompts=entries,inference_calls=0,status='PASSED_NO_MODEL_WEIGHTS_LOADED'));print('Dry run passed, no inference')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['archived','native','dry']);a=p.parse_args();{'archived':archived,'native':native,'dry':dry}[a.mode]()
