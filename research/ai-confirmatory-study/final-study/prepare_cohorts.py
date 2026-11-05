"""Development-only projections and freezes; never creates a test cohort."""
from study_common import *
from dataset_tools import screen
from common import normalize
from families import FAMILIES,V3_GROUPS

def fresh_review_input():
    if (run_root()/'fresh_verified_raw_v2.json').exists():
        from reference_construction_v2 import curate
        curate()
    else:
        from generation import refresh_verified
        refresh_verified()
    verified=read(run_root()/'fresh_verified_raw.json');exposed=read(run_root()/'v3_input.json')
    ensure(all(c.get('reference_validation_variant')=='rigid_declaration_type_and_universe_v1' for c in verified),'NO_GO_VALIDATION: every fresh reference needs rigid type/universe validation before review')
    from overlap import fingerprint
    seen={fingerprint(c['expected_lean_statement']):c['id'] for c in exposed};kept=[];excluded=[]
    concerns={r['id']:r for r in read(run_root()/'assistant_audit_concerns.json')} if (run_root()/'assistant_audit_concerns.json').exists() else {}
    for c in sorted(verified,key=lambda r:content_hash(['prospective-duplicate-representative',r['id']])):
        from overlap import flags,fingerprint
        if c['id'] in concerns:
            ensure(concerns[c['id']]['raw_response_sha256']==c['generation_provenance']['raw_response_sha256'],'Concern belongs to different raw response')
            excluded.append(dict(id=c['id'],reason='unresolved_assistant_source_audit: '+concerns[c['id']]['reason'],not_AI_reviewer_decision=True));continue
        exposure_flags=flags(c)
        if exposure_flags:excluded.append(dict(id=c['id'],reason='; '.join(exposure_flags)));continue
        normalized=fingerprint(c['expected_lean_statement'])
        if normalized in seen:
            excluded.append(dict(id=c['id'],reason='alpha_duplicate_or_exposed_V3_statement',related_id=seen[normalized]));continue
        seen[normalized]=c['id'];row=dict(c);row['generated_family_label']=row['family'];row['family']=row['canonical_family'];row['status']='FORMALLY_VERIFIED_PENDING_AI_REVIEW';kept.append(row)
    path=run_root()/'fresh_verified.json';dump(path,kept,exclusive=True);dump(run_root()/'pre_review_exclusions.json',excluded,exclusive=True)
    base=read(HERE/'freezes/review_v2.json');lock=dict(base['files'])
    for f in ('fresh_review.py','adjudication.py','prepare_cohorts.py','families.py','strict_verifier.py','rigid_verifier.py','reference_construction_v2.py','overlap.py'):lock[str((HERE/f).relative_to(ROOT))]=sha(HERE/f)
    for p in (path,run_root()/'pre_review_exclusions.json',run_root()/'fresh_verified_raw.json',run_root()/'expanded_historical_exposure.json'):lock[str(p.relative_to(ROOT))]=sha(p)
    concerns=run_root()/'assistant_audit_concerns.json'
    if concerns.exists():lock[str(concerns.relative_to(ROOT))]=sha(concerns)
    dump(HERE/'freezes/fresh_review_v1.json',dict(status='FROZEN_BEFORE_FRESH_AI_REVIEWS',files=lock,old_V3_review_outcomes_not_reparsed=True,schema='explicit boolean check polarity, explicit relation enums, full rationale, confidence heuristic0.8, two blinded acceptances required'),exclusive=True)
    print('Fresh verified review subjects:',len(kept),'; prereview exclusions:',len(excluded))

def development():
    accepted=read(run_root()/'v3_ai_accepted_candidates.json')+read(run_root()/'development_ai_accepted_candidates.json')
    # One representative per broad predeclared family is conservative for donors.
    by_family={}
    for c in sorted(accepted,key=lambda r:content_hash(['development-selection-v1',r['id']])):
        family=c.get('canonical_family',V3_GROUPS.get(c['id'],c['family']))
        if family not in by_family:by_family[family]=c
    families=sorted(by_family,key=lambda f:content_hash(['development-family-order-v1',f]))[:20]
    selected=[]
    for family in families:
        c=dict(by_family[family]);c['review_subject_sha256']=subject_hash(c);c['generated_family_label']=c.get('generated_family_label',c['family']);c['family']=family;c['canonical_family']=family;selected.append(c)
    dump(run_root()/'accepted_development.json',selected,exclusive=True)
    manifest=dict(status='AI_SCREENED_EXPLORATORY_DEVELOPMENT_ONLY',count=len(selected),independent_type_count=len(selected),canonical_family_count=len(families),ids=[c['id'] for c in selected],families=families,dataset_sha256=sha(run_root()/'accepted_development.json'),selection='hashed whole-family order, at most20 families, one hashed representative per canonical family, frozen before any CDE outcomes',seeds=protocol()['seeds'],test_count=0,confirmatory_authorized=False)
    dump(run_root()/'development_dataset_freeze.json',manifest,exclusive=True)
    registry={c['id']:dict(generated_label=c.get('generated_family_label',c['family']),canonical_family=c.get('canonical_family',V3_GROUPS.get(c['id'],c['family'])),scope='development_exposed') for c in read(run_root()/'v3_input.json')+read(run_root()/'fresh_verified_raw.json')}
    dump(run_root()/'mathematical_family_registry.json',dict(definitions=dict(FAMILIES),assignments=registry,not_exhaustive_equivalence_certification=True))
    (run_root()/'cross_partition_leakage_report.md').write_text('# Exposure and partition audit\n\nAll V3 and fresh generated proposals are development-exposed, including rejected proposals. No confirmatory stream is authorized or created. The frozen development cohort uses one representative per declared canonical family. Exact/alpha and bounded AI relationship checks do not establish exhaustive mathematical independence or absence of pretraining contamination. All these subjects and their mathematical equivalents/specializations must be excluded from future untouched test construction.\n')
    print('Frozen development types/families:',len(selected))

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['fresh-review','development']);a=p.parse_args();{'fresh-review':fresh_review_input,'development':development}[a.mode]()
