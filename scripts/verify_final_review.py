"""Append actual final verification logs/status; no inference and no raw rewrites."""
import datetime
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'data/final_review/20261029_v2';LOCAL=BASE/'local'
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'eval')]
from final_study import read,sha,validate_protocol,validate_freeze
from local_protocol import live_lean_environment
from local_llm_client import snapshot_inventory
from verify import check_lean_file_detailed,VerificationPolicy


def write(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')


def main():
    events=[]
    def run(name,command,cwd=ROOT):
        path=LOCAL/(name+'.log')
        if path.exists():raise ValueError('Refusing to overwrite '+str(path))
        started=datetime.datetime.now(datetime.timezone.utc).isoformat()
        with path.open('w') as stream:r=subprocess.run(command,cwd=cwd,stdout=stream,stderr=subprocess.STDOUT)
        events.append({'step':name,'command':command,'cwd':str(cwd.relative_to(ROOT)) or '.',
                       'exit_code':r.returncode,'log':str(path.relative_to(ROOT)),'log_sha256':sha(path),
                       'started_at':started,'finished_at':datetime.datetime.now(datetime.timezone.utc).isoformat()})
        write(BASE/'verification_steps.json',events)
        if r.returncode:raise RuntimeError('Final check failed: '+name)
        print(name,'PASS',flush=True)
    p=validate_protocol(ROOT/'configs/repair_experiment_local_v0.4.2.json');freeze=validate_freeze()
    live=live_lean_environment({'lean_environment':{'mathlib_revision':p['mathlib_revision']}})
    actual=snapshot_inventory(Path.home()/p['model']['snapshot_home_relative'])
    assert actual==read(ROOT/p['model']['inventory_path'])
    write(BASE/'environment_verification.json',{'valid':True,'lean':live,'runtime_packages':p['runtime_packages'],
          'model_revision':actual['snapshot_revision'],'tokenizer_revision':actual['tokenizer_revision'],
          'model_inventory_sha256':p['model']['inventory_sha256'],'all_snapshot_files_match':True,
          'weights_loaded':False,'new_inference_calls':0,'dataset':freeze})
    print('Environment, all weight/tokenizer hashes and AI-eligibility policy PASS',flush=True)
    run('pytest_final',[sys.executable,'-m','pytest','-q'])
    run('lean_build_final',['lake','build'],ROOT/'lean_project')
    run('references_final',['lake','env','lean','--json',str(ROOT/'data/ai_semantic_audit/20261028/lean_reference_check/all_references.lean')],ROOT/'lean_project')
    proofs=[]
    for path in sorted((ROOT/'data/final_study/v1/final_runs/heldout').rglob('verification.json')):
        old=read(path)
        if not old['success']:continue
        folder=path.parent;ident=folder.parent.name;row=next(r for r in read(ROOT/'data/final_study/v1/test.json') if r['id']==ident)
        v=check_lean_file_detailed((folder/'candidate.lean').read_text(),ROOT/'lean_project','final_review_'+ident+'_'+folder.name,
            expected_statement='open scoped BigOperators\n'+row['expected_lean_statement']+' := by sorry',policy=VerificationPolicy(timeout_seconds=180)).to_record()
        proofs.append({'problem_id':ident,'step':folder.name,'candidate_sha256':sha(folder/'candidate.lean'),'source_verification':str(path.relative_to(ROOT)),'fresh_verification':v})
    write(LOCAL/'model_success_reverification.json',proofs)
    assert len(proofs)==2 and all(v['fresh_verification']['success'] for v in proofs)
    print('Both actual model successes freshly reverified PASS',flush=True)
    run('analysis_determinism',[sys.executable,'eval/final_review_analysis.py','--output','data/final_review/20261029_v2/analysis_repeat'])
    assert (BASE/'analysis_repeat/results.json').read_bytes()==(BASE/'analysis_verified/results.json').read_bytes()
    baseline=read(LOCAL/'original_artifact_hashes.json');changed=[name for name,h in baseline['files'].items() if sha(ROOT/name)!=h]
    assert not changed,changed
    refmessages=[json.loads(line) for line in (LOCAL/'references_final.log').read_text().splitlines() if line.startswith('{')]
    assert not any(d.get('severity')=='error' for d in refmessages)
    axiom_reports=[d for d in refmessages if 'depends on axioms' in d.get('data','')]
    assert not any('sorryAx' in d['data'] for d in axiom_reports)
    write(BASE/'reproducibility_verification.json',{'valid':True,'original_artifacts_checked':len(baseline['files']),
        'original_artifacts_unchanged':True,'dataset_and_AI_review_valid':True,'pinned_environment_valid':True,
        'all_model_files_hashed':True,'frozen_pinned_source_files_valid':True,'reference_batch_compilation_exit_code':0,
        'reference_batch_candidates':96,'reference_axiom_reports':len(axiom_reports),'fresh_model_successes_verified':2,
        'metric_regeneration_byte_identical':True,'new_inference_calls':0,
        'limits':'Local original-byte reproducibility established for logs/metrics/proofs. Public redaction does not support exact original prompt replay or external pretest publication claims.'})
    print('All original artifacts preserved; deterministic metrics PASS',flush=True)


if __name__=='__main__':main()
