"""Check new outputs and tracked frozen-file immutability without rebinding evidence."""
import json
import re
import subprocess
from .common import ROOT,OUT,private_text,write_json

BASELINE='5ecbe7b74fd653e7fbd315474a3b19bb1425ca03'


def main():
    if not (OUT/'dev_placebo/execution_finished.json').exists():raise ValueError('Experiment still running')
    frozen=['data/final_study','data/local_model','configs','src','eval','scripts/run_final_study.py','lean_project/lean-toolchain','lean_project/lakefile.lean','lean_project/lake-manifest.json','paper/generated']
    changed=subprocess.check_output(['git','diff','--name-only',BASELINE,'--',*frozen],cwd=ROOT,text=True).splitlines()
    if changed:raise ValueError('Tracked frozen-source modification detected; retain evidence and inspect')
    findings=[];checked=0;pdfs=0
    from pypdf import PdfReader
    credential=re.compile(r'\b(?:sk-proj-[A-Za-z0-9_-]{16,}|gsk_[A-Za-z0-9]{16,}|github_pat_[A-Za-z0-9_]{16,}|ghp_[A-Za-z0-9]{20,}|AKIA[A-Z0-9]{16})\b')
    for path in sorted(OUT.rglob('*')):
        if not path.is_file() or '__pycache__' in path.parts:continue
        if path.suffix=='.pdf':
            reader=PdfReader(path);content='\n'.join(page.extract_text() or '' for page in reader.pages)+str(reader.metadata);pdfs+=1
        else:
            try:content=path.read_text()
            except UnicodeDecodeError:raise ValueError('Unrecognized binary output requires inspection: '+str(path.relative_to(ROOT)))
        checked+=1
        if private_text(content) or credential.search(content) or re.search(r'/(?:private/(?:tmp|var)|var/folders)/',content):
            findings.append(str(path.relative_to(ROOT)))
    if findings:raise ValueError('Potential private content detected in '+', '.join(findings))
    write_json(OUT/'post_hoc_final_privacy_integrity_audit.json',{'valid':True,'new_output_files_checked':checked,'PDFs_checked':pdfs,
        'tracked_frozen_paths_changed':changed,'comparison_baseline':BASELINE,'new_output_private_content_findings':[],
        'method':'Git tracked-path diff plus new-output text/PDF extraction and private-path/identity/contact/common-secret-pattern checks. No frozen artifact digest was rewritten or rebound.',
        'scope_limits':['This is a local review, not publication authorization.','Pattern scanning cannot establish licensing clearance or absence of every possible secret.','Ignored original compiler scratch files are transient and outside frozen-record paths.'],
        'push_or_merge_performed':False,'Study2_model_execution':False})
    print('New-output privacy scan and tracked frozen-source immutability check passed:',checked,'files')


if __name__=='__main__':main()
