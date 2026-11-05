"""Separate-process consistency audit of actual new-scope evidence; no inference."""
from sprint_common import *
from reviews import evidence
from study_common import subject_hash
from fresh_review import parse_review

def audit():
    failures=[];warnings=[];checks={};stages={}
    def check(ok,label):
        checks[label]=checks.get(label,0)+1
        if not ok:failures.append(label)
    preservation=read(HERE/'preservation_manifest.json')
    for rel,r in preservation['files'].items():check((ROOT/rel).is_file() and sha(ROOT/rel)==r['sha256'],'historical_bytes_preserved')
    for rel,r in preservation['symlinks'].items():check((ROOT/rel).is_symlink() and os.readlink(ROOT/rel)==r['target'],'historical_symlinks_preserved')
    a=read(HERE/'resource_authorization.json');check(a['status']=='AUTHORIZED' and a['source']=='direct_user_reply' and a['exact_user_instruction']=='Expanded exploratory — 1,728 calls (Recommended)' and a['proposal_sha256']==sha(HERE/'COMPUTE_PROPOSAL.md'),'actual_fresh_user_authorization')
    total=0;validated=set()
    for stage,spec in a['stages'].items():
        out=RUN/stage;events=rows(out/'calls/budget.jsonl');total+=len(events);completed=0;inputs=outputs=0;latencies=[];peaks=[];started=[];finished=[]
        check(len(events)<=spec['max_calls'],'per_phase_cap');check(len({content_hash(e['key']) for e in events})==len(events),'no_duplicate_charged_keys')
        if stage.endswith('generation'):check(len({e['key']['key']['id'] for e in events})==len(events),'no_generation_candidate_resampled')
        for e in events:
            folder=out/'calls/calls'/content_hash(e['key']);intent=read(folder/'intent.json');binding=intent['binding'];locks=[binding['source_freeze_sha256']]
            for name in ('development_construction.json','development_prompt_v2.json','development_reviews.json','development_evaluation.json','test_construction.json','test_reviews.json','test_evaluation.json'):
                p=HERE/'freezes'/name
                expected=e['key']['key'].get('additional_source_freeze_sha256')
                if p.exists() and sha(p) in locks+[expected]:
                    if name not in validated:
                        try:frozen(name);check(True,'actual_used_freezes_match')
                        except (ValueError,FileNotFoundError):check(False,'actual_used_freeze_changed:'+name)
                        validated.add(name)
            check(binding['authorization_sha256']==sha(HERE/'resource_authorization.json') and content_hash(intent)==e['intent_sha256'],'intent_authority_and_hash')
            cp=folder/'completion.json'
            if not cp.exists():warnings.append('Unknown consumed intent: '+str(folder.relative_to(HERE)));continue
            r=read(cp)
            if r['status']!='completed':warnings.append('Unavailable response: '+str(folder.relative_to(HERE)));continue
            completed+=1;m=r['metadata'];inputs+=m['prompt_tokens'];outputs+=m['completion_tokens'];latencies.append(m['latency_seconds']);peaks.append(m['peak_memory_gb']);model=a['models'][spec['model_key']]
            check((folder/'raw_response.txt').read_bytes()==r['content'].encode(),'exact_raw_response_bytes')
            check(m['model']==model['id'] and m['snapshot_revision']==model['revision'] and m['base_seed']==e['key']['seed'],'actual_pinned_identity_and_base_seed')
            check(0<=m['completion_tokens']<=1200 and m['prompt_tokens']<=4096 and m['prompt_tokens']==intent['prompt_tokens_reserved'],'actual_token_caps')
            check(m['logical_generations']==1 and not m['retry_events'],'one_actual_generation_no_retries')
            start=read(folder/'call_started.json');end=read(folder/'call_finished.json');c=read(out/'phase_clock.json');started.append(start['epoch']);finished.append(end['epoch']);check(c==start['phase_clock'] and c['started_epoch']<=start['epoch']<=end['epoch']<=c['started_epoch']+c['max_runtime_seconds'],'original_clock_and_deadline')
            check(m['prompt_sha256']==intent['prompt_sha256'] and text_hash(m['rendered_chat_text'])==m['rendered_chat_sha256'],'prompt_rendered_chat_hashes')
            expected_seed=int.from_bytes(hashlib.sha256(f"{e['key']['seed']}:{m['generation_context']}:{m['prompt_sha256']}".encode()).digest()[:4],'big');check(expected_seed==m['generation_seed'],'actual_derived_seed_policy')
            traces=list((folder/'stream').glob('*.jsonl'));check(len(traces)==1,'one_stream_per_call')
            if len(traces)==1:
                trace=rows(traces[0]);check(''.join(x.get('text','') for x in trace)==r['content'] and trace[-1].get('status')=='generation_finished' and trace[-1]['completion_tokens']==m['completion_tokens'],'stream_and_finish_match_actual_response')
        stages[stage]=dict(charged=len(events),completed=completed,unknown=len(events)-completed,input_tokens_observed=inputs,output_tokens_observed=outputs,max_calls=spec['max_calls'],observed_call_latency_seconds=sum(latencies),reported_max_mlx_peak_memory_gb=max(peaks) if peaks else None,observed_first_call_epoch=min(started) if started else None,observed_last_call_epoch=max(finished) if finished else None,observed_call_span_seconds=max(finished)-min(started) if started else None,clock=read(out/'phase_clock.json') if (out/'phase_clock.json').exists() else None,status=read(out/'status.json') if (out/'status.json').exists() else 'NOT_STARTED')
    check(total<=1728,'total_approved_cap');check(not any('reference_repair' in p.name for p in RUN.iterdir()) if RUN.exists() else True,'no_unauthorized_reference_repair_phase')
    transition=RUN/'development_generation/prompt_v2_transition.json'
    if transition.exists():
        t=read(transition);now=rows(RUN/'development_generation/calls/budget.jsonl');check(now[:len(t['old_events'])]==t['old_events'],'old_generation_ledger_prefix_preserved');check(t['original_clock']==read(RUN/'development_generation/phase_clock.json'),'prompt_revision_did_not_reset_clock')
        lines=(RUN/'development_generation/records.jsonl').read_text().splitlines(keepends=True);check(text_hash(''.join(lines[:60]))==t['old_records_sha256'],'old_generation_outcomes_preserved')
    concerns=read(HERE/'mathematical_concerns.json')['items']
    source_audit=RUN/'development_pre_review_source_audit.json'
    if source_audit.exists():
        d=read(source_audit);check(d['dataset_sha256']==sha(RUN/'development_verified.json') and d['critical_concerns_sha256']==sha(HERE/'mathematical_concerns.json') and set(d['inspected_ids'])=={c['id'] for c in read(RUN/'development_verified.json')} and d['actor_kind']=='assistant_source_audit_not_human_validation','pre_review_source_inspection_exact_final_dataset')
    if (RUN/'development_ai_accepted.json').exists():check(not any(c['id']==x['id'] for c in read(RUN/'development_ai_accepted.json') for x in concerns),'no_critical_concern_in_eligible_acceptances')
    candidates={r['id']:r['candidate'] for r in rows(RUN/'development_generation/records.jsonl') if r.get('candidate')}
    for concern in concerns:
        c=candidates[concern['id']];c=dict(c,generated_family_label=c['family'],family=c['canonical_family'])
        check(concern['subject_sha256']==subject_hash(c) and concern['severity']=='critical' and concern['actor_kind']=='assistant_source_audit_not_human_validation','mathematical_concern_exact_subject_not_human_approval')
    for scope in ('development','test'):
        for r in rows(RUN/(scope+'_generation/records.jsonl')):
            if r.get('record',{}).get('status')=='completed':check(text_hash(r['prompt'])==r['prompt_sha256']==r['record']['metadata']['prompt_sha256'],'actual_generation_prompt_binding')
        for c in read(RUN/(scope+'_selected.json')) if (RUN/(scope+'_selected.json')).exists() else []:
            check(c['status']=='AI_SCREENED_FORMALLY_VERIFIED' and evidence(scope,c),'selected_actual_reference_evidence_AI_only');check(not any(x['id']==c['id'] for x in concerns),'no_selected_critical_semantic_concern')
        for i in (1,2):
            for r in rows(RUN/f'{scope}_review_{i}/reviews.jsonl'):
                if 'record' not in r:check(r['decision']=='UNCERTAIN','unissued_review_not_approval');continue
                cp=r['record']
                if cp['status']!='completed':check(r['decision']=='UNCERTAIN','unavailable_review_not_approval');continue
                check(read(HERE/r['source_call']/'completion.json')==cp and r['response_sha256']==text_hash(cp['content']),'review_actual_response_binding')
                try:parsed=parse_review(cp);check(parsed==r['review'] and parsed['decision']==r['decision'],'review_frozen_boolean_policy')
                except (ValueError,KeyError,TypeError):check(r['decision']=='UNCERTAIN' and r.get('parse_error'),'invalid_review_remains_uncertain')
    for r in rows(RUN/'formal_checks.jsonl'):
        folder=HERE/r['record_path'];check(read(folder/'verification.json')==r['result'],'actual_formal_checkpoint')
        check(read(folder/'verification_intent.json')==dict(candidate_sha256=r['source_sha256'],target_sha256=r['target_sha256']),'exact_formal_source_target')
        if r['result'].get('success') is True:check(r['result'].get('harness_variant')=='rigid_declaration_type_and_universe_v1' and r['result'].get('exit_code')==0 and r['result']['candidate_sha256']==r['source_sha256'],'actual_rigid_kernel_success')
    if any(stages[k]['charged'] for k in stages if k.startswith('test_')):check((RUN/'test_construction_go.json').exists(),'test_only_after_real_development_and_prospective_freeze')
    return dict(status='PASS_RECORDED_CONSISTENCY' if not failures else 'FAIL',failures=failures,warnings=warnings,checks=checks,actual_charged_calls=total,stages=stages,source_sha256=sha(Path(__file__)),scope='Internal source/data consistency; not external replication or exhaustive mathematical-equivalence certification')
if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path);a=p.parse_args();r=audit()
    if a.output:dump(a.output,r)
    print(json.dumps(r,indent=2));sys.exit(bool(r['failures']))
