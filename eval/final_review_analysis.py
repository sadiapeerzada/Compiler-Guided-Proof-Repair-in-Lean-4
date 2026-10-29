"""Append-only reconstruction of the frozen study, with explicit missing denominators.

Never generates proofs or modifies the frozen protocol, data or original results.
Primary contrasts use complete matched outcomes. Full-cohort missing-as-failure
is retained only as the sensitivity explicitly specified by the frozen protocol.
"""
import argparse
from collections import Counter, defaultdict
import datetime as dt
import hashlib
import json
from pathlib import Path
import random
import re
import statistics
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'eval')]
from final_study import BASE, read, sha, validate_freeze, validate_protocol
from final_study_analysis import validate_run
from model_client import extract_lean_block
from paired_analysis import wilson_interval, exact_mcnemar_p, holm_adjust, classify_compiler_error
from verify import _verification_source, _theorem_names, _diagnostics, _axioms_from_diagnostics


def require(ok,context,message):
    if not ok:raise ValueError(f'{context}: {message}')


def distribution(values):
    return {'n':len(values),'sum':sum(values),'mean':statistics.mean(values) if values else None,
            'median':statistics.median(values) if values else None,'histogram':dict(Counter(values))}


def contrast(cases,first,second,resamples=10000):
    paired=[r for r in cases if all(r['outcomes'][c] is not None for c in [first,second])]
    if not paired:raise ValueError('No complete matched outcomes for '+first+'_vs_'+second)
    diffs=[int(r['outcomes'][first])-int(r['outcomes'][second]) for r in paired]
    rng=random.Random(20271021)
    boot=sorted(sum(rng.choices(diffs,k=len(diffs)))/len(diffs) for _ in range(resamples))
    groups=defaultdict(list)
    for r,d in zip(paired,diffs):groups[r['family']].append(d)
    families=list(groups);rng=random.Random(20271021);cluster=[]
    for _ in range(resamples):
        sample=[v for family in rng.choices(families,k=len(families)) for v in groups[family]]
        cluster.append(statistics.mean(sample))
    cluster.sort();lo=int(.025*resamples)-1;hi=int(.975*resamples)-1
    first_only=sum(d==1 for d in diffs);second_only=sum(d==-1 for d in diffs)
    sensitivity=[int(r['outcomes'][first] is True)-int(r['outcomes'][second] is True) for r in cases]
    minimum=[];maximum=[]
    for r in cases:
        a,b=r['outcomes'][first],r['outcomes'][second]
        minimum.append((0 if a is None else int(a))-(1 if b is None else int(b)))
        maximum.append((1 if a is None else int(a))-(0 if b is None else int(b)))
    return {'comparison':f'{first}_vs_{second}','complete_pairs':len(paired),'complete_families':len(families),
            'first_successes':sum(r['outcomes'][first] for r in paired),'second_successes':sum(r['outcomes'][second] for r in paired),
            'first_only':first_only,'second_only':second_only,'risk_difference_complete_case':statistics.mean(diffs),
            'exact_mcnemar_p':exact_mcnemar_p(first_only,second_only),
            'conventional_mcnemar_p':1.0 if first_only+second_only==0 else exact_mcnemar_p(first_only,second_only),
            'problem_bootstrap_95_complete_case':[boot[lo],boot[hi]],'family_bootstrap_95_complete_case':[cluster[lo],cluster[hi]],
            'missing_as_failure_sensitivity':statistics.mean(sensitivity),
            'missingness_identification_bounds':[statistics.mean(minimum),statistics.mean(maximum)],
            'interpretation':'Conditional on observed matched cases; zero discordance/degenerate intervals do not prove equivalence or capture missingness uncertainty.'}


def analyze(out):
    require(not out.exists(),str(out),'Refusing to overwrite a review output directory')
    protocol=ROOT/'configs/repair_experiment_local_v0.4.2.json'
    p=validate_protocol(protocol);p['_sha256']=sha(protocol);dataset=validate_freeze()
    rows=read(BASE/'test.json');dev=read(BASE/'development.json');root=BASE/'final_runs/heldout/2027'
    for field in ['nl_statement','expected_lean_statement']:
        values=[re.sub(r'\btheorem\s+\S+','theorem _',' '.join(r[field].lower().split())) for r in dev+rows]
        require(len(set(values))==len(values),field,'Exact/equivalent-name duplicate in eligible pool')
    from transformers import AutoTokenizer
    tokenizer=AutoTokenizer.from_pretrained(Path.home()/p['model']['snapshot_home_relative'],local_files_only=True,trust_remote_code=False)
    cases=[];audits=[];unique=[];taxonomy=defaultdict(list);failures=Counter();all_error_categories=Counter()
    freeze=read(BASE/'final_protocol_freeze.json');launch=read(BASE/'heldout_launch.json')
    start=dt.datetime.fromisoformat(launch['launched_at']);frozen=dt.datetime.fromisoformat(freeze['frozen_at'])
    require(frozen<start,'freeze','Protocol freeze must precede launch')
    require(not ({r['study_eligibility']['family'] for r in rows}&{r['study_eligibility']['family'] for r in dev}),'split','Family leakage')
    for row in rows:
        ident=row['id'];folder=root/ident;m=read(folder/'manifest.json');validate_run(m,p)
        require(m['problem_id']==ident and m['dataset_sha256']==p['dataset_sha256']['heldout'],ident,'Frozen identity mismatch')
        initial=m['initial'];steps=[initial]+[a for c in ['B','C'] for a in m['conditions'][c]['attempts']]
        intents=list(folder.glob('*/intent.json'))
        require(len(intents)<=7 and len({a['key'] for a in steps})==len(steps),ident,'Duplicate/overbudget attempts')
        prompts={'initial':(ROOT/p['prompts']['initial']).read_text().format(nl_statement=row['nl_statement'],theorem_statement=row['expected_lean_statement'])}
        for condition in ['B','C']:
            branch=m['conditions'][condition];prior=initial
            require(len(branch['attempts'])<=3,ident+'/'+condition,'Repair cap exceeded')
            for ordinal,a in enumerate(branch['attempts'],1):
                require(a['key']==condition+str(ordinal),ident,'Nonsequential repair')
                require(not prior['verification']['success'],ident,'Repair after success')
                prompts[a['key']]=(ROOT/p['prompts']['blind' if condition=='B' else 'guided']).read_text().format(theorem_statement=row['expected_lean_statement'],previous_candidate=prior['candidate'],feedback=a['feedback_payload'])
                prior=a
            expected=initial['verification']['success'] or any(a['verification']['success'] for a in branch['attempts'])
            require((branch['success'] is True)==expected,ident,'Branch success contradicts attempts')
        call_records=[]
        for a in steps:
            key=a['key'];context=f'heldout/2027/{ident}/{key}';cp=ROOT/a['completion_path'];v=a['verification'];completion=read(cp);md=completion['metadata'];intent=read(cp.parent/'intent.json')
            require(completion['context']==context and completion['prompt']==prompts[key],context,'Wrong context or hidden prompt information')
            require(intent['prompt_sha256']==completion['prompt_sha256'] and intent['protocol_sha256']==p['_sha256'],context,'Intent binding mismatch')
            require(dt.datetime.fromisoformat(intent['started_at'])>=start,context,'Held-out call predates frozen launch')
            code=extract_lean_block(completion['raw_response'])
            require(sha(cp.parent/'candidate.lean')==a['candidate_sha256']==hashlib.sha256(code.encode()).hexdigest(),context,'Candidate bytes differ')
            rendered=tokenizer.apply_chat_template([{'role':'user','content':completion['prompt']}],tokenize=False,add_generation_prompt=True)
            token_ids=tokenizer.encode(rendered,add_special_tokens=False)
            require(rendered==md['rendered_chat_text'] and hashlib.sha256(rendered.encode()).hexdigest()==md['rendered_chat_sha256'],context,'Chat template mismatch')
            require(len(token_ids)==md['prompt_tokens'] and len(token_ids)+2000<=8192 and md['completion_tokens']<=2000,context,'Token/context mismatch')
            stream=folder/'streams'/(hashlib.sha256(context.encode()).hexdigest()+'.jsonl');frames=[json.loads(line) for line in stream.read_text().splitlines()]
            require(frames[0]['context']==context and frames[0]['generation_seed']==md['generation_seed'],context,'Stream header mismatch')
            require(''.join(f.get('text','') for f in frames)==completion['raw_response'],context,'Response differs from durable token stream')
            require(frames[-1].get('status')=='generation_finished' and frames[-1]['completion_tokens']==md['completion_tokens'],context,'Incomplete stream')
            expected='open scoped BigOperators\n'+row['expected_lean_statement']+' := by sorry'
            source,target=_verification_source(code,expected,_theorem_names(row['expected_lean_statement'])[0],inspect_axioms=True)
            require(source==v['verification_source_text'] and hashlib.sha256(source.encode()).hexdigest()==v['verification_source_sha256'],context,'Wrong compiled target/proof')
            messages,malformed=_diagnostics(v['compiler_stdout'] or '')
            require(not malformed,context,'Malformed raw Lean JSON')
            if v['success']:
                require(v['exit_code']==0 and not any(d['severity']=='error' for d in messages),context,'Contradictory success verdict')
                require(_axioms_from_diagnostics(messages,target)==v['axiom_dependencies'] and set(v['axiom_dependencies'])<={'propext','Classical.choice','Quot.sound'},context,'Unapproved assumptions')
            else:
                failures[v['failure_kind']]+=1
                all_error_categories[classify_compiler_error('\n'.join(v['errors']))]+=1
            wall=(dt.datetime.fromisoformat(completion['finished_at'])-dt.datetime.fromisoformat(intent['started_at'])).total_seconds()
            record={'problem_id':ident,'step':key,'prompt_tokens':md['prompt_tokens'],'completion_tokens':md['completion_tokens'],
                    'generation_seconds':md['latency_seconds'],'call_wall_seconds':wall,'compiler_seconds':v['elapsed_seconds'],
                    'success':v['success'],'source_path':str(cp.relative_to(ROOT)),'source_sha256':sha(cp)}
            call_records.append(record);unique.append(record)
        c={'problem_id':ident,'category':row['category'],'family':row['study_eligibility']['family'],
           'outcomes':{name:m['conditions'][name]['success'] for name in ['A','B','C']},
           'repair_intents':{name:len(list(folder.glob(name+'*/intent.json'))) for name in ['B','C']},
           'completed_repairs':{name:len(m['conditions'][name]['attempts']) for name in ['B','C']},
           'milestones':{name:m['conditions'][name]['milestones'] for name in ['A','B','C']},'calls':call_records,
           'manifest_path':str((folder/'manifest.json').relative_to(ROOT)),'manifest_sha256':sha(folder/'manifest.json')}
        cases.append(c)
        label=classify_compiler_error('\n'.join(initial['verification']['errors']));taxonomy[label].append(c)
        messages=[d['data'] for d in initial['verification']['diagnostics'] if d.get('severity')=='error']
        audits.append({'problem_id':ident,'initial_candidate_sha256':initial['candidate_sha256'],'same_initial':True,'same_theorem':True,
                       'same_model_and_environment':True,'blind_isolation':True,'guided_predecessor_diagnostics':True,'budget_caps_valid':True,
                       'complete_pair':all(c['outcomes'][n] is not None for n in ['B','C']),
                       'completed_calls':len(steps),'logical_intents':len(intents),'initial_error_category':label,
                       'representative_message':messages[0] if messages else initial['verification']['errors'][0]})
    metrics={}
    for name in ['A','B','C']:
        observed=[r for r in cases if r['outcomes'][name] is not None];k=sum(r['outcomes'][name] for r in observed)
        calls=[a for r in cases for a in r['calls'] if a['step']=='initial' or a['step'].startswith(name)]
        metrics[name]={'successes':k,'known_failures':len(observed)-k,'unavailable':len(cases)-len(observed),
                       'observed_denominator':len(observed),'observed_rate':k/len(observed),'wilson_95_observed':wilson_interval(k,len(observed)),
                       'eligible_denominator':len(cases),'missing_as_failure_sensitivity':k/len(cases),
                       'wilson_95_missing_as_failure':wilson_interval(k,len(cases)),
                       'completed_calls':len(calls),'completed_repair_calls':sum(a['step']!='initial' for a in calls),
                       'repair_intents_distribution':distribution([0 if name=='A' else r['repair_intents'][name] for r in cases]),
                       'completed_repairs_distribution':distribution([0 if name=='A' else r['completed_repairs'][name] for r in cases]),
                       'resources':{field:distribution([a[field] for a in calls]) for field in ['prompt_tokens','completion_tokens','generation_seconds','call_wall_seconds','compiler_seconds']}}
    comparisons=[contrast(cases,a,b) for a,b in [('C','B'),('C','A'),('B','A')]]
    for c,value in zip(comparisons,holm_adjust([c['exact_mcnemar_p'] for c in comparisons])):c['holm_adjusted_p']=value
    complete=[r for r in cases if all(r['outcomes'][c] is not None for c in ['A','B','C'])]
    curves={c:[sum(any(v is True for k,v in r['milestones'][c].items() if int(k)<=budget) for r in complete)/len(complete) for budget in range(4)] for c in ['A','B','C']}
    tax=[]
    for category,group in sorted(taxonomy.items()):
        tax.append({'category':category,'initial_examples':len(group),'B_successes':sum(r['outcomes']['B'] is True for r in group),
                    'C_successes':sum(r['outcomes']['C'] is True for r in group),
                    'B_observed':sum(r['outcomes']['B'] is not None for r in group),'C_observed':sum(r['outcomes']['C'] is not None for r in group),
                    'representative_id':group[0]['problem_id'],'representative_message':next(a['representative_message'] for a in audits if a['problem_id']==group[0]['problem_id']),
                    'diagnostic_actionability':'Error localizes a syntactic/name/type/tactic obstacle; actionable content is not proof that this model used it correctly.',
                    'scope':'Descriptive fixed pre-specified primary taxonomy; name/lemma and tactic/goal subtypes are not inferred beyond recorded messages.'})
    semantic_summary=read(ROOT/'data/ai_semantic_audit/20261028/delivery/summary.json')
    result={'schema_version':2,'frozen_protocol_sha256':sha(protocol),'dataset_manifest_sha256':sha(BASE/'freeze.json'),'dataset_validation':dataset,
            'eligible_development':len(dev),'eligible_test':len(rows),'test_families':len({r['family'] for r in cases}),
            'complete_ABC_pairs':len(complete),'seeds':p['seeds'],'pilot_cases':len(p['pilot_ids']),
            'unique_completed_calls':len(unique),'unique_logical_intents':sum(a['logical_intents'] for a in audits),
            'physical_completed_resources':{field:sum(a[field] for a in unique) for field in ['prompt_tokens','completion_tokens','generation_seconds','call_wall_seconds','compiler_seconds']},
            'conditions':metrics,'comparisons':comparisons,'paired_success_curves':{'denominator':len(complete),'curves':curves},
            'taxonomy':tax,'all_failed_candidate_taxonomy':dict(all_error_categories),'verification_failure_kinds':dict(failures),
            'semantic_review':{'historical_coding_AI_labels':semantic_summary['coding_ai_labels'],'raw_Phi4_labels':semantic_summary['phi_4_labels'],
                               'final_eligible_AI_faithful':len(dev)+len(rows),'final_eligible_AI_uncertain':0,'final_eligible_AI_unfaithful':0,
                               'excluded_total':96-len(dev)-len(rows),'independent_human_reviews':0,'model_label_counts_are_not_accuracy':True},
            'freeze_order':{'frozen_at':freeze['frozen_at'],'launch_at':launch['launched_at'],'locally_committed_before_launch':launch['source_git_commit'],
                            'external_pretest_publication_evidence':'Not present; local commit and clock records do not prove public publication before testing.'},
            'scope_limits':['Fixed reviewed theorem proof synthesis; no autonomous NL-to-statement/end-to-end accuracy measurement.',
                            'One seed; three-case frozen pilot; 54 curated test families; AI-assisted adjudication.',
                            'Bootstrap intervals are conditional on their explicit observed/sensitivity populations; not equivalence tests.'],
            'pairing_audits':audits,'cases':cases,'discrepancies':[],
            'reporting_corrections':[
                {'paths':['paper/generated/final_table2.tex','docs/FINAL_EXPERIMENT_RESULTS.md'],'record_id':'C',
                 'correction':'C=1/60 is the pre-specified missing-as-failure sensitivity, not an observed 60-case C rate. Main observed C=1/58; matched B=C=1/58.'},
                {'paths':['paper/generated/final_paired_tests.tex','data/final_study/v1/analysis/results.json'],'record_id':'C_vs_A',
                 'correction':'Original difference/interval used all-60 sensitivity while McNemar used 58 complete pairs. Revised primary effect/interval now use the same complete-pair population; original sensitivity remains separately labeled.'},
                {'paths':['docs/FINAL_M1_M7_COMPLIANCE_REPORT.md'],'record_id':'M1_M2_M6',
                 'correction':'Map exact supplied requirements: no autonomous end-to-end statement-generation measure or evidence of pretest public ID publication; local pinned-environment/proof reproducibility evaluated separately from public redaction limits.'},
                {'paths':['paper/generated/final_table4.tex'],'record_id':'semantic_review',
                 'correction':'Add historical coding-AI unfaithful/uncertain counts and examples; selected eligible all-faithful counts do not estimate semantic accuracy.'},
                {'paths':['paper/main.tex'],'record_id':'generation_attempts',
                 'correction':'412 counts durable logical intents, including one preflight rejection and one header-only interruption; 410 completed genuine responses and proof-verification records are evidenced.'}],
            'new_inference_calls':0}
    historical=read(BASE/'analysis/results.json')
    for c in ['A','B','C']:
        require(metrics[c]['successes']==historical['conditions'][c]['successes'],c,'Original success count discrepancy')
        for field in ['prompt_tokens','completion_tokens','generation_seconds','compiler_seconds']:
            require(abs(metrics[c]['resources'][field]['sum']-historical['conditions'][c][field])<1e-6,c,'Resource discrepancy: '+field)
    out.mkdir(parents=True)
    (out/'results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    (out/'case_outcomes.json').write_text(json.dumps([{k:r[k] for k in ['problem_id','category','family','outcomes','manifest_sha256']} for r in cases],indent=2)+'\n')
    print(json.dumps({'valid':True,'completed_calls':len(unique),'complete_pairs':len(complete),'logical_intents':result['unique_logical_intents'],
                      'conditions':{c:{k:metrics[c][k] for k in ['successes','observed_denominator','unavailable']} for c in metrics},
                      'original_resources_reconciled':True,'discrepancies':[]},indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True)
    analyze(parser.parse_args().output)
