"""Focused read-only validation beyond PRs #19–21. No inference or old-output writes.

Default execution reads frozen evidence and writes only this new validation dir.
Lean relationship certificates are checked separately by check_certificates.py.
"""
from __future__ import annotations

import csv
import hashlib
import importlib.util
import itertools
import json
import random
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).parent
BASE='a3a709c383ceb016de3e746f962e543bbcc8b2a5'
ARMS=['B_neutral','C_real','D_shuffled','E_token_matched','R_resample']


def digest(data): return hashlib.sha256(data).hexdigest()
def load(path): return json.loads((ROOT/path).read_text())
def csvrows(path): return list(csv.DictReader((ROOT/path).open()))
def require(condition,message):
    if not condition: raise ValueError(message)

def module(name,path):
    spec=importlib.util.spec_from_file_location(name,ROOT/path)
    value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value)
    return value

def output(name,value):
    (OUT/name).write_text(json.dumps(value,indent=2,sort_keys=True,ensure_ascii=False)+'\n')

def report(name,text): (OUT/name).write_text(text.strip()+'\n')

def table(name,records):
    with (OUT/name).open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(records[0]),lineterminator='\n')
        writer.writeheader();writer.writerows(records)


def independent_cluster_interval(records,baseline,cluster,seed=20261104,replicates=10000):
    """Paired percentile bootstrap of whole clusters; unequal sizes stay weighted."""
    groups={}
    for row in records:
        groups.setdefault(row[cluster],[]).append(int(row['C_real']=='True')-int(row[baseline]=='True'))
    units=[(sum(v),len(v)) for v in groups.values()]
    generator=random.Random(seed); estimates=[]
    for _ in range(replicates):
        total=n=0
        for _ in units:
            value,size=units[generator.randrange(len(units))]
            total+=value;n+=size
        estimates.append(total/n)
    estimates.sort()
    return [estimates[int(.025*(replicates-1))],estimates[int(.975*(replicates-1))]]


def check_statistics(studies):
    previous=load('analysis/taimma_20261104/results/results.json')
    result={}
    for label,d in studies.items():
        rows=d['outcomes']; counts={'A':sum(r['initial_success']=='True' for r in rows)}
        counts.update({a:sum(r[a]=='True' for r in rows) for a in ARMS})
        comparisons=[]
        for old in previous[label]['paired']:
            baseline=old['contrast'].split(' minus ')[1]
            cells=Counter((r['C_real']=='True',r[baseline]=='True') for r in rows)
            values=dict(both=cells[True,True],C_only=cells[True,False],baseline_only=cells[False,True],neither=cells[False,False])
            for key,value in values.items():require(old[key]==value,'Discordance mismatch '+label+key)
            interval=independent_cluster_interval(rows,baseline,'id')
            family_interval=independent_cluster_interval(rows,baseline,'family')
            require(interval==old['theorem_CI'] and family_interval==old['family_CI'],'PR20 interval mismatch '+label+baseline)
            comparisons.append(dict(baseline=baseline,**values,difference=(values['C_only']-values['baseline_only'])/len(rows),theorem_95=interval,family_95=family_interval))
        coverage={a:len({r['id'] for r in rows if r[a]=='True'}) for a in ARMS}
        for old in previous[label]['theorems']:
            require(coverage[old['arm']]==old['theorem_types'],'Solved-theorem coverage mismatch')
        result[label]=dict(counts=counts,solved_theorem_coverage=coverage,theorem_types=len({r['id'] for r in rows}),family_sizes=dict(Counter(r['family'] for r in rows)),comparisons=comparisons)
    original=load('publication/results/review_v2/analysis_verified/case_outcomes.json')
    complete=[r for r in original if r['outcomes']['B'] is not None and r['outcomes']['C'] is not None]
    both=[r['problem_id'] for r in complete if r['outcomes']['B'] and r['outcomes']['C']]
    counts={a:dict(observed=sum(r['outcomes'][a] is not None for r in original),verified=sum(r['outcomes'][a] is True for r in original)) for a in ('A','B','C')}
    require(len(original)==60 and len(complete)==58 and len(both)==1,'Study1 cohort changed')
    require(all(r['outcomes']['B']==r['outcomes']['C'] for r in complete),'Study1 discordance changed')
    archived=load('publication/results/review_v2/analysis_verified/results.json')
    for arm in ('A','B','C'):
        require(counts[arm]['observed']==archived['conditions'][arm]['observed_denominator'] and counts[arm]['verified']==archived['conditions'][arm]['successes'],'Study1 aggregate mismatch')
    lower=sum(int(r['outcomes']['C'] is True)-int(r['outcomes']['B'] is not False) for r in original)/len(original)
    upper=sum(int(r['outcomes']['C'] is not False)-int(r['outcomes']['B'] is True) for r in original)/len(original)
    original_comparison=next(r for r in archived['comparisons'] if r['comparison']=='C_vs_B')
    require([lower,upper]==original_comparison['missingness_identification_bounds'],'Study1 missingness bound mismatch')
    require(original_comparison['problem_bootstrap_95_complete_case']==[0,0] and original_comparison['family_bootstrap_95_complete_case']==[0,0],'Study1 conditional interval mismatch')
    result['Study1']=dict(counts=counts,complete_pairs=len(complete),shared_success=both,conditional_bootstrap=[0,0],missingness_bounds=[lower,upper])
    return result


def recorded_acceptance(record,candidate):
    require(record['success'] is True and record['exit_code']==0,'Recorded accepted call has no clean exit')
    require(isinstance(record.get('axiom_dependencies'),list),'Accepted call lacks an observed axiom report')
    require(set(record['axiom_dependencies']) <= {'propext','Classical.choice','Quot.sound'},'Unsupported accepted-call axiom')
    require(not re.search(r'\b(sorry|sorryAx|admit|axiom|constant|opaque)\b',candidate),'Prohibited candidate accepted')


def step_key(r): return r['model'],str(r['seed']),r['id'],r['arm'],int(r['index'])


def study1_controls():
    protocol_path='publication/source_snapshot/configs/repair_experiment_local_v0.4.2.json'
    raw=(ROOT/protocol_path).read_bytes();protocol=json.loads(raw)
    cases=load('publication/results/review_v2/analysis_verified/case_outcomes.json')
    checked=Counter();models=set()
    for case in cases:
        base='publication/evidence/redacted_runs/heldout/2027/'+case['problem_id']+'/'
        manifest=load(base+'manifest.json')
        require(manifest['protocol_sha256']==digest(raw),'Study1 frozen protocol mismatch')
        initial=manifest['initial'];initial_sha=digest(initial['candidate'].encode())
        require(initial_sha==initial['candidate_sha256'],'Study1 initial SHA mismatch')
        checked['shared_initial_evaluations']+=1
        for arm in ('A','B','C'):
            branch=manifest['conditions'][arm]
            require(branch['initial_candidate_sha256']==initial_sha,'Study1 initial differs by condition')
            require(len(branch['attempts'])<=protocol['maximum_repairs'],'Study1 repair budget exceeded')
            require(branch['success']==case['outcomes'][arm],'Study1 unavailable endpoint was reclassified')
            previous=initial
            for step in branch['attempts']:
                candidate=step['candidate'];key=step['key']
                require(digest(candidate.encode())==step['candidate_sha256'],'Study1 repair SHA mismatch')
                completion=load(base+key+'/completion.json');meta=completion['metadata']
                require(previous['candidate'] in completion['prompt'],'Study1 wrong predecessor')
                expected_seed=int.from_bytes(hashlib.sha256(f"{meta['base_seed']}:{meta['generation_context']}:{meta['prompt_sha256']}".encode()).digest()[:4],'big')
                require(meta['generation_seed']==expected_seed,'Study1 seed-policy mismatch')
                require(candidate in completion['raw_response'],'Study1 candidate absent from response')
                models.add(meta['model']);checked['completed_'+arm+'_repairs']+=1
                previous=step
    return dict(protocol=protocol_path,protocol_sha256=digest(raw),settings=dict(maximum_repairs=protocol['maximum_repairs'],condition_order=protocol['condition_order'],seeds=protocol['seeds'],max_output_tokens=protocol['decoding']['max_tokens'],max_context_tokens=protocol['decoding']['max_context_tokens']),checks=dict(checked),models=sorted(models),note='Public redacted views checked; original prompt hashes are retained metadata and are not hashes of the redacted prompt view.')


def controls(studies,archive,runner):
    token_rows=[];summaries={}; raw_digests={}
    ref={r['id']:r for r in runner.bridge_rows('test')}
    for label,d in studies.items():
        ct=Counter();delta_first=[];rotations=Counter();later_difference=[];later_predecessor=Counter()
        calls={step_key(r):r for r in d['calls']}
        transition_index={step_key(r):r for r in d['transitions']}
        byseed=defaultdict(dict)
        for _,t in d['trajectories']:byseed[t['seed']][t['id']]=t
        for source,t in d['trajectories']:
            tid=t['id'];seed=t['seed'];initial=t['initial']
            require(digest(initial['candidate'].encode())==initial['candidate_sha256'],'Initial candidate binding')
            expected=runner.rotating_arms(tid,seed)
            require(t['order']==expected,'Rotation mismatch')
            rotations[' > '.join(expected)]+=1
            ct['shared_initial_evaluations']+=1
            initial_base=(source.split('::',1)[1] if label=='V8' else source).replace('/trajectories/','/runs/').removesuffix('.json')+'/initial/'
            def initial_raw(name):
                if label=='V8':return archive.get(initial_base+name)
                path=ROOT/(initial_base+name)
                if not path.exists():return None
                raw=path.read_bytes();raw_digests[initial_base+name]=digest(raw);return raw
            iraw=[initial_raw(n) for n in ('completion.json','intent.json','verification.json')]
            if all(v is not None for v in iraw):
                completion,intent,verification=map(json.loads,iraw)
                require(completion['prompt']==runner.initial_prompt(ref[tid]),'Initial target/prompt changed')
                require(digest(completion['prompt'].encode())==completion['prompt_sha256']==intent['prompt_sha256'],'Initial prompt SHA mismatch')
                expected_seed=int.from_bytes(hashlib.sha256((str(seed)+'/'+completion['context']+'/'+completion['prompt_sha256']).encode()).digest()[:4],'big')
                require(completion['call_seed']==expected_seed,'Initial sampling seed mismatch')
                require(intent['model']==t['model'] and intent['seed']==seed,'Initial model/base seed mismatch')
                require(initial['candidate'] in completion['raw_response'] and verification['candidate_sha256']==initial['candidate_sha256'],'Initial response/verifier binding mismatch')
                require(verification['success']==initial['verification']['success'],'Initial recorded outcome mismatch')
                outcome=next(r for r in d['outcomes'] if r['id']==tid and r['seed']==str(seed))
                require(runner.failure_class(verification)==outcome['initial_error'],'Initial error category mismatch')
                initial_call=calls[(t['model'],str(seed),tid,'A',0)]
                for field in ('prompt_tokens','completion_tokens'):
                    require(int(initial_call[field])==completion['metadata'][field]==initial['metadata'][field],'Initial token accounting mismatch')
                if verification['success']:
                    recorded_acceptance(verification,initial['candidate'])
                ct['raw_initial_calls_verified']+=1
            else:ct['raw_initial_calls_unavailable']+=1
            for arm in ARMS:
                steps=t['arms'][arm]['steps']
                require(len(steps)<=3,'Repair-call budget exceeded')
                require([s['key'] for s in steps]==[f'{arm}_{i}' for i in range(1,len(steps)+1)],'Nonconsecutive steps')
                previous=initial
                for i,s in enumerate(steps,1):
                    k=(t['model'],str(seed),tid,arm,i)
                    require(int(calls[k]['prompt_tokens'])==s['metadata']['prompt_tokens'],'Prompt accounting mismatch')
                    require(int(calls[k]['completion_tokens'])==s['metadata']['completion_tokens'],'Output accounting mismatch')
                    ct['completed_repairs_checked']+=1
                    if arm=='E_token_matched':
                        details=s['details'];actual=s['metadata']['prompt_tokens'];target=details['target']
                        require(details['actual']==actual and details['delta']==actual-target,'E metadata mismatch')
                        require(details['matched']==(abs(actual-target)<=3),'E tolerance flag mismatch')
                        cs=t['arms']['C_real']['steps'];c_at=cs[i-1] if len(cs)>=i else None
                        cactual=c_at['metadata']['prompt_tokens'] if c_at else None
                        cprev=initial if i==1 else cs[i-2] if len(cs)>=i else None
                        same=cprev is not None and previous['candidate_sha256']==cprev['candidate_sha256']
                        if i==1:
                            require(cactual==target and same,'First repair does not share C target/predecessor')
                            delta_first.append(actual-cactual)
                        elif cactual is not None:
                            later_difference.append(actual-cactual);later_predecessor[str(same)]+=1
                        token_rows.append(dict(study=label,seed=seed,theorem=tid,step=i,target_on_E_history=target,actual_E_tokens=actual,delta_E_target=actual-target,matched_within_3=details['matched'],actual_C_tokens=cactual,delta_E_actual_C=actual-cactual if cactual is not None else None,same_predecessor_as_C=same if c_at else None))
                    # Raw journal checks: V8 is indexed, V7 remains a local-source check.
                    if label=='V8':
                        base=source.split('::',1)[1].replace('/trajectories/','/runs/').removesuffix('.json')+'/'+s['key']+'/'
                        def rawfile(name):return archive.get(base+name)
                    else:
                        base='study2_outputs/bridge_v7_base/runs/'+source.split('/trajectories/')[1].removesuffix('.json')+'/'+s['key']+'/'
                        def rawfile(name):
                            p=ROOT/(base+name)
                            if not p.exists():return None
                            raw=p.read_bytes();raw_digests[base+name]=digest(raw);return raw
                    raw=rawfile('completion.json');intent_raw=rawfile('intent.json');verify_raw=rawfile('verification.json')
                    if raw is None or intent_raw is None or verify_raw is None:
                        ct['raw_call_unavailable']+=1;previous=s;continue
                    completion=json.loads(raw);intent=json.loads(intent_raw);verification=json.loads(verify_raw)
                    ct['raw_calls_verified']+=1
                    require(digest(completion['prompt'].encode())==completion['prompt_sha256']==intent['prompt_sha256'],'Prompt SHA mismatch')
                    calculated=int.from_bytes(hashlib.sha256((str(seed)+'/'+completion['context']+'/'+completion['prompt_sha256']).encode()).digest()[:4],'big')
                    require(completion['call_seed']==calculated,'Per-arm deterministic call seed mismatch')
                    require(intent['model']==t['model'] and intent['seed']==seed,'Model/seed changed')
                    require(s['candidate'] in completion['raw_response'],'Candidate absent from response')
                    require(verification['candidate_sha256']==s['candidate_sha256'],'Raw verifier candidate hash mismatch')
                    require(verification['success']==s['verification']['success'],'Raw verifier outcome mismatch')
                    if verification.get('verification_source_text') is not None:
                        require(digest(verification['verification_source_text'].encode())==verification['verification_source_sha256'],'Verification source hash mismatch')
                    require('Fixed theorem:\n```lean\n'+ref[tid]['expected_lean_statement']+'\n```' in completion['prompt'],'Fixed target changed')
                    if arm!='R_resample':
                        require('Previous candidate:\n```lean\n'+previous['candidate']+'\n```' in completion['prompt'],'Wrong predecessor in paired prompt')
                        ct['predecessor_prompt_bindings']+=1
                    else:
                        require('Previous candidate:' not in completion['prompt'],'Resampling includes previous candidate')
                    pkey='initial' if i==1 else f'{arm}_{i-1}'
                    previous_path=base.rsplit('/',2)[0]+'/'+pkey+'/verification.json'
                    previous_raw=archive[previous_path] if label=='V8' else (ROOT/previous_path).read_bytes()
                    previous_verification=json.loads(previous_raw)
                    transition=transition_index[k]
                    require(runner.failure_class(previous_verification)==transition['previous_error'] and runner.failure_class(verification)==transition['new_error'],'Recorded error category does not match frozen classifier')
                    ct['category_transitions_reclassified']+=1
                    if arm=='D_shuffled':
                        donor=s['details']['donor_id'];pool=byseed[seed]
                        require(donor!=tid and pool[donor]['family']!=t['family'],'Donor is self/same recorded family')
                        options=[]
                        for donor_id,dt in pool.items():
                            if donor_id==tid or dt['family']==t['family']:continue
                            if label=='V8':
                                dp=next(n for n in archive if n.endswith('/'+str(seed)+'/test/'+donor_id+'/initial/verification.json') and 'coder_exploratory/runs/' in n)
                                dv=json.loads(archive[dp])
                            else:
                                dp=ROOT/('study2_outputs/bridge_v7_base/runs/'+source.split('/trajectories/')[1].split('/')[0]+'/'+str(seed)+'/test/'+donor_id+'/initial/verification.json')
                                if not dp.exists():continue
                                dv=json.loads(dp.read_bytes())
                            payload=runner.diagnostic(dv)
                            if payload:options.append((digest(f'donor/{tid}/{seed}/{i}/{donor_id}'.encode()),donor_id,payload))
                        require(bool(options),'No valid donor options')
                        _,expected_donor,payload=min(options)
                        require(expected_donor==donor,'Shuffled donor selection mismatch')
                        # These test traces show no cap truncation; payload must match exactly.
                        require(s['details']['truncated'] is False,'Unexpected truncation requires explicit reconstruction')
                        require(completion['prompt']==runner.repair_prompt(ref[tid],previous['candidate'],payload,arm),'Wrong shuffled diagnostic payload')
                        ct['donor_assignments_verified']+=1
                    if arm=='C_real':
                        # Obtain actual predecessor's raw verification (slim V7 views omit diagnostics).
                        pkey='initial' if i==1 else f'C_real_{i-1}'
                        if label=='V8':pr=archive[base.rsplit('/',2)[0]+'/'+pkey+'/verification.json']
                        else:pr=(ROOT/(base.rsplit('/',2)[0]+'/'+pkey+'/verification.json')).read_bytes()
                        payload=runner.diagnostic(json.loads(pr))
                        require(s['details']['truncated'] is False,'Unexpected C truncation')
                        require(completion['prompt']==runner.repair_prompt(ref[tid],previous['candidate'],payload,arm),'Real feedback not from own predecessor')
                        ct['genuine_feedback_bindings_verified']+=1
                    if verification['success']:
                        recorded_acceptance(verification,s['candidate'])
                        ct['recorded_verified_repair_policies_checked']+=1
                    previous=s
        require(len(delta_first)==sum(r['initial_success']=='False' for r in d['outcomes']),'Wrong eligible first-repair denominator')
        summaries[label]=dict(checks=dict(ct),first_repair_token_deltas=dict(sorted(Counter(delta_first).items())),first_repair_n=len(delta_first),first_repair_tolerance_failures=sum(abs(v)>3 for v in delta_first),rotations=dict(rotations),later_comparable_E_C=len(later_difference),later_E_C_same_predecessor=dict(later_predecessor),later_actual_E_minus_C_min=min(later_difference) if later_difference else None,later_actual_E_minus_C_max=max(later_difference) if later_difference else None)
    table('TOKEN_MATCHING_VERIFICATION.csv',token_rows)
    return dict(studies=summaries,local_raw_file_count=len(raw_digests),local_raw_inventory_digest=digest(json.dumps(raw_digests,sort_keys=True).encode()),local_provenance='Local V7 raw journal consistency check, not an independently indexed public archive')


def normalize_statement(statement,alpha=False):
    body=statement.split(' ',2)[2]
    if alpha:
        names=[]
        for binder in re.findall(r'\(([^()]*)\)',body):
            if ':' in binder: names.extend(binder.split(':')[0].split())
        replacements={name:'v'+str(i) for i,name in enumerate(names)}
        body=re.sub(r'\b\w+\b',lambda m:replacements.get(m.group(),m.group()),body)
    return re.findall(r'\w+|[^\w\s]',body)


def benchmark(studies,archive,runner):
    reference=[dict(split=split,**r) for split in ('development','test') for r in runner.bridge_rows(split)]
    old_audit=json.loads(archive[next(n for n in archive if n.endswith('validation/BENCHMARK_AUDIT.json'))])
    byid={r['id']:r for r in reference}
    screens=[json.loads(raw) for path,raw in archive.items() if '/reference_screen/reference_screen/bridge_t' in path and path.endswith('.json')]
    require({r['id'] for r in screens}=={r['id'] for r in reference if r['split']=='test'},'Reference screen cohort mismatch')
    require(all(r['constructed_reference_proof_kernel_verified'] and r['verification']['success'] for r in screens),'Reference strict screen failure')
    ai=json.loads(archive[next(n for n in archive if n.endswith('ai_review/AI_REVIEW_SUMMARY.json'))])
    prior={r['id']:r for r in old_audit['records']}
    inventory=[]
    for r in reference:
        tid=r['id'];statement=r['expected_lean_statement'];proof=r['reference_lean_proof']
        require(digest(statement.encode())==prior[tid]['theorem_sha256'],'Statement differs from archived benchmark')
        require(digest(proof.encode())==prior[tid]['reference_sha256'],'Reference proof differs from archive')
        inventory.append(dict(id=tid,split=r['split'],family=r['study_eligibility']['family'],statement=statement,statement_sha256=digest(statement.encode()),reference_proof_sha256=digest(proof.encode())))
    table('STATEMENT_INVENTORY.csv',inventory)
    require(len(reference)==36 and sum(r['split']=='test' for r in reference)==24,'Wrong benchmark sizes')
    exact=[];alpha=[]
    for a,b in itertools.combinations(reference,2):
        if normalize_statement(a['expected_lean_statement'])==normalize_statement(b['expected_lean_statement']):exact.append([a['id'],b['id']])
        if normalize_statement(a['expected_lean_statement'],True)==normalize_statement(b['expected_lean_statement'],True):alpha.append([a['id'],b['id']])
    pairs=[('bridge_d06','bridge_t11','Proof transport by pow_two','d06_to_t11'),('bridge_d06','bridge_t12','Definitional equality after binder renaming','d06_t12_definitional'),('bridge_t11','bridge_t12','Proof transport by pow_two in both directions','t11_to_t12; t12_to_t11'),('bridge_d07','bridge_t13','Forward specialization z=1 from t13 to d07; no converse claim','t13_specializes_to_d07'),('bridge_t07','bridge_t08','Different successor/addition expressions; transport uses commutativity','t07_to_t08; t08_to_t07')]
    cert_source=(OUT/'OverlapCertificates.lean').read_text()
    definitions=dict(re.findall(r'^def (\w+) : Prop := (.+)$',cert_source,re.M))
    for tid,name in {'bridge_d06':'D06','bridge_t11':'T11','bridge_t12':'T12','bridge_d07':'D07','bridge_t13':'T13','bridge_t07':'T07','bridge_t08':'T08'}.items():
        source=byid[tid]['expected_lean_statement'].split(' ',2)[2]
        match=re.fullmatch(r'((?:\([^()]*\)\s*)+)\s*:\s*(.*)',source)
        require(match is not None,'Unexpected certificate binder structure')
        expected='∀ '+match.group(1).strip()+', '+match.group(2)
        require(re.findall(r'\w+|[^\w\s]',expected)==re.findall(r'\w+|[^\w\s]',definitions[name]),'Certificate proposition differs from frozen source')
    log=json.loads((OUT/'lean_certificate_check.json').read_text())
    require(log['certificate_sha256']==digest((OUT/'OverlapCertificates.lean').read_bytes()),'Certificate changed after local check')
    cert_status=log['status']
    out=[]
    for a,b,relationship,cert in pairs:
        successes={}
        for label,d in studies.items():
            successes[label]={tid:{arm:sum(r[arm]=='True' for r in d['outcomes'] if r['id']==tid) for arm in ['initial_success']+ARMS} for tid in (a,b)}
        out.append(dict(left=a,right=b,left_statement=byid[a]['expected_lean_statement'],right_statement=byid[b]['expected_lean_statement'],cross_split=byid[a]['split']!=byid[b]['split'],exact_text_after_removing_name=normalize_statement(byid[a]['expected_lean_statement'])==normalize_statement(byid[b]['expected_lean_statement']),alpha_normalized_match=normalize_statement(byid[a]['expected_lean_statement'],True)==normalize_statement(byid[b]['expected_lean_statement'],True),relationship_under_examination=relationship,certificate=cert,certificate_status=cert_status,test_successes=json.dumps(successes,sort_keys=True),human_adjudication='Outstanding: independence, family grouping, split leakage, NL fidelity; not certified by Lean implication'))
    table('BENCHMARK_OVERLAP_EVIDENCE.csv',out)
    scopes=[]
    for excluded in [[],['bridge_t11','bridge_t12'],['bridge_t11','bridge_t12','bridge_t13'],['bridge_t11','bridge_t12','bridge_t13','bridge_t08']]:
        r=[r for r in studies['V7']['outcomes'] if r['id'] not in excluded]
        scopes.append(dict(excluded=excluded,n=len(r),B=sum(x['B_neutral']=='True' for x in r),C=sum(x['C_real']=='True' for x in r),D=sum(x['D_shuffled']=='True' for x in r)))
    previous=load('analysis/taimma_20261104/results/results.json')['sensitivity']
    for now,old in zip(scopes,previous):
        require(now['n']==old['n_theorem_seed'],'Exclusion denominator mismatch')
        require([now[a] for a in ('B','C','D')]==[old['counts'][a] for a in ARMS[:3]],'Exclusion success mismatch')
    return dict(statements_checked=36,recorded_strict_reference_successes=len(screens),ai_review_flags=ai['flag_or_uncertain_ids'],normalized_text_pairs=exact,alpha_pairs=alpha,scopes=scopes,heuristic_within_test=len(old_audit['near_duplicates_HEURISTIC']),heuristic_cross_split=len(old_audit['cross_split_similarity_HEURISTIC']),certificate_status=cert_status,certificate_sha256=digest((OUT/'OverlapCertificates.lean').read_bytes()))


def failure_check(studies,runner,archive):
    result={}
    for label,d in studies.items():
        transitions=d['transitions'];guided=[r for r in transitions if r['arm']=='C_real']
        repeated=sum(r['candidate_repeated']=='True' for r in guided)
        changed_failed=sum(r['previous_error']!=r['new_error'] and r['verified']=='False' for r in guided)
        curves={}
        for arm in ARMS:
            vals=[]
            for budget in range(4):
                count=0
                for _,t in d['trajectories']:
                    success=t['initial']['verification']['success'] or any(s['verification']['success'] for s in t['arms'][arm]['steps'][:budget])
                    count+=bool(success)
                vals.append(count)
            old=csvrows(f'analysis/taimma_20261104/results/{label}_budgets.csv')
            require(vals==[int(r['success']) for r in old if r['arm']==arm],'Repair-budget curve mismatch')
            curves[arm]=vals
        curves['A']=[sum(r['initial_success']=='True' for r in d['outcomes'])]*4
        # Validate repetition and error-class transitions directly against trajectory bytes.
        for _,t in d['trajectories']:
            for arm in ARMS:
                prev=t['initial']
                for i,s in enumerate(t['arms'][arm]['steps'],1):
                    tr=next(r for r in transitions if r['id']==t['id'] and r['seed']==str(t['seed']) and r['arm']==arm and int(r['index'])==i)
                    require((prev['candidate']==s['candidate'])==(tr['candidate_repeated']=='True'),'Repetition mismatch')
                    require(s['verification']['success']==(tr['verified']=='True'),'Verification transition mismatch')
                    prev=s
        result[label]=dict(guided_repetitions=repeated,guided_calls=len(guided),changed_category_unverified=changed_failed,budget_curves=curves)
    excerpts=load('analysis/taimma_supervisor_final/case_excerpts.json')
    case_checks=[]
    for case in excerpts:
        require(case['seed']==2027,'Case seed mismatch')
        if case['id'].startswith('bridge_'):
            t=next(t for _,t in studies['V7']['trajectories'] if t['id']==case['id'] and t['seed']==case['seed'])
            require(case['model']==t['model'] and case['family']==t['family'],'Case model/family mismatch')
            available={s['key']:s for a in ARMS for s in t['arms'][a]['steps']};available['initial']=t['initial']
            steps=[dict(key='initial',**case['initial'])]+case['steps']
            for s in steps:
                original=available[s['key']]
                require(s['candidate']==original['candidate'] and s['verified']==original['verification']['success'],'V7 case excerpt mismatch')
                require(s['diagnostic']==original['verification']['diagnostic_text'],'V7 case diagnostic mismatch')
        else:
            manifest=load(case['source'])
            available={s['key']:s for a in ('B','C') for s in manifest['conditions'][a]['attempts']};available['initial']=manifest['initial']
            steps=[dict(key='initial',**case['initial'])]+case['steps']
            for s in steps:
                original=available[s['key']]
                require(s['candidate']==original['candidate'] and s['candidate_sha256']==digest(s['candidate'].encode()),'Study1 case candidate mismatch')
                require(s['verified']==original['verification']['success'] and s['diagnostic']==original['verification'].get('diagnostic_text'),'Study1 case verification mismatch')
                completion=load(case['source'].rsplit('/',1)[0]+'/'+s['key']+'/completion.json')
                require(case['model']==completion['metadata']['model'] and case['seed']==completion['metadata']['base_seed'],'Case model/seed binding mismatch')
                require(s['candidate'] in completion['raw_response'],'Case candidate absent from response')
        case_checks.append(dict(id=case['id'],model=case['model'],seed=case['seed'],candidate_and_diagnostic_bindings='passed',selection='Existing post-hoc illustrative selection; not representative or favorable-only efficacy evidence'))
    return dict(studies=result,cases=case_checks)


def provenance(archive,studies):
    plan=load('research/study2-v7/test/plan.json')
    checked=[]
    for path,expected in plan['source_files'].items():
        exists=(ROOT/path).is_file()
        actual=digest((ROOT/path).read_bytes()) if exists else None
        checked.append(dict(path=path,status='matches frozen plan' if actual==expected else 'missing' if not exists else 'differs from frozen plan',expected=expected,actual=actual))
    require(all(r['status']=='matches frozen plan' for r in checked),'Frozen V7 source-file provenance mismatch')
    require(digest((ROOT/'research/study2-v7/test/outcomes.csv').read_bytes())=='e766a98ae53830e748da273aaace3ff958e15d53dd72cd92387f25928a3cc72a','V7 frozen outcome hash mismatch')
    require(digest((ROOT/'study2_supervisor_suite_v7.py').read_bytes())==plan['script_sha256'],'Frozen V7 runner hash changed')
    lock=json.loads(archive[next(n for n in archive if n.endswith('FINAL_1_4_6_LOCK.json'))])
    for e in lock['data_hashes']:
        path=e['path']
        if path in archive:raw=archive[path]
        elif path.startswith('study2_outputs/bridge_v7_base/'):
            tail=path.split('bridge_v7_base/')[1].replace('reports/','')
            raw=(ROOT/('research/study2-v7/'+('test/plan.json' if tail=='plan.json' else tail))).read_bytes()
        else:raw=(ROOT/path).read_bytes()
        require(digest(raw)==e['sha256'],'Frozen lock mismatch '+path)
    v8plan=json.loads(archive[next(n for n in archive if n.endswith('coder_exploratory/plan.json'))])
    require(v8plan['script_sha256']==plan['script_sha256'],'V8 runner revision differs')
    for label,p in [('V7',plan),('V8',v8plan)]:
        require(p['repairs']==3 and p['arms']==ARMS and p['seeds']==[2027,2028,2029],'Study2 plan policy mismatch')
        require(set(p['models'])=={r['model'] for r in studies[label]['outcomes']},'Study2 model mismatch')
    warnings=load('research/study2-raw-v8-v9/PRIVACY_SCAN_WARNINGS.json')
    warning_records=[r for r in warnings['warnings'] if r['type']=='local_mac_path']
    v9=json.loads(archive[next(n for n in archive if n.endswith('new_repair_arm/development_results.json'))])
    return dict(archive_members_verified=len(archive),frozen_lock_entries=len(lock['data_hashes']),v7_plan_sha256=digest((ROOT/'research/study2-v7/test/plan.json').read_bytes()),v7_source_files=checked,privacy_warning_records=len(warning_records),privacy_path_occurrences=sum(r['count'] for r in warning_records),privacy_manual_review_required=warnings['public_release_requires_manual_review'],v9=dict(planned=v9['planned'],new_arm_verified=v9['new_arm_verified'],comparison=v9['original_v8_coder_guided_verified'],unknown=v9['unknown_outcomes'],scope='development only, no new test'))


def reports(result):
    stats=result['statistics'];ctrl=result['controls']['studies'];bench=result['benchmark'];prov=result['provenance'];failure=result['failure']['studies']
    report('EXPERIMENTAL_CONTROL_VERIFICATION.md',f'''# Experimental controls: focused additional verification

Baseline `{BASE}` includes PRs #19–21. No experimental source or outcome changed. `TOKEN_MATCHING_VERIFICATION.csv` is the new row-level reconstruction; `verification_results.json` contains all check counts.

First repairs: V7 **{ctrl['V7']['first_repair_n']}/68** and V8 **{ctrl['V8']['first_repair_n']}/61** E prompts agree with their recorded C targets within the declared ±3-token tolerance, with **zero failures**. Actual E−C deltas are V7 `{ctrl['V7']['first_repair_token_deltas']}` and V8 `{ctrl['V8']['first_repair_token_deltas']}`: every absolute delta is ≤1. These comparisons use recorded rendered prompt-token counts; no tokenizer/model was loaded. E's metadata actual/target/delta/matched fields agree with call records. This validates the first-repair tolerance; it does not establish equal compute or isolate diagnostic content.

Frozen source `study2_supervisor_suite_v7.py::one_trajectory` targets E to a hypothetical genuine-feedback prompt built on **E's own predecessor**. After step one that need not be C's predecessor. The new CSV distinguishes that target from actual C prompt length at the same step; unavailable C steps after early success remain blank. Comparable later E−C ranges are V7 [{ctrl['V7']['later_actual_E_minus_C_min']},{ctrl['V7']['later_actual_E_minus_C_max']}] and V8 [{ctrl['V8']['later_actual_E_minus_C_min']},{ctrl['V8']['later_actual_E_minus_C_max']}] tokens. No trajectory-level matching is inferred.

Checks validate a shared initial candidate per theorem/seed, fixed target text in each recorded prompt, ≤3 repair calls, ordered step keys, deterministic hash-rotated arm order, own-predecessor C diagnostics, and cross-ID/cross-recorded-family D donors selected by the frozen hashed rank. D is a deterministic donor assignment from the initial-failure pool, not necessarily a one-to-one permutation and not mathematically independent just because family labels differ. Seed derivation is SHA256(base seed/context/prompt hash), first four digest bytes; contexts include arm and step. Thus sampling streams are condition-specific, not common random draws. R excludes the failed candidate but uses the shared initial outcome to decide whether repair is needed.

Raw journal checks: V7 {ctrl['V7']['checks'].get('raw_calls_verified',0)} repairs checked; V8 {ctrl['V8']['checks'].get('raw_calls_verified',0)} checked. Missing V7 originals, if any, are separately counted; local raw checks do not upgrade their historical provenance. Prompt/candidate/verifier hashes, token fields and recorded accepted-repair policy were checked. Frozen `src/verify.py` rejects prohibited proof escapes/declarations, checks the fixed type via its expected/candidate harness, inspects named candidate axiom dependencies, and accepts only allowed standard axioms. Exit code alone is insufficient. Parser/elaborator/tactic diagnostics arise before trusted kernel checking of accepted terms.

Study 1 additionally validates all 60 shared-initial manifests, frozen v0.4.2 protocol SHA, B/C repair budgets, recorded predecessor strings and colon-delimited seed derivation in the published redacted views. Its order is fixed B then C, output cap 2000, and one seed 2027. Study 2 rotates five repair arms, uses output cap 1200 and three seeds. Original prompt hashes in redacted Study 1 views are not hashes of the redacted display text. Do not pool the designs or describe Study 1 as rotated.

Controlled: target, shared initial candidate, model within run, verifier/prompt policies and maximum calls. Not equalized: realized input/output tokens, early stopping, diagnostic meaning, later histories, sampling draws, total runtime, or benchmark dependence/contamination. **C versus B is equal maximum calls, not equal compute.** Existing cost tables remain authoritative. The prompt-length control neither proves causality nor rules out contextual/sampling alternatives.

Measurement clarification beyond PR21: `MLXModel.count(payload)` applies the chat template, so the recorded original/used feedback-token counts include its wrapper; the 384-token prefix cap uses plain tokenizer encoding. They are not interchangeable measures of full diagnostic length.
''')
    comparisons=[]
    for label in ('V7','V8'):
        for c in stats[label]['comparisons']:
            comparisons.append(f"- {label} C−{c['baseline']}: both/C-only/baseline-only/neither = {c['both']}/{c['C_only']}/{c['baseline_only']}/{c['neither']}; difference {100*c['difference']:.2f} pp; theorem interval {[round(100*x,2) for x in c['theorem_95']]}; family interval {[round(100*x,2) for x in c['family_95']]}. Exact stored proportions match PR20.")
    report('STATISTICAL_INTEGRITY_REPORT.md','''# Independent statistical cross-check

`validate.py::independent_cluster_interval` independently reconstructs the paired percentile bootstrap from the frozen outcome rows without invoking PR20's bootstrap function or writing its outputs. Seed 20261104; 10,000 draws; endpoints floor(.025×9999), floor(.975×9999). Cluster insertion order follows the frozen CSV. All seeds of a sampled theorem remain together. Family sensitivity samples eight recorded families uniformly and computes sum(differences)/sum(rows) in each resample, retaining unequal family sizes. It is a row-weighted ratio, not an unweighted mean of family rates. Family sizes are recorded below.

'''+ '\n'.join(comparisons)+f'''

V7 family row sizes: `{stats['V7']['family_sizes']}`. There are 24 nominal theorem types × three dependent repeated seeds, not 72 independent mathematical problems. PR20's pooled intervals preserve this clustering. Original per-seed family intervals use seed 20271102 and 24 rows for that seed, a different scope; per-seed Wilson and McNemar calculations should not be portrayed as family-adjusted pooled inference. Related theorems can violate independence across nominal clusters. No new p-values are calculated.

Study 1 independently reconstructs A 0/60, B 1/60, C 1/58 observed, two missing C outcomes and 58 complete B/C pairs; the shared success is `{stats['Study1']['shared_success']}`. The complete-pair difference vector is identically zero, so empirical conditional theorem/family bootstraps are [0,0]. That degeneracy is not equivalence. Full-cohort missingness identification bounds [0,2/60] = [0,+3.33] pp remain separate from sampling confidence intervals. Missing C is never converted into observed failure.

V7 totals `{stats['V7']['counts']}` and V8 totals `{stats['V8']['counts']}` are derived from actual CSVs. All V8 B/C/D/E successes were initially verified. R adds three successes to reach 14/72.

Preserved discrepancy: `research/study2-final/FINAL_RESEARCH_HANDOFF.md` quotes pooled family intervals [−1.67,+15.39] and [−2.78,+6.41] pp; PR20 gives [−1.52,+15.38] and [−3.03,+6.67]. The handoff's exact pooled draw stream/recipe is not supplied; attributing the difference solely to random seed would be speculation. PR20's reproducible values are not silently substituted into historical records. Both analyses are inconclusive; no positive significance, equivalence or general causal advantage is inferred.
''')
    report('BENCHMARK_VALIDITY_VERIFICATION.md',f'''# New structural and Lean-certificate evidence

All 36 source statements (12 development, 24 test) and reference-proof hashes match the archived benchmark audit. `STATEMENT_INVENTORY.csv` records exact statements and hashes. A deterministic token comparison excluding theorem names finds exact text pairs `{bench['normalized_text_pairs']}` and alpha-normalized pairs `{bench['alpha_pairs']}`. This is a syntactic screen only; absence of a match does not establish independence.

`OverlapCertificates.lean` gives explicit, inspectable transport statements for the five previously flagged pairs; status **{bench['certificate_status']}**, source SHA `{bench['certificate_sha256']}`. `lean_certificate_check.json` records the actual local command and full axiom reports. D06/T12 checks by definitional reflexivity; square expansion transports D06→T11 and T11↔T12; T13 specialized at z=1 transports to D07; T07↔T08 transport explicitly uses addition commutativity. Different syntax is not automatically a different mathematical template. The specialization certificate asserts no converse/generalization, and successor transport is not labeled textual identity.

These are new audit certificates, not repaired model candidates and not reruns of held-out evaluations. All named certificates were checked locally, but compilation is not independent human mathematical adjudication, benchmark approval or a contamination test. Allowed axiom reports are retained; there are no proof placeholders or newly declared axioms. No frozen item is edited, regrouped or deleted. `BENCHMARK_OVERLAP_EVIDENCE.csv` distinguishes exact text, binder-renamed forms, explicit transport and cross-split status. All other mathematical relations remain unadjudicated.

Existing recorded screens attest 24/24 test reference proofs, {bench['heuristic_within_test']} heuristic within-test pairs and {bench['heuristic_cross_split']} cross-split similarities; these are not all logical equivalences. The nine AI flags remain relevant and are not human sign-off. Placeholder English cannot establish NL fidelity; training overlap remains unassessed. Reference-screen success is formal acceptance, not benchmark independence.

Reproduced existing exclusion scopes: `{bench['scopes']}`. Denominators 72/66/63/60 retain B/C/D successes 5/10/9 because the removed cases had none. Percentage increases are denominator changes, not new successes; exclusions chosen after inspection cannot restore untouched held-out status. Independent review requirements are in HUMAN_ADJUDICATION_REQUIRED.md and the existing PR21 worksheet.
''')
    report('HUMAN_ADJUDICATION_REQUIRED.md','''# Outstanding independent review

Use `analysis/taimma_supervisor_final/INDEPENDENT_BENCHMARK_REVIEW_PACKET.md` for exact statements, references, development/test success contribution and signature blanks. This supplement adds checkable certificates and structural screening, not a second copy of that packet.

An independent mathematician/Lean expert must assess the five flagged pairs, the broader 12/10 heuristic candidate lists and nine AI flags; choose defensible mathematical-family and split-leakage criteria; inspect NL fidelity; and give signed/dated reasoning with conflicts disclosed. Review the explicit certificate direction for D07/T13: specialization does not assert a converse or benchmark equivalence. Decide how T07/T08's commutativity-based transport affects practical task independence. Formal proof acceptance cannot answer these design questions.

Required sign-off: reviewer/affiliation ____; independence/conflicts ____; pairs and exact source hashes inspected ____; mathematical disposition and rationale ____; split/benchmark implications ____; signature/date ____. Training contamination remains unassessed without independent evidence. No automated or model-generated judgment is relabeled human validation.
''')
    report('DIAGNOSTIC_AND_FAILURE_AUDIT.md',f'''# Verification of existing process findings

Recomputed from actual transition CSVs and checked against candidate bytes in 72 trajectories per model: V7 guided repetition **{failure['V7']['guided_repetitions']}/{failure['V7']['guided_calls']}**; V8 **{failure['V8']['guided_repetitions']}/{failure['V8']['guided_calls']}**. V7 guided changed-category/unverified count is **{failure['V7']['changed_category_unverified']}**; V8 guided adds zero verified repairs. These are completed-call denominators with dependent seeds and early stopping, not independent mathematical trials.

All A/B/C/D/E/R budget endpoints 0–3 reconstruct PR20's tables (A is a constant initial-success reference, not a repair arm). Curves are recorded in `verification_results.json`; no duplicate plot or budget table is created. Candidate repetition and stored verification flags match source trajectories. The priority taxonomy remains the frozen runner's `failure_class`; mixed compiler errors can receive one dominant label. A category change is not kernel-verified mathematical progress, and a changed string is not automatically a repair.

All three existing post-hoc illustrative cases—`lib_a_exp_add`, `div_008`, `bridge_t16`/2027—have candidate SHA, diagnostics, model ID, seed and verification flags cross-checked against manifests/raw responses or source-bound V7 views. Raw recorded prompts additionally bind previous candidates, and every available raw transition category is independently re-evaluated using the frozen priority classifier against both predecessor and new verification records. PR21 CASE_STUDIES.md and case_excerpts.json remain unchanged. The selection deliberately includes a blind/guided shared success, an unsuccessful edited repair, and a C/D discordance; it does not estimate average effect or represent random sampling. V7 views are audit-time derivatives with weaker historical provenance than V8's indexed archive.

New control verification corroborates first-step prompt matching but does not upgrade these process findings into efficacy evidence. Parser/elaborator/tactic diagnostics describe candidate failures; trusted kernel acceptance of a valid term is a separate endpoint under the recorded strict policy.
''')
    report('REPRODUCIBILITY_FINAL_VERIFICATION.md',f'''# Scope-specific final evidence verification

Read-only audit at `{BASE}` (PRs #19–21 merged). V7 frozen outcomes match `e766a98ae53830e748da273aaace3ff958e15d53dd72cd92387f25928a3cc72a`; plan SHA is `{prov['v7_plan_sha256']}`; frozen runner and recorded source-file hash checks are in `verification_results.json`. ZIP and every one of {prov['archive_members_verified']} indexed members verify, along with all {prov['frozen_lock_entries']} lock entries. The new script reuses PR21's read-only archive loader, not its report generator, and never writes old outputs.

Case bindings, independent post-hoc bootstrap reconstruction, token matching and trace/CSV agreement pass in their documented scopes. Offline tests/commands are recorded in TEST_RESULTS.md. Model weights/caches/original runtime and hardware are not rebuilt. No inference replay or original held-out Lean candidate replay occurred. The new local relationship certificates are explicitly scoped checks; their success is not independent reproduction of the full experiment or independent benchmark approval.

Privacy count clarification: `{prov['privacy_warning_records']}` local-path WARNING RECORDS identify affected files; their `count` fields sum to `{prov['privacy_path_occurrences']}` path occurrences. Do not call these interchangeable quantities. Manual privacy review remains required; no credential-regex hits is not full clearance. Originals/archives are untouched and publication-facing new reports avoid personal home prefixes.

V7 original raw calls are locally available here and checked for consistency, but not independently authenticated by the V8 archive. PR21's committed sanitized views allow descriptive reanalysis without claiming to restore original raw-inference provenance. V8 raw journals have indexed byte-integrity verification. V9 is development-only: `{prov['v9']}`; it supplies no held-out replication. Reproducing summaries, verifying hashes, locally checking selected proof certificates, rerunning inference, replaying historical verification and independent human adjudication are distinct claims.

The renamed repository is https://github.com/sadiapeerzada/Compiler-Guided-Proof-Repair-in-Lean-4; frozen plans still record its historical name, which is provenance and is not edited. No manuscript, bibliography, figure, existing PDF, dataset, model response, prompt or protocol is modified.
''')


def main():
    prior=module('prior_supplement','analysis/taimma_supervisor_final/supplement.py')
    archive=prior.load_archive();studies=prior.load_studies(archive)
    runner=module('frozen_runner','study2_supervisor_suite_v7.py')
    results=dict(baseline=BASE,study1_controls=study1_controls(),statistics=check_statistics(studies),controls=controls(studies,archive,runner),benchmark=benchmark(studies,archive,runner),failure=failure_check(studies,runner,archive),provenance=provenance(archive,studies))
    output('verification_results.json',results)
    reports(results)
    print('Validation passed: token controls, independent clustered intervals, 36 statement hashes, trace/case bindings and frozen archive checks.')

if __name__=='__main__':main()
