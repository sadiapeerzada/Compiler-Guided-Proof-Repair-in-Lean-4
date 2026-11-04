"""Fail-closed evidence/approval gate and immutable source lock. No model imports."""
import argparse
from datetime import date
from pathlib import Path
from common import HERE,ROOT,ensure,sha,read,content_hash,text_hash,normalize,dump
from dataset_tools import subject_hash,screen,cohort_flags

IMPLEMENTATION=['common.py','dataset_tools.py','isolated_repair_validation.py','isolated_repair_runner.py','paired_analysis.py','checkpoint.py','matching.py','backend.py','lean_adapter.py']

def relative(base,name):
    p=(base/name).resolve();ensure(p.is_relative_to(base.resolve()),'Bundle path escapes its root');return p

def artifact(spec,base):
    ensure(isinstance(spec,dict) and bool(spec.get('path')) and bool(spec.get('sha256')),'Missing evidence artifact')
    p=relative(base,spec['path']);ensure(p.is_file() and p.stat().st_size>0 and sha(p)==spec['sha256'],'Evidence artifact missing/changed')
    return p

def human(record,base,expected_status,independent=True):
    ensure(record.get('status')==expected_status,'Missing explicit human decision')
    ensure(record.get('actor_kind') in ({'independent_human'} if independent else {'independent_human','human_authority'}) and record.get('name') and record.get('independence_statement' if independent else 'authority_statement'),'Required human provenance absent')
    ensure(not record.get('unit_test_only',False),'Test fixture is not production approval')
    when=date.fromisoformat(record['signed_on']);ensure(when<=date.today(),'Future-dated approval')
    artifact(record.get('signed_evidence'),base)
    # This checks recorded attestation integrity, NOT reviewer identity/signature authenticity.


def check_source_lock(path):
    lock=read(path)
    for p,expected in lock['files'].items():ensure((ROOT/p).resolve().is_relative_to(ROOT.resolve()) and (ROOT/p).is_file() and sha(ROOT/p)==expected,'Frozen implementation/environment changed: '+p)
    ensure(all('research/confirmatory-study/'+n in lock['files'] for n in IMPLEMENTATION),'Incomplete implementation lock')
    return lock

def gate(bundle_path,phase):
    """Calibration never opens the test dataset, including for content hashing."""
    ensure(phase in ('development','test'),'Unknown phase')
    path=Path(bundle_path).resolve();base=path.parent;bundle=read(path);reasons=[]
    try:
        protocol_path=relative(base,bundle['protocol']);protocol=read(protocol_path)
        manifest_path=relative(base,bundle['dataset_manifest']);manifest=read(manifest_path)
        lock_path=relative(base,bundle['source_lock']);check_source_lock(lock_path)
        ensure(protocol['status']=='FROZEN_FOR_EXECUTION','Protocol is not genuinely frozen for execution')
        ensure(manifest[phase]['count']==protocol['sample_size'][phase] and manifest[phase]['count']>0,'No approved eligible sample of the frozen size')
        ensure(set(protocol['arms'])=={'C','D','E'} and protocol['repairs_per_arm']==1,'Wrong isolated arm/budget design')
        ensure(protocol['budget']['input_tokens_per_call']==4096 and protocol['budget']['output_tokens_per_call']==1200,'Unapproved call-token limits')
        ensure(protocol['seeds']==[2037,2038,2039],'Seed grid changed')
        ensure(protocol['decoding']['max_context_tokens']>=5296,'Insufficient total context')
        benchmark_path=relative(base,bundle['benchmark_approval']);benchmark=read(benchmark_path);human(benchmark,base,'APPROVED_BENCHMARK')
        ensure(benchmark['dataset_manifest_sha256']==sha(manifest_path),'Benchmark approval binds different manifest')
        authorization_path=relative(base,bundle['authorization']);authorization=read(authorization_path)
        human(authorization,base,'AUTHORIZED_EXECUTION',independent=False)
        ensure(authorization['phase']==phase,'Authorization is for another phase')
        bindings={'protocol_sha256':sha(protocol_path),'dataset_manifest_sha256':sha(manifest_path),'source_lock_sha256':sha(lock_path),'benchmark_approval_sha256':sha(benchmark_path)}
        for k,v in bindings.items():ensure(authorization.get(k)==v,'Authorization does not bind '+k)
        ensure(authorization['model_revision']==protocol['model']['revision'],'Wrong authorized model')
        budget=authorization['resource_limits']
        ensure(0<budget['max_calls']<=protocol['budget']['max_total_calls'],'Invalid explicit call authorization')
        ensure(0<budget['max_runtime_seconds']<=protocol['budget']['max_runtime_seconds'],'Invalid runtime authorization')
        needed=manifest[phase]['count']*len(protocol['seeds'])*4
        ensure(budget['max_calls']>=needed,'Authorization does not cover planned worst-case phase calls')
        frozen_path=relative(base,bundle['freeze']);frozen=read(frozen_path)
        human(frozen,base,'FROZEN_BEFORE_OUTCOMES',independent=False)
        for k,v in bindings.items():ensure(frozen.get(k)==v,'Freeze does not bind '+k)
        ensure(frozen['no_test_outcomes_observed'] is True and frozen['test_statements_not_used_for_calibration_or_tuning'] is True,'Test data used for calibration/tuning or outcome-dependent freeze')
        ensure(authorization['freeze_sha256']==sha(frozen_path),'Authorization does not bind freeze')
        evidence_path=relative(base,bundle['verification_evidence']);evidence=read(evidence_path)
        ensure(evidence['status']=='REAL_LEAN_INTEGRATION_PASSED' and evidence['source_lock_sha256']==sha(lock_path),'Real integration evidence absent or stale')
        log=read(artifact(evidence['log_artifact'],base))
        ensure(log['lean_status']=='passed' and log['tokenizer_status']=='passed' and set(log['rendered_counts'].values())=={4096},'Real Lean/tokenizer checks failed or absent')
        expected_scope=content_hash({'lean':protocol['lean'],'model_revision':protocol['model']['revision'],'chat_template_sha256':protocol['model']['chat_template_sha256'],'input_tokens':4096})
        ensure(log['verification_scope_sha256']==expected_scope,'Integration evidence describes another verifier/tokenizer scope')
        ensure(authorization['verification_evidence_sha256']==sha(evidence_path),'Authorization does not bind executable checks')
        # Only now open selected phase rows. Never open the test path in development.
        dataset_path=relative(base,manifest[phase]['path']);ensure(sha(dataset_path)==manifest[phase]['sha256'],'Dataset changed after freeze')
        records=read(dataset_path);ensure(len(records)==manifest[phase]['count'],'Wrong cohort denominator')
        ensure(not any(cohort_flags(records)),'Duplicate/alpha-equivalent prospective subjects')
        ids=[r['id'] for r in records];ensure(len(ids)==len(set(ids)),'Duplicate subject ID')
        reviews=benchmark['subjects']
        for row in records:
            ensure(not screen(row)['quarantine'],'Historical/incomplete candidate must be quarantined: '+row['id'])
            h=subject_hash(row);ensure(manifest[phase]['statement_fingerprints'][row['id']]==content_hash(normalize(row['expected_lean_statement'],True)),'Statement fingerprint changed');ensure(manifest[phase]['subject_hashes'][row['id']]==h,'Subject content changed')
            review=reviews[row['id']];ensure(review['subject_sha256']==h,'Human review binds different subject')
            ensure(all(review.get(k)=='APPROVED' for k in ('mathematics','semantic_fidelity','family_independence','source_license','historical_overlap_clearance')),'Incomplete independent subject decisions')
            proof=read(artifact(row['reference_verification'],base))
            ensure(proof['success'] is True and proof['exit_code']==0 and proof['reference_sha256']==text_hash(row['reference_proof']) and proof['target_sha256']==text_hash(row['expected_lean_statement']),'Reference proof is not bound/verified')
            ensure(proof['verifier_implementation_sha256']==sha(ROOT/'src/verify.py') and proof['adapter_sha256']==sha(HERE/'lean_adapter.py'),'Reference used another verification implementation')
            ensure(isinstance(proof.get('axiom_dependencies'),list) and set(proof['axiom_dependencies'])<={'propext','Classical.choice','Quot.sound'},'Missing/unsupported reference axiom report')
        dev=set(manifest['development']['families']);test=set(manifest['test']['families']);ensure(not dev&test,'Declared family crosses development/test')
        ensure(not set(manifest['development']['statement_fingerprints'].values())&set(manifest['test']['statement_fingerprints'].values()),'Alpha-equivalent statement crosses partitions')
        # Raw statements on the other partition are never read here.
        ensure(not set(manifest['development']['subject_hashes'])&set(manifest['test']['subject_hashes']),'Identifier crosses partitions')
        ensure(set(row['family'] for row in records)==set(manifest[phase]['families']),'Manifest family labels changed')
        return dict(status='GO',phase=phase,protocol=protocol,protocol_sha256=sha(protocol_path),source_lock_sha256=sha(lock_path),manifest=manifest,records=records,authorization=authorization,bundle=str(path),attestation_caveat='Artifact consistency only; genuine human authority must be established outside software.')
    except (ValueError,KeyError,TypeError,FileNotFoundError) as error:
        reasons.append(str(error))
        return dict(status='NO_GO',phase=phase,reasons=reasons,records_not_released=True)

def require_go(bundle,phase):
    result=gate(bundle,phase);ensure(result['status']=='GO','NO_GO: '+'; '.join(result.get('reasons',[])));return result

def freeze_implementation(output=None):
    files={str((HERE/n).relative_to(ROOT)):sha(HERE/n) for n in IMPLEMENTATION}
    for n in ['isolated_repair_protocol.json','prepare_protocol.py','integration_checks.py','reference_check.py','tests/test_confirmatory.py','benchmark_inventory.csv','historical_exposure_index.json']:
        files[str((HERE/n).relative_to(ROOT))]=sha(HERE/n)
    for p in ['src/verify.py','src/model_client.py','src/local_llm_client.py','lean_project/lean-toolchain','lean_project/lake-manifest.json','lean_project/lakefile.toml']:
        files[p]=sha(ROOT/p)
    # This engineering lock grants no benchmark approval or inference authorization.
    dump(output or HERE/'implementation_lock.json',dict(status='ENGINEERING_LOCK_NOT_HUMAN_PREREGISTRATION',files=files),exclusive=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--bundle',default=str(HERE/'execution_bundle.json'));p.add_argument('--phase',choices=['development','test'],default='test');p.add_argument('--freeze-implementation',action='store_true');p.add_argument('--lock-output');a=p.parse_args()
    if a.freeze_implementation:freeze_implementation(relative(HERE,a.lock_output) if a.lock_output else None)
    else:print(__import__('json').dumps(gate(a.bundle,a.phase),indent=2))
