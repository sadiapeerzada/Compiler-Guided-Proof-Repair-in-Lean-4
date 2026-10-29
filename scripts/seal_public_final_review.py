"""Scan and hash the revised local proposal; never push, merge or alter originals."""
import hashlib
import io
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from pypdf import PdfReader
from PIL import Image

ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'data/final_review/20261029_v2'
DEST=Path('/private/tmp/nl2lean-publication-final-v2-20261029')


def main():
    old=json.loads((BASE/'local/original_artifact_hashes.json').read_text())
    changed=[name for name,h in old['files'].items() if hashlib.sha256((ROOT/name).read_bytes()).hexdigest()!=h]
    assert not changed,changed
    patterns={'private_author':r'(?i)sadiapeerzada(?:2006)?|Sadia Peerzada',
              'private_home':r'(?:/Users/|/home/)[A-Za-z0-9_.-]+',
              'personal_contact':r'[A-Za-z0-9.!#$%&\x27*+/=?^_`{|}~-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+',
              'private_key':r'-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----',
              'credential_token':r'(?<![A-Za-z0-9])(?:sk-(?:proj-)?[A-Za-z0-9_-]{20,}|gsk_[A-Za-z0-9]{20,}|gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|AKIA[0-9A-Z]{16}|xox[baprs]-[A-Za-z0-9-]{15,}|AIza[0-9A-Za-z_-]{30,})',
              'labeled_personal_data':r'(?i)\b(?:phone|telephone|home address|date of birth|passport|aadhaar|iban|serial number|mac address)\s*[\"\x27]?\s*[:=]\s*[^\r\n]{3,100}',
              'signed_secret_url':r'(?i)[?&](?:access_token|api_key|password|signature|x-amz-signature|x-amz-credential)=[^\s&\"\x27<>]+'}
    values=[v.encode() for k,v in os.environ.items() if any(w in k.upper() for w in ['API_KEY','ACCESS_TOKEN','SECRET_KEY','PASSWORD']) and len(v)>=16]
    files={};findings=[];excluded_untracked=[]
    for path in sorted(DEST.rglob('*')):
        if not path.is_file():continue
        rel=str(path.relative_to(DEST))
        if path.name=='.git' or rel=='PUBLIC_PAYLOAD_MANIFEST.json':continue
        if path.name=='.DS_Store':excluded_untracked.append(rel);continue
        data=path.read_bytes()
        if path.suffix=='.pdf':
            reader=PdfReader(io.BytesIO(data));text='\n'.join(p.extract_text() or '' for p in reader.pages)+str(reader.metadata)
        elif path.suffix=='.png':
            im=Image.open(io.BytesIO(data));text=json.dumps(im.info,default=str)+str(im.getexif())
        else:text=data.decode('utf-8')
        for category,pattern in patterns.items():
            if re.search(pattern,text):findings.append({'path':rel,'category':category})
        if any(v in data for v in values):findings.append({'path':rel,'category':'available_environment_secret_value'})
        assert len(data)<20*1024*1024,rel
        files[rel]={'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data),'classification':'SAFE TO PUBLISH'}
    record={'valid':not findings,'proposed_files_excluding_payload_manifest':len(files),'findings':findings,
            'excluded_untracked_local_metadata':excluded_untracked,'original_artifacts_unchanged':len(old['files']),
            'scope':'All proposed file bytes/text, all PDF text/metadata and PNG metadata; generated scientific plots visually reviewed. Heuristic triage, not exhaustive secret detection or independent legal clearance.'}
    (BASE/'publication_safety_scan.json').write_text(json.dumps(record,indent=2)+'\n')
    assert not findings,findings
    inventory={'schema_version':2,'approval_status':'AWAITING_EXACT_REVISED_PAYLOAD_APPROVAL_NO_PUSH','files':files,
               'total_bytes':sum(v['bytes'] for v in files.values()),'privacy_check_summary':record,
               'manifest_scope':'All proposed tracked release files except this manifest and Git/untracked OS metadata. Prior public release ancestry only; no private study/audit commits.',
               'reproduction_scope':'Public redacted-view aggregate/paired reanalysis; local original-byte proof/metric reconstruction. Exact public prompt replay remains limited.'}
    manifest=DEST/'PUBLIC_PAYLOAD_MANIFEST.json';manifest.write_text(json.dumps(inventory,indent=2)+'\n')
    result=subprocess.run([sys.executable,'-B',str(DEST/'verify_payload.py')],cwd=DEST,capture_output=True,text=True)
    (BASE/'local/public_payload_validation_v2.json').write_text(result.stdout)
    (BASE/'local/public_payload_validation_v2.stderr').write_text(result.stderr)
    assert result.returncode==0,result.stderr
    result2=subprocess.run([sys.executable,'-B',str(DEST/'reanalyze_review_v2.py')],cwd=DEST,capture_output=True,text=True)
    (BASE/'local/public_metrics_validation_v2.json').write_text(result2.stdout)
    assert result2.returncode==0,result2.stderr
    summary={'proposed_files':len(files)+1,'payload_manifest_sha256':hashlib.sha256(manifest.read_bytes()).hexdigest(),
             'total_bytes_excluding_manifest':inventory['total_bytes'],'public_payload_validation_exit_code':result.returncode,
             'public_reanalysis_exit_code':result2.returncode,'new_inference_calls':0,'pushed_or_merged':False}
    (BASE/'publication_proposal.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2))


if __name__=='__main__':main()
