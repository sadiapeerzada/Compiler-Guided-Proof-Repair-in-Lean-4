"""Reuse the frozen Boolean review policy; new scope, real calls, no old writes."""
import importlib.util,csv
from difflib import SequenceMatcher
from sprint_common import *
from study_common import subject_hash
from fresh_review import parse_review
from overlap import fingerprint

def evidence(scope,c):
    if text_hash(c['reference_proof'])!=c['proof_sha256'] or text_hash(c['expected_lean_statement'])!=c['statement_sha256']:return False
    if c.get('reused_qualified_development'):
        ensure(scope=='development','Exposed old subject cannot enter test')
        old=read(OLD/'runs/20261105T041720Z_development/development_ai_accepted_candidates.json');match=next(r for r in old if r['id']==c['id']);ensure(subject_hash(c)==subject_hash(match) and match['status']=='AI_SCREENED_FORMALLY_VERIFIED','Old acceptance changed');return True
    checks=rows(RUN/'formal_checks.jsonl')
    return any(r['id']==c['id'] and r['source_sha256']==text_hash(c['reference_proof']) and r['target_sha256']==c['statement_sha256'] and r['result'].get('success') is True and r['result'].get('harness_variant')=='rigid_declaration_type_and_universe_v1' and read(HERE/r['record_path']/'verification.json')==r['result'] for r in checks)

def prepare(scope):
    verified=read(RUN/(scope+'_verified.json'));kept=[];excluded=[];seen=set();out=RUN/(scope+'_review_input')
    for c in sorted(verified,key=lambda r:content_hash(['review-duplicate-representative',r['id']])):
        ensure(evidence(scope,c),'No real rigid check');key=fingerprint(c['expected_lean_statement'])
        if key in seen:excluded.append(dict(id=c['id'],reason='exact_alias_alpha_duplicate'));continue
        seen.add(key);c=dict(c,generated_family_label=c['family'],family=c['canonical_family']);kept.append(c)
    old=next(c for c in read(OLD/'runs/20261105T041720Z_development/development_ai_accepted_candidates.json') if c['id']=='final_dev_0146')
    dump(out/'fresh_verified.json',kept,exclusive=True);dump(out/'v3_input.json',[old] if scope=='development' else [],exclusive=True);dump(out/'exclusions.json',excluded,exclusive=True)
    dump(out/'formal_checks_snapshot.json',[r for r in rows(RUN/'formal_checks.jsonl') if r['id'] in {c['id'] for c in kept}],exclusive=True)
    paths=[HERE/x for x in ('sprint_common.py','reviews.py','resource_authorization.json','proposal_options.json','COMPUTE_PROPOSAL.md')]+[OLD/'fresh_review.py',OLD/'review_protocol.py',OLD/'study_common.py',ROOT/'src/local_llm_client.py',LEGACY/'checkpoint.py',LEGACY/'common.py',out/'fresh_verified.json',out/'v3_input.json',out/'exclusions.json',HERE/('exposure_index.json' if scope=='development' else 'test_exposure_index.json'),RUN/(scope+'_verified.json'),out/'formal_checks_snapshot.json']
    view=OLD/'model_views/ac1c269cb4222a4e136a3d09edad301056c1f36a.json'
    paths.append(view)
    freeze(scope+'_reviews.json',paths,status='FROZEN_BEFORE_BOTH_REVIEWERS',policy='Unchanged prospective Boolean schema; two valid blinded acceptances, no critical concerns',subjects=len(kept));print(scope,'review subjects',len(kept),flush=True)

def adapter(scope):
    spec=importlib.util.spec_from_file_location('sprint_private_review_prompt',OLD/'fresh_review.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    module.run_root=lambda:RUN/(scope+'_review_input')
    index=read(HERE/('exposure_index.json' if scope=='development' else 'test_exposure_index.json'))['items']
    def neighbors(c):
        selected=sorted(index,key=lambda r:SequenceMatcher(None,c['expected_lean_statement'],r['statement'],autojunk=False).ratio(),reverse=True)[:5]
        return [dict(id=r['id'],statement=r['statement'],family=r.get('family','UNASSESSED'),exposure_only_not_truth_certification=True) for r in selected]
    module.neighbors=neighbors;return module

def review(scope,reviewer):
    stage=f'{scope}_review_{reviewer}';authorize(stage);lock=scope+'_reviews.json';frozen(lock);subjects=read(RUN/(scope+'_review_input/fresh_verified.json'));out=RUN/stage;done={r['id'] for r in rows(out/'reviews.jsonl')};module=adapter(scope);model=None
    try:
        for c in subjects:
            if c['id'] in done:continue
            if model is None:model=Model(stage,lock)
            text=module.prompt(c);r=dict(id=c['id'],subject_sha256=subject_hash(c),prompt=text,prompt_sha256=text_hash(text),reviewer=reviewer,model=model.model,decision='UNCERTAIN')
            try:cp,folder=model.call(text,dict(id=c['id'],subject_sha256=subject_hash(c)),2026110520+reviewer if scope=='development' else 2026110620+reviewer)
            except ValueError as error:
                if str(error)!='PROMPT_OVER_CAP_NO_CALL':raise
                r['parse_error']=str(error);append(out/'reviews.jsonl',r);continue
            r.update(record=cp,source_call=str(folder.relative_to(HERE)))
            if cp['status']=='completed':
                r['response_sha256']=text_hash(cp['content'])
                try:r['review']=parse_review(cp);r['decision']=r['review']['decision']
                except (ValueError,TypeError,KeyError) as error:r['parse_error']=str(error)
            append(out/'reviews.jsonl',r);ensure(cp['status']=='completed','New unavailable review, no replacement')
    finally:
        if model:model.close()

def adjudicate(scope):
    frozen(scope+'_reviews.json');subjects=read(RUN/(scope+'_review_input/fresh_verified.json'));maps=[{r['id']:r for r in rows(RUN/f'{scope}_review_{i}/reviews.jsonl')} for i in (1,2)];accepted=[];excluded=[]
    for c in subjects:
        reasons=[];ensure(evidence(scope,c),'Rigid reference evidence changed')
        for i,mapping in enumerate(maps,1):
            r=mapping.get(c['id'])
            if not r or r['decision']!='ACCEPT' or r.get('parse_error'):reasons.append(f'review_{i}_not_qualified_ACCEPT');continue
            ensure(r['subject_sha256']==subject_hash(c) and read(HERE/r['source_call']/'completion.json')==r['record'],'Review not tied to real subject/completion');ensure(parse_review(r['record'])==r['review'],'Raw response does not support decision')
        if not reasons:
            ensure(maps[0][c['id']]['model']['family']!=maps[1][c['id']]['model']['family'],'Review model families not distinct');accepted.append(dict(c,status='AI_SCREENED_FORMALLY_VERIFIED',review_evidence=[m[c['id']]['source_call'] for m in maps]))
        else:excluded.append(dict(id=c['id'],reasons=reasons))
    dump(RUN/(scope+'_ai_accepted.json'),accepted);dump(RUN/(scope+'_ai_quarantined.json'),excluded);print(scope,'qualified AI acceptances',len(accepted),flush=True)

def select(scope):
    candidates=read(RUN/(scope+'_ai_accepted.json'))
    if scope=='development':
        old=next(c for c in read(OLD/'runs/20261105T041720Z_development/development_ai_accepted_candidates.json') if c['id']=='final_dev_0146');candidates.append(dict(old,reused_qualified_development=True,original_evidence_root=str(OLD.relative_to(ROOT))))
    representatives={}
    for c in sorted(candidates,key=lambda r:content_hash(['sprint-family-representative',r['id']])):
        group=c['canonical_family']
        if group not in representatives:representatives[group]=c
    target=16 if scope=='development' else 32
    selected=[representatives[k] for k in sorted(representatives,key=lambda k:content_hash(['sprint-family-order',k]))[:target]]
    for c in selected:ensure(evidence(scope,c),'Unverified selected proof');ensure(c['status']=='AI_SCREENED_FORMALLY_VERIFIED','Unqualified acceptance')
    dump(RUN/(scope+'_selected.json'),selected,exclusive=True)
    dump(RUN/(scope+'_dataset_freeze.json'),dict(status='FROZEN_BEFORE_EVALUATION',count=len(selected),family_count=len({c['canonical_family'] for c in selected}),target=target,dataset_sha256=sha(RUN/(scope+'_selected.json')),scope=scope,selection='One hashed qualified representative per predeclared mathematical family; actual count fixed before outcomes',ids=[c['id'] for c in selected]),exclusive=True)
    print(scope,'frozen types/families',len(selected),flush=True)

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('action',choices=['prepare','review','adjudicate','select']);p.add_argument('scope',choices=['development','test']);p.add_argument('reviewer',nargs='?',type=int);a=p.parse_args()
    review(a.scope,a.reviewer) if a.action=='review' else globals()[a.action](a.scope)
