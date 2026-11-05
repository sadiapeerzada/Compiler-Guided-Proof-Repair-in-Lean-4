"""Versioned post-hoc header recovery plus bounded real reference-proof repair.

Original generation outcomes remain unchanged. Header extraction supplies no
mathematics: exact provided source is kernel-checked before repair eligibility.
"""
import argparse
from study_common import *
from header_parser import NativeHeaderParser
from native_parser import ParseError,ParserUnavailable
from runtime_v2 import PhaseModelV2
from generation_prompts import repair_prompt
from families import FAMILIES
from generation import verify
from rigid_verifier import RigidVerifier as StrictVerifier
from lean_adapter import live_environment

def curate():
    source=run_root()/'reference_candidate_pool_v2.json'
    if not source.exists():return
    pool=read(source);repairs={r['index']:r for r in rows(run_root()/'reference_repair/records.jsonl')};verified=[]
    for item in pool:
        repaired=repairs.get(item['index']);chosen=item if item.get('verification',{}).get('success') is True else repaired
        if not chosen or chosen.get('verification',{}).get('success') is not True:continue
        c=dict(item['candidate']);c['reference_proof']=chosen['source'];c['proof_sha256']=text_hash(chosen['source']);c['status']='FORMALLY_VERIFIED_PENDING_AI_REVIEW';c['verification_source_call']=chosen['source_call']
        c['original_generation_intake_status']=item['original_generation_intake_status']
        ensure(chosen['verification'].get('harness_variant')=='rigid_declaration_type_and_universe_v1','Reference lacks rigid closed-type verification')
        c['reference_validation_variant']='rigid_declaration_type_and_universe_v1';c['reference_validation_source_sha256']=chosen['verification']['rigid_variant_source_sha256']
        c['construction_path']=('initial' if item['origin']=='original_full_parser' else 'posthoc_header_check_without_repair') if chosen is item else ('one_reference_repair' if item['origin']=='original_full_parser' else 'posthoc_header_recovery_one_reference_repair')
        if chosen is not item:
            prefix=c['expected_lean_statement']+' := ';ensure(chosen['source'].startswith(prefix),'Fixed target changed');c['proof_block']=chosen['source'][len(prefix):]
        verified.append(c)
    dump(run_root()/'fresh_verified_raw_v2.json',verified);dump(run_root()/'fresh_verified_raw.json',verified)

def execute(stage):
    ensure(stage=='reference_repair','Reference-construction phase only');authorize(stage);frozen('reference_construction_v3.json');out=run_root()/stage;out.mkdir(parents=True,exist_ok=True);dump(out/'environment.json',live_environment(protocol()['environment']))
    verifier=StrictVerifier();parser=None;model=None;pool_path=run_root()/'reference_candidate_pool_v2.json'
    try:
        if not pool_path.exists():
            pool=[];recovered={r['index']:r for r in rows(run_root()/'posthoc_header_recovery.jsonl')}
            for initial in rows(run_root()/'generation/records.jsonl'):
                index=initial['index']
                if initial.get('candidate') and 'verification' in initial:
                    checked=initial['verification']
                    if checked.get('success') is True:
                        checked=verify(initial['candidate'],initial['source'],'rigid_initial_recheck',verifier)
                        if checked.get('success') is None:raise RuntimeError('Unknown rigid reference recheck, stop')
                    pool.append(dict(index=index,candidate=initial['candidate'],source=initial['source'],verification=checked,origin='original_full_parser',original_generation_verification=initial['verification'],original_generation_intake_status=initial['status'],source_call=initial['source_call']));continue
                if initial['status']!='STRUCTURE_REJECTED':continue
                if index in recovered:
                    r=recovered[index]
                    if r.get('candidate') and 'verification' in r:pool.append(r)
                    continue
                record=initial.get('record',{});entry=dict(index=index,origin='posthoc_header_recovery',original_generation_intake_status=initial['status'],source_call=initial.get('source_call'),status='HEADER_REJECTED')
                if record.get('status')!='completed':continue
                folder=out/'header_recovery'/str(index);folder.mkdir(parents=True,exist_ok=True)
                try:
                    if parser is None:parser=NativeHeaderParser(out/'header_parser')
                    group,category=FAMILIES[index%len(FAMILIES)];meta=record['metadata']
                    c=parser.candidate(record['content'].encode(),f'final_dev_{index:04d}',category,meta['completion_tokens'],meta['finish_reason'],folder)
                    c['canonical_family']=group;c['generation_provenance']=dict(model=protocol()['models']['G'],seed=protocol()['base_seed'],source_call=initial['source_call'],raw_response_sha256=text_hash(record['content']),prompt_sha256=initial['prompt_sha256'],scope='DEVELOPMENT_ONLY_NEVER_TEST')
                    result=verify(c,c['reference_proof'],'posthoc_header_check',verifier)
                    entry.update(candidate=c,source=c['reference_proof'],status='HEADER_COMPLETE_AND_KERNEL_CHECKED',verification=result)
                except ParseError as error:entry['reason']=str(error)
                except ParserUnavailable as error:
                    entry.update(status='PARSER_UNAVAILABLE',reason=str(error));append(run_root()/'posthoc_header_recovery.jsonl',entry);raise
                append(run_root()/'posthoc_header_recovery.jsonl',entry)
                if entry.get('candidate') and 'verification' in entry:pool.append(entry)
                if entry.get('verification',{}).get('success','not_checked') is None:raise RuntimeError('Unknown header-source verification; no retry')
            dump(pool_path,pool,exclusive=True)
        pool=read(pool_path);eligible=[r for r in pool if r.get('verification',{}).get('success') is False and r['verification'].get('failure_kind')=='compiler_error'];queue=sorted(eligible,key=lambda r:content_hash(['reference-repair-order',r['candidate']['id']]))[:120]
        queue_path=out/'frozen_repair_queue_v2.json';queue_ids=[r['index'] for r in queue]
        if queue_path.exists():ensure(read(queue_path)==queue_ids,'Queue changed')
        else:dump(queue_path,queue_ids,exclusive=True)
        done={r['index'] for r in rows(out/'records.jsonl')}
        for initial in queue:
            index=initial['index']
            if index in done:continue
            c=initial['candidate'];entry=dict(index=index,stage=stage,version='reference_construction_v3_rigid_types',origin=initial['origin'],status='PENDING')
            try:text=repair_prompt(c,initial['verification'])
            except ValueError as error:entry.update(status='SKIPPED_NO_INFERENCE',reason=str(error));append(out/'records.jsonl',entry);continue
            entry.update(prompt=text,prompt_sha256=text_hash(text))
            if model is None:model=PhaseModelV2(stage,'reference_construction_v3.json')
            try:record,folder=model.call(text,dict(index=index,id=c['id']),protocol()['base_seed'])
            except ValueError as error:
                if str(error)!='PROMPT_OVER_CAP_NO_CALL':raise
                entry.update(status='SKIPPED_NO_INFERENCE',reason=str(error));append(out/'records.jsonl',entry);continue
            entry.update(record=record,source_call=str(folder.relative_to(HERE)))
            if record['status']!='completed':entry['status']='UNAVAILABLE';append(out/'records.jsonl',entry);raise RuntimeError('Unavailable reference repair, no retry')
            try:
                if parser is None:parser=NativeHeaderParser(out/'header_parser')
                meta=record['metadata'];source=parser.repair(record['content'].encode(),c,meta['completion_tokens'],meta['finish_reason'],folder)
                entry.update(candidate=c,source=source,status='HEADER_COMPLETE_REPAIR',verification=verify(c,source,'reference_repair_v2',verifier))
            except ParseError as error:entry.update(status='STRUCTURE_REJECTED',reason=str(error))
            except ParserUnavailable as error:
                entry.update(status='PARSER_UNAVAILABLE',reason=str(error));append(out/'records.jsonl',entry);raise
            append(out/'records.jsonl',entry);append(run_root()/'reference_repair_attempts.jsonl',entry)
            if entry.get('verification',{}).get('success','not_checked') is None:raise RuntimeError('Unknown repaired-proof verification, stop')
    finally:
        if parser:parser.close()
        if model:model.close()
        curate()

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('stage');execute(p.parse_args().stage)
