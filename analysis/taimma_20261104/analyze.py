"""Read-only post-hoc audit. Run: python3 analysis/taimma_20261104/analyze.py."""
import csv
import hashlib
import io
import json
import random
import zipfile
from collections import defaultdict, Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).parent / 'results'
ARMS = ['B_neutral', 'C_real', 'D_shuffled', 'E_token_matched', 'R_resample']
SEED = 20261104
ROUNDS = 10000


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def checked(raw, expected):
    if digest(raw) != expected:
        raise ValueError('Frozen checksum mismatch')
    return raw


def csvrows(raw):
    text = raw.decode('utf-8-sig')
    # Two review files have a pasted-sheet envelope, preserved in source.
    if text.startswith('<PARSED TEXT'):
        text = text[text.index('index,type,'):]
    return list(csv.DictReader(io.StringIO(text)))


def validate(rows):
    keys = [(r['model'], r['seed'], r['id']) for r in rows]
    if len(keys) != len(set(keys)):
        raise ValueError('Duplicate pairs')
    if len(rows) != 72 or len({r['model'] for r in rows}) != 1:
        raise ValueError('Invalid denominator/model')
    expected = {(str(s), f'bridge_t{i:02}') for s in (2027,2028,2029) for i in range(1,25)}
    if {(r['seed'],r['id']) for r in rows} != expected:
        raise ValueError('Missing/unexpected pairs')
    for r in rows:
        if any(r[a] not in ('True','False') for a in ARMS+['initial_success']):
            raise ValueError('Missing outcome')
    for tid in {r['id'] for r in rows}:
        if len({r['family'] for r in rows if r['id']==tid}) != 1:
            raise ValueError('Inconsistent family')


def yes(r,a):
    return int(r[a]=='True')


def bootstrap(rows,a,b,unit,seed=SEED,rounds=ROUNDS):
    groups = defaultdict(list)
    for r in rows:
        groups[r[unit]].append(yes(r,a)-yes(r,b))
    vals = [(sum(g),len(g)) for g in groups.values()]
    rng=random.Random(seed); draws=[]
    for _ in range(rounds):
        batch=[vals[rng.randrange(len(vals))] for _ in vals]
        draws.append(sum(v[0] for v in batch)/sum(v[1] for v in batch))
    draws.sort()
    return [draws[int(p*(rounds-1))] for p in (.025,.975)]


def table(name,rows):
    if not rows: return
    with (OUT/(name+'.csv')).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
    cols=list(rows[0]); lines=['| '+' | '.join(cols)+' |','| '+' | '.join(['---']*len(cols))+' |']
    lines += ['| '+' | '.join(str(r[c]).replace('|','\\|').replace('\n','<br>') for c in cols)+' |' for r in rows]
    (OUT/(name+'.md')).write_text('\n'.join(lines)+'\n')


def analyze(label,rows,calls,trans):
    validate(rows)
    index={(r['model'],r['seed'],r['id']):r for r in rows}
    for records in (calls,trans):
        keys=[(r['model'],r['seed'],r['id'],r['arm'],r['index']) for r in records]
        if len(keys)!=len(set(keys)): raise ValueError('Duplicate trace')
        if any(k[:3] not in index for k in keys): raise ValueError('Unmatched trace')
    def tracekey(r): return (r['model'],r['seed'],r['id'],r['arm'],r['index'])
    if {tracekey(r) for r in calls if r['arm']!='A'} != {tracekey(r) for r in trans}:
        raise ValueError('Missing repair call or transition')
    if {(r['model'],r['seed'],r['id']) for r in calls if r['arm']=='A'} != set(index):
        raise ValueError('Missing initial call')
    if any(int(r['index']) not in (1,2,3) for r in trans): raise ValueError('Invalid repair index')
    paired=[]
    for b in ['B_neutral','D_shuffled','E_token_matched']:
        a='C_real'; cells=Counter((yes(r,a),yes(r,b)) for r in rows)
        paired.append(dict(contrast=a+' minus '+b,n=72,theorems=24,families=len({r['family'] for r in rows}),both=cells[1,1],neither=cells[0,0],C_only=cells[1,0],baseline_only=cells[0,1],difference=(cells[1,0]-cells[0,1])/72,theorem_CI=bootstrap(rows,a,b,'id'),family_CI=bootstrap(rows,a,b,'family')))
    table(label+'_paired',paired)
    theorem=[]; seeds=[]; errors=[]; budgets=[]; costs=[]
    for a in ARMS:
        wins=[r for r in rows if yes(r,a)]
        theorem.append(dict(arm=a,success=len(wins),n=72,theorem_types=len({r['id'] for r in wins}),families=len({r['family'] for r in wins}),new_beyond_initial=sum(not yes(r,'initial_success') for r in wins),unique_vs_all_other_arms=sum(all(not yes(r,b) for b in ARMS if b!=a) for r in wins),statuses=dict(Counter(r[a+'_status'] for r in rows))))
        for s in ('2027','2028','2029'):
            subset=[r for r in rows if r['seed']==s];seeds.append(dict(arm=a,seed=s,n=len(subset),success=sum(yes(r,a) for r in subset)))
        for cat in sorted({r['initial_error'] for r in rows}):
            subset=[r for r in rows if r['initial_error']==cat]
            errors.append(dict(arm=a,initial_error=cat,n=len(subset),theorems=len({r['id'] for r in subset}),success=sum(yes(r,a) for r in subset),new_success=sum(yes(r,a) and not yes(r,'initial_success') for r in subset),C_minus_arm_theorem_CI=bootstrap(subset,'C_real',a,'id')))
        steps={k:0 for k in index}
        for t in trans:
            if t['arm']==a and t['verified']=='True':
                k=(t['model'],t['seed'],t['id']);step=int(t['index'])
                steps[k]=min(steps[k] or step,step)
        for k,r in index.items():
            if bool(yes(r,a)) != bool(yes(r,'initial_success') or steps[k]): raise ValueError('Trace/outcome mismatch')
        repaired=sum(bool(v) for k,v in steps.items() if not yes(index[k],'initial_success'))
        for b in range(4):
            first=sum(v==b for k,v in steps.items() if b and not yes(index[k],'initial_success')) if b else 0
            budgets.append(dict(arm=a,budget=b,n=72,success=sum(bool(yes(r,'initial_success') or (steps[k] and steps[k]<=b)) for k,r in index.items()),first_repair_successes=first,percent_of_successful_repairs=100*first/repaired if repaired else None))
    for a in ['A']+ARMS:
        cs=[r for r in calls if r['arm']==a]
        inp=sum(int(r['prompt_tokens']) for r in cs); output=sum(int(r['completion_tokens']) for r in cs)
        successes=sum(yes(r,'initial_success' if a=='A' else a) for r in rows)
        initial_input=sum(int(r['prompt_tokens']) for r in calls if r['arm']=='A')
        newly_repaired=successes-sum(yes(r,'initial_success') for r in rows)
        costs.append(dict(arm=a,calls=len(cs),input_tokens=inp,output_tokens=output,verified_evaluations=successes,recorded_input_tokens_per_final_verified_evaluation=inp/successes if successes else None,initial_plus_repair_input_per_verified_evaluation=(inp+(initial_input if a!='A' else 0))/successes if successes else None,repair_input_per_new_verified_evaluation=inp/newly_repaired if a!='A' and newly_repaired else None))
    for name,data in [('theorems',theorem),('seeds',seeds),('errors',errors),('budgets',budgets),('costs',costs)]:table(label+'_'+name,data)
    return dict(paired=paired,theorems=theorem,costs=costs,initial=sum(yes(r,'initial_success') for r in rows),model=rows[0]['model'])


def main():
    OUT.mkdir(exist_ok=True)
    packet=ROOT/'research/study2-raw-v8-v9'; manifest=json.loads((packet/'ARCHIVE_INDEX.json').read_text()); archive={}
    for part in manifest['archives']:
        raw=checked((packet/part['filename']).read_bytes(),part['sha256'])
        with zipfile.ZipFile(io.BytesIO(raw)) as z:
            for n in z.namelist():
                if n in archive: raise ValueError('Duplicate archive member')
                archive[n]=z.read(n)
    for e in manifest['entries']:checked(archive[e['path']],e['sha256'])
    lock=json.loads(next(v for k,v in archive.items() if k.endswith('FINAL_1_4_6_LOCK.json')))
    checks=[]
    for e in lock['data_hashes']:
        p=e['path']; raw=archive.get(p)
        if raw is None and (ROOT/p).is_file(): raw=(ROOT/p).read_bytes()
        if p.startswith('study2_outputs/bridge_v7_base/'):
            suffix=p.split('bridge_v7_base/')[1].replace('reports/','')
            local=ROOT/'research/study2-v7'/suffix
            if suffix=='plan.json':local=ROOT/'research/study2-v7/test/plan.json'
            if local.exists():raw=local.read_bytes()
        if raw is not None:checked(raw,e['sha256'])
        checks.append(dict(path=p,status='verified' if raw is not None else 'unavailable',expected=e['sha256']))
    table('lock_checks',checks)
    result={}
    for label in ('V7','V8'):
        def read(name):
            if label=='V7':return (ROOT/'research/study2-v7/test'/name).read_bytes()
            return next(v for k,v in archive.items() if k.endswith('coder_exploratory/reports/test/'+name))
        rows=csvrows(read('outcomes.csv'))
        result[label]=analyze(label,rows,csvrows(read('calls.csv')),csvrows(read('transitions.csv')))
        # Importing this module defines functions only; no experiment entry point runs.
        import importlib.util
        hist_spec=importlib.util.spec_from_file_location('historical',ROOT/'study2_supervisor_suite_v7.py')
        hist=importlib.util.module_from_spec(hist_spec);hist_spec.loader.exec_module(hist)
        summary=json.loads(read('summary.json')); verification=[]
        call_rows=csvrows(read('calls.csv'))
        for key,v in summary['costs_by_model_seed_arm'].items():
            model,seed,arm=key.split(' / ')
            subset=[r for r in call_rows if r['model']==model and r['seed']==seed and r['arm']==arm]
            assert len(subset)==v['completed_calls']
            for field in ('prompt_tokens','completion_tokens'):
                assert sum(int(r[field]) for r in subset)==v[field]['total']

        for key,g in summary['grouped'].items():
            seed=key.split(' / ')[-1]; subset=[r for r in rows if r['seed']==seed]
            items=[dict(family=r['family'],arms={a:dict(outcome=bool(yes(r,a))) for a in ARMS}) for r in subset]
            for a in ARMS:
                count=sum(yes(r,a) for r in subset)
                assert count==g['arms'][a]['success']
                assert hist.wilson(count,len(subset))==g['arms'][a]['wilson95']
            for contrast,v in g['paired_comparisons'].items():
                baseline=contrast.split('_minus_')[1]
                reconstructed=hist.family_bootstrap(items,baseline,'C_real')
                assert reconstructed==v['conditional_family_bootstrap'], 'Historical interval mismatch'
                c_only=sum(yes(r,'C_real') and not yes(r,baseline) for r in subset)
                b_only=sum(yes(r,baseline) and not yes(r,'C_real') for r in subset)
                assert hist.mcnemar(b_only,c_only)==v['mcnemar_p']
                verification.append(dict(group=key,contrast=contrast,status='exact match: counts, historical family CI and McNemar',historical_interval=reconstructed['interval']))
        table(label+'_historical_verification',verification)
    import importlib.util
    spec=importlib.util.spec_from_file_location('sensitivity',ROOT/'research/study2-final/study2_sensitivity.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    result['sensitivity']=mod.audit(csvrows((ROOT/'research/study2-v7/test/outcomes.csv').read_bytes()))
    # Reconstruct Study 1 descriptive counts from archived per-case evidence.
    cases=json.loads((ROOT/'publication/results/review_v2/analysis_verified/case_outcomes.json').read_text())
    study1={a:dict(n=len(cases),observed=sum(r['outcomes'][a] is not None for r in cases),success=sum(r['outcomes'][a] is True for r in cases),missing=sum(r['outcomes'][a] is None for r in cases)) for a in ('A','B','C')}
    complete=[r for r in cases if all(r['outcomes'][a] is not None for a in ('B','C'))]
    study1['paired_B_C']=dict(n=len(complete),both=sum(r['outcomes']['B'] and r['outcomes']['C'] for r in complete),B_only=sum(r['outcomes']['B'] and not r['outcomes']['C'] for r in complete),C_only=sum(r['outcomes']['C'] and not r['outcomes']['B'] for r in complete),distinct_theorems=len({r['problem_id'] for r in cases}),families=len({r['family'] for r in cases}))
    result['Study1_descriptive_reconstruction']=study1
    table('overlap_sensitivity',[{k:json.dumps(v,sort_keys=True) if isinstance(v,(dict,list)) else v for k,v in r.items()} for r in result['sensitivity']])
    result['provenance']=dict(archive_members_verified=len(manifest['entries']),archive_parts_verified=len(manifest['archives']),lock_checks=checks)
    result['method']=dict(classification='Exploratory post-hoc reanalysis of frozen evidence',resampling_unit='theorem (all three seeds retained); family sensitivity retains all members',method='paired nonparametric percentile cluster bootstrap, row-weighted mean',seed=SEED,replicates=ROUNDS,p_values='not calculated; three exploratory contrasts, no multiplicity-adjusted claims')
    (OUT/'results.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    refs={r['id']:r for split in ('development','test') for r in hist.bridge_rows(split)}
    review=[]
    for name in ('PROPOSED_VALIDATION_DECISIONS.csv','ADDITIONAL_BENCHMARK_OVERLAPS.csv'):
        for r in csvrows((ROOT/'research/study2-final'/name).read_bytes()):
            r['source']=name
            ids=[r.get('left',''),r.get('right','')]
            r['reference_records']='; '.join(k for k in archive if '/reference_screen/' in k and any(k.endswith('/'+tid+'.json') for tid in ids if tid))
            r['theorem_types']='; '.join(ids)
            r['reference_proofs']='; '.join(refs[tid]['reference_lean_proof'] for tid in ids if tid in refs)
            r['recorded_families']='; '.join(refs[tid]['study_eligibility']['family'] for tid in ids if tid in refs)
            r['independent_review']='Outstanding: signed dated human mathematical and split-independence adjudication'
            review.append(r)
    table('benchmark_review',[{k:r.get(k,'') for k in sorted(set().union(*(x.keys() for x in review)))} for r in review])
    (OUT/'benchmark_review.json').write_text(json.dumps(review,indent=2,sort_keys=True)+'\n')
    # Reference evidence paths are listed without treating proof checks as adjudication.
    (OUT/'reference_evidence.json').write_text(json.dumps([k for k in archive if any(s in k for s in ('reference_screen','validation','benchmark'))],indent=2)+'\n')

if __name__=='__main__':main()
