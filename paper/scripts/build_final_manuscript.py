"""Actually compile the empirical PDF with the verified free Springer toolchain."""
from pathlib import Path
import datetime
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'data/final_study/v1'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    claims=json.loads((ROOT/'paper/generated/final_claims_manifest.json').read_text())
    if claims['main_tex_sha256']!=sha(ROOT/'paper/main.tex') or claims['results_sha256']!=sha(BASE/'analysis/results.json'):
        raise ValueError('Manuscript quantitative source changed')
    engine=Path('/tmp/nl2lean-tectonic-0.17.0/tectonic');template=Path('/tmp/nl2lean-springer-template')
    if not engine.exists() or not (template/'llncs.cls').exists():raise RuntimeError('Recorded free TeX toolchain must be restored before build')
    work=Path(tempfile.mkdtemp(prefix='nl2lean-final-paper-'))
    shutil.copytree(ROOT/'paper',work,dirs_exist_ok=True,ignore=shutil.ignore_patterns('build','*.pdf','__pycache__'))
    # Keep generated plot PDFs, which are document inputs rather than prior builds.
    for p in (ROOT/'paper/generated').glob('final_*.pdf'):shutil.copyfile(p,work/'generated'/p.name)
    for name in ['llncs.cls','splncs04.bst']:shutil.copyfile(template/name,work/name)
    out=ROOT/'paper/build';out.mkdir(exist_ok=True);env=dict(os.environ);env['XDG_CACHE_HOME']='/tmp/nl2lean-tex-cache'
    previous=list(BASE.glob('latex_final_attempt_*.log'));log=BASE/f'latex_final_attempt_{len(previous)+1}.log'
    command=[str(engine),'--untrusted','--keep-logs','--keep-intermediates','--outdir',str(out),str(work/'main.tex')]
    started=datetime.datetime.now(datetime.timezone.utc).isoformat()
    with log.open('w') as stream:result=subprocess.run(command,env=env,stdout=stream,stderr=subprocess.STDOUT)
    manifest={'command':command,'started_at':started,'finished_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'exit_code':result.returncode,'log':str(log.relative_to(ROOT)),'log_sha256':sha(log),'engine_binary_sha256':sha(engine),
        'class_sha256':sha(template/'llncs.cls'),'bibliography_style_sha256':sha(template/'splncs04.bst')}
    if result.returncode:
        (BASE/f'paper_build_failed_attempt_{len(previous)+1}.json').write_text(json.dumps(manifest,indent=2)+'\n');raise SystemExit(result.returncode)
    pdf=ROOT/'paper/compiled_final_manuscript.pdf';shutil.copyfile(out/'main.pdf',pdf)
    inputs=[ROOT/'paper/main.tex',ROOT/'paper/references.bib',*sorted((ROOT/'paper/generated').glob('final_*'))]
    manifest.update(pdf=str(pdf.relative_to(ROOT)),pdf_sha256=sha(pdf),source_sha256={str(p.relative_to(ROOT)):sha(p) for p in inputs if p.is_file()},
        warning_lines=[line for line in log.read_text().splitlines() if 'warning' in line.lower()])
    (BASE/'paper_build_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print('Actual empirical PDF compiled:',pdf,manifest['pdf_sha256'])

if __name__=='__main__':
    main()
    subprocess.run([sys.executable,str(ROOT/'paper/scripts/check_final_pdf.py')],check=True)
