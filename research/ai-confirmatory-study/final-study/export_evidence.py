"""Derived reporting projections of immutable calls; no inference or source edits."""
from collections import Counter,defaultdict
from study_common import *

def jsonl(path,records):
    Path(path).write_text(''.join(json.dumps(r,sort_keys=True,ensure_ascii=False)+'\n' for r in records))

def csv_(path,records,fields):
    import csv
    with Path(path).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n');w.writeheader();w.writerows(records)

def usage(stages):
    result={}
    for stage in stages:
        out=run_root()/stage;events=rows(out/'calls/budget.jsonl');complete=[]
        for event in events:
            call=out/'calls/calls'/content_hash(event['key']);path=call/'completion.json'
            if path.exists() and read(path)['status']=='completed':complete.append(read(path)['metadata'])
        result[stage]=dict(charged=len(events),completed=len(complete),unknown_or_unavailable=len(events)-len(complete),actual_input_tokens_observed=sum(r['prompt_tokens'] for r in complete),actual_output_tokens_observed=sum(r['completion_tokens'] for r in complete),actual_generation_seconds_observed=sum(r['latency_seconds'] for r in complete),maximum_reported_MLX_peak_memory_gb=max((r['peak_memory_gb'] for r in complete if 'peak_memory_gb' in r),default=None),memory_caveat='Maximum model-runtime MLX report, not measured whole-process or system peak; unknown cost not estimated')
    return dict(stages=result,total_charged=sum(v['charged'] for v in result.values()),unknown_cost_not_estimated=True,outer_CDE_checkpoint_ledger_not_double_counted=True)

def main():
    out=run_root();g=rows(out/'generation/records.jsonl');repairs=rows(out/'reference_repair/records.jsonl');verified=read(out/'fresh_verified_raw_v2.json') if (out/'fresh_verified_raw_v2.json').exists() else []
    exclusions=[]
    for r in g:
        if r.get('verification',{}).get('success') is not True:exclusions.append(dict(id=f"final_dev_{r['index']:04d}",stage='original_generation_intake',reason=r.get('reason',r['status']),historical_outcome_unchanged=True))
    for r in repairs:
        if r.get('verification',{}).get('success') is not True:exclusions.append(dict(id=f"final_dev_{r['index']:04d}",stage='reference_repair',reason=r.get('reason',r['status'])))
    for name,stage in (('pre_review_exclusions.json','prereview_exposure'),('development_ai_quarantined_candidates.json','fresh_AI_adjudication'),('v3_ai_quarantined_candidates.json','V3_AI_adjudication')):
        for r in read(out/name) if (out/name).exists() else []:exclusions.append(dict(id=r.get('id',r.get('candidate',{}).get('id')),stage=stage,reason=r.get('reason','; '.join(r.get('reasons',[])))))
    jsonl(out/'candidate_exclusions.jsonl',exclusions);csv_(out/'candidate_exclusion_registry.csv',[{k:r[k] for k in ('id','stage','reason')} for r in exclusions],['id','stage','reason'])
    reviews=[r for stage in ('v3_review_1','v3_review_2','development_review_1','development_review_2') for r in rows(out/stage/'reviews.jsonl')]
    jsonl(out/'ai_semantic_review.jsonl',reviews)
    if not (out/'reference_repair_attempts.jsonl').exists():jsonl(out/'reference_repair_attempts.jsonl',[])
    dump(out/'generation_manifest.json',dict(status='RECORDED_DEVELOPMENT_ONLY',run_id=protocol()['run_id'],baseline=protocol()['baseline'],planning_target=20,generation_pool_cap=240,recorded_generation_responses=len(g),original_structural_parse_passes=sum('candidate' in r for r in g),rigid_verified_references=len(verified),original_generation_freeze_sha256=sha(HERE/'freezes/generation_v1.json'),reference_construction_freeze_sha256=sha(HERE/'freezes/reference_construction_v3.json'),authorization_sha256=sha(HERE/'resource_authorization.json'),models=protocol()['models'],source_raw='generation/records.jsonl plus phase-local calls/streams',no_confirmatory_generation=True))
    dump(out/'generation_resource_usage.json',usage(('generation','reference_repair','v3_review_1','v3_review_2','development_review_1','development_review_2')))
    audit_rows=[]
    for name in ('v3_ai_overlap_screen.csv','development_ai_overlap_screen.csv'):
        path=out/name
        if path.exists():
            import csv
            audit_rows.extend(csv.DictReader(path.open()))
    for r in audit_rows:r['scope']='Bounded automated/AI screening; nonexhaustive equivalence and pretraining exposure'
    csv_(out/'historical_overlap_audit.csv',audit_rows,['id','automated_flags','pretraining_contamination','scope'])
    dump(out/'development_resource_usage.json',usage(('development_initial','development_repairs')))
    from scientific_audit import recorded_analysis,permit,load_core
    data=[];analysis={'status':'NO_EXECUTED_DATA'}
    if (out/'development_gate_status.json').exists() and read(out/'development_gate_status.json')['status']=='READY_FOR_DEVELOPMENT':
        data,analysis=recorded_analysis();p=permit();core=load_core();root=out/'development_experiment';initials=[];diagnostics=[];arms={a:[] for a in ('C','D','E')};failures=[]
        for item in data:
            subject=next(c for c in p['records'] if c['id']==item['id'])
            for arm in ('A','C','D','E'):
                folder=root/'calls'/content_hash(core.key_for(p,subject,item['seed'],arm));cp=folder/'completion.json';vp=folder/'verification.json';completion=read(cp) if cp.exists() else None;verification=read(vp) if vp.exists() else None
                row=dict(id=item['id'],family=item['family'],seed=item['seed'],arm=arm,scope='DEVELOPMENT_ONLY',status=item[arm+'_generation_status'],source_checkpoint=str(folder.relative_to(HERE)),actual_completion=completion,verification=verification,strict_verified=verification.get('success') if verification else None,paired_eligible=item['comparison_valid'] and item['initial_success'] is False,paired_outcome=item.get(arm))
                if arm=='A':initials.append(row)
                else:arms[arm].append(row)
                if verification:
                    diagnostics.append(dict(id=item['id'],seed=item['seed'],arm=arm,candidate_sha256=verification.get('candidate_sha256'),success=verification.get('success'),failure_kind=verification.get('failure_kind'),diagnostics=verification.get('diagnostics'),source_checkpoint=str(folder.relative_to(HERE))))
                    if verification.get('success') is not True:failures.append(dict(id=item['id'],seed=item['seed'],arm=arm,success=verification.get('success'),failure_kind=verification.get('failure_kind'),errors=json.dumps(verification.get('errors'),ensure_ascii=False)))
        jsonl(out/'development_initial_candidates.jsonl',initials);jsonl(out/'development_diagnostics.jsonl',diagnostics)
        for arm,records in arms.items():jsonl(out/f'development_{arm}_results.jsonl',records)
        csv_(out/'development_compiler_failures.csv',failures,['id','seed','arm','success','failure_kind','errors'])
    else:
        dump(out/'development_execution_not_started.json',dict(status='BLOCKED',reason=read(out/'development_gate_status.json') if (out/'development_gate_status.json').exists() else 'Pending actual candidate gates',fabricated_or_synthetic_evaluation_rows=0))
    csv_(out/'development_paired_results.csv',data,list(data[0]) if data else ['id','family','seed','initial_success','C','D','E'])
    per_family=[]
    for family in sorted({r['family'] for r in data}):
        group=[r for r in data if r['family']==family];eligible=[r for r in group if r['initial_success'] is False]
        per_family.append(dict(family=family,types=len({r['id'] for r in group}),seeds=len(group),initial_verified=sum(r['initial_success'] is True for r in group),initial_unknown=sum(r['initial_success'] is None for r in group),known_initial_failures=len(eligible),**{a:dict(verified=sum(r[a] is True for r in eligible),unknown=sum(r[a] is None for r in eligible)) for a in ('C','D','E')}))
    dump(out/'development_per_family.json',per_family);dump(out/'development_paired_analysis.json',analysis)
    dump(out/'confirmatory_not_started.json',dict(status='NOT_STARTED',gate='NO_GO_RESOURCES',actual_calls=0,actual_test_types=0,reason='The researcher authorized only phases1–6 of the consolidated compute proposal; no fresh confirmatory construction, review or evaluation was authorized',future_requirement='Separate explicit confirmatory compute allocation plus prospectively frozen scientifically defensible untouched-family benchmark; no development examples or equivalents may be reused'))
    print('Derived evidence projections saved; no inference executed')

if __name__=='__main__':main()
