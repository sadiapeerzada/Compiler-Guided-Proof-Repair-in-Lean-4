"""Step 0: post-hoc reconciliation directly against original per-attempt records."""
from collections import Counter
import json
import statistics
from .common import ROOT,OUT,read,load_originals,write_csv,write_json


def main():
    cases,repairs,calls=load_originals();rows=[]
    def check(metric,actual,reported,source):
        same=abs(actual-reported)<1e-6 if isinstance(actual,(int,float)) else actual==reported
        rows.append({'metric':metric,'recomputed':actual,'reported':reported,'matches':same,'reported_source':source})
    paired=[c for c in cases if c['outcomes']['B'] is not None and c['outcomes']['C'] is not None]
    for condition,success,denominator in [('A',0,60),('B',1,60),('C',1,58)]:
        observed=[c for c in cases if c['outcomes'][condition] is not None]
        check(condition+'_success',sum(c['outcomes'][condition] for c in observed),success,'paper/main.tex')
        check(condition+'_observed_denominator',len(observed),denominator,'paper/main.tex')
    for metric,actual,expected in [('complete_BC_pairs',len(paired),58),('paired_family_clusters',len({c['family'] for c in paired}),52),
            ('full_test_families',len({c['family'] for c in cases}),54),('logical_intents',sum(len(c['intents']) for c in cases),412),
            ('completed_responses',len(calls),410),('shared_initial_responses',sum(c['condition']=='A' for c in calls),60),
            ('B_completed_repairs',sum(r['condition']=='B' for r in repairs),178),('C_completed_repairs',sum(r['condition']=='C' for r in repairs),172),
            ('C_repair_intents',sum(p.parent.name.startswith('C') for c in cases for p in c['intents']),174),
            ('unique_input_tokens',sum(c['prompt_tokens'] for c in calls),362035),('unique_output_tokens',sum(c['completion_tokens'] for c in calls),130401)]:check(metric,actual,expected,'paper/main.tex')
    counts=Counter(c['initial_category'] for c in cases)
    for key,expected in [('other_compiler_error',1),('syntax_or_parser',26),('tactic_or_unsolved_goal',9),('type_mismatch_or_elaboration',4),('unknown_identifier_or_name',20)]:
        check('Table3_'+key,counts[key],expected,'paper/generated/review_v2/table3.tex')
    missing=Counter(c['initial_category'] for c in cases if c['outcomes']['C'] is None)
    check('C_missing_parser',missing['syntax_or_parser'],1,'paper/generated/review_v2/table3.tex');check('C_missing_tactic',missing['tactic_or_unsolved_goal'],1,'paper/generated/review_v2/table3.tex')
    expected=read(ROOT/'data/final_review/20261029_v2/analysis_verified/results.json')
    for condition in ['A','B','C']:
        group=[c for c in calls if c['condition']=='A' or c['condition']==condition]
        for field,oldfield in [('prompt_tokens','prompt_tokens'),('completion_tokens','completion_tokens'),('wall_seconds','call_wall_seconds'),('generation_seconds','generation_seconds')]:
            check(condition+'_mean_'+field,statistics.mean(c[field] for c in group),expected['conditions'][condition]['resources'][oldfield]['mean'],'paper/generated/review_v2/resources.tex (underlying precision)')
    for condition,expected_identical in [('B',90),('C',70)]:
        check(condition+'_byte_identical_repairs',sum(r['before']['candidate']==r['after']['candidate'] for r in repairs if r['condition']==condition),expected_identical,'earlier draft post-hoc count')
    write_csv(OUT/'reconciliation.csv',rows)
    mismatch=[r for r in rows if not r['matches']]
    write_json(OUT/'reconciliation_summary.json',{'post_hoc':True,'original_sources_used':True,'publication_views_used':False,'checks':len(rows),'mismatches':mismatch,
        'missing_C_ids':[c['id'] for c in cases if c['outcomes']['C'] is None],'solved_ids':[c['id'] for c in cases if c['outcomes']['B'] is True or c['outcomes']['C'] is True]})
    print(json.dumps({'checks':len(rows),'mismatches':mismatch,'observed_A':[0,60],'observed_B':[1,60],'observed_C':[1,58],
                      'complete_pairs':len(paired),'completed_responses':len(calls),'B_identical':90,'C_identical':70},indent=2))
    if mismatch:raise SystemExit('Reconciliation mismatch; investigate before further analysis')


if __name__=='__main__':main()
