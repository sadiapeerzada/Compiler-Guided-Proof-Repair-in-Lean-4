"""Read-only fast path: bind all31 references to actual checks and decisions.

No model inference, no reinterpretation of old reviews, no old-run writes.
"""
import csv,json,sys,hashlib,subprocess,os
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
OLD=HERE.parent/'final-study'
sys.path.insert(0,str(OLD))
from study_common import read,dump,rows,sha,text_hash,ensure,subject_hash,run_root
from fresh_review import parse_review
from overlap import flags,fingerprint

def main():
    baseline=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    manifest=HERE/'preservation_manifest.json'
    if not manifest.exists():
        files={};links={}
        for item in subprocess.check_output(['git','ls-tree','-rz',baseline],cwd=ROOT).split(b'\0'):
            if not item:continue
            meta,name=item.split(b'\t',1);mode,kind,blob=meta.decode().split();rel=name.decode();p=ROOT/rel
            if mode=='120000':links[rel]=dict(target=os.readlink(p),git_blob=blob)
            else:files[rel]=dict(sha256=sha(p),git_blob=blob)
        dump(manifest,dict(baseline=baseline,files=files,symlinks=links),exclusive=True)
    preserved=read(manifest);baseline=preserved['baseline']
    for rel,item in preserved['files'].items():ensure(sha(ROOT/rel)==item['sha256'],'Historical file changed: '+rel)
    for rel,item in preserved['symlinks'].items():ensure((ROOT/rel).is_symlink() and os.readlink(ROOT/rel)==item['target'],'Historical link changed: '+rel)
    data=read(run_root()/'fresh_verified_raw_v2.json');ensure(len(data)==31,'Unexpected old verified count')
    excluded={r['id']:r for r in read(run_root()/'pre_review_exclusions.json')};concerns={r['id']:r for r in read(run_root()/'assistant_audit_concerns.json')};subjects={r['id']:r for r in read(run_root()/'fresh_verified.json')};accepted={r['id']:r for r in read(run_root()/'development_ai_accepted_candidates.json')}
    reviews=[{r['id']:r for r in rows(run_root()/stage/'reviews.jsonl')} for stage in ('development_review_1','development_review_2')];formal=rows(run_root()/'strict_reference_verification.jsonl');byid={r['id']:r for r in data};result=[]
    for c in data:
        checks=[r for r in formal if r['id']==c['id'] and r['source_sha256']==text_hash(c['reference_proof']) and r['target_sha256']==c['statement_sha256'] and r['result'].get('success') is True and r['result'].get('harness_variant')=='rigid_declaration_type_and_universe_v1']
        ensure(checks,'No actual rigid proof check: '+c['id'])
        for check in checks:ensure(read(OLD/check['record_path']/'verification.json')==check['result'],'Verification checkpoint mismatch')
        reason='';decisions=[];status='ELIGIBLE_UNREVIEWED'
        if c['id'] in excluded:
            e=excluded[c['id']];reason=e['reason'];status='EXCLUDED'
            if 'related_id' in e:ensure(fingerprint(c['expected_lean_statement'])==fingerprint(byid[e['related_id']]['expected_lean_statement']),'Incorrect duplicate exclusion')
            elif reason.startswith('unresolved_assistant_source_audit:'):
                ensure(c['id'] in concerns and concerns[c['id']]['raw_response_sha256']==c['generation_provenance']['raw_response_sha256'],'Unbound source concern')
            else:ensure(set(reason.split('; '))<=set(flags(c)),'Historical exclusion no longer matches its recorded rule')
        elif c['id'] in subjects:
            for mapping in reviews:
                r=mapping[c['id']];ensure(r['subject_sha256']==subject_hash(subjects[c['id']]),'Review subject changed');ensure(read(OLD/r['source_call']/'completion.json')==r['record'],'Review lacks real completion')
                try:parsed=parse_review(r['record']);ensure(parsed==r['review'] and parsed['decision']==r['decision'],'Old decision mismatch')
                except (ValueError,KeyError,TypeError):ensure(r['decision']=='UNCERTAIN' and r.get('parse_error'),'Invalid review cannot become approval')
                decisions.append(r['decision'])
            status='QUALIFIED_AI_ACCEPTANCE_REUSABLE_DEV_ONLY' if c['id'] in accepted else 'QUARANTINED_NO_RETROSPECTIVE_ACCEPTANCE'
            if c['id'] in accepted:ensure(decisions==['ACCEPT','ACCEPT'] and accepted[c['id']]['status']=='AI_SCREENED_FORMALLY_VERIFIED','False approval')
            else:reason='Original valid/nonvalid decisions: '+','.join(decisions)
        result.append(dict(id=c['id'],canonical_family=c['canonical_family'],rigid_verified=True,old_disposition=status,reviewer_decisions=','.join(decisions),recorded_reason=reason,record_rule_binding_verified=True,external_mathematical_review=False,development_only=True))
    with (HERE/'previous_31_audit.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(result[0]),lineterminator='\n');w.writeheader();w.writerows(result)
    summary=dict(baseline=baseline,strict_references=len(result),excluded=sum(r['old_disposition']=='EXCLUDED' for r in result),previously_reviewed=len(subjects),qualified_acceptances=len(accepted),qualified_families=len({r['canonical_family'] for r in accepted.values()}),eligible_unreviewed=sum(r['old_disposition']=='ELIGIBLE_UNREVIEWED' for r in result),prior_qualified_selected=read(run_root()/'development_dataset_freeze.json')['ids'],scope='Source/checkpoint/record-rule audit, not external mathematical replication; no old decisions altered',new_model_calls=0)
    dump(HERE/'previous_31_audit.json',summary)
    clocks={str(p.relative_to(ROOT)):sha(p) for p in run_root().glob('*/phase_clock.json')}
    dump(HERE/'previous_run_closed.json',dict(run_id=run_root().name,status='PERMANENTLY_CLOSED',clock_hashes=clocks,prohibited=['resetting deadlines','replaying intents','transferring unused allocations'],old_authorization_sha256=sha(OLD/'resource_authorization.json'),no_new_inference_authorized=True))
    print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
