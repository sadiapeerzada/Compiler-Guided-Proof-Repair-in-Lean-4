"""Analyze only the new completed DEV extension; descriptive, no hypothesis tests."""
from collections import Counter
import json
from pathlib import Path
import statistics
from .common import ROOT,OUT,read,write_csv,write_json,category
from .metrics import normalized_distance,targeted_fix,distinct_errors,transition_direction
from .statistics import wilson
from extensions.filename_normalization import feedback


def main():
    root=OUT/'dev_placebo'
    if not (root/'execution_finished.json').exists():raise ValueError('Dev execution has not reached its durable end marker; do not invent completion')
    protocol=read(ROOT/'extensions/placebo_protocol.json')
    from transformers import AutoTokenizer
    tokenizer=AutoTokenizer.from_pretrained(Path.home()/protocol['model']['snapshot_home_relative'],local_files_only=True,trust_remote_code=False)
    token_cache={}
    def tokens(code):
        if code not in token_cache:token_cache[code]=tokenizer.encode(code,add_special_tokens=False)
        return token_cache[code]
    cases=[];metrics=[];donors=[];incomplete=[];resources=[]
    for ident in protocol['development_ids']:
        folder=root/'runs'/ident;m=read(folder/'manifest.json')
        assert m['status'] in ['completed','incomplete']
        outcomes={c:m['conditions'].get(c,{}).get('success') for c in ['A','B','C','C_placebo']}
        cases.append({'id':ident,'family':m['family'],'outcomes':outcomes,'initial_success':m['initial']['verification']['success'] if m['initial'] else None})
        for cp in sorted(folder.glob('*/completion.json')):
            completion=read(cp);md=completion['metadata'];vp=cp.parent/'verification.json'
            resources.append({'id':ident,'key':cp.parent.name,'condition':('A_shared' if cp.parent.name=='shared_initial' else 'C_placebo' if cp.parent.name.startswith('placebo') else 'C' if cp.parent.name.startswith('real') else 'B'),
                'input_tokens':md['prompt_tokens'],'output_tokens':md['completion_tokens'],
                'generation_seconds':md['latency_seconds'],'model_call_wall_seconds':completion['model_call_wall_seconds'],
                'compiler_seconds':read(vp)['elapsed_seconds'] if vp.exists() else None,
                'cumulative_process_peak_rss_bytes':completion['rss_peak_bytes'],'native_mlx_peak_memory_gb':md.get('peak_memory_gb')})
        if m['initial'] is None:incomplete.append({'id':ident,'reason':'shared_initial_unavailable'});continue
        for c in ['B','C','C_placebo']:
            branch=m['conditions'][c];before=m['initial']
            if branch['success'] is None:incomplete.append({'id':ident,'condition':c,'reason':branch['status']})
            for index,after in enumerate(branch['attempts'],1):
                assert not before['verification']['success'] and index<=3
                a,b=before['candidate'],after['candidate'];v,w=before['verification'],after['verification']
                row={'id':ident,'family':m['family'],'condition':c,'repair_index':index,'initial_category':category(m['initial']['verification']),'identical':int(a.encode()==b.encode()),
                     'character_distance':normalized_distance(a,b),'token_distance':normalized_distance(tokens(a),tokens(b)),
                     'before_category':category(v),'after_category':category(w),'before_distinct_errors':distinct_errors(v),
                     'after_distinct_errors':distinct_errors(w),'input_tokens':after['prompt_tokens']}
                row['diagnostic_count_change']=row['after_distinct_errors']-row['before_distinct_errors'] if row['before_distinct_errors'] is not None and row['after_distinct_errors'] is not None else None
                own_feedback=feedback(v)
                row['own_predecessor_diagnostic_tokens']=len(tokens(own_feedback)) if own_feedback is not None else None
                row['supplied_feedback_tokens']=len(tokens(after['feedback_payload']))
                row['transition_direction']=transition_direction(row['before_category'],row['after_category']);row.update(targeted_fix(a,b,v,w));metrics.append(row)
                before=after
        for intent in sorted(folder.glob('placebo_repair_*/intent.json')):
            selection=read(intent).get('selection')
            if selection:donors.append({'id':ident,'repair_index':int(intent.parent.name.rsplit('_',1)[1]),
                'completed_response':(intent.parent/'completion.json').exists(),**selection})
    summaries={}
    for c in ['A','B','C','C_placebo']:
        observed=[r for r in cases if r['outcomes'][c] is not None];k=sum(r['outcomes'][c] for r in observed);repairs=[r for r in metrics if r['condition']==c]
        fields={}
        for field in ['identical','character_distance','token_distance','any_unknown_removed','all_unknown_removed','hallucinated_substitution','before_distinct_errors','after_distinct_errors','diagnostic_count_change','input_tokens','own_predecessor_diagnostic_tokens','supplied_feedback_tokens']:
            values=[r[field] for r in repairs if r.get(field) is not None];fields[field]={'n':len(values),'sum':sum(values),'mean':statistics.mean(values) if values else None,'median':statistics.median(values) if values else None}
        trajectories=[]
        for case in cases:
            group=[r for r in repairs if r['id']==case['id']]
            if group:trajectories.append({'any_identical':int(any(r['identical'] for r in group)),'all_identical':int(all(r['identical'] for r in group))})
        summaries[c]={'verified_successes':k,'observed_problems':len(observed),'unavailable':15-len(observed),'Wilson95_success_nominal':wilson(k,len(observed)),
                       'completed_repairs':len(repairs),'repair_metrics':fields,
                       'transition_directions':dict(Counter(r['transition_direction'] for r in repairs)),
                       'trajectory_repetition':{f:{'successes':sum(r[f] for r in trajectories),'eligible_trajectories':len(trajectories),
                                                   'Wilson95_nominal':wilson(sum(r[f] for r in trajectories),len(trajectories))} for f in ['any_identical','all_identical']},
                       'nonidentical_edits':{field:{'n':sum(not r['identical'] for r in repairs),'mean':statistics.mean(r[field] for r in repairs if not r['identical']) if any(not r['identical'] for r in repairs) else None} for field in ['character_distance','token_distance']}}
    real=summaries['C']['repair_metrics'];placebo=summaries['C_placebo']['repair_metrics']
    realfix=real['any_unknown_removed']['mean'];placebofix=placebo['any_unknown_removed']['mean'];realrepeat=real['identical']['mean'];placeborepeat=placebo['identical']['mean']
    if None in [realfix,placebofix,realrepeat,placeborepeat]:interpretation='Diagnostic-content sensitivity is not assessable on both predeclared process metrics because an eligible denominator is empty.'
    elif realfix>placebofix and realrepeat<placeborepeat:interpretation='The observed higher own-name removal and lower repetition under real diagnostics are consistent with diagnostic-content sensitivity. This exploratory one-seed pattern does not prove that the model uses diagnostic content.'
    elif realfix==placebofix and realrepeat==placeborepeat:interpretation='The two process metrics do not display diagnostic-content sensitivity in this small control; the identical descriptive values are not proof that content is ignored.'
    else:interpretation='The process metrics do not show a consistent directional diagnostic-content-sensitivity pattern; mixed descriptive differences are compatible with content sensitivity and sampling/seed variation, not proof of use or nonuse.'
    result={'post_hoc':True,'development_only':True,'problems':len(cases),'family_clusters':len({c['family'] for c in cases}),'seeds':[2027],
            'conditions':summaries,'incomplete':incomplete,'physical_completed_model_responses':len(list(root.glob('runs/*/*/completion.json'))),
            'logical_intents':len(list(root.glob('runs/*/*/intent.json'))),'donor_category_fallbacks':sum(r['category_fallback'] for r in donors),
            'donor_selections_including_missing':len(donors),'completed_donor_selections':sum(r['completed_response'] for r in donors),
            'diagnostic_length_match_abs_difference':{'mean':statistics.mean(r['token_length_difference'] for r in donors) if donors else None,'maximum':max((r['token_length_difference'] for r in donors),default=None)},
            'interpretation':interpretation,'limitations':['Exploratory n=15, only five curated dev families and one seed.','No hypothesis tests or proof of use/nonuse.',
                'Nominal problem-level Wilson intervals do not account for family dependence; repair-level metrics are descriptive counts only.',
                'B-before-C-before-placebo order and context-derived independent RNG streams can affect outcomes and timing.',
                'Placebo matching uses own error category/length, and different-problem diagnostics can still supply useful generic tactics.',
                'No new held-out model execution and no missing original C outcome was changed.']}
    write_csv(OUT/'post_hoc_dev_repair_metrics.csv',metrics);write_csv(OUT/'post_hoc_dev_donor_selections.csv',donors)
    write_csv(OUT/'post_hoc_dev_resources.csv',resources)
    resource_summary={}
    for c in ['A_shared','B','C','C_placebo']:
        group=[r for r in resources if r['condition']==c]
        resource_summary[c]={'physical_completed_calls':len(group)}
        for field in ['input_tokens','output_tokens','generation_seconds','model_call_wall_seconds','compiler_seconds','cumulative_process_peak_rss_bytes','native_mlx_peak_memory_gb']:
            values=[r[field] for r in group if r[field] is not None]
            resource_summary[c][field]={'n':len(values),'sum':sum(values),'mean':statistics.mean(values) if values else None,'maximum':max(values,default=None)}
            if field in ['cumulative_process_peak_rss_bytes','native_mlx_peak_memory_gb']:resource_summary[c][field].pop('sum')
    result['resources']=resource_summary
    result['resource_caveats']='Initial calls are physically shared once, not four times. RSS is cumulative process high-water telemetry within each worker session, not instantaneous per-call memory; it resets at resume, and native MLX telemetry is separately labeled. Memory peaks are not summed. Sequential order and weight reloads confound timing. Worker interruption/resume records are retained; time between separate worker sessions is not compute time.'
    grouped=[]
    for c in ['B','C','C_placebo']:
        for dimension in ['initial_category','repair_index']:
            for value in sorted({r[dimension] for r in metrics if r['condition']==c}):
                group=[r for r in metrics if r['condition']==c and r[dimension]==value]
                grouped.append({'condition':c,'dimension':dimension,'value':value,'identical':sum(r['identical'] for r in group),'completed_repairs':len(group),'repetition_fraction':statistics.mean(r['identical'] for r in group)})
    write_csv(OUT/'post_hoc_dev_grouped_repetition.csv',grouped)
    length_bins=[]
    for c in ['B','C','C_placebo']:
        group=[r for r in metrics if r['condition']==c]
        if not group:continue
        lengths=sorted(r['supplied_feedback_tokens'] for r in group)
        cut=[lengths[int((len(lengths)-1)*q)] for q in [.25,.5,.75]]
        for index in range(4):
            rows=[r for r in group if sum(r['supplied_feedback_tokens']>v for v in cut)==index]
            length_bins.append({'condition':c,'quartile_bin':index+1,'completed_repairs':len(rows),'identical':sum(r['identical'] for r in rows),'repetition_fraction':statistics.mean(r['identical'] for r in rows) if rows else None,'minimum_feedback_tokens':min((r['supplied_feedback_tokens'] for r in rows),default=None),'maximum_feedback_tokens':max((r['supplied_feedback_tokens'] for r in rows),default=None)})
    write_csv(OUT/'post_hoc_dev_feedback_length_bins.csv',length_bins)
    transitions=[]
    for c in ['B','C','C_placebo']:
        group=[r for r in metrics if r['condition']==c];counts=Counter((r['before_category'],r['after_category']) for r in group)
        transitions.extend({'condition':c,'before':a,'after':b,'completed_repairs':n} for (a,b),n in sorted(counts.items()))
    write_csv(OUT/'post_hoc_dev_transitions.csv',transitions);write_json(OUT/'post_hoc_dev_summary.json',result)
    from .render import table
    rows=[]
    for c,s in summaries.items():
        rep=s['repair_metrics']['identical'];fix=s['repair_metrics']['any_unknown_removed']
        rows.append([c,f"{s['verified_successes']}/{s['observed_problems']}",s['unavailable'],f"{rep['sum']}/{rep['n']}" if rep['n'] else 'NA',f"{fix['sum']}/{fix['n']}" if fix['n'] else 'NA'])
    table(OUT/'latex/post_hoc_dev_control.tex','Exploratory development-only placebo control (15 problems, one seed, five families). Repair denominators include completed repairs only; unknown-name removal is relative to each arm\x27s own preceding diagnostics. No hypothesis test or proof of diagnostic use.',
          ['Condition','Verified/observed','Missing','Identical repairs','Own-name removal'],rows)
    with (OUT/'SUMMARY.md').open('a') as stream:
        stream.write('\n## Completed exploratory development control\n\n')
        for c,s in summaries.items():stream.write(f"- {c}: {s['verified_successes']}/{s['observed_problems']} observed verified outcomes; {s['unavailable']} unavailable; {s['completed_repairs']} completed repairs.\n")
        stream.write('\n'+interpretation+'\n\nThese results are exploratory and development-only. Fifteen problems in five families and one seed do not support a general claim of diagnostic-content use or nonuse. Study 2 model execution remains deferred.\n')
    print(json.dumps({'conditions':{c:[s['verified_successes'],s['observed_problems']] for c,s in summaries.items()},'interpretation':interpretation},indent=2))


if __name__=='__main__':main()
