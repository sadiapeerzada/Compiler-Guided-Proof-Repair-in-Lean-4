"""Pre-specified single-seed paired analysis, including family-cluster sensitivity."""
import argparse
from collections import Counter
import csv
import json
from pathlib import Path
import hashlib
import random
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'eval'))
from final_study import BASE,read,sha,validate_protocol
from paired_analysis import wilson_interval,exact_mcnemar_p,holm_adjust,paired_bootstrap_interval,classify_compiler_error

def validate_run(m,p,expected_phase='heldout'):
    if m['protocol_sha256']!=p['_sha256'] or m['phase']!=expected_phase or m['seed'] not in p['seeds']:raise ValueError('Invalid result protocol/phase/seed')
    initial=m['initial']
    if initial is None:return
    for name,c in m['conditions'].items():
        if c['initial_candidate_sha256']!=initial['candidate_sha256']:raise ValueError('Unpaired initial candidate')
        if len(c['attempts'])>3:raise ValueError('Repair budget exceeded')
    for s in [initial,*[a for c in m['conditions'].values() for a in c['attempts']]]:
        cp=ROOT/s['completion_path'];vp=ROOT/s['verification_path']
        if sha(cp)!=s['completion_sha256'] or sha(vp)!=s['verification_sha256']:raise ValueError('Run evidence changed')
        completion=read(cp);md=completion['metadata']
        if md['provider']!='mlx_local' or md['model']!=p['model']['model_id'] or md['snapshot_revision']!=p['model']['snapshot_revision'] or md['api_attempts']!=0 or md['max_completion_tokens']!=2000 or md['temperature']!=0.2 or md['top_p']!=1.0 or md['base_seed']!=m['seed']:
            raise ValueError('Uncontrolled generation metadata')
        if hashlib.sha256(completion['prompt'].encode()).hexdigest()!=md['prompt_sha256'] or completion['prompt_sha256']!=md['prompt_sha256'] or completion['context']!=md['generation_context']:
            raise ValueError('Prompt/context provenance mismatch')
        expected_seed=int.from_bytes(hashlib.sha256(f'{md["base_seed"]}:{md["generation_context"]}:{md["prompt_sha256"]}'.encode()).digest()[:4],'big')
        if expected_seed!=md['generation_seed']:raise ValueError('Incorrect generation seed')
        from model_client import extract_lean_block
        if hashlib.sha256(extract_lean_block(completion['raw_response']).encode()).hexdigest()!=s['candidate_sha256'] or read(vp)!=s['verification']:
            raise ValueError('Candidate or verifier result changed')
        if s['verification']['success'] and (s['verification']['exit_code']!=0 or s['verification']['axiom_dependencies'] is None or set(s['verification']['axiom_dependencies'])-{'propext','Classical.choice','Quot.sound'}):
            raise ValueError('Unsafe/unverified success')
    for condition in ['B','C']:
        prior=initial
        for a in m['conditions'][condition]['attempts']:
            if condition=='B' and a['feedback_payload']!='No compiler diagnostics are provided in the blind-retry condition.':raise ValueError('Blind leakage')
            if condition=='C':
                v=prior['verification'];ds=[d for d in v['diagnostics'] or [] if d.get('kind')!='hasSorry']
                expected={'diagnostic_state':'available','diagnostics':ds}
                if v['diagnostic_state']!='available' or not ds or json.loads(a['feedback_payload'])!=expected or a['feedback_source_candidate_sha256']!=prior['candidate_sha256']:
                    raise ValueError('Guided diagnostics not from immediately preceding candidate')
            prior=a

def analyze(protocol,out):
    p=validate_protocol(protocol);p['_sha256']=sha(protocol);rows=read(BASE/'test.json');root=ROOT/p['output_root']/'heldout'/'2027'
    runs=[]
    for r in rows:
        m=read(root/r['id']/'manifest.json');validate_run(m,p)
        if m['problem_id']!=r['id'] or m['dataset_sha256']!=p['dataset_sha256']['heldout']:raise ValueError('Result/dataset mismatch')
        runs.append(m)
    out.mkdir(parents=True,exist_ok=False)
    metrics={};table=[];errors=Counter()
    for name in ['A','B','C']:
        success=sum(m['conditions'].get(name,{}).get('success') is True for m in runs)
        incomplete=sum(m['conditions'].get(name,{}).get('success') is None for m in runs)
        steps=[]
        for m in runs:
            if m['initial']:steps.append(m['initial'])
            steps+=m['conditions'].get(name,{}).get('attempts',[])
        metrics[name]={'successes':success,'denominator':len(rows),'incomplete':incomplete,'success_rate':success/len(rows),
            'wilson_95':wilson_interval(success,len(rows)),'repair_calls':sum(m['conditions'].get(name,{}).get('repair_calls',0) for m in runs),
            'prompt_tokens':sum(s['prompt_tokens'] for s in steps),'completion_tokens':sum(s['completion_tokens'] for s in steps),
            'generation_seconds':sum(s['generation_seconds'] for s in steps),'compiler_seconds':sum(s['verification']['elapsed_seconds'] for s in steps)}
        table.append({'condition':name,**metrics[name]})
    pairs=[]
    for first,second in [('C','B'),('C','A'),('B','A')]:
        complete=[m for m in runs if all(m['conditions'].get(c,{}).get('success') is not None for c in [first,second])]
        b=sum(m['conditions'][first]['success'] and not m['conditions'][second]['success'] for m in complete)
        c=sum(m['conditions'][second]['success'] and not m['conditions'][first]['success'] for m in complete)
        diffs=[float(m['conditions'].get(first,{}).get('success') is True)-float(m['conditions'].get(second,{}).get('success') is True) for m in runs]
        groups={}
        for r,d in zip(rows,diffs):groups.setdefault(r['study_eligibility']['family'],[]).append(d)
        rng=random.Random(20271021);cluster=[];families=list(groups)
        for _ in range(10000):
            values=[v for family in rng.choices(families,k=len(families)) for v in groups[family]];cluster.append(sum(values)/len(values))
        cluster.sort()
        pairs.append({'comparison':first+'_vs_'+second,'complete_pairs':len(complete),'first_only':b,'second_only':c,
            'exact_mcnemar_p':exact_mcnemar_p(b,c),'difference_missing_as_failure':sum(diffs)/len(diffs),
            'problem_bootstrap_95':paired_bootstrap_interval(diffs),'family_cluster_bootstrap_95':[cluster[249],cluster[9749]],
            'inference_caution':'McNemar/Wilson/problem bootstrap assume independent problem units; related problems exist within 54 test families. Cluster interval is the robustness analysis; no unqualified independence/significance claim.'})
    for pair,adjusted in zip(pairs,holm_adjust([x['exact_mcnemar_p'] for x in pairs])):
        pair['holm_adjusted_p']=adjusted
        lo,hi=pair['family_cluster_bootstrap_95']
        pair['unqualified_significance_claim_permitted']=False
        pair['concordant_problem_test_and_cluster_interval_evidence']=adjusted is not None and adjusted<0.05 and (lo>0 or hi<0) and pair['complete_pairs']==len(rows)
    qualitative=[];failure_kinds=Counter()
    for r,m in zip(rows,runs):
        steps=([m['initial']] if m['initial'] else [])+[a for c in m['conditions'].values() for a in c['attempts']]
        for s in steps:
            if not s['verification']['success']:
                kind=s['verification']['failure_kind'];failure_kinds[kind]+=1
                if kind=='compiler_error':errors[classify_compiler_error('\n'.join(s['verification']['errors']))]+=1
        if m['initial'] and (m['conditions']['C']['attempts'] or m['conditions']['B']['attempts']):
            qualitative.append({'id':r['id'],'nl_statement':r['nl_statement'],'run':str((root/r['id']/'manifest.json').relative_to(ROOT)),
                'A':m['conditions']['A']['success'],'B':m['conditions']['B']['success'],'C':m['conditions']['C']['success'],
                'initial_candidate':m['initial']['candidate'],'initial_errors':m['initial']['verification']['errors'],
                'C_attempts':m['conditions']['C']['attempts']})
    unique_steps=[s for m in runs for s in (([m['initial']] if m['initial'] else [])+[a for c in m['conditions'].values() for a in c['attempts']])]
    result={'protocol_sha256':p['_sha256'],'eligible_test_examples':len(rows),'test_families':len({r['study_eligibility']['family'] for r in rows}),'seeds':p['seeds'],
        'actual_unique_generation_calls':len(unique_steps),'actual_unique_prompt_tokens':sum(s['prompt_tokens'] for s in unique_steps),
        'actual_unique_completion_tokens':sum(s['completion_tokens'] for s in unique_steps),
        'actual_unique_generation_seconds':sum(s['generation_seconds'] for s in unique_steps),
        'condition_resource_accounting':'Each counterfactual condition includes the shared initial cost; actual unique-call totals count it only once.',
        'conditions':metrics,'comparisons':pairs,'compiler_error_categories':dict(errors),'verifier_failure_kinds':dict(failure_kinds),
        'actual_unique_generation_attempts':sum(1 for r in rows for _ in (root/r['id']).glob('*/intent.json')),
        'actual_trajectory_wall_seconds':sum((__import__('datetime').datetime.fromisoformat(m['finished_at'])-__import__('datetime').datetime.fromisoformat(m['started_at'])).total_seconds() for m in runs),
        'genuine_qualitative_examples_available':len(qualitative),
        'incomplete_trajectories':sum(m['status']!='completed' for m in runs),'approval_provenance':read(BASE/'approvals/student_reported.json'),
        'run_manifest_sha256':{str((root/r['id']/'manifest.json').relative_to(ROOT)):sha(root/r['id']/'manifest.json') for r in rows}}
    (out/'results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');(out/'qualitative_examples.json').write_text(json.dumps(qualitative,ensure_ascii=False,indent=2)+'\n')
    with (out/'condition_results.csv').open('w') as f:
        w=csv.DictWriter(f,fieldnames=table[0].keys());w.writeheader();w.writerows(table)
    print(json.dumps(metrics,indent=2))

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--protocol',type=Path,required=True);a.add_argument('--output',type=Path,required=True);args=a.parse_args();analyze(args.protocol,args.output)
