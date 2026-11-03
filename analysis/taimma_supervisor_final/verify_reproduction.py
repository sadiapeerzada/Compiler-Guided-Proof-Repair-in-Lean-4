"""Check determinism and clean-checkout reproduction without V7 raw originals."""
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
GENERATED=['CASE_STUDIES.md','CONTEXT_WINDOW_ANALYSIS.md','RESOURCE_ANALYSIS.md','FAILURE_ANALYSIS.md','INDEPENDENT_BENCHMARK_REVIEW_PACKET.md','FINAL_SCIENTIFIC_AUDIT.md','case_excerpts.json','integrity_checks.json','SOURCE_HASHES.json','resources.csv','repair_observations.csv','prompt_lengths.csv','diagnostic_length_bins.csv','failure_persistence.csv']

def hashes(path):
    return {n:hashlib.sha256((path/n).read_bytes()).hexdigest() for n in GENERATED}

def main():
    before=hashes(HERE)
    subprocess.run([sys.executable,str(HERE/'supplement.py')],check=True)
    assert before==hashes(HERE),'Non-deterministic generation'
    ledger=json.loads((HERE/'SOURCE_HASHES.json').read_text())
    with tempfile.TemporaryDirectory(prefix='taimma-evidence-reproduce-') as tmp:
        checkout=Path(tmp)
        for item in ledger:
            rel=item['path']
            if '::' in rel or rel.startswith('study2_outputs/'):
                continue
            source=ROOT/rel
            target=checkout/rel
            target.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(source,target)
        target=checkout/'analysis/taimma_supervisor_final'
        shutil.copytree(HERE,target,dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__','.pytest_cache'))
        assert not (checkout/'study2_outputs').exists()
        subprocess.run([sys.executable,str(target/'supplement.py')],check=True,cwd=checkout)
        assert before==hashes(target),'Clean-checkout reproduction differs'
    for name in GENERATED:
        text=(HERE/name).read_text()
        assert '/Users/' not in text and '/home/' not in text,'Personal path in '+name
    result=dict(repeated_run_byte_identical=True,without_local_v7_originals_byte_identical=True,generated_files_checked=len(GENERATED),personal_home_prefix_scan='passed for generated publication-facing outputs')
    (HERE/'reproduction_checks.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps(result,sort_keys=True))

if __name__=='__main__':main()
