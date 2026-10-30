"""Existing held-out data only: completed-repair behavior, explicitly post hoc."""
from collections import Counter,defaultdict
import json
import statistics
import numpy as np
from .common import ROOT,OUT,STUDY,read,load_originals,write_json,write_csv,category
from .metrics import normalized_distance,targeted_fix,distinct_errors,transition_direction
from .statistics import bootstrap_difference


def summarize(rows,fields):
    result={}
    for key in fields:
        vals=[r[key] for r in rows if r.get(key) is not None]
        result[key]={'n':len(vals),'mean':statistics.mean(vals) if vals else None,'median':statistics.median(vals) if vals else None,
                     'sum':sum(vals) if vals else None,'minimum':min(vals) if vals else None,'maximum':max(vals) if vals else None}
    return result


def main():
    cases,repairs,calls=load_originals();p=read(ROOT/'configs/repair_experiment_local_v0.4.2.json')
    from transformers import AutoTokenizer
    from pathlib import Path
    tokenizer=AutoTokenizer.from_pretrained(Path.home()/p['model']['snapshot_home_relative'],local_files_only=True,trust_remote_code=False)
    token_cache={}
    def tokens(code):
        if code not in token_cache:token_cache[code]=tokenizer.encode(code,add_special_tokens=False)
        return token_cache[code]
    records=[]
    for r in repairs:
        before=r['before'];after=r['after'];a,b=before['candidate'],after['candidate'];v,w=before['verification'],after['verification']
        diagnostics=[d for d in v.get('diagnostics') or [] if d.get('kind')!='hasSorry']
        feedback=json.dumps({'diagnostic_state':'available','diagnostics':diagnostics},ensure_ascii=False,indent=2)
        if r['condition']=='C' and feedback!=after['feedback_payload']:raise ValueError('Predecessor diagnostic mismatch')
        row={k:r[k] for k in ['id','family','condition','repair_index','initial_category']}
        row.update(identical=int(a.encode()==b.encode()),character_distance=normalized_distance(a,b),token_distance=normalized_distance(tokens(a),tokens(b)),
                   before_category=category(v),after_category=category(w),before_distinct_errors=distinct_errors(v),after_distinct_errors=distinct_errors(w),
                   input_tokens=after['prompt_tokens'],diagnostic_tokens=len(tokens(feedback)),compiler_feedback_exposed=r['condition']=='C')
        row['diagnostic_count_change']=row['after_distinct_errors']-row['before_distinct_errors'] if row['before_distinct_errors'] is not None and row['after_distinct_errors'] is not None else None
        row['transition_direction']=transition_direction(row['before_category'],row['after_category']);row.update(targeted_fix(a,b,v,w));records.append(row)
    write_csv(OUT/'post_hoc_repair_metrics.csv',records)
    repetitions=[]
    for dimension in ['overall','initial_category','repair_index']:
        levels=['all'] if dimension=='overall' else sorted({r[dimension] for r in records})
        for value in levels:
            for condition in ['B','C']:
                group=[r for r in records if r['condition']==condition and (dimension=='overall' or r[dimension]==value)]
                repetitions.append({'grouping':dimension,'group':value,'condition':condition,'identical':sum(r['identical'] for r in group),'completed_repairs':len(group),
                                    'fraction':sum(r['identical'] for r in group)/len(group) if group else None})
    write_csv(OUT/'post_hoc_repetition.csv',repetitions)
    trajectories=[]
    for case in cases:
        for condition in ['B','C']:
            group=[r for r in records if r['id']==case['id'] and r['condition']==condition]
            if group:trajectories.append({'id':case['id'],'family':case['family'],'condition':condition,'completed_repairs':len(group),
                                         'any_identical':int(any(r['identical'] for r in group)),'all_identical':int(all(r['identical'] for r in group))})
    write_csv(OUT/'post_hoc_trajectory_repetition.csv',trajectories)
    comparisons={}
    for metric in ['identical','character_distance','token_distance','any_unknown_removed','all_unknown_removed','hallucinated_substitution','diagnostic_count_change']:
        comparisons[metric]={unit:bootstrap_difference(records,metric,unit) for unit in ['family','id']}
    for metric in ['character_distance','token_distance']:
        comparisons[metric+'_excluding_identical']={unit:bootstrap_difference([r for r in records if not r['identical']],metric,unit) for unit in ['family','id']}
    for metric in ['any_identical','all_identical']:comparisons['trajectory_'+metric]={'family':bootstrap_difference(trajectories,metric,'family')}
    fields=['identical','character_distance','token_distance','input_tokens','diagnostic_tokens','before_distinct_errors','after_distinct_errors','diagnostic_count_change',
            'unknown_prior_n','unknown_removed_n','any_unknown_removed','all_unknown_removed','unknown_newly_introduced_n','hallucinated_substitution']
    summary={c:summarize([r for r in records if r['condition']==c],fields) for c in ['B','C']}
    for c in ['B','C']:
        summary[c]['trajectory_metrics']=summarize([r for r in trajectories if r['condition']==c],['any_identical','all_identical'])
        group=[r for r in records if r['condition']==c and r['unknown_prior_n']>0]
        summary[c]['targeted_name_pair_denominator']=sum(r['unknown_prior_n'] for r in group)
        summary[c]['targeted_removed_name_pairs']=sum(r['unknown_removed_n'] for r in group)
        summary[c]['excluding_identical']=summarize([r for r in records if r['condition']==c and not r['identical']],['character_distance','token_distance'])
    transitions=[];directions=[]
    categories=['syntax_or_parser','unknown_identifier_or_name','type_mismatch_or_elaboration','tactic_or_unsolved_goal','other_compiler_error','verified','guard/infra/incomplete']
    for c in ['B','C']:
        group=[r for r in records if r['condition']==c];counter=Counter((r['before_category'],r['after_category']) for r in group)
        for before in categories:
            transitions.append({'condition':c,'before':before,**{after:counter[(before,after)] for after in categories}})
        for direction in ['advanced','same_category','regressed','verified','unranked']:
            n=sum(r['transition_direction']==direction for r in group);directions.append({'condition':c,'direction':direction,'repairs':n,'denominator':len(group),'fraction':n/len(group)})
    write_csv(OUT/'post_hoc_error_transitions.csv',transitions);write_csv(OUT/'post_hoc_transition_directions.csv',directions)
    c_records=[r for r in records if r['condition']=='C'];cuts=np.quantile([r['diagnostic_tokens'] for r in c_records],[.25,.5,.75]);bins=[]
    for index in range(4):
        group=[r for r in c_records if int(np.searchsorted(cuts,r['diagnostic_tokens'],side='left'))==index]
        bins.append({'quartile_bin':index+1,'completed_repairs':len(group),'identical':sum(r['identical'] for r in group),
                     'repetition_fraction':statistics.mean(r['identical'] for r in group) if group else None,
                     'diagnostic_tokens_min':min((r['diagnostic_tokens'] for r in group),default=None),'diagnostic_tokens_max':max((r['diagnostic_tokens'] for r in group),default=None)})
    write_csv(OUT/'post_hoc_prompt_length_bins.csv',bins)
    length=np.array([r['diagnostic_tokens'] for r in c_records]);repeat=np.array([r['identical'] for r in c_records]);correlation=float(np.corrcoef(length,repeat)[0,1]) if np.std(length)>0 and np.std(repeat)>0 else None
    result={'post_hoc':True,'heldout_model_calls':0,'completed_repairs':len(records),'per_condition':summary,'C_minus_B':comparisons,
            'prompt_length_descriptive':{'C_diagnostic_tokens_vs_identical_Pearson':correlation,'quartile_cutpoints':cuts.tolist(),'ties_can_make_bins_unequal':True,'causal_or_significance_claim':False},
            'unknown_name_parser':'Structured name fields preferred; original lean.unknownIdentifier._namedError lacks name fields, so parse backtick identifier from structured data only.',
            'token_distance':'Exact frozen Qwen tokenizer token IDs; Levenshtein / max sequence length, including whitespace information. Character metric uses Unicode code points.',
            'observational_limits':['Post hoc; correlated families; single seed; repeated repairs are not independent units.','C has two missing trajectories; denominators are completed repairs only.','B unknown-name diagnostics are analyst-only chance baseline, never sent to B.','Name removal is syntactic; fewer diagnostics or later category need not be mathematical progress.','C prompts are longer; category, length and failure difficulty confound descriptive relations.']}
    write_json(OUT/'post_hoc_task1.json',result)
    print(json.dumps({'B_repetition':summary['B']['identical'],'C_repetition':summary['C']['identical'],'cluster_C_minus_B':comparisons['identical']['family']},indent=2))


if __name__=='__main__':main()
