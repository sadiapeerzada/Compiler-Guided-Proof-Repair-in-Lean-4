"""Post-hoc calibration of the null result; no model execution or imputation."""
import json
from .common import OUT,load_originals,write_json,write_csv
from .statistics import bootstrap_difference,newcombe_paired,mcnemar,identification_bounds,approximate_mde,exact_mde,exact_power


def main():
    cases,_,_=load_originals();results=[]
    for first,second in [('C','B'),('C','A'),('B','A')]:
        group=[r for r in cases if r['outcomes'][first] is not None and r['outcomes'][second] is not None]
        a=sum(r['outcomes'][first] and r['outcomes'][second] for r in group)
        b=sum(r['outcomes'][first] and not r['outcomes'][second] for r in group)
        c=sum(r['outcomes'][second] and not r['outcomes'][first] for r in group);d=len(group)-a-b-c
        records=[{'id':r['id'],'family':r['family'],'condition':condition,'success':int(r['outcomes'][condition])} for r in group for condition in [second,first]]
        results.append({'contrast':first+'_minus_'+second,'n_pairs':len(group),'family_clusters':len({r['family'] for r in group}),
                        'matched_table_success_first':[[a,b],[c,d]],'risk_difference':(b-c)/len(group),
                        'exact_McNemar_p':mcnemar(b,c),'discordant_pairs':b+c,
                        'McNemar_text':'0 discordant pairs; conventional exact two-sided p = 1.0; no equivalence claim.' if b+c==0 else 'Exact two-sided conditional binomial McNemar test.',
                        'paired_score_sensitivity':newcombe_paired(a,b,c,d),
                        'family_cluster_primary':bootstrap_difference(records,'success','family',conditions=(second,first)),
                        'problem_bootstrap_secondary':bootstrap_difference(records,'success','id',conditions=(second,first)),
                        'full_cohort_identification_bounds':identification_bounds(cases,first,second)})
    n=results[0]['n_pairs'];mde=[]
    for q in [.05,.10,.20,.30,.50]:
        row=approximate_mde(n,q);row['exact_discrete_MDE']=exact_mde(n,q);row['maximum_exact_power_at_delta_equal_q']=exact_power(n,q,q)
        row['interpretation']='Assumption-based independent-pair planning sensitivity, not observed discordance or family-adjusted achieved power.';mde.append(row)
    result={'post_hoc':True,'contrasts':results,'MDE_sensitivity':mde,
            'method_sources':{'paired_score':'https://www.statsmodels.org/dev/generated/statsmodels.stats.proportion.confint_proportions_paired.html',
                              'primary_reference':'https://doi.org/10.1002/(SICI)1097-0258(19981130)17:22<2635::AID-SIM954>3.0.CO;2-C'},
            'interpretation':['Primary family bootstrap is degenerate when all observed paired differences are zero; this is not evidence of precision or equivalence.',
                'Newcombe paired-score interval is an independent-pair sensitivity and can remain nonzero with perfect observed agreement. Related families limit its coverage interpretation.',
                'The observed discordance rate is zero; it must not be plugged into a normal MDE formula to claim zero detectable effect.',
                'For assumed q, |risk difference| cannot exceed q. Sparse discordance can make 80% power unattainable; exact discrete power quantifies that under the stated model.',
                'Family dependence can reduce effective power; no correlation-adjusted n or additional study is invented.'],
            'largest_positive_difference_inside_paired_score_interval':results[0]['paired_score_sensitivity']['interval'][1]}
    write_json(OUT/'post_hoc_calibrated_null.json',result)
    write_csv(OUT/'post_hoc_MDE_sensitivity.csv',mde)
    print(json.dumps({'complete_BC_pairs':n,'conventional_McNemar_p':results[0]['exact_McNemar_p'],
                      'paired_score_interval':results[0]['paired_score_sensitivity']['interval'],
                      'primary_cluster_interval':results[0]['family_cluster_primary']['interval'],
                      'full_cohort_bounds':results[0]['full_cohort_identification_bounds']},indent=2))


if __name__=='__main__':main()
