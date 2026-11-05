"""Read saved evidence in a separate process; never load inference models or spend calls.

PASS describes consistency of recorded evidence, not mathematical novelty or human
semantic validation. Missing/interrupted outcomes remain unknown.
"""
import argparse, importlib.util, subprocess
from types import SimpleNamespace
from study_common import *

def load_core():
    spec=importlib.util.spec_from_file_location('audit_recorded_core',LEGACY/'isolated_repair_runner.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module

def actual_prompt(stage,key):
    """Recover exact saved/frozen prompt; its pre-inference intent hash must match."""
    if stage=='generation':
        from generation_prompts import generation_prompt
        return generation_prompt(key['key']['index'])
    if stage=='reference_repair':
        records=rows(run_root()/stage/'records.jsonl')
        matches=[r['prompt'] for r in records if r['index']==key['key']['index'] and 'prompt' in r]
        if matches:return matches[0]
        original=next(r for r in read(run_root()/'reference_candidate_pool_v2.json') if r['index']==key['key']['index'])
        if key['key'].get('prompt_version')=='v4':
            from reference_repair_v4 import prompt
            return prompt(original['candidate'],original['verification'])
        from generation_prompts import repair_prompt
        return repair_prompt(original['candidate'],original['verification'])
    if 'review' in stage:
        v3=stage.startswith('v3_');subjects=read(run_root()/('v3_input.json' if v3 else 'fresh_verified.json'))
        c=next(c for c in subjects if c['id']==key['key']['id'])
        if v3:
            from review_protocol import review_prompt
            return review_prompt(c)
        from fresh_review import prompt
        return prompt(c)
    from matching import initial_prompt
    outer=key['key']['outer_key'];c=next(c for c in read(run_root()/'accepted_development.json') if c['id']==outer['id'])
    if outer['arm']=='A':return initial_prompt(c)
    return read(run_root()/'development_experiment/cases'/content_hash([outer['id'],outer['seed']])/'matching.json')['conditions'][outer['arm']]['prompt']

def permit():
    p=read(run_root()/'development_protocol.json');data=read(run_root()/'accepted_development.json')
    return dict(phase='development',protocol=p,protocol_sha256=sha(run_root()/'development_protocol.json'),source_lock_sha256=sha(HERE/'freezes/development_CDE_v1.json'),records=data,authorization=dict(actor_kind='researcher_resource_authority',source='actual consolidated phases1–6 approval; not human mathematical adjudication',resource_limits=dict(max_calls=240,max_runtime_seconds=64800)),manifest={'development':{'sha256':sha(run_root()/'accepted_development.json')}})

def recorded_analysis():
    """Recollect all planned rows, even if a deadline prevented the first call."""
    core=load_core();p=permit();root=run_root()/'development_experiment'
    binding=read(root/'run.json')['binding'] if (root/'run.json').exists() else {}
    store=SimpleNamespace(root=root,binding=binding,events=lambda:rows(root/'budget.jsonl'))
    data=core.collect(store,p)
    analysis=core.analyze(data,replicates=p['protocol']['statistics']['replicates'],seed=p['protocol']['statistics']['bootstrap_seed'],expected_keys=[(r['id'],s) for r in p['records'] for s in p['protocol']['seeds']],expected_phase='development',expected_model_revision=p['protocol']['model']['revision'])
    return data,analysis

def audit():
    failures=[];warnings=[];checks={};stages={}
    def check(ok,label):
        checks[label]=checks.get(label,0)+1
        if not ok:failures.append(label)
    baseline=read(HERE/'preservation_manifest.json')
    for rel,h in baseline['files'].items():check((ROOT/rel).is_file() and sha(ROOT/rel)==h,'historical_file_hashes_unchanged')
    tree=subprocess.check_output(['git','ls-tree','-rz',baseline['baseline']],cwd=ROOT).split(b'\0')
    for entry in tree:
        if not entry or not entry.startswith(b'120000 '):continue
        metadata,path=entry.split(b'\t',1);rel=path.decode();original=subprocess.check_output(['git','show',baseline['baseline']+':'+rel],cwd=ROOT).decode()
        check((ROOT/rel).is_symlink() and os.readlink(ROOT/rel)==original,'historical_symlink_targets_unchanged')
    used={'generation':'generation_v1.json','v3_review_1':'review_v2.json','v3_review_2':'review_v2.json','reference_repair':'reference_construction_v3.json','development_review_1':'fresh_review_v1.json','development_review_2':'fresh_review_v1.json','development_initial':'development_CDE_v1.json','development_repairs':'development_CDE_v1.json'}
    checked=set();total=0;cde_configs=set()
    for stage,spec in read(HERE/'resource_authorization.json')['stages'].items():
        authorize(stage);folder=run_root()/stage;ledger=rows(folder/'calls/budget.jsonl');total+=len(ledger)
        check(len(ledger)<=spec['max_calls'],'per_phase_call_caps')
        check(len({content_hash(r['key']) for r in ledger})==len(ledger),'no_duplicate_charged_keys')
        if stage=='reference_repair':check(len({r['key']['key']['id'] for r in ledger})==len(ledger),'at_most_one_reference_repair_per_candidate')
        tokenizer=None
        if ledger:
            from transformers import AutoTokenizer
            model=protocol()['models'][spec['model_key']];view=HERE/'model_views'/(model['revision']+'.json')
            snapshot=HERE/read(view)['view_path'] if view.exists() else Path.home()/'.cache/huggingface/hub'/model['cache_name']/'snapshots'/model['revision']
            tokenizer=AutoTokenizer.from_pretrained(str(snapshot),local_files_only=True,trust_remote_code=False)
        if ledger and used[stage] not in checked:
            try:frozen(used[stage]);check(True,'used_source_and_input_freezes_unchanged')
            except (ValueError,FileNotFoundError):check(False,'used_source_and_input_freezes_unchanged:'+used[stage])
            checked.add(used[stage])
        completed=0;input_sum=0;output_sum=0
        for event in ledger:
            extra=event['key'].get('key',{}).get('additional_source_freeze_sha256')
            if extra:
                check(extra==sha(HERE/'freezes/reference_prompt_v4.json'),'new_repair_prompt_intent_additional_freeze_binding')
                if 'reference_prompt_v4.json' not in checked:
                    try:frozen('reference_prompt_v4.json');check(True,'used_source_and_input_freezes_unchanged')
                    except (ValueError,FileNotFoundError):check(False,'used_source_and_input_freezes_unchanged:reference_prompt_v4.json')
                    checked.add('reference_prompt_v4.json')
            call=folder/'calls/calls'/content_hash(event['key'])
            if not (call/'intent.json').exists():
                warnings.append('Charged reservation without durable intent: '+str(call.relative_to(HERE)));continue
            intent=read(call/'intent.json');prompt=actual_prompt(stage,event['key'])
            check(content_hash(intent)==event['intent_sha256'],'durable_intent_hashes')
            check(text_hash(prompt)==intent['prompt_sha256'],'exact_prompt_hashes')
            rendered=tokenizer.apply_chat_template([{'role':'user','content':prompt}],tokenize=False,add_generation_prompt=True)
            check(len(tokenizer.encode(rendered,add_special_tokens=False))==intent['prompt_tokens_reserved'],'independently_recounted_rendered_input_tokens')
            check(intent['prompt_tokens_reserved']<=4096 and intent['output_tokens_reserved']==1200,'reserved_token_caps')
            check(intent['key']==event['key'],'intent_key_binding')
            cp=call/'completion.json'
            if not cp.exists():warnings.append('Unknown consumed intent: '+str(call.relative_to(HERE)));continue
            c=read(cp)
            if c['status']!='completed':warnings.append('Unavailable completion: '+str(call.relative_to(HERE)));continue
            completed+=1;m=c['metadata'];input_sum+=m['prompt_tokens'];output_sum+=m['completion_tokens'];model=protocol()['models'][spec['model_key']]
            check((call/'raw_response.txt').read_bytes()==c['content'].encode(),'raw_response_bytes_match_completion')
            check(m['prompt_sha256']==text_hash(prompt),'model_prompt_hash_binding')
            check(m['rendered_chat_text']==rendered and m['rendered_chat_sha256']==text_hash(rendered),'actual_rendered_chat_matches_pinned_tokenizer')
            check(m['model']==model['id'] and m['snapshot_revision']==model['revision'],'actual_model_identity')
            check(m['temperature']==.2 and m['top_p']==1.0,'actual_fixed_decoding_configuration')
            if stage in ('development_initial','development_repairs'):cde_configs.add((m['model'],m['snapshot_revision'],m['temperature'],m['top_p'],m['max_completion_tokens'],m['mlx_version'],m['mlx_lm_version'],m['chat_template_sha256']))
            check(m['prompt_tokens']<=4096 and m['completion_tokens']<=1200 and m['max_completion_tokens']==1200,'actual_token_caps')
            if stage=='development_repairs':check(m['prompt_tokens']==4096,'actual_CDE_inputs_exactly_4096_tokens')
            check(m['logical_generations']==1 and not m['retry_events'],'one_actual_generation_per_charged_completion')
            started=read(call/'call_started.json');ended=read(call/'call_finished.json');clock_record=read(folder/'phase_clock.json')
            check(started['phase_clock']==clock_record,'original_phase_clock_preserved')
            check(clock_record['started_epoch']<=started['epoch']<=ended['epoch']<=clock_record['started_epoch']+clock_record['max_runtime_seconds'],'actual_call_times_within_phase_deadline')
            streams=list((call/'stream').glob('*.jsonl'));check(len(streams)==1,'one_stream_per_actual_completion')
            if len(streams)==1:
                trace=rows(streams[0]);check(''.join(t.get('text','') for t in trace)==c['content'],'stream_text_matches_raw_response')
                check(trace[-1].get('status')=='generation_finished' and trace[-1].get('completion_tokens')==m['completion_tokens'],'stream_finish_and_token_count')
        status_path=folder/('status_v2.json' if stage.startswith('v3_review') else 'status.json')
        if stage in ('development_initial','development_repairs'):status_path=run_root()/'development_experiment/status.json'
        stages[stage]=dict(charged=len(ledger),completed=completed,unknown_or_unavailable=len(ledger)-completed,input_tokens_observed=input_sum,output_tokens_observed=output_sum,max_calls=spec['max_calls'],phase_status=read(status_path)['status'] if status_path.exists() else 'NOT_STARTED' if not ledger else 'IN_PROGRESS_OR_INTERRUPTED')
    check(total<=1084,'consolidated_development_call_cap')
    check(len(cde_configs)<=1,'same_CDE_model_decoding_runtime_and_chat_template')
    transition=run_root()/'reference_repair/prompt_v4_transition.json'
    if transition.exists():
        t=read(transition);current=rows(run_root()/'reference_repair/calls/budget.jsonl')
        check(current[:len(t['original_charged_events'])]==t['original_charged_events'],'old_repair_ledger_prefix_preserved_across_prompt_change')
        check(read(run_root()/'reference_repair/phase_clock.json')==t['original_phase_clock'],'repair_prompt_change_did_not_reset_deadline')
    check(sum(stages[s]['charged'] for s in ('v3_review_1','development_review_1'))<=242 and sum(stages[s]['charged'] for s in ('v3_review_2','development_review_2'))<=242,'separate_reviewer_aggregate_caps')
    for stage in ('confirmatory_generation','confirmatory_review_1','confirmatory_review_2','confirmatory_initial','confirmatory_repairs','test'):
        check(not (run_root()/stage).exists(),'no_unauthorized_confirmatory_phase')
    formal=rows(run_root()/'strict_reference_verification.jsonl')
    for r in formal:
        folder=HERE/r['record_path'];vp=folder/'verification.json';intent=read(folder/'verification_intent.json')
        if not vp.exists() and r['result'].get('success') is None:warnings.append('Consumed formal intent without durable outcome: '+r['record_path'])
        else:check(vp.exists() and read(vp)==r['result'],'formal_log_matches_actual_verification_checkpoint')
        check(intent==dict(candidate_sha256=r['source_sha256'],target_sha256=r['target_sha256']),'formal_intent_exact_source_target_binding')
        result=r['result']
        if isinstance(result.get('verification_source_text'),str):check(text_hash(result['verification_source_text'])==result['verification_source_sha256'],'actual_compiled_harness_text_hash')
        elif result.get('success') is True:check(False,'successful_formal_check_has_saved_compiled_source')
        if result.get('success') is True:check(result.get('candidate_sha256')==r['source_sha256'] and result.get('exit_code')==0,'actual_formal_success_source_and_exit_code')
    for name in ('fresh_verified_raw_v2.json','fresh_verified.json'):
        for c in read(run_root()/name) if (run_root()/name).exists() else []:
            check(text_hash(c['reference_proof'])==c['proof_sha256'],'curated_reference_exact_source_hash')
            check(any(r['id']==c['id'] and r['source_sha256']==c['proof_sha256'] and r['target_sha256']==c['statement_sha256'] and r['result'].get('success') is True and r['result'].get('harness_variant')=='rigid_declaration_type_and_universe_v1' and r['result'].get('rigid_variant_source_sha256')==sha(HERE/'rigid_verifier.py') for r in formal),'curated_reference_has_real_rigid_success')
    for prefix,review_stages in (('v3_ai',('v3_review_1','v3_review_2')),('development_ai',('development_review_1','development_review_2'))):
        path=run_root()/(prefix+'_accepted_candidates.json')
        for c in read(path) if path.exists() else []:
            for stage in review_stages:
                record=next((r for r in rows(run_root()/stage/'reviews.jsonl') if r['id']==c['id']),None)
                check(record is not None,'accepted_subject_has_both_real_reviews')
                if record is None:continue
                check(record['subject_sha256']==subject_hash(c) and record['decision']=='ACCEPT' and not record.get('parse_error'),'accepted_subject_review_binding')
                if stage.startswith('v3_'):
                    from review_protocol import parse_review
                else:
                    from fresh_review import parse_review
                try:check(parse_review(record['record'])['decision']=='ACCEPT','accepted_raw_review_satisfies_frozen_policy')
                except (ValueError,KeyError):check(False,'accepted_raw_review_satisfies_frozen_policy')
    if (HERE/'freezes/development_CDE_v1.json').exists():
        from development_experiment import gate
        g=gate();check(g['status'] in ('READY_FOR_DEVELOPMENT','NO_GO_DATA'),'development_gate_actual_source_bound_evidence')
        if g['status']=='READY_FOR_DEVELOPMENT':
            data,analysis=recorded_analysis();p=permit();core=load_core();root=run_root()/'development_experiment';byid={r['id']:r for r in p['records']}
            from matching import repair_prompt,NEUTRAL,donor_order,planned_orders
            from development_experiment import available_diagnostic as diagnostic_payload
            orders=planned_orders(p['records'],p['protocol']['seeds'],p['protocol']['order_seed'])
            initial_finishes=[];repair_starts=[]
            for stage,bag in (('development_initial',initial_finishes),('development_repairs',repair_starts)):
                for event in rows(run_root()/stage/'calls/budget.jsonl'):
                    call=run_root()/stage/'calls/calls'/content_hash(event['key']);time_file=call/('call_finished.json' if stage=='development_initial' else 'call_started.json')
                    if time_file.exists():bag.append(read(time_file)['epoch'])
            if repair_starts:check(len(initial_finishes)==len(data) and max(initial_finishes)<=min(repair_starts),'all_initial_completions_frozen_before_any_repair')
            for r in data:
                row=byid[r['id']];seed=r['seed'];case=root/'cases'/content_hash([row['id'],seed])/'matching.json'
                for arm in ('A','C','D','E'):
                    folder=root/'calls'/content_hash(core.key_for(p,row,seed,arm));vp=folder/'verification.json'
                    if not vp.exists():continue
                    verification=read(vp)
                    if verification.get('success') is True:
                        check(verification.get('harness_variant')=='rigid_declaration_type_and_universe_v1' and verification.get('rigid_variant_source_sha256')==sha(HERE/'rigid_verifier.py'),'actual_CDE_success_uses_rigid_verifier')
                        source=core.extract(read(folder/'completion.json')['content']);check(verification['candidate_sha256']==text_hash(source),'actual_CDE_success_exact_candidate_hash')
                if not case.exists() or not read(case)['valid']:continue
                match=read(case);donor=byid[match['donor_id']];check(donor['family']!=row['family'],'donor_mathematical_family_disjoint')
                def call(arm,theorem=row):return root/'calls'/content_hash(core.key_for(p,theorem,seed,arm))
                predecessor=(call('A')/'candidate.lean').read_text() if (call('A')/'candidate.lean').exists() else core.extract(read(call('A')/'completion.json')['content'])
                donor_source=core.extract(read(call('A',donor)/'completion.json')['content']);real_v=read(call('A')/'verification.json');donor_v=read(call('A',donor)/'verification.json')
                real=diagnostic_payload(real_v,predecessor);shuffled=diagnostic_payload(donor_v,donor_source)
                check(real is not None and shuffled is not None and real!=shuffled,'genuine_distinct_candidate_bound_diagnostics')
                expected_donor=None
                for donor_id in donor_order(row,p['records'],seed,p['protocol']['forbidden_donor_pairs']):
                    donor_folder=call('A',byid[donor_id]);cp=donor_folder/'completion.json';vp=donor_folder/'verification.json'
                    if not cp.exists() or not vp.exists():continue
                    source=core.extract(read(cp)['content']);payload=diagnostic_payload(read(vp),source)
                    if payload is not None and payload!=real:expected_donor=donor_id;break
                check(match['donor_id']==expected_donor,'predeclared_first_eligible_distinct_donor')
                check(match['order']==orders[row['id'],seed],'predeclared_counterbalanced_orders')
                check(match['predecessor_sha256']==text_hash(predecessor),'same_frozen_failed_predecessor')
                for arm,payload in zip(('C','D','E'),(real,shuffled,NEUTRAL)):
                    m=match['conditions'][arm];expected=repair_prompt(row,predecessor,payload,' [PAD]'*m['padding_markers']+m['padding_suffix'])
                    check(m['prompt']==expected and m['prompt_tokens']==4096 and m['truncated'] is False,'matched_full_payload_exact_4096_controls')
                    check(not any(c['reference_proof'] in m['prompt'] for c in p['records']),'no_reference_proof_leak')
                    if (call(arm)/'completion.json').exists():
                        check(read(call(arm)/'intent.json')['prompt_sha256']==text_hash(m['prompt']),'actual_CDE_prompt_matches_frozen_plan')
                        bind=read(call(arm)/'inner_call_binding.json');inner=HERE/bind['inner_call'];check(bind['stage']=='development_repairs' and read(inner/'completion.json')['content']==read(call(arm)/'completion.json')['content'],'outer_checkpoint_matches_actual_inner_inference')
            export=root/'exports'/content_hash(data)
            if (export/'analysis.json').exists():
                recorded=read(export/'analysis.json');check(read(export/'rows.json')==data,'rows_regenerated_from_actual_checkpoints')
                check(all(recorded.get(k)==v for k,v in analysis.items()),'paired_statistics_independently_regenerated')
            elif (root/'status.json').exists():check(False,'final_recorded_export_exists')
            else:warnings.append('C/D/E export not yet final; audit is interim')
    return dict(status='PASS_RECORDED_CONSISTENCY' if not failures else 'FAIL',scope='Internal evidence consistency only; not independent semantic/human validation or exhaustive novelty',failures=failures,warnings=warnings,checks=checks,actual_model_call_total=total,stages=stages,confirmatory='NOT_STARTED_NO_AUTHORIZATION',historical_baseline=baseline['baseline'],audit_source_sha256=sha(Path(__file__)))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path);args=parser.parse_args();result=audit()
    if args.output:dump(args.output,result)
    print(json.dumps(result,indent=2));sys.exit(bool(result['failures']))
