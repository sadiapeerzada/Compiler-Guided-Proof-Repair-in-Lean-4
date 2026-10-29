"""Seal only the separately prepared release after private preservation/privacy checks."""
import collections
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import re
import subprocess
from pypdf import PdfReader
from PIL import Image

ROOT=Path(__file__).resolve().parents[2]
DEST=Path('/private/tmp/nl2lean-publication-ready-20261029')
LOCAL=ROOT/'publication_review/local'


def read(path):return json.loads(path.read_text())
def sha(data):return hashlib.sha256(data).hexdigest()


def main():
    baseline=read(LOCAL/'tracked_file_scan.json')
    changed=[r['path'] for r in baseline['files'] if sha((ROOT/r['path']).read_bytes())!=r['sha256']]
    preservation={'source_commit':baseline['summary']['target_commit'],'files_checked':len(baseline['files']),
                  'changed_original_files':changed,'all_original_tracked_bytes_preserved':not changed}
    (LOCAL/'source_preservation.json').write_text(json.dumps(preservation,indent=2)+'\n')
    if changed:raise ValueError('Original evidence changed; stop: '+str(changed))
    manifest=read(DEST/'PUBLIC_RELEASE_MANIFEST.json')
    for entry in manifest['prepared_exports']:
        path=DEST/entry['path'];data=path.read_bytes();entry['sha256']=sha(data);entry['bytes']=len(data)
        if 'original_sha256' in entry:entry['byte_identical']=sha(data)==entry['original_sha256']
    (DEST/'PUBLIC_RELEASE_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
    patterns={
        'private_author':r'(?i)sadiapeerzada(?:2006)?|Sadia Peerzada',
        'actual_home_path':r'(?:/Users/|/home/)[A-Za-z0-9_.-]+',
        'private_email':r'[A-Za-z0-9.!#$%&\x27*+/=?^_`{|}~-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+',
        'credential':r'(?<![A-Za-z0-9])(?:sk-(?:proj-)?[A-Za-z0-9_-]{20,}|gsk_[A-Za-z0-9]{20,}|gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|AKIA[0-9A-Z]{16}|xox[baprs]-[A-Za-z0-9-]{15,})',
        'private_key':r'-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----',
    }
    secret_values=[v.encode() for k,v in os.environ.items() if any(w in k.upper() for w in ['API_KEY','ACCESS_TOKEN','SECRET_KEY','PASSWORD']) and len(v)>=16]
    findings=[];coverage=collections.Counter();files={}
    for path in sorted(DEST.rglob('*')):
        if not path.is_file() or path.name in {'.git','PUBLIC_PAYLOAD_MANIFEST.json'}:continue
        rel=str(path.relative_to(DEST));data=path.read_bytes()
        if path.suffix=='.pdf':
            reader=PdfReader(io.BytesIO(data));text='\n'.join(p.extract_text() or '' for p in reader.pages)+str(reader.metadata);coverage['pdf_text_metadata']+=1
        elif path.suffix=='.png':
            im=Image.open(io.BytesIO(data));text=json.dumps(im.info,default=str)+str(im.getexif());coverage['png_metadata_and_prior_visual_review']+=1
        else:
            text=data.decode('utf-8');coverage['utf8_text']+=1
        for category,pattern in patterns.items():
            if re.search(pattern,text):findings.append({'path':rel,'category':category})
        if any(v in data for v in secret_values):findings.append({'path':rel,'category':'known_environment_credential_value'})
        files[rel]={'sha256':sha(data),'bytes':len(data)}
    record={'valid':not findings,'file_count_excluding_payload_manifest':len(files),'coverage':dict(coverage),'findings':findings,
            'original_tracked_files_preserved':5632,'no_new_inference':True,
            'limitations':'Heuristic checks plus documented content review; not exhaustive secret detection, legal clearance, or exact-byte public inference replay.'}
    (LOCAL/'public_privacy_scan.json').write_text(json.dumps(record,indent=2)+'\n')
    if findings:raise ValueError('Unsafe release entries require correction: '+json.dumps(findings))
    payload={'schema_version':1,'source_commit':baseline['summary']['target_commit'],'approval_status':'AWAITING_USER_APPROVAL_NO_PUSH',
             'files':files,'total_bytes':sum(x['bytes'] for x in files.values()),'privacy_check_summary':record,
             'manifest_scope':'All release files except this manifest itself and Git administrative metadata. File membership and hashes are exact. Private research ancestry is not part of this orphan branch.',
             'reproduction_scope':'Public aggregate reanalysis and redacted evidence inspection; all original exact-byte evidence retained privately.'}
    target=DEST/'PUBLIC_PAYLOAD_MANIFEST.json';target.write_text(json.dumps(payload,indent=2)+'\n')
    result=subprocess.run([str(ROOT/'.venv/bin/python'),'-B',str(DEST/'verify_payload.py')],cwd=DEST,capture_output=True,text=True)
    (LOCAL/'public_payload_validation.json').write_text(result.stdout)
    (LOCAL/'public_payload_validation.stderr').write_text(result.stderr)
    if result.returncode:raise RuntimeError('Public payload verification failed: '+result.stderr)
    print(json.dumps({'public_files_including_manifest':len(files)+1,'total_bytes_excluding_manifest':payload['total_bytes'],
                      'payload_manifest_sha256':sha(target.read_bytes()),'all_original_files_preserved':True,'public_validation_exit_code':result.returncode},indent=2))


if __name__=='__main__':main()
