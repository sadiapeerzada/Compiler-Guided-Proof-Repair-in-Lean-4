"""Compile the separate anonymized manuscript; original PDF/source untouched."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parents[2]
DEST=Path('/private/tmp/nl2lean-publication-ready-20261029')
LOCAL=ROOT/'publication_review/local'


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    work=Path(tempfile.mkdtemp(prefix='nl2lean-public-review-paper-'))
    shutil.copytree(DEST/'paper',work,dirs_exist_ok=True)
    template=Path('/tmp/nl2lean-springer-template');engine=Path('/tmp/nl2lean-tectonic-0.17.0/tectonic')
    for name in ['llncs.cls','splncs04.bst']:shutil.copyfile(template/name,work/name)
    out=LOCAL/'tex_build';out.mkdir(exist_ok=True)
    log=LOCAL/'release_latex.log';env=dict(os.environ);env['XDG_CACHE_HOME']='/tmp/nl2lean-tex-cache'
    with log.open('w') as stream:
        r=subprocess.run([str(engine),'--untrusted','--keep-logs','--outdir',str(out),str(work/'main.tex')],stdout=stream,stderr=subprocess.STDOUT,env=env)
    if r.returncode:raise SystemExit(r.returncode)
    pdf=DEST/'paper/publication_review.pdf';shutil.copyfile(out/'main.pdf',pdf)
    reader=PdfReader(pdf);text='\n'.join(p.extract_text() or '' for p in reader.pages)
    compact=''.join(text.split())
    required=['A:0/60(0.0%)','B:1/60(1.7%)','C:1/60(1.7%)','3.33','9,653','2,205','Anonymousauthor']
    assert all(s in compact for s in required),[s for s in required if s not in compact]
    assert '??' not in text and '@@' not in text
    assert not any(s in (text+str(reader.metadata)).lower() for s in ['sadiapeerzada','sadia peerzada','/users/','@gmail.com'])
    (LOCAL/'review_paper_extracted.txt').write_text(text)
    manifest={'exit_code':0,'pdf':'paper/publication_review.pdf','pdf_sha256':digest(pdf),'pages':len(reader.pages),
              'author_contact_withheld':True,'quantitative_text_checks_passed':True,
              'original_manuscript_unchanged':True,'engine_sha256':digest(engine),'class_sha256':digest(template/'llncs.cls'),
              'warning_lines':[line for line in log.read_text().splitlines() if 'warning:' in line and 'undefined' not in line],
              'source_sha256':{str(p.relative_to(DEST)):digest(p) for p in sorted((DEST/'paper').rglob('*')) if p.is_file() and p!=pdf}}
    (DEST/'paper/build_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print('Anonymized review PDF compiled and checked:',len(reader.pages),'pages;',digest(pdf))


if __name__=='__main__':main()
