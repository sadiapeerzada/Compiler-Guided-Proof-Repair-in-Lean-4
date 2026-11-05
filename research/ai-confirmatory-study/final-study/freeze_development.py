"""Freeze actual selected development data and protocol before its initial calls."""
import copy
from study_common import *

def main():
    authorize('development_initial');authorize('development_repairs')
    dataset=read(run_root()/'accepted_development.json');p=copy.deepcopy(protocol()['legacy_CDE_protocol']);p.update(study='AI-screened exploratory development evaluation; not confirmatory',status='FROZEN_BEFORE_DEVELOPMENT_OUTCOMES',sample_size={'development':len(dataset),'test':0})
    p['budget'].update(max_total_calls=240,max_initial_calls=60,max_repair_calls=180,max_runtime_seconds=64800,input_tokens_per_call=4096,output_tokens_per_call=1200)
    p['budget']['calibration_accounting']='New approved development-only allocation: initial60/6h and repairs180/12h; no historical or confirmatory budget transfer'
    p['lean']['timeout_seconds']=180;p['lean']['verification_policy']='Unchanged strict axiom checks plus explicit-all-argument equality and rigid closed declaration-type/universe checks; real negative fixtures passed'
    p['validation_gate']='Separate genuine AI-screened development gate; historical human gate remains unchanged';p['statistics']['sample_precision']='Actual selected count is frozen before outcomes; intervals descriptive/exploratory, not a power guarantee';p['source_control']='Exact prompts/decoding/matching/donor/order/stopping/statistical code frozen below before all development initial results'
    dump(run_root()/'development_protocol.json',p,exclusive=True)
    files=['study_common.py','local_runtime.py','runtime_v2.py','development_experiment.py','cde_verifier.py','strict_verifier.py','rigid_verifier.py','families.py','protocol.json','resource_authorization.json','COMPUTE_PROPOSAL.md','fresh_review.py','review_protocol.py','adjudication.py','prepare_cohorts.py','freeze_development.py','overlap.py']
    lock={str((HERE/f).relative_to(ROOT)):sha(HERE/f) for f in files}
    for f in ('isolated_repair_runner.py','matching.py','checkpoint.py','paired_analysis.py','lean_adapter.py','backend.py','common.py','dataset_tools.py','benchmark_inventory.csv','historical_exposure_index.json'):lock[str((LEGACY/f).relative_to(ROOT))]=sha(LEGACY/f)
    for f in ('src/verify.py','src/local_llm_client.py','src/model_client.py'):lock[f]=sha(ROOT/f)
    for f in ('accepted_development.json','development_dataset_freeze.json','development_protocol.json','v3_ai_accepted_candidates.json','development_ai_accepted_candidates.json','strict_reference_verification.jsonl','fresh_verified.json','expanded_historical_exposure.json'):lock[str((run_root()/f).relative_to(ROOT))]=sha(run_root()/f)
    for stage in ('v3_review_1','v3_review_2','development_review_1','development_review_2'):
        path=run_root()/stage/'reviews.jsonl'
        if path.exists():lock[str(path.relative_to(ROOT))]=sha(path)
    concerns=run_root()/'assistant_audit_concerns.json'
    if concerns.exists():lock[str(concerns.relative_to(ROOT))]=sha(concerns)
    for p in (HERE/'reference_repair_v4.py',HERE/'freezes/reference_prompt_v4.json',HERE/'reference_resource_v5.py',HERE/'freezes/reference_resource_v5.json',run_root()/'reference_prompt_exposure.json',run_root()/'reference_repair/records.jsonl'):
        if p.exists():lock[str(p.relative_to(ROOT))]=sha(p)
    dump(HERE/'freezes/development_CDE_v1.json',dict(status='FROZEN_BEFORE_ANY_DEVELOPMENT_INITIAL_INFERENCE',files=lock,confirmatory=False,required_acceptance='AI_SCREENED_FORMALLY_VERIFIED',resource_approval='Actual consolidated phases1–6 user authorization'),exclusive=True)
    print('Development protocol and actual cohort frozen:',len(dataset))

if __name__=='__main__':main()
