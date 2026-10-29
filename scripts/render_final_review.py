"""Generate revised paper tables/figures from one validated reconstruction only."""
from collections import Counter,defaultdict
import difflib
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'src')]
from render_final_study import table as source_table,esc,ascii_code
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter

BASE=ROOT/'data/final_review/20261029_v2'
OUT=ROOT/'paper/generated/review_v2'


def read(path):return json.loads(path.read_text())
def pct(x):return f'{100*x:.2f}'


def table(path,*args,**kwargs):
    source_table(path,*args,**kwargs)
    if kwargs.get('numbered') is False:
        content=path.read_text().replace(r'\begin{center}',r'\begin{center}\begin{minipage}{\linewidth}\centering')
        content=content.replace(r'\end{center}',r'\end{minipage}\end{center}')
        path.write_text(content)


def main():
    r=read(BASE/'analysis_verified/results.json');OUT.mkdir(parents=True,exist_ok=True)
    allrows={s:read(ROOT/f'data/final_study/v1/{s}.json') for s in ['development','test']}
    rows=[]
    for field,label in [('category','Category'),('difficulty','Difficulty')]:
        for value in sorted({v[field] for group in allrows.values() for v in group}):
            d=sum(v[field]==value for v in allrows['development']);t=sum(v[field]==value for v in allrows['test'])
            rows.append([esc(label+': '+str(value).replace('_',' ')),d,t,d+t])
    for islib,label in [(False,'Textbook / CC BY-SA 4.0'),(True,'Formal library / Apache-2.0')]:
        d=sum(v['id'].startswith('lib_')==islib for v in allrows['development']);t=sum(v['id'].startswith('lib_')==islib for v in allrows['test']);rows.append([label,d,t,d+t])
    rows.append(['Total unique statements',15,60,75])
    table(OUT/'table1.tex','Frozen composition. Category, difficulty and provenance rows are separate partitions, not additive totals. Development/test occupy 5/54 curated families with no family overlap.','tab:dataset',['Partition','Dev.','Test','Total'],rows,'lrrr')
    lines=[r'\begin{table}[t]',r'\centering',r'\caption{A/B/C observed outcomes and known completed-response resources. C has two unavailable outcomes; its primary observed rate is 1/58. Repair means use the 60 eligible-case denominator, including zero completed repairs. Resource totals include the shared initial in each counterfactual row.}',r'\label{tab:abc}',r'\small',r'\begin{tabular}{lrrrr}',r'\toprule',r'Condition & Verified/observed & Missing & Rate & Wilson 95\% \\',r'\midrule']
    for c in ['A','B','C']:
        m=r['conditions'][c];ci=m['wilson_95_observed'];lines.append(f'{c} & {m["successes"]}/{m["observed_denominator"]} & {m["unavailable"]} & {pct(m["observed_rate"])}'+r'\% & '+f'[{pct(ci[0])}, {pct(ci[1])}]'+r' \\')
    lines += [r'\bottomrule',r'\end{tabular}',r'\par\vspace{4pt}',r'\begin{tabular}{lrrrr}',r'\toprule',r'Cond. & Repairs (mean) & Tokens in/out & Call wall s & Lean s \\',r'\midrule']
    for c in ['A','B','C']:
        m=r['conditions'][c];s=m['resources'];lines.append(f'{c} & {m["completed_repair_calls"]} ({m["completed_repairs_distribution"]["mean"]:.2f}) & {s["prompt_tokens"]["sum"]:,}/{s["completion_tokens"]["sum"]:,} & {s["call_wall_seconds"]["sum"]:.1f} & {s["compiler_seconds"]["sum"]:.1f}'+r' \\')
    lines += [r'\bottomrule',r'\end{tabular}',r'\par\vspace{4pt}',r'\begin{minipage}{.98\linewidth}\footnotesize',
              r'Initial success is 0/60. On the 58 complete B/C pairs each method succeeds once: paired difference 0.00 percentage points. B consumes 178 logical repair intents; C consumes 174, of which 172 complete. Sensitivity counting missing C as failure is 1/60 (1.67\%), not the observed C rate. Call wall times exclude the unavailable response and preflight rejection; they are not full-run cost estimates.',r'\end{minipage}',r'\end{table}']
    (OUT/'table2.tex').write_text('\n'.join(lines)+'\n')
    paired=[]
    for c in r['comparisons']:
        ci=c['family_bootstrap_95_complete_case'];p='non-informative' if c['exact_mcnemar_p'] is None else f'{c["exact_mcnemar_p"]:.3g}'
        paired.append([esc(c['comparison']),c['complete_pairs'],f'{100*c["risk_difference_complete_case"]:+.2f}',f'[{100*ci[0]:+.2f}, {100*ci[1]:+.2f}]',p])
    table(OUT/'paired.tex','Complete-case paired effects (percentage points), family-cluster bootstrap sensitivity, and exact McNemar tests. Point estimate, interval and test share the same cases.','', ['Contrast','Pairs','Difference',r'Cluster 95\%','$p$'],paired,'lrrrr',numbered=False)
    names={'other_compiler_error':'Other','syntax_or_parser':'Parser/syntax','tactic_or_unsolved_goal':'Tactic/goals','type_mismatch_or_elaboration':'Type/elaboration','unknown_identifier_or_name':'Unknown name'}
    tax=[]
    for x in r['taxonomy']:
        tax.append([names[x['category']],x['initial_examples'],f"{x['B_successes']}/{x['B_observed']}",f"{x['C_successes']}/{x['C_observed']}",x['initial_examples']-x['C_observed']])
    table(OUT/'table3.tex','Primary initial-error taxonomy and observed repair success fractions. Categories are pre-specified and mutually exclusive; denominators are observed B/C outcomes within each group. Groups below five cases remain descriptive.','tab:errors',['Initial error','Cases','B solved/obs.','C solved/obs.','C missing'],tax,'lrrrr')
    sem=r['semantic_review'];raw=sem['historical_coding_AI_labels'];phi=sem['raw_Phi4_labels']
    table(OUT/'table4.tex','AI-assisted reference faithfulness, not autonomous translation accuracy or human-gold accuracy. Original 96-item labels precede correction, source exclusion and final adjudication.','tab:semantic',['Evidence population','Faithful','Not faithful','Uncertain/invalid'],[
          ['Coding-AI original references (96)',raw['faithful'],raw['not faithful'],str(raw['uncertain'])+' uncertain'],
          ['Phi-4 original responses (96)',phi['faithful'],phi['not faithful'],str(phi['invalid_format'])+' invalid'],
          ['Selected AI-eligible references (75)',75,0,'0 uncertain'],
          ['Independent human labels',0,0,'Not measured']], 'lrrl')
    # Diagnostic-level tags are post-hoc, overlapping and descriptive, distinct from the frozen primary taxonomy.
    tags=defaultdict(dict);tag_patterns={'Unknown identifier/theorem name':['unknown identifier','unknown constant','unknown namespace'],
          'Type mismatch/elaboration':['type mismatch','application type mismatch','function expected'],
          'Unsolved goals':['unsolved goals'],'Tactic failure':['tactic','simp made no progress','no goals to be solved'],
          'Syntax/parser':['unexpected token','expected command','parse error','invalid syntax'],
          'Missing instance':['failed to synthesize','failed to infer instance']}
    for case in r['cases']:
        m=read(ROOT/case['manifest_path']);messages=[d['data'] for d in m['initial']['verification']['diagnostics'] if d.get('severity')=='error']
        for label,patterns in tag_patterns.items():
            match=next((s for s in messages if any(p in s.lower() for p in patterns)),None)
            if match:tags[label][case['problem_id']]={'case':case,'message':match}
    tagrows=[];tag_evidence=[]
    for label,group in tags.items():
        values=list(group.values());tagrows.append([label,len(values),sum(v['case']['outcomes']['B'] is True for v in values),sum(v['case']['outcomes']['C'] is True for v in values)])
        v=values[0];tag_evidence.append({'tag':label,'examples':len(values),'representative_id':v['case']['problem_id'],'representative_message':v['message'],
             'B_observed':sum(v['case']['outcomes']['B'] is not None for v in values),'C_observed':sum(v['case']['outcomes']['C'] is not None for v in values),
             'B_successes':sum(v['case']['outcomes']['B'] is True for v in values),'C_successes':sum(v['case']['outcomes']['C'] is True for v in values),
             'actionability_assessment':'Potentially actionable localization of a name/type/syntax/proof-state problem; this is author interpretation, not a measured helpfulness score or a guarantee of repair.'})
    (BASE/'diagnostic_subtypes.json').write_text(json.dumps({'scope':'Post-hoc overlapping tags on initial compiler error messages only; not independent tests or replacements for primary categories.','groups':tag_evidence,'unobserved_tags':[k for k in tag_patterns if k not in tags],'timeout_initials':0},ensure_ascii=False,indent=2)+'\n')
    selected=read(ROOT/'data/final_study/v1/analysis/rendered_evidence.json')['selected_examples'];qual=[];qual_index=[]
    for ident in selected:
        record=next(v for v in allrows['test'] if v['id']==ident);case=next(v for v in r['cases'] if v['problem_id']==ident);m=read(ROOT/case['manifest_path'])
        branch='B' if m['conditions']['B']['success'] else ('C' if m['conditions']['C']['attempts'] else 'B')
        attempts=m['conditions'][branch]['attempts'];after=attempts[-1];before=attempts[-2] if len(attempts)>1 else m['initial']
        errors=[d['data'] for d in before['verification']['diagnostics'] if d.get('severity')=='error']
        message=errors[0] if errors else '; '.join(before['verification']['errors'])
        change='byte-identical to its predecessor' if before['candidate_sha256']==after['candidate_sha256'] else 'different candidate bytes; success is determined by Lean, not the edit itself'
        edits=[(tag,before['candidate'][i:j],after['candidate'][k:l]) for tag,i,j,k,l in difflib.SequenceMatcher(None,before['candidate'],after['candidate']).get_opcodes() if tag!='equal']
        first_edit=('First actual changed text: removed ['+ascii_code(edits[0][1])[:45]+']; inserted ['+ascii_code(edits[0][2])[:45]+'].' if edits else 'No text changed in this actual retry.')
        qual += [r'\paragraph{'+esc(ident)+' ('+branch+').}',esc(record['nl_statement']),
                 'Actual last repair: '+esc(after['key'])+'; Lean success: '+str(after['verification']['success'])+'. Candidate is '+esc(change)+'.',
                 esc(first_edit),
                 'Immediately preceding genuine diagnostic: '+esc(ascii_code(message)[:180])+'.',
                 ('The blind model did not receive this diagnostic.' if branch=='B' else 'C received this predecessor diagnostic in its structured feedback.'),
                 r'\textit{Before (display-only excerpt):}',r'\begin{verbatim}',
                 '\n'.join(line[:58].rstrip() for line in ascii_code(before['candidate']).splitlines()[:5]),r'\end{verbatim}',
                 r'\textit{After (display-only excerpt):}',r'\begin{verbatim}',
                 '\n'.join(line[:58].rstrip() for line in ascii_code(after['candidate']).splitlines()[:5]),r'\end{verbatim}']
        qual_index.append({'id':ident,'branch':branch,'before_sha256':before['candidate_sha256'],'after_sha256':after['candidate_sha256'],
                          'after_success':after['verification']['success'],'genuine_predecessor_message':message,'change':change,'first_actual_edit':first_edit})
    (OUT/'qualitative.tex').write_text('\n'.join(qual)+'\n')
    (BASE/'qualitative_cases.json').write_text(json.dumps(qual_index,ensure_ascii=False,indent=2)+'\n')
    resource_rows=[]
    for c in ['A','B','C']:
        for key,label in [('prompt_tokens','Input tokens'),('completion_tokens','Output tokens'),('call_wall_seconds','Call wall s'),('generation_seconds','Generation s')]:
            d=r['conditions'][c]['resources'][key];resource_rows.append([c,label,d['n'],f"{d['mean']:.1f}",f"{d['median']:.1f}"])
    table(OUT/'resources.tex','Known completed-response resource distributions. Loading is included in call wall time. These are calls, not independent theorem observations. Missing response costs are not imputed.','', ['Cond.','Measure','Calls','Mean','Median'],resource_rows,'llrrr',numbered=False)
    paired_resources=read(BASE/'paired_resources.json')
    matched=[]
    for c in ['B','C']:
        s=paired_resources['conditions'][c]['summary']
        matched.append([c,f"{s['prompt_tokens']['mean']:.1f}/{s['completion_tokens']['mean']:.1f}",f"{s['call_wall_seconds']['mean']:.1f}/{s['call_wall_seconds']['median']:.1f}",f"{s['generation_seconds']['mean']:.1f}"])
    table(OUT/'matched_resources.tex','Resources per theorem on the same 58 complete pairs (230 completed calls per condition, including the shared initial). Observed costs are descriptive; B-before-C order and shared-host activity prevent a causal speed claim.','',
          ['Cond.','Mean tokens in/out','Wall s mean/median','Mean generation s'],matched,'lrrr',numbered=False)
    plt.rcParams.update({'font.size':9,'pdf.fonttype':42,'ps.fonttype':42})
    fig,ax=plt.subplots(figsize=(5.4,2.6))
    for name,color,marker in [('A','#555555','s'),('B','#D18B00','o'),('C','#0072B2','^')]:
        ax.plot(range(4),r['paired_success_curves']['curves'][name],color=color,marker=marker,label=name)
    ax.set(xlabel='Maximum repair calls',ylabel='Verified success (58 paired cases)',xticks=range(4),ylim=(0,.05));ax.yaxis.set_major_formatter(PercentFormatter(1));ax.grid(alpha=.25);ax.legend();fig.tight_layout()
    for ext in ['pdf','png']:fig.savefig(OUT/f'success_budget.{ext}',dpi=200)
    plt.close(fig)
    fig,ax=plt.subplots(figsize=(5.4,2.8));groups=r['taxonomy'];xx=list(range(len(groups)))
    for c,offset,color in [('B',-.17,'#D18B00'),('C',.17,'#0072B2')]:
        ax.bar([v+offset for v in xx],[t[c+'_successes']/t[c+'_observed'] for t in groups],width=.34,label=c,color=color)
    ax.set_xticks(xx,[names[t['category']].replace('/','/\n').replace(' ','\n') for t in groups]);ax.set_ylabel('Verified / observed in error group');ax.yaxis.set_major_formatter(PercentFormatter(1));ax.set_ylim(0,.1);ax.legend();fig.tight_layout()
    for ext in ['pdf','png']:fig.savefig(OUT/f'error_rates.{ext}',dpi=200)
    plt.close(fig)
    manifest={'analysis_sha256':hashlib.sha256((BASE/'analysis_verified/results.json').read_bytes()).hexdigest(),
              'figure1_denominator':58,'figure1_curves':r['paired_success_curves']['curves'],'selected_qualitative_ids':selected,
              'files':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(OUT.iterdir()) if p.is_file()}}
    (BASE/'render_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print('Rendered four main tables, paired/resource supplements, two figures and five genuine before/after cases.')


if __name__=='__main__':main()
