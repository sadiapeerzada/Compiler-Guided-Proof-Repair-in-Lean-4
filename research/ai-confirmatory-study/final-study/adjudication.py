import csv
from study_common import *
from dataset_tools import screen,cohort_flags
from families import V3_GROUPS

def write_csv(path,rows_,fields):
    with path.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n');w.writeheader();w.writerows(rows_)

def adjudicate(stream):
    ensure(stream in ('v3','development'),'No confirmatory review authorization')
    prefix='v3_ai' if stream=='v3' else 'development_ai';candidates=read(run_root()/('v3_input.json' if stream=='v3' else 'fresh_verified.json'))
    stages=('v3_review_1','v3_review_2') if stream=='v3' else ('development_review_1','development_review_2')
    reviewers=[{r['id']:r for r in rows(run_root()/s/'reviews.jsonl')} for s in stages]
    accepted=[];quarantined=[];decisions=[];overlap=[]
    for c,within in zip(candidates,cohort_flags(candidates)):
        check=screen(dict(c,source_url='Local AI generation with preserved provenance',license='Model/upstream source rights unassessed',library_dependencies=[]));reasons=check['automated_flags']+within;evidence=[]
        if stream=='development':
            verified=any(r['id']==c['id'] and r['source_sha256']==c['proof_sha256'] and r['target_sha256']==c['statement_sha256'] and r['result'].get('success') is True and r['result'].get('harness_variant')=='rigid_declaration_type_and_universe_v1' for r in rows(run_root()/'strict_reference_verification.jsonl'))
            if not verified:reasons.append('rigid_strict_reference_verification_not_established')
        if (run_root()/'expanded_historical_exposure.json').exists():
            from overlap import flags
            reasons+=flags(c)
        concerns_path=run_root()/'assistant_audit_concerns.json'
        if concerns_path.exists():
            for concern in read(concerns_path):
                if concern['id']==c['id']:
                    ensure(concern['raw_response_sha256']==c['generation_provenance']['raw_response_sha256'],'Audit concern bound to different response')
                    reasons.append('unresolved_assistant_audit_concern: '+concern['reason'])
        for i,mapping in enumerate(reviewers,1):
            r=mapping.get(c['id']);evidence.append(r)
            if not r:reasons.append('review_'+str(i)+'_not_executed');continue
            ensure(r['subject_sha256']==subject_hash(c),'Review bound to different candidate')
            if r['decision']!='ACCEPT' or 'review' not in r or r.get('parse_error'):reasons.append('review_'+str(i)+'_unresolved_or_schema_invalid')
            if r.get('record',{}).get('status')=='completed':ensure(r['response_sha256']==text_hash(r['record']['content']),'Review response hash changed')
        if all(evidence):
            if evidence[0]['model']['family']==evidence[1]['model']['family']:reasons.append('review_families_not_distinct')
        else:reasons.append('two_real_blinded_acceptances_absent')
        status='AI_SCREENED_FORMALLY_VERIFIED' if not reasons else 'QUARANTINED'
        d=dict(id=c['id'],reviewer_1=evidence[0]['decision'] if evidence[0] else 'NOT_REVIEWED',reviewer_2=evidence[1]['decision'] if evidence[1] else 'NOT_REVIEWED',status=status,reasons='; '.join(sorted(set(reasons))));decisions.append(d)
        overlap.append(dict(id=c['id'],automated_flags='; '.join(check['automated_flags']+within),pretraining_contamination='UNASSESSED'))
        if reasons:quarantined.append(dict(candidate=c,reasons=sorted(set(reasons))))
        else:accepted.append(dict(c,status=status,canonical_family=c.get('canonical_family',V3_GROUPS.get(c['id'],c['family'])),review_evidence=[r['source_call'] for r in evidence]))
    dump(run_root()/(prefix+'_accepted_candidates.json'),accepted);dump(run_root()/(prefix+'_quarantined_candidates.json'),quarantined)
    write_csv(run_root()/(prefix+'_adjudication.csv'),decisions,['id','reviewer_1','reviewer_2','status','reasons']);write_csv(run_root()/(prefix+'_overlap_screen.csv'),overlap,['id','automated_flags','pretraining_contamination'])
    for i,stage in enumerate(stages,1):
        source=run_root()/stage/'reviews.jsonl';(run_root()/(prefix+f'_review_{i}.jsonl')).write_text(source.read_text() if source.exists() else '')
    if stream=='v3':
        dump(run_root()/'v3_accepted_candidates.json',accepted);dump(run_root()/'v3_quarantined_candidates.json',quarantined)
        write_csv(run_root()/'v3_overlap_screen.csv',overlap,['id','automated_flags','pretraining_contamination'])
    dump(run_root()/(prefix+'_agreement.json'),dict(valid_schema_pairs=sum(all(c['id'] in r and not r[c['id']].get('parse_error') and 'review' in r[c['id']] for r in reviewers) for c in candidates),qualified_agreement=sum(c['id'] in reviewers[0] and c['id'] in reviewers[1] and reviewers[0][c['id']]['decision']==reviewers[1][c['id']]['decision'] for c in candidates),interpretation='Schema failures are unresolved, not semantic acceptances; agreement is not truth or independent errors'))
    print(stream,'accepted',len(accepted),'quarantined',len(quarantined))

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('stream',choices=['v3','development']);adjudicate(p.parse_args().stream)
