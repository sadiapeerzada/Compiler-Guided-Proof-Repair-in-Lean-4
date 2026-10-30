"""Privacy-safe post-hoc booktabs tables, grayscale plots and neutral prose."""
import csv
import json
import os
from pathlib import Path
os.environ.setdefault('MPLCONFIGDIR','/tmp/nl2lean-mpl')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from .common import OUT,read,private_text


def table(path,caption,headers,rows):
    def esc(x):
        return str(x).replace('_',r'\_').replace('%',r'\%').replace('&',r'\&')
    text=[r'\begin{table}[t]',r'\centering',r'\caption{'+caption+'}',r'\small',r'\resizebox{\linewidth}{!}{%',r'\begin{tabular}{'+'l'*len(headers)+'}',r'\toprule',
          ' & '.join(esc(v) for v in headers)+r' \\',r'\midrule']
    text+=[' & '.join(esc(v) for v in row)+r' \\' for row in rows]
    text += [r'\bottomrule',r'\end{tabular}}',r'\end{table}']
    path.write_text('\n'.join(text)+'\n')


def main():
    t=read(OUT/'post_hoc_task1.json');null=read(OUT/'post_hoc_calibrated_null.json');latex=OUT/'latex';figures=OUT/'figures';latex.mkdir(exist_ok=True);figures.mkdir(exist_ok=True)
    rows=[]
    for c in ['B','C']:
        s=t['per_condition'][c]
        rows.append([c,f"{s['identical']['sum']}/{s['identical']['n']}",f"{100*s['identical']['mean']:.2f}%",f"{s['character_distance']['mean']:.4f}",f"{s['token_distance']['mean']:.4f}",f"{s['any_unknown_removed']['sum']}/{s['any_unknown_removed']['n']}"])
    table(latex/'post_hoc_process_table.tex','Exploratory held-out process metrics. Denominators are completed repairs; unknown-name removal has its own eligible-predecessor denominator. No new test inference.',
          ['Condition','Identical','Rate','Char edit','Token edit','Any name removed'],rows)
    contrasts=[]
    for key in ['identical','character_distance','token_distance','character_distance_excluding_identical','token_distance_excluding_identical','any_unknown_removed','diagnostic_count_change']:
        d=t['C_minus_B'][key]['family'];scale=100 if key in ['identical','any_unknown_removed'] else 1
        contrasts.append([key,f"{scale*d['difference']:+.4f}",f"[{scale*d['interval'][0]:+.4f}, {scale*d['interval'][1]:+.4f}]",f"{d['B_denominator']}/{d['C_denominator']}"])
    table(latex/'post_hoc_cluster_contrasts.tex','Exploratory C-minus-B differences with 10,000 whole-family bootstrap draws (seed 20271021). Repetition/name-removal effects are percentage points; edit distances are normalized units. No multiplicity-adjusted confirmatory claim.',
          ['Metric','Difference','Cluster 95% interval','B/C eligible repairs'],contrasts)
    table(latex/'post_hoc_calibrated_null.tex','Paired success differences: conventional exact two-sided McNemar, family-cluster bootstrap (primary), and independent-pair Newcombe method-10 score sensitivity. Zero discordance does not establish equivalence.',
          ['Contrast','Pairs','Difference pp','Cluster 95% pp','Score 95% pp','Exact p'],[
          [x['contrast'],x['n_pairs'],f"{100*x['risk_difference']:+.2f}",f"[{100*x['family_cluster_primary']['interval'][0]:+.2f}, {100*x['family_cluster_primary']['interval'][1]:+.2f}]",f"[{100*x['paired_score_sensitivity']['interval'][0]:+.2f}, {100*x['paired_score_sensitivity']['interval'][1]:+.2f}]",x['exact_McNemar_p']] for x in null['contrasts']])
    table(latex/'post_hoc_MDE.tex','Assumption-based 80% power sensitivity, n=58 independent pairs, two-sided alpha=.05. NA means no feasible effect at the stated discordance probability reaches 80% exact power; these are not observed rates or family-adjusted power.',
          ['Assumed q','Expected discordant','Normal MDE pp','Exact MDE pp','Max exact power'],[
          [x['assumed_discordance'],f"{x['expected_discordant_pairs']:.1f}",f"{100*x['normal_approximation_MDE']:.2f}",'NA' if x['exact_discrete_MDE'] is None else f"{100*x['exact_discrete_MDE']:.2f}",f"{x['maximum_exact_power_at_delta_equal_q']:.3f}"] for x in null['MDE_sensitivity']])
    transitions=list(csv.DictReader((OUT/'post_hoc_error_transitions.csv').open()));names=list(transitions[0])[2:];short=['Parser','Name','Type','Tactic','Other','Verified','Guard/infra']
    import numpy as np
    arrays=[np.array([[int(row[k]) for k in names] for row in transitions if row['condition']==c]) for c in ['B','C']]
    plt.rcParams.update({'font.size':9,'pdf.fonttype':42,'ps.fonttype':42})
    fig,axes=plt.subplots(2,1,figsize=(4.7,7.2));vmax=max(v.max() for v in arrays)
    for ax,data,c in zip(axes,arrays,['B','C']):
        ax.imshow(data,cmap='Greys',vmin=0,vmax=vmax)
        ax.set_xticks(range(7),short,rotation=30,ha='right');ax.set_yticks(range(7),short);ax.set(xlabel='After',ylabel='Before',title=f'{c}: completed-repair error transitions')
        for i in range(7):
            for j in range(7):ax.text(j,i,str(data[i,j]),ha='center',va='center',color='white' if data[i,j]>vmax*.55 else 'black',fontsize=8)
    fig.tight_layout();fig.savefig(figures/'post_hoc_transition_heatmaps.pdf');plt.close(fig)
    bins=list(csv.DictReader((OUT/'post_hoc_prompt_length_bins.csv').open()));fig,ax=plt.subplots(figsize=(4.7,2.7))
    ax.bar([1,2,3,4],[float(r['repetition_fraction']) for r in bins],color=['.25','.4','.6','.75'],edgecolor='black');ax.set(xticks=[1,2,3,4],xlabel='C diagnostic-length quartile bin',ylabel='Identical completed repairs',ylim=(0,1));fig.tight_layout();fig.savefig(figures/'post_hoc_length_repetition.pdf');plt.close(fig)
    repeat=t['C_minus_B']['identical']['family'];score=null['contrasts'][0]['paired_score_sensitivity']['interval'];prose=[]
    prose += [f"Repetition: B repeated its predecessor in 90/178 repairs (50.56%); C did so in 70/172 (40.70%). The exploratory repair-weighted C-minus-B difference is {100*repeat['difference']:+.2f} percentage points, with a whole-family bootstrap interval [{100*repeat['interval'][0]:+.2f}, {100*repeat['interval'][1]:+.2f}]. This post-hoc contrast does not establish diagnostic-content use or a proof-success benefit."]
    for key,label in [('character_distance','Character edit distance'),('token_distance','Frozen-tokenizer edit distance')]:
        b=t['per_condition']['B'][key];c=t['per_condition']['C'][key];ci=t['C_minus_B'][key]['family']['interval'];prose.append(f"{label}: completed-repair means are B {b['mean']:.4f} (n={b['n']}) and C {c['mean']:.4f} (n={c['n']}); the cluster difference interval is [{ci[0]:+.4f}, {ci[1]:+.4f}]. Conditioning on nonidentical repairs changes the denominators and is reported separately; no mathematical-progress inference is implied.")
    b=t['per_condition']['B']['any_unknown_removed'];c=t['per_condition']['C']['any_unknown_removed'];prose.append(f"Targeted-name removal: at least one preceding unknown identifier disappears in B {b['sum']}/{b['n']} eligible repairs and C {c['sum']}/{c['n']}. B's diagnostics are used by the analyst only, as a chance baseline. Syntactic disappearance and newly introduced unknown symbols are not verified mathematical fixes.")
    prose.append('Error transitions and diagnostic counts: all rows are actual completed consecutive-candidate pairs; stage advancement follows the declared parser/name/type/tactic order. Other and guard states are not forced into an ordered scale, and fewer error messages need not mean a stronger or correct proof.')
    prose.append('Prompt length: C and B input-token distributions and C diagnostic-length repetition bins are descriptive. The same theorem, category, previous output length, and branch stopping affect these quantities; no causal length effect or independent-repair test is claimed.')
    prose.append(f"Calibrated null: on 58 complete B/C pairs there are zero discordant outcomes; conventional exact two-sided McNemar p=1.0. The family bootstrap interval is [0,0] because all observed paired differences are zero, while the independent-pair Newcombe method-10 sensitivity interval is [{100*score[0]:+.2f}, {100*score[1]:+.2f}] percentage points. Neither interval establishes equivalence; family dependence and two unavailable C outcomes remain limitations.")
    prose.append(f"Under the score approximation, effects larger than {100*score[1]:.2f} pp are not supported by this data at this n; values up to that boundary remain inside the model-dependent interval. This statement is conditional on independent-pair score assumptions, not a general exclusion of effects under family dependence. Full-cohort C-minus-B identification bounds remain 0 to +3.33 pp, separately from confidence intervals.")
    prose.append('Power: the MDE sensitivity table varies an assumed discordance probability; it does not use the observed zero to claim perfect precision. The normal formula is (z_.975+z_.8)*sqrt(q/58); exact discrete McNemar power additionally respects |difference|<=q, and sparse discordance can make 80% power unattainable. Family dependence can further reduce power.')
    text='# Post-hoc paste-ready result prose\n\n'+'\n\n'.join(prose)+'\n';assert not private_text(text);(OUT/'POST_HOC_PROSE.md').write_text(text)
    summary='# Exploratory post-hoc summary\n\nReconciliation: 38 checks, zero mismatches. All measurements use original private raw records, never redacted publication substitutes. No held-out model call was run.\n\n'+'\n\n'.join(prose)+'\n\nTasks 1–2 completed; development placebo execution follows only after its protocol, filename-only normalizer and code are committed and validation passes. Study 2 execution is deferred.\n\nCaveats: post hoc, multiple descriptive comparisons, one seed, 54 original/52 complete-pair families, B-before-C execution order, longer C prompts, two unavailable C outcomes, and correlated repair attempts. No existing missing outcome is imputed, replayed or replaced.\n'
    (OUT/'SUMMARY.md').write_text(summary)
    (latex/'post_hoc_figure_snippets.tex').write_text(r'''\begin{figure}[t]
\centering\includegraphics[width=.92\linewidth]{post_hoc_transition_heatmaps.pdf}
\caption{Exploratory completed-repair transition counts. Common grayscale scale; attempts are not independent experimental units.}
\end{figure}
\begin{figure}[t]
\centering\includegraphics[width=.92\linewidth]{post_hoc_length_repetition.pdf}
\caption{Descriptive C repetition by diagnostic-length quartile bin. Ties can make bin sizes unequal; no causal relationship is established.}
\end{figure}
''')
    print('Post-hoc tables, grayscale PDFs, neutral prose and initial summary generated.')


if __name__=='__main__':main()
