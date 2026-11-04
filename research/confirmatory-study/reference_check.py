"""Curator-only offline reference checks; never an inference or calibration entry point."""
import argparse
from pathlib import Path
from common import HERE,ROOT,read,dump,ensure,content_hash,text_hash,sha,clean
from dataset_tools import subject_hash
from lean_adapter import LeanVerifier,live_environment

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('candidate_file');p.add_argument('new_output_directory');p.add_argument('--curator-reference-validation',action='store_true',required=True);a=p.parse_args()
    protocol=read(HERE/'isolated_repair_protocol.json');environment=live_environment(protocol)
    directory=Path(a.new_output_directory);directory.mkdir(parents=True,exist_ok=False)
    verify=LeanVerifier(protocol['lean']['imports'],protocol['lean']['timeout_seconds'])
    manifest=[]
    for row in read(a.candidate_file):
        result=verify(row['reference_proof'],row['expected_lean_statement'],'curator_'+subject_hash(row)[:24])
        result.update(subject_sha256=subject_hash(row),reference_sha256=text_hash(row['reference_proof']),target_sha256=text_hash(row['expected_lean_statement']),verifier_implementation_sha256=sha(ROOT/'src/verify.py'),adapter_sha256=sha(HERE/'lean_adapter.py'),environment=environment,scope='formal reference checking only; no independent semantic/split adjudication')
        result=__import__('json').loads(clean(__import__('json').dumps(result)))
        path=directory/(content_hash(row['id'])+'.json');dump(path,result,exclusive=True)
        manifest.append(dict(id=row['id'],subject_sha256=subject_hash(row),path=path.name,sha256=sha(path),strict_success=result.get('success')))
    dump(directory/'manifest.json',manifest,exclusive=True)
