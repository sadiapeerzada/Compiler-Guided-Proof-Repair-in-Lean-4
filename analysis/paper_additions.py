"""New paper-only table views; original generated tables stay unchanged."""
import re
from .common import OUT,read
from .render import table


def main():
    values=read(OUT/'post_hoc_calibrated_null.json')['contrasts'];path=OUT/'latex/post_hoc_paired_p1.tex'
    rows=[]
    for v in values:
        ci=v['family_cluster_primary']['interval'];score=v['paired_score_sensitivity']['interval']
        rows.append([v['contrast'],v['n_pairs'],f"{100*v['risk_difference']:+.2f}",f"[{100*ci[0]:+.2f}, {100*ci[1]:+.2f}]",f"[{100*score[0]:+.2f}, {100*score[1]:+.2f}]",f"{v['exact_McNemar_p']:.1f}"])
    table(path,'Paired success differences in percentage points; conventional exact McNemar p=1.0 for zero discordance. Cluster bootstrap is primary; paired-score bounds are an independent-pair sensitivity, not equivalence bounds.',
          ['Contrast','Pairs','Diff. pp','Cluster 95% pp','Score 95% pp','Exact p'],rows)
    text=path.read_text().replace(r'\begin{table}[t]',r'\begin{center}\begin{minipage}{\linewidth}')
    text=re.sub(r'\\caption\{([^}]*)\}',lambda m:r'\textbf{'+m[1]+r'}\par\vspace{3pt}',text)
    text=text.replace(r'\end{table}',r'\end{minipage}\end{center}');path.write_text(text)


if __name__=='__main__':main()
