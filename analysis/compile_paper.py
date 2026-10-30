"""Compile the editable manuscript to a NEW post-hoc output, no old PDF rewrite."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
from pypdf import PdfReader
from .common import ROOT,OUT,write_json,private_text,sanitize


def main():
    out=OUT/'manuscript';out.mkdir(exist_ok=True)
    if (out/'post_hoc_pilot.pdf').exists():raise ValueError('Refusing to replace existing post-hoc PDF')
    (out/'source').mkdir(exist_ok=True)
    for name in ['main.tex','references.bib']:shutil.copyfile(ROOT/'paper'/name,out/'source'/name)
    work=Path(tempfile.mkdtemp(prefix='lean-posthoc-paper-'));(work/'paper').mkdir()
    shutil.copytree(ROOT/'paper',work/'paper',dirs_exist_ok=True,ignore=shutil.ignore_patterns('build','*.pdf','__pycache__'))
    shutil.copytree(OUT/'latex',work/'outputs/post_hoc/latex')
    for p in (ROOT/'paper/generated/review_v2').glob('*.pdf'):shutil.copyfile(p,work/'paper/generated/review_v2'/p.name)
    template=Path('/tmp/nl2lean-springer-template');engine=Path('/tmp/nl2lean-tectonic-0.17.0/tectonic')
    for n in ['llncs.cls','splncs04.bst']:shutil.copyfile(template/n,work/'paper'/n)
    env=dict(os.environ);env['XDG_CACHE_HOME']='/tmp/nl2lean-tex-cache'
    result=subprocess.run([str(engine),'--untrusted','--keep-logs','--outdir',str(out.resolve()),str(work/'paper/main.tex')],env=env,capture_output=True,text=True)
    # Compiler build logs are a redacted representation, never raw private paths.
    log=sanitize(result.stdout+result.stderr)
    log=__import__('re').sub(r'(?:/private)?/tmp/[^\s`"\x27<>]+','[TEMP_BUILD_PATH]',log)
    (out/'post_hoc_build.log').write_text(log)
    if result.returncode:raise RuntimeError('Paper build failed; inspect privacy-redacted post-hoc build log')
    shutil.copyfile(out/'main.pdf',out/'post_hoc_pilot.pdf')
    # Tectonic .log contains absolute command paths: retain only the sanitized log.
    for path in out.glob('main.*'):
        if path.suffix!='.pdf':path.unlink()
    reader=PdfReader(out/'post_hoc_pilot.pdf');text='\n'.join(page.extract_text() or '' for page in reader.pages)
    compact=''.join(text.split());expected='Compiler-GuidedProofRepairinLean4:AControlledLocal-ModelPilotonFixedTheoremTypes'
    assert expected in compact and '??' not in text and '@@' not in text
    assert 'p=1.0' in compact and 'Exploratorydevelopmentplacebo' in compact
    assert not private_text(text+str(reader.metadata))
    write_json(out/'post_hoc_build_manifest.json',{'post_hoc':True,'exit_code':result.returncode,'pages':len(reader.pages),
        'pdf':'outputs/post_hoc/manuscript/post_hoc_pilot.pdf','pdf_sha256':hashlib.sha256((out/'post_hoc_pilot.pdf').read_bytes()).hexdigest(),
        'source_sha256':{'paper/main.tex':hashlib.sha256((ROOT/'paper/main.tex').read_bytes()).hexdigest(),'paper/references.bib':hashlib.sha256((ROOT/'paper/references.bib').read_bytes()).hexdigest()},
        'title_checked':True,'old_manuscript_PDFs_unchanged':True,
        'warning_lines':[s for s in log.splitlines() if 'warning:' in s]})
    print('New post-hoc paper compiled:',len(reader.pages),'pages; requested exact title checked.')


if __name__=='__main__':
    try:main()
    except Exception as error:print('Paper build stopped:',type(error).__name__,sanitize(str(error)));raise SystemExit(1)
