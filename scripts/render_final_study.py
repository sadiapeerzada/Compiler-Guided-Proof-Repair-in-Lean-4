"""Render empirical tables/figures from validated immutable run evidence."""
import argparse
from collections import Counter
import csv
import datetime
import hashlib
import json
import os
from pathlib import Path
import sys
import statistics
os.environ.setdefault('MPLCONFIGDIR','/tmp/nl2lean-mpl')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'eval'))
from final_study import BASE,read,sha,validate_protocol
from final_study_analysis import validate_run
from paired_analysis import classify_compiler_error

LABELS={'arithmetic_identity':'Arithmetic identities','divisibility':'Divisibility','induction':'Induction','inequality':'Inequalities','modular_arithmetic':'Modular arithmetic'}
def esc(x):
    mapping={'\\':r'\textbackslash{}','{':r'\{','}':r'\}','$':r'\$','_':r'\_','%':r'\%','&':r'\&','#':r'\#','^':r'\textasciicircum{}','~':r'\textasciitilde{}'}
    return ''.join(mapping.get(c,c) for c in ascii_code(str(x)))
def pct(x):return f'{100*x:.1f}'
def pp(x):return f'{100*x:+.1f}'
def pval(x):return 'non-informative' if x is None else f'{x:.5g}'
def ascii_code(x):
    x=x.replace('⟨','<').replace('⟩','>')
    replacements={'ℕ':'Nat','ℤ':'Int','ℝ':'Real','ℚ':'Rat','ℂ':'Complex','∀':'forall','∃':'exists','∈':'in','∑':'sum','∏':'prod','≤':'<=','≥':'>=','≠':'!=','→':'->','←':'<-','↔':'<->','∧':'and','∨':'or','≡':'congruent','λ':'fun',
        '−':'-','–':'-','—':'--','²':'^2','³':'^3','×':'*','⋅':'*','∣':' | ','⊆':'subseteq','∅':'emptyset','⊢':'|-','↦':'=>','“':'"','”':'"','‘':"'",'’':"'",'\u00a0':' '}
    for a,b in replacements.items():x=x.replace(a,b)
    return ''.join(c if ord(c)<128 else '?' for c in x)
def table(path,caption,label,headers,rows,align,numbered=True):
    prefix=[r'\begin{table}[t]',r'\centering',r'\caption{'+caption+'}',r'\label{'+label+'}'] if numbered else [r'\begin{center}',r'\textbf{'+caption+r'}\par\vspace{3pt}']
    lines=prefix+[r'\small',r'\begin{tabular}{'+align+'}',r'\toprule',' & '.join(headers)+r' \\',r'\midrule']
    lines+=[' & '.join(str(x) for x in row)+r' \\' for row in rows]
    lines += [r'\bottomrule',r'\end{tabular}',r'\end{table}' if numbered else r'\end{center}']
    path.write_text('\n'.join(lines)+'\n')

def render(protocol):
    p=validate_protocol(protocol);p['_sha256']=sha(protocol)
    results=read(BASE/'analysis/results.json')
    if results['protocol_sha256']!=p['_sha256']:raise ValueError('Analysis protocol mismatch')
    test=read(BASE/'test.json');dev=read(BASE/'development.json');root=ROOT/p['output_root']/'heldout'/'2027'
    runs=[read(root/r['id']/'manifest.json') for r in test]
    for m in runs:validate_run(m,p)
    for name in ['A','B','C']:
        if sum(m['conditions'].get(name,{}).get('success') is True for m in runs)!=results['conditions'][name]['successes']:raise ValueError('Reported success differs from raw runs')
    out=ROOT/'paper/generated';out.mkdir(exist_ok=True)
    composition=[]
    for category,label in LABELS.items():
        d=sum(r['category']==category for r in dev);t=sum(r['category']==category for r in test);composition.append([label,d,t,d+t])
    composition.append(['Total',len(dev),len(test),len(dev)+len(test)])
    for difficulty in sorted({r['difficulty'] for r in dev+test}):
        d=sum(r['difficulty']==difficulty for r in dev);t=sum(r['difficulty']==difficulty for r in test)
        composition.append([f'Difficulty {difficulty}',d,t,d+t])
    for name,is_library in [('Textbook',False),('Formal library',True)]:
        d=sum(r['id'].startswith('lib_')==is_library for r in dev);t=sum(r['id'].startswith('lib_')==is_library for r in test)
        composition.append([name,d,t,d+t])
    table(out/'final_table1.tex','Frozen AI-policy dataset composition. Development has five curated family clusters and test has 54; no family crosses the split.','tab:dataset',['Category','Dev.','Test','Total'],composition,'lrrr')
    resources={};rows=[];resource_rows=[]
    for name in ['A','B','C']:
        metrics=results['conditions'][name];attempts=0;per_case_attempts=[]
        for r in test:
            folder=root/r['id'];pattern='initial/intent.json' if name=='A' else name+'*/intent.json'
            count=sum(1 for _ in folder.glob(pattern));attempts+=count;per_case_attempts.append(0 if name=='A' else count)
        resources[name]={'actual_repair_generation_attempts':0 if name=='A' else attempts,
                         'completed_repair_generations':metrics['repair_calls'],
                         'mean_repair_attempts_per_eligible_problem':statistics.mean(per_case_attempts),
                         'median_repair_attempts_per_eligible_problem':statistics.median(per_case_attempts),
                         'repair_attempts_by_ordered_test_id':dict(zip([r['id'] for r in test],per_case_attempts))}
        callwall=0.0;unknown=0
        for record in test:
            folder=root/record['id'];intents=list(folder.glob('initial/intent.json'))
            if name!='A':intents+=list(folder.glob(name+'*/intent.json'))
            for intent in intents:
                end=intent.parent/'completion.json'
                if not end.exists():end=intent.parent/'generation_failure.json'
                if end.exists():callwall+=(datetime.datetime.fromisoformat(read(end)['finished_at'])-datetime.datetime.fromisoformat(read(intent)['started_at'])).total_seconds()
                else:unknown+=1
        resources[name].update(known_model_call_wall_seconds=callwall,unmeasured_interrupted_call_durations=unknown)
        resource_rows.append([name,f'{metrics["prompt_tokens"]:,}',f'{metrics["completion_tokens"]:,}',f'{callwall:.1f}',f'{metrics["compiler_seconds"]:.1f}'])
        ci=metrics['wilson_95'];rows.append([name,f'{metrics["successes"]}/{len(test)}',pct(metrics['success_rate'])+r'\%',
            f'[{pct(ci[0])}, {pct(ci[1])}]',resources[name]['actual_repair_generation_attempts'],f'{metrics["completion_tokens"]:,}'])
    table(out/'final_table2.tex','Observed strict proof success; full eligible denominator, counting missing outcomes as failures. Wilson intervals assume problem independence. Decode-token totals include the shared initial for each counterfactual condition; physical totals count it once.','tab:abc',
          ['Condition','Success','Rate',r'95\% CI','Repairs','Output tokens'],rows,'lrrrrr')
    pairs=[]
    for c in results['comparisons']:
        ci=c['family_cluster_bootstrap_95'];pairs.append([esc(c['comparison']),pp(c['difference_missing_as_failure']),f'[{pp(ci[0])}, {pp(ci[1])}]',pval(c['exact_mcnemar_p']),pval(c['holm_adjusted_p'])])
    table(out/'final_paired_tests.tex','Paired differences in percentage points (pp), family-cluster bootstrap intervals, exact McNemar tests on complete pairs, and Holm adjustment over three comparisons. Cluster dependence limits the problem-level tests.','tab:paired',
          ['Comparison','Diff. pp',r'Cluster 95\% CI','$p$',r'$p_{\mathrm{Holm}}$'],pairs,'lrrrr',numbered=False)
    table(out/'final_resources.tex','Condition resource totals (including shared initial).','',
          ['Cond.','Input tokens','Output tokens','Call s','Lean s'],resource_rows,'lrrrr',numbered=False)
    distribution_rows=[]
    for name in ['A','B','C']:
        values={'tokens':[],'generation_seconds':[],'call_wall_seconds':[]}
        for record in test:
            folder=root/record['id'];paths=list(folder.glob('initial/completion.json'))
            if name!='A':paths+=list(folder.glob(name+'*/completion.json'))
            for path in paths:
                completion=read(path);metadata=completion['metadata']
                values['tokens'].append(metadata['prompt_tokens']+metadata['completion_tokens'])
                values['generation_seconds'].append(metadata['latency_seconds'])
                values['call_wall_seconds'].append((datetime.datetime.fromisoformat(completion['finished_at'])-datetime.datetime.fromisoformat(read(path.parent/'intent.json')['started_at'])).total_seconds())
        resources[name]['completed_call_distributions']={key:{'n':len(v),'mean':statistics.mean(v),'median':statistics.median(v)} for key,v in values.items()}
        for key,label in [('tokens','Total tokens'),('generation_seconds','Generation s'),('call_wall_seconds','Call wall s')]:
            v=values[key];distribution_rows.append([name,label,len(v),f'{statistics.mean(v):.1f}',f'{statistics.median(v):.1f}'])
    table(out/'final_resource_distributions.tex','Completed-call resource distributions. Tokens include input and output; call wall time includes loading. Each condition includes the shared initial. Interrupted calls are excluded, not assigned zero.','',
          ['Cond.','Measure','Calls','Mean','Median'],distribution_rows,'llrrr',numbered=False)
    table(out/'final_repair_calls.tex','Repair generation attempts per eligible problem (60-case denominator, including zero calls and consumed interrupted intents).','',
          ['Condition','Total','Mean','Median'],[[name,resources[name]['actual_repair_generation_attempts'],
          f"{resources[name]['mean_repair_attempts_per_eligible_problem']:.2f}",f"{resources[name]['median_repair_attempts_per_eligible_problem']:.1f}"] for name in ['A','B','C']],'lrrr',numbered=False)
    incomplete_streams=[]
    for record in test:
        folder=root/record['id']
        for intent in sorted(folder.glob('*/intent.json')):
            if (intent.parent/'completion.json').exists():continue
            context=read(intent)['context'];stream=folder/'streams'/(hashlib.sha256(context.encode()).hexdigest()+'.jsonl')
            frames=[json.loads(line) for line in stream.read_text().splitlines()] if stream.exists() else []
            observed=max([0]+[int(frame.get('generation_tokens',0)) for frame in frames])
            incomplete_streams.append({'problem_id':record['id'],'step':intent.parent.name,'observed_generated_tokens':observed,
                'stream_path':str(stream.relative_to(ROOT)) if stream.exists() else None,
                'interpretation':'Durably observed partial tokens, not a fabricated completed response or exact total beyond the retained stream.'})
    incomplete_details=[];incomplete_counts=Counter()
    for record,m in zip(test,runs):
        for name in ['A','B','C']:
            condition=m['conditions'].get(name,{})
            if condition.get('success') is not None:continue
            reason=condition.get('incomplete_reason',m.get('incomplete_reason',''))
            failures=list((root/record['id']).glob(('initial' if name=='A' else name+'*')+'/generation_failure.json'))
            if not failures and m['initial'] is None:failures=list((root/record['id']).glob('initial/generation_failure.json'))
            errors=[read(path).get('error','') for path in failures]
            combined=' '.join([reason,*errors])
            if 'context budget' in combined:kind='Context budget exceeded'
            elif 'Prior generation intent' in combined:kind='Interrupted generation'
            elif 'verification' in condition.get('status','') or 'verifier' in condition.get('status',''):kind='Verifier unavailable'
            else:kind='Generation unavailable'
            incomplete_counts[(name,kind)]+=1
            incomplete_details.append({'problem_id':record['id'],'condition':name,'category':kind,'reason':reason,'generation_errors':errors,'status':condition.get('status',m['status'])})
    missing_rows=[[name,esc(kind),count] for (name,kind),count in sorted(incomplete_counts.items())]
    table(out/'final_missingness.tex','Unavailable condition outcomes, retained in the eligible denominator.','',
          ['Condition','Recorded cause','Count'],missing_rows or [['All','None','0']],'llr',numbered=False)
    initial_groups={}
    for m in runs:
        if m['initial'] is None:category='unavailable_initial'
        else:
            v=m['initial']['verification']
            if v['success']:continue
            category=classify_compiler_error('\n'.join(v['errors'])) if v['failure_kind']=='compiler_error' else (v['failure_kind'] or 'unclassified_verifier_failure')
        group=initial_groups.setdefault(category,{'N':0,'B':0,'C':0});group['N']+=1
        for c in ['B','C']:group[c]+=int(m['conditions'].get(c,{}).get('success') is True)
    assert sum(g['N'] for g in initial_groups.values())==len(test)-results['conditions']['A']['successes']
    for condition in ['B','C']:
        assert sum(g[condition] for g in initial_groups.values())==results['conditions'][condition]['successes']-results['conditions']['A']['successes']
    names={'syntax_or_parser':'Parser / syntax','unknown_identifier_or_name':'Unknown name','type_mismatch_or_elaboration':'Type / elaboration','tactic_or_unsolved_goal':'Tactic / goals','proof_rejected':'Safety guard','timeout':'Timeout','other_compiler_error':'Other compiler error','unavailable_initial':'No initial output','unclassified_verifier_failure':'Unclassified verifier'}
    erows=[[names.get(k,esc(k)),v['N'],v['B'],v['C']] for k,v in sorted(initial_groups.items())]
    table(out/'final_table3.tex','Repair outcomes grouped by the primary initial failure category (one category per failed initial proof). Guard/infrastructure failures are separated from genuine compiler errors. Small groups are descriptive.','tab:errors',
          ['Initial failure','Cases','B solved','C solved'],erows,'lrrr')
    table(out/'final_table4.tex','Semantic and correctness evidence. AI adjudication is an eligibility decision, not independently measured semantic accuracy. No independent human semantic review is claimed.','tab:semantic',
          ['Evidence','Count','Interpretation'],[
          ['AI-adjudicated references','75/75','Policy-screened, not human gold'],
          ['Independent human review','0/75','Student-reported substitution'],
          ['Raw Phi-4 faithful labels','72/96','Before adjudication; not accuracy'],
          ['Raw Phi-4 invalid format','13/96','Not accepted as faithful votes'],
          ['Corrected original pairs','2','Reviewed again; excluded for provenance']], 'lrl')
    plt.rcParams.update({'font.size':10,'pdf.fonttype':42,'ps.fonttype':42})
    fig,ax=plt.subplots(figsize=(5.4,3.1))
    curves={}
    for name,color,marker in [('A','#555555','s'),('B','#D18B00','o'),('C','#0072B2','^')]:
        curve=[]
        for budget in range(4):
            curve.append(sum(any(v is True for k,v in m['conditions'].get(name,{}).get('milestones',{}).items() if int(k)<=budget) for m in runs)/len(test))
        curves[name]=curve;ax.plot(range(4),curve,marker=marker,color=color,label=name)
    assert curves['A'][0]==curves['B'][0]==curves['C'][0]
    ax.set(xlabel='Maximum repair calls',ylabel='Observed verified success',xticks=range(4),ylim=(0,1));ax.yaxis.set_major_formatter(PercentFormatter(1));ax.grid(alpha=.25);ax.legend();fig.tight_layout();fig.savefig(out/'final_success_budget.pdf');fig.savefig(out/'final_success_budget.png',dpi=200);plt.close(fig)
    fig,ax=plt.subplots(figsize=(5.4,3.2));keys=sorted(initial_groups);x=list(range(len(keys)))
    ax.bar([v-.25 for v in x],[initial_groups[k]['N'] for k in keys],width=.25,label='Initial failures',color='#BBBBBB')
    ax.bar(x,[initial_groups[k]['B'] for k in keys],width=.25,label='B solved',color='#D18B00')
    ax.bar([v+.25 for v in x],[initial_groups[k]['C'] for k in keys],width=.25,label='C solved',color='#0072B2')
    ax.set_xticks(x,[names.get(k,k).replace(' / ','/').replace(' ','\n') for k in keys]);ax.set_ylabel('Cases / verified repairs');ax.set_ylim(0,max([1]+[initial_groups[k]['N'] for k in keys])*1.15);ax.legend();fig.tight_layout();fig.savefig(out/'final_error_outcomes.pdf');fig.savefig(out/'final_error_outcomes.png',dpi=200);plt.close(fig)
    examples=[];unchanged={'B':0,'C':0};repair_totals={'B':0,'C':0}
    for r,m in zip(test,runs):
        if not m['initial']:continue
        a,b,c=[m['conditions'].get(k,{}).get('success') for k in ['A','B','C']]
        for condition in ['B','C']:
            prior=m['initial']['candidate_sha256']
            for attempt in m['conditions'][condition]['attempts']:
                repair_totals[condition]+=1;unchanged[condition]+=int(attempt['candidate_sha256']==prior);prior=attempt['candidate_sha256']
        label='incomplete' if any(v is None for v in [a,b,c]) else 'guided_only' if c and not b else 'blind_only' if b and not c else 'both_repair' if not a and b and c else 'one_shot' if a else 'both_failed'
        v=m['initial']['verification'];error_kind='verified_initial' if v['success'] else classify_compiler_error('\n'.join(v['errors'])) if v['failure_kind']=='compiler_error' else v['failure_kind']
        examples.append({'id':r['id'],'kind':label,'category':r['category'],'initial_error_category':error_kind,'A':a,'B':b,'C':c,'nl_statement':r['nl_statement'],'initial':m['initial'],'B_attempts':m['conditions']['B']['attempts'],'C_attempts':m['conditions']['C']['attempts'],'manifest_sha256':sha(root/r['id']/'manifest.json')})
    selected=[]
    for kind in ['guided_only','blind_only','both_repair','both_failed','incomplete','one_shot']:
        if len(selected)>=5:break
        match=next((e for e in examples if e['kind']==kind),None)
        if match:selected.append(match)
    for field in ['initial_error_category','category',None]:
        for e in examples:
            if len(selected)>=5:break
            if e not in selected and (field is None or e[field] not in {s[field] for s in selected}):selected.append(e)
    selected=selected[:5]
    text=[]
    for e in selected:
        if e['kind']=='blind_only' and e['B_attempts']:display=e['B_attempts'][-1];branch='B'
        elif e['C_attempts']:display=e['C_attempts'][-1];branch='C'
        elif e['B_attempts']:display=e['B_attempts'][-1];branch='B'
        else:display=e['initial'];branch='shared initial'
        code=display['candidate'];e['display_branch']=branch;e['display_candidate_sha256']=display['candidate_sha256'];e['display_verified_success']=display['verification']['success']
        excerpt='\n'.join(line[:60] for line in ascii_code(code).splitlines()[:7]).replace('\\end{verbatim}','[end marker]')
        text += [r'\paragraph{'+esc(e['id'])+' ('+esc(e['kind'].replace('_',' '))+').}',
                 esc(e['nl_statement'])+' A/B/C verified outcomes were '+esc('/'.join(str(e[k]) for k in ['A','B','C']))+'.',
                 'Displayed candidate: '+esc(branch)+'; verifier success: '+str(display['verification']['success'])+'.',
                 'Initial diagnostic: '+esc(ascii_code('; '.join(e['initial']['verification']['errors']))[:210] or 'none; initial proof verified')+'.',
                 r'\begin{verbatim}',excerpt,r'\end{verbatim}']
    (out/'final_qualitative.tex').write_text('\n'.join(text)+'\n')
    (BASE/'analysis/selected_qualitative_examples.json').write_text(json.dumps({'selection':'Post-hoc illustrative coverage of available outcome types, initial error classes and mathematical categories, then stored test order; no effect on statistical sample.','examples':selected},ensure_ascii=False,indent=2)+'\n')
    detail={'incomplete_generation_streams':incomplete_streams,'observed_partial_generation_tokens':sum(x['observed_generated_tokens'] for x in incomplete_streams),'incomplete_condition_outcomes':incomplete_details,'source_results_sha256':sha(BASE/'analysis/results.json'),'condition_resources':resources,'initial_failure_outcomes':initial_groups,'success_budget_curves':curves,'selected_examples':[e['id'] for e in selected],
            'posthoc_repeated_candidate_diagnostic':{'byte_identical_to_previous':unchanged,'completed_repair_generations':repair_totals,'purpose':'Descriptive process diagnostic, not an additional hypothesis test or independent samples.'},
            'display_note':'Qualitative code is truncated and ASCII-transliterated for typesetting only. Complete original Unicode model outputs and compiler logs remain unchanged.'}
    (BASE/'analysis/rendered_evidence.json').write_text(json.dumps(detail,indent=2)+'\n')
    with (BASE/'analysis/initial_failure_outcomes.csv').open('w') as f:
        w=csv.writer(f);w.writerow(['category','cases','B_solved','C_solved']);w.writerows([[k,v['N'],v['B'],v['C']] for k,v in initial_groups.items()])
    print('Rendered actual results, paired tests, two figures and',len(selected),'authentic examples.')

if __name__=='__main__':
    a=argparse.ArgumentParser(description=__doc__);a.add_argument('--protocol',type=Path,required=True);render(a.parse_args().protocol)
