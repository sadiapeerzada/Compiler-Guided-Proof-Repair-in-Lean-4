"""Actual V2 generation, strict reference verification and non-inference screens."""
import argparse,time,collections,json,csv
from v2_common import *
from parser_v2 import parse_response,ParseError
from prompts_v2 import generation_prompt,CATEGORIES

def root():return HERE/'runs'/read(HERE/'protocol_v2.json')['run_id']

def raw_file(path,raw):
    if path.exists():ensure(path.read_bytes()==raw,'Raw response changed')
    else:
        with path.open('xb') as stream:stream.write(raw);stream.flush();__import__('os').fsync(stream.fileno())

def generate():
    from runtime_v2 import Generator
    model=Generator();out=root();previous=rows(out/'v2_candidates.jsonl');done={r['index'] for r in previous};seen={r['candidate']['id'] for r in previous if r.get('candidate')}
    try:
        for index in range(10):
            if index in done:continue
            prompt=generation_prompt(index);record,folder=model.generate(index,prompt)
            entry=dict(index=index,prompt=prompt,prompt_sha256=text_hash(prompt),source_call=str(folder.relative_to(HERE)),record=record,cohort_use='DEVELOPMENT_ONLY_NEVER_CONFIRMATORY',model=model.model['id'],revision=model.model['revision'])
            entry['parse_status']='UNAVAILABLE_GENERATION'
            if record['status']=='completed':
                raw=record['content'].encode('utf-8');raw_file(folder/'raw_response.txt',raw)
                entry['raw_response_sha256']=text_hash(record['content'])
                try:
                    candidate=parse_response(raw,output_tokens=record['metadata']['completion_tokens'],finish_reason=record['metadata']['finish_reason'],seen_ids=seen)
                    ensure(candidate['id']==f'v2_gen_{index:03d}','Generated ID differs from the assigned ID')
                    candidate['generation_provenance']=dict(model=model.model['id'],revision=model.model['revision'],prompt_sha256=text_hash(prompt),response_sha256=entry['raw_response_sha256'],source_call=entry['source_call'],seed=model.protocol['base_seed'],cohort_use=entry['cohort_use'])
                    entry['candidate']=candidate;entry['parse_status']='PARSED';seen.add(candidate['id'])
                except (ParseError,ValueError) as error:entry['parse_status']='PARSE_REJECTED';entry['reason']=str(error)
            append(out/'v2_candidates.jsonl',entry)
            if entry['parse_status']!='PARSED':append(out/'v2_rejections.jsonl',dict(stage='parsing',index=index,status=entry['parse_status'],reason=entry.get('reason','unavailable consumed intent'),source_call=entry['source_call']))
            if record['status']!='completed':raise RuntimeError('Unavailable generation; preserve intent and stop. No automatic retry.')
    finally:model.close();metrics()

def verify():
    from lean_adapter import LeanVerifier,live_environment
    from checkpoint import RunStore
    p=frozen();out=root();environment=live_environment(p['environment'])
    verifier=LeanVerifier(['Mathlib'],timeout=p['reference_timeout_seconds'])
    store=RunStore(out/'reference_checks',dict(protocol_sha256=sha(HERE/'protocol_v2.json'),kind='reference_only_no_inference'),dict(max_runtime_seconds=2400))
    done={r['id'] for r in rows(out/'v2_formal_verification.jsonl')}
    for candidate in rows(out/'v2_parsed_candidates.jsonl'):
        if candidate['id'] in done:continue
        key=content_hash([candidate['id'],candidate['proof_sha256']]);folder=out/'reference_checks'/key;folder.mkdir(parents=True,exist_ok=True)
        result=store.verify_once(folder,candidate['reference_proof'],candidate['expected_lean_statement'],verifier)
        # The old adapter returns no timing for early policy rejection; unknown remains explicit.
        append(out/'v2_formal_verification.jsonl',dict(id=candidate['id'],candidate_sha256=candidate['proof_sha256'],target_sha256=candidate['statement_sha256'],result=result,environment=environment,verifier_sha256=sha(ROOT/'src/verify.py'),adapter_sha256=sha(LEGACY/'lean_adapter.py')))
        if result['success'] is not True:append(out/'v2_rejections.jsonl',dict(stage='formal_verification',id=candidate['id'],failure_kind=result['failure_kind'],success=result['success']))
    results={r['id']:r for r in rows(out/'v2_formal_verification.jsonl')}
    verified=[dict(c,status='FORMALLY_VERIFIED_PENDING_AI_REVIEW') for c in rows(out/'v2_parsed_candidates.jsonl') if c['id'] in results and results[c['id']]['result']['success'] is True]
    dump(out/'v2_verified_candidates.json',verified);screens();metrics();print('Strictly verified:',len(verified),'of',len(results),'checked')

def screens():
    from dataset_tools import screen,cohort_flags
    out=root();candidates=read(out/'v2_verified_candidates.json');flags=cohort_flags(candidates);results=[]
    for candidate,within in zip(candidates,flags):
        item=screen(dict(candidate,source_url='Locally AI generated; upstream sources unassessed',license='Model/upstream rights unassessed',library_dependencies=[]))
        item['automated_flags']=sorted(set(item['automated_flags']+within));item['quarantine']=bool(item['automated_flags']);item['AI_review_status']='NOT_EXECUTED_NO_AUTHORIZATION';item['eligibility']='NOT_AI_SCREENED';results.append(item)
    dump(out/'automated_historical_screen.json',dict(records=results,scope='Historical 193-version/exposure exact-normalized/template/family screen, not exhaustive semantic equivalence',pretraining_contamination='UNASSESSED',AI_review_not_inferred=True))

def metrics():
    out=root();records=rows(out/'v2_candidates.jsonl');ledger=rows(out/'calls/budget.jsonl');completed=[read(p) for p in (out/'calls/calls').glob('*/completion.json')]
    formal=rows(out/'v2_formal_verification.jsonl');parsed=[r['candidate'] for r in records if r.get('parse_status')=='PARSED']
    # This is a rebuildable view of the append-only canonical candidate log.
    # A crash cannot leave a separately appended parsed row with no canonical entry.
    ensure(len({c['id'] for c in parsed})==len(parsed),'Duplicate durable candidate IDs')
    temporary=out/'v2_parsed_candidates.jsonl.tmp'
    with temporary.open('w') as stream:
        for candidate in parsed:stream.write(json.dumps(candidate,sort_keys=True,ensure_ascii=False)+'\n')
        stream.flush();__import__('os').fsync(stream.fileno())
    temporary.replace(out/'v2_parsed_candidates.jsonl')
    from dataset_tools import cohort_flags
    duplicate_flags=cohort_flags(parsed)
    value=dict(charged_intents=len(ledger),durable_responses=len(completed),unknown_consumed_intents=len(ledger)-len(completed),recorded_attempts=len(records),parse_statuses=dict(collections.Counter(r['parse_status'] for r in records)),parsed_candidates=len(parsed),strict_verified=sum(r['result']['success'] is True for r in formal),formal_failures=sum(r['result']['success'] is False for r in formal),formal_unknown=sum(r['result']['success'] is None for r in formal),formal_checked=len(formal),alpha_duplicate_candidates=sum(bool(f) for f in duplicate_flags),actual_input_tokens=sum(r['metadata']['prompt_tokens'] for r in completed),actual_output_tokens=sum(r['metadata']['completion_tokens'] for r in completed),recorded_generation_seconds=sum(r['metadata']['latency_seconds'] for r in completed),max_reported_MLX_peak_memory_gb=max((r['metadata']['peak_memory_gb'] for r in completed),default=None),durable_response_rate=len(completed)/len(ledger) if ledger else None,parse_rate_per_response=len(parsed)/len(completed) if completed else None,strict_verified_rate_per_parsed=sum(r['result']['success'] is True for r in formal)/len(parsed) if parsed else None,AI_review_calls=0,development_calls=0,confirmatory_calls=0,unknown_compute_not_estimated=True)
    dump(out/'v2_generation_metrics.json',value)

def dry_run():
    p=frozen();spec,_=authorize('generation')
    from transformers import AutoTokenizer
    model=p['generator'];snapshot=Path.home()/'.cache/huggingface/hub'/model['cache_name']/'snapshots'/model['revision']
    tokenizer=AutoTokenizer.from_pretrained(str(snapshot),local_files_only=True,trust_remote_code=False)
    prompts=[]
    for i in range(10):
        prompt=generation_prompt(i);rendered=tokenizer.apply_chat_template([{'role':'user','content':prompt}],tokenize=False,add_generation_prompt=True)
        count=len(tokenizer.encode(rendered,add_special_tokens=False));ensure(count<=spec['max_input_tokens'],'Dry-run prompt exceeds allocation')
        prompts.append(dict(index=i,category=CATEGORIES[i],prompt=prompt,prompt_sha256=text_hash(prompt),rendered_input_tokens=count))
    dump(HERE/'offline/no_inference_dry_run.json',dict(status='PASSED_NO_MODEL_LOADING_OR_INFERENCE',prompts=prompts,model=model,actual_inference_calls=0,source_lock_sha256=sha(HERE/'source_lock_v2.json')))
    print('Dry run passed:',len(prompts),'prompts; no inference')

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('command',choices=['generate','verify','metrics','dry-run']);a=parser.parse_args();{'generate':generate,'verify':verify,'metrics':metrics,'dry-run':dry_run}[a.command]()
