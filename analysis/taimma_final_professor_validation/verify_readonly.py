"""Repeat new validation and ensure protected evidence stays byte-identical."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
GENERATED=['verification_results.json','TOKEN_MATCHING_VERIFICATION.csv','STATEMENT_INVENTORY.csv','BENCHMARK_OVERLAP_EVIDENCE.csv','EXPERIMENTAL_CONTROL_VERIFICATION.md','STATISTICAL_INTEGRITY_REPORT.md','BENCHMARK_VALIDITY_VERIFICATION.md','HUMAN_ADJUDICATION_REQUIRED.md','DIAGNOSTIC_AND_FAILURE_AUDIT.md','REPRODUCIBILITY_FINAL_VERIFICATION.md']

def hashes(paths):
    return {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}

def main():
    roots=['research/study2-v7/','research/study2-final/','research/study2-raw-v8-v9/','analysis/taimma_20261104/','analysis/taimma_supervisor_final/','publication/results/review_v2/']
    protected=subprocess.check_output(['git','ls-files','--']+roots,cwd=ROOT,text=True).splitlines()
    before=hashes([ROOT/p for p in protected])
    old=hashes([HERE/p for p in GENERATED])
    subprocess.run([sys.executable,str(HERE/'validate.py')],cwd=ROOT,check=True)
    assert old==hashes([HERE/p for p in GENERATED]),'New outputs are not deterministic'
    assert before==hashes([ROOT/p for p in protected]),'Protected source was modified'
    changed=subprocess.check_output(['git','diff','--name-only','a3a709c383ceb016de3e746f962e543bbcc8b2a5'],cwd=ROOT,text=True).splitlines()
    assert all(p.startswith('analysis/taimma_final_professor_validation/') for p in changed),'Existing tracked file changed'
    for path in HERE.glob('*.md'):
        assert '/Users/' not in path.read_text() and '/home/' not in path.read_text(),'Private home prefix in report'
    result=dict(generated_artifacts_byte_identical=len(GENERATED),protected_files_byte_identical=len(protected),prior_tracked_files_modified=0,publication_report_home_prefix_scan='passed')
    (HERE/'READONLY_CHECKS.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps(result,sort_keys=True))

if __name__=='__main__':main()
