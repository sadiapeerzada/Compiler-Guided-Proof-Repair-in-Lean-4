"""Finite, prospectively scheduled development generation and one-step repair."""
import argparse
from study_common import *
from runtime_v2 import PhaseModelV2
from native_parser import NativeParser,ParseError,ParserUnavailable
from generation_prompts import generation_prompt,repair_prompt
from families import FAMILIES
from strict_verifier import StrictVerifier
from lean_adapter import live_environment

def verify(c,source,variant,verifier):
    out=run_root()/'formal';store=RunStore(out,dict(protocol_sha256=sha(HERE/'protocol.json'),generation_freeze_sha256=sha(HERE/'freezes/generation_v1.json')),dict(max_runtime_seconds=172800))
    folder=out/content_hash([variant,c['id'],text_hash(source)]);folder.mkdir(parents=True,exist_ok=True)
    r=store.verify_once(folder,source,c['expected_lean_statement'],verifier)
    entry=dict(id=c['id'],variant=variant,source_sha256=text_hash(source),target_sha256=c['statement_sha256'],result=r,record_path=str(folder.relative_to(HERE)))
    existing=[e for e in rows(run_root()/'strict_reference_verification.jsonl') if e['record_path']==entry['record_path']]
    if existing:ensure(existing==[entry],'Reference check binding changed')
    else:append(run_root()/'strict_reference_verification.jsonl',entry)
    return r

def refresh_verified():
    initial=rows(run_root()/'generation/records.jsonl');repairs={r['index']:r for r in rows(run_root()/'reference_repair/records.jsonl')};verified=[]
    for r in initial:
        chosen=r if r.get('verification',{}).get('success') is True else repairs.get(r['index'])
        if chosen and chosen.get('verification',{}).get('success') is True:
            c=dict(r['candidate']);c.update(reference_proof=chosen['source'],proof_sha256=text_hash(chosen['source']),construction_path='initial' if chosen is r else 'one_reference_repair',verification_source_call=chosen['source_call'],status='FORMALLY_VERIFIED_PENDING_AI_REVIEW');verified.append(c)
            if chosen is not r:
                prefix=c['expected_lean_statement']+' := ';ensure(c['reference_proof'].startswith(prefix),'Repair target binding changed');c['proof_block']=c['reference_proof'][len(prefix):]
    dump(run_root()/'fresh_verified_raw.json',verified)

def execute(stage):
    spec,_=authorize(stage);ensure(stage in ('generation','reference_repair'),'Development reference construction only');frozen('generation_v1.json');out=run_root()/stage;out.mkdir(parents=True,exist_ok=True)
    dump(out/'environment.json',live_environment(protocol()['environment']));verifier=StrictVerifier();done={r['index'] for r in rows(out/'records.jsonl')};model=None;parser=None
    if stage=='generation':jobs=[(i,None) for i in range(240)]
    else:
        eligible=[r for r in rows(run_root()/'generation/records.jsonl') if r.get('candidate') and r.get('verification',{}).get('success') is False and r['verification'].get('failure_kind')=='compiler_error']
        jobs=[(r['index'],r) for r in sorted(eligible,key=lambda r:content_hash(['reference-repair-order',r['candidate']['id']]))[:120]]
        path=out/'frozen_repair_queue.json';queue=[i for i,r in jobs]
        if path.exists():ensure(read(path)==queue,'Reference-repair queue changed')
        else:dump(path,queue,exclusive=True)
    try:
        for index,initial in jobs:
            if index in done:continue
            c=initial['candidate'] if initial else None
            try:text=generation_prompt(index) if stage=='generation' else repair_prompt(c,initial['verification'])
            except ValueError as error:append(out/'records.jsonl',dict(index=index,status='SKIPPED_NO_INFERENCE',reason=str(error)));continue
            if model is None:model=PhaseModelV2(stage,'generation_v1.json')
            entry=dict(index=index,stage=stage,prompt=text,prompt_sha256=text_hash(text),scope='DEVELOPMENT_ONLY_NEVER_TEST')
            try:record,folder=model.call(text,dict(index=index,id=f'final_dev_{index:04d}'),protocol()['base_seed'])
            except ValueError as error:
                if str(error)!='PROMPT_OVER_CAP_NO_CALL':raise
                entry.update(status='SKIPPED_NO_INFERENCE',reason=str(error));append(out/'records.jsonl',entry);continue
            entry.update(record=record,source_call=str(folder.relative_to(HERE)),status='UNAVAILABLE')
            if record['status']!='completed':append(out/'records.jsonl',entry);raise RuntimeError('Unavailable generation, no automatic replay')
            try:
                if parser is None:parser=NativeParser(out/'native_parser')
                metadata=record['metadata'];group,category=FAMILIES[index%len(FAMILIES)]
                if stage=='generation':
                    c=parser.candidate(record['content'].encode(),f'final_dev_{index:04d}',category,metadata['completion_tokens'],metadata['finish_reason'],folder)
                    c['canonical_family']=group;c['generation_provenance']=dict(model=model.model,seed=protocol()['base_seed'],source_call=entry['source_call'],raw_response_sha256=text_hash(record['content']),prompt_sha256=text_hash(text),scope=entry['scope']);source=c['reference_proof']
                else:source=parser.repair(record['content'].encode(),c,metadata['completion_tokens'],metadata['finish_reason'],folder)
                entry.update(candidate=c,source=source,status='STRUCTURALLY_VALID',verification=verify(c,source,stage,verifier))
            except ParseError as error:entry.update(status='STRUCTURE_REJECTED',reason=str(error))
            except ParserUnavailable as error:
                entry.update(status='PARSER_UNAVAILABLE',reason=str(error));append(out/'records.jsonl',entry);raise
            append(out/'records.jsonl',entry)
            if stage=='generation':append(run_root()/'raw_generations.jsonl',entry)
            else:append(run_root()/'reference_repair_attempts.jsonl',entry)
            if entry.get('verification',{}).get('success','not_checked') is None:raise RuntimeError('Unknown verification, stop with intent preserved')
    finally:
        if parser:parser.close()
        if model:model.close()
        refresh_verified()

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['generation','reference_repair']);execute(p.parse_args().stage)
