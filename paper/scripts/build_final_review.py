"""Compile and check the revised Springer paper, retaining historical PDFs."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'data/final_review/20261029_v2'


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    claims=json.loads((BASE/'manuscript_claims.json').read_text())
    assert sha(ROOT/'paper/main.tex')==claims['main_tex_sha256']
    assert sha(BASE/'analysis_verified/results.json')==claims['analysis_sha256']
    engine=Path('/tmp/nl2lean-tectonic-0.17.0/tectonic');template=Path('/tmp/nl2lean-springer-template')
    work=Path(tempfile.mkdtemp(prefix='nl2lean-final-review-tex-'))
    shutil.copytree(ROOT/'paper',work,dirs_exist_ok=True,ignore=shutil.ignore_patterns('build','*.pdf','__pycache__'))
    for p in (ROOT/'paper/generated/review_v2').glob('*.pdf'):shutil.copyfile(p,work/'generated/review_v2'/p.name)
    for name in ['llncs.cls','splncs04.bst']:shutil.copyfile(template/name,work/name)
    out=BASE/'local/tex_build';out.mkdir(exist_ok=True)
    existing=list((BASE/'local').glob('latex_v2_attempt_*.log'));log=BASE/f'local/latex_v2_attempt_{len(existing)+1}.log'
    env=dict(os.environ);env['XDG_CACHE_HOME']='/tmp/nl2lean-tex-cache'
    with log.open('w') as stream:
        result=subprocess.run([str(engine),'--untrusted','--keep-logs','--outdir',str(out),str(work/'main.tex')],stdout=stream,stderr=subprocess.STDOUT,env=env)
    if result.returncode:raise SystemExit(result.returncode)
    pdf=ROOT/'paper/compiled_final_review_v2.pdf';shutil.copyfile(out/'main.pdf',pdf)
    reader=PdfReader(pdf);text='\n'.join(p.extract_text() or '' for p in reader.pages);compact=''.join(text.split())
    required=['0/60','1/60','1/58','58complete','3.33','9,653','2,205','Anonymousauthor']
    missing=[s for s in required if s not in compact]
    assert not missing,missing
    assert '@@' not in text and '??' not in text
    assert not any(s in (text+str(reader.metadata)).lower() for s in ['sadiapeerzada','sadia peerzada','/users/','@gmail.com'])
    assert 6<=len(reader.pages)<=15,('Unexpected submission page range',len(reader.pages))
    (BASE/'local/final_pdf_text.txt').write_text(text)
    record={'valid':True,'exit_code':result.returncode,'pdf':'paper/compiled_final_review_v2.pdf','pdf_sha256':sha(pdf),'pages':len(reader.pages),
            'quantitative_text_checks':required,'author_contact_withheld':True,'original_PDFs_preserved':True,
            'engine_sha256':sha(engine),'springer_class_sha256':sha(template/'llncs.cls'),'bibliography_style_sha256':sha(template/'splncs04.bst'),
            'source_sha256':{'paper/main.tex':sha(ROOT/'paper/main.tex'),'paper/references.bib':sha(ROOT/'paper/references.bib'),
                             **{str(p.relative_to(ROOT)):sha(p) for p in sorted((ROOT/'paper/generated/review_v2').glob('*')) if p.is_file()}},
            'log':str(log.relative_to(ROOT)),'log_sha256':sha(log),
            'warning_lines':[s for s in log.read_text().splitlines() if 'warning:' in s]}
    (BASE/'paper_build_manifest.json').write_text(json.dumps(record,indent=2)+'\n')
    print('Final revised Springer PDF compiled and text-checked:',len(reader.pages),'pages;',record['pdf_sha256'])


if __name__=='__main__':main()
