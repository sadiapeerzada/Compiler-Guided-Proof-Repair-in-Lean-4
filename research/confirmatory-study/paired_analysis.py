"""Predeclared conditional paired analysis; synthetic fixtures are tests only."""
import argparse
import csv
import math
import random
from collections import defaultdict,Counter
from common import ensure,read,dump

ARMS=('C','D','E')

def validate_rows(rows):
    keys=[(r['id'],r['seed']) for r in rows]
    ensure(len(keys)==len(set(keys)),'Duplicate theorem/seed rows')
    ensure(len({r.get('phase') for r in rows})<=1,'Never pool development and test')
    ensure(len({r.get('model_revision') for r in rows})<=1,'Never pool model revisions')
    for r in rows:
        ensure(r['initial_success'] is None or type(r['initial_success']) is bool,'Missing/invalid initial outcome')
        for a in ARMS:ensure(r[a] is None or type(r[a]) is bool,'Invalid arm outcome')
        ensure(bool(r.get('family')),'Missing mathematical family')
    byid=defaultdict(set)
    for r in rows:byid[r['id']].add(r['family'])
    ensure(all(len(f)==1 for f in byid.values()),'Theorem assigned inconsistent families')


def bootstrap(rows,baseline,unit,replicates,seed,alpha):
    if not rows:return None
    groups=defaultdict(list)
    for r in rows:groups[r[unit]].append(int(r['C'])-int(r[baseline]))
    values=list(groups.values());rng=random.Random(seed);draws=[]
    for _ in range(replicates):
        sample=[values[rng.randrange(len(values))] for _ in values]
        draws.append(sum(sum(g) for g in sample)/sum(len(g) for g in sample))
    draws.sort();return [draws[math.floor(alpha/2*(replicates-1))],draws[math.floor((1-alpha/2)*(replicates-1))]]


def analyze(rows,replicates=20000,seed=2037001,expected_keys=None,expected_phase=None,expected_model_revision=None):
    validate_rows(rows)
    if expected_phase is not None:ensure(all(r['phase']==expected_phase for r in rows),'Wrong planned phase')
    if expected_model_revision is not None:ensure(all(r['model_revision']==expected_model_revision for r in rows),'Wrong planned model revision')
    if expected_keys is not None:ensure({(r['id'],r['seed']) for r in rows}==set(tuple(k) for k in expected_keys),'Incomplete/unexpected planned evaluation grid')
    if not rows:return dict(status='NO_EXECUTED_DATA',comparisons=[])
    eligible=[r for r in rows if r['initial_success'] is False]
    results=[]
    for baseline in ('D','E'):
        paired=[r for r in eligible if r['C'] is not None and r[baseline] is not None]
        cells=Counter((r['C'],r[baseline]) for r in paired)
        n=len(eligible)
        bounds=None
        if n:
            lower=sum(int(r['C'] is True)-int(r[baseline] is not False) for r in eligible)/n
            upper=sum(int(r['C'] is not False)-int(r[baseline] is True) for r in eligible)/n
            bounds=[lower,upper]
        results.append(dict(contrast='C-'+baseline,role='primary' if baseline=='D' else 'secondary',known_initial_failures=n,complete_pairs=len(paired),missing_pairs=n-len(paired),independent_theorem_clusters=len({r['id'] for r in paired}),family_clusters=len({r['family'] for r in paired}),both=cells[True,True],C_only=cells[True,False],baseline_only=cells[False,True],neither=cells[False,False],difference=(sum(int(r['C'])-int(r[baseline]) for r in paired)/len(paired) if paired else None),theorem_95=bootstrap(paired,baseline,'id',replicates,seed,.05),theorem_bonferroni_97_5=bootstrap(paired,baseline,'id',replicates,seed,.025),family_bonferroni_97_5=bootstrap(paired,baseline,'family',replicates,seed,.025),missingness_identification_bounds=bounds))
    category=[]
    for name in sorted({r.get('initial_error','unclassified') for r in eligible}):
        sub=[r for r in eligible if r.get('initial_error','unclassified')==name]
        category.append(dict(category=name,n=len(sub),theorems=len({r['id'] for r in sub}),**{a:dict(verified=sum(r[a] is True for r in sub),unknown=sum(r[a] is None for r in sub)) for a in ARMS}))
    return dict(status='SYNTHETIC_TEST_ANALYSIS_ONLY' if any(r.get('unit_test_only') for r in rows) else 'ANALYZED_RECORDED_DATA',planned_rows=len(rows),initial_verified=sum(r['initial_success'] is True for r in rows),initial_unknown=sum(r['initial_success'] is None for r in rows),known_initial_failures=len(eligible),possible_initial_failure_denominator=[len(eligible),len(eligible)+sum(r['initial_success'] is None for r in rows)],comparisons=results,category_wise=category,method=dict(replicates=replicates,seed=seed,resampling='whole theorem clusters, all available seeds retained; family sensitivity retains unequal-size groups; row-weighted mean',multiplicity='Two simultaneous nominal97.5% percentile intervals (Bonferroni), plus descriptive95%; approximate bootstrap coverage, no new p-values',warning='Complete-pair intervals are conditional; missingness bounds are not confidence intervals. Zero-spanning or degenerate intervals are not equivalence.'))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('recorded_rows');p.add_argument('output');p.add_argument('--plan',required=True);a=p.parse_args();dump(a.output,analyze(read(a.recorded_rows),expected_keys=read(a.plan)['expected_keys'],expected_phase=read(a.plan)['phase'],expected_model_revision=read(a.plan)['model_revision']))
