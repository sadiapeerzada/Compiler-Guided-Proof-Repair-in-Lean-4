"""Validate and seal the prepared publication tree; no network writes."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from .common import private_text,sanitize
from .export_privacy import private_export_text


def main(destination):
    public=Path(destination).resolve()/'publication';target=public/'post_hoc';record=target/'PUBLIC_VALIDATION.json'
    if record.exists():raise ValueError('Preserve previous public validation')
    protocol=json.loads((target/'extensions/placebo_protocol.json').read_text())
    views={f['release']:f for f in json.loads((target/'SOURCE_VIEW_MANIFEST.json').read_text())['files']}
    pins=[]
    for name,expected in protocol['pinned_implementation_files'].items():
        actual=hashlib.sha256((target/name).read_bytes()).hexdigest();view=views['post_hoc/'+name]
        if actual!=expected:assert view['byte_identical_to_local'] is False and view['transformations']
        else:assert view['byte_identical_to_local'] is True
        pins.append({'path':name,'matches_original_protocol_pin':actual==expected,'public_derivative_changes':view['transformations']})
    env=dict(os.environ);env['PYTHONDONTWRITEBYTECODE']='1'
    commands=[('public_source_unit_tests',[sys.executable,'-B','-m','pytest','-q','-p','no:cacheprovider','analysis/tests'],target),
              ('public_dev_records',[sys.executable,'-B','-m','analysis.check_public_dev'],target),
              ('historical_public_reanalysis',[sys.executable,'-B','reanalyze_review_v2.py'],public)]
    results=[]
    for name,command,cwd in commands:
        result=subprocess.run(command,cwd=cwd,env=env,capture_output=True,text=True)
        text=sanitize(result.stdout+result.stderr)
        if result.returncode:raise ValueError(name+' failed; '+text)
        results.append({'check':name,'exit_code':0,'output':text});print(name,'passed',flush=True)
    from pypdf import PdfReader
    findings=[];pdfs=0;files_checked=0
    for path in sorted(public.rglob('*')):
        if not path.is_file():continue
        if path.suffix=='.pdf':
            pdf=PdfReader(path);text='\n'.join(p.extract_text() or '' for p in pdf.pages)+str(pdf.metadata);pdfs+=1
        elif path.suffix=='.png':
            from PIL import Image
            image=Image.open(path);text=json.dumps(image.info,default=str)+str(image.getexif())
        else:text=path.read_text()
        files_checked+=1
        if private_export_text(text):findings.append(str(path.relative_to(public)))
    if findings:raise ValueError('Public private-content scan failed: '+', '.join(findings))
    report={'post_hoc':True,'valid':True,'checks':results,'frozen_source_view_checks':pins,'whole_publication_files_scanned':files_checked,'PDFs_scanned':pdfs,
            'private_content_findings':[],'scope':'New public derivative unit tests and stored dev-record checks; existing public aggregate reanalysis; all publication text/PDF metadata scanning. Exact file/token checks follow in verify_payload.py.',
            'model_calls':0,'network_writes':False}
    record.write_text(json.dumps(report,indent=2)+'\n')
    mp=public/'PUBLIC_PAYLOAD_MANIFEST.json';manifest=json.loads(mp.read_text());files={}
    for path in sorted(public.rglob('*')):
        if not path.is_file() or path==mp:continue
        data=path.read_bytes();files[str(path.relative_to(public))]={'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data),'classification':'SAFE TO PUBLISH'}
    manifest['files']=files;manifest['total_bytes']=sum(f['bytes'] for f in files.values())
    mp.write_text(json.dumps(manifest,indent=2)+'\n')
    result=subprocess.run([sys.executable,'-B','verify_payload.py'],cwd=public,env=env,capture_output=True,text=True)
    if result.returncode:raise ValueError('Exact payload verification failed: '+sanitize(result.stdout+result.stderr))
    print(result.stdout,flush=True)
    print('Public derivative, numerical checks and exact sealed payload passed; no push or merge performed.')


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--destination',required=True);args=parser.parse_args();main(args.destination)
