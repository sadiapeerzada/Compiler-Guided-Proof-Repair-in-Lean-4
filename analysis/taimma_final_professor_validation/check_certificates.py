"""Explicit local Lean check of new audit certificates; never runs model inference."""
import hashlib
import json
import os
import re
import shutil
import signal
import subprocess
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]

def run(command,timeout):
    process=subprocess.Popen(command,cwd=ROOT/'lean_project',stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,start_new_session=True)
    try:
        stdout,stderr=process.communicate(timeout=timeout)
        return process.returncode,stdout,stderr
    except subprocess.TimeoutExpired:
        os.killpg(process.pid,signal.SIGKILL)
        stdout,stderr=process.communicate()
        return None,stdout,stderr+'\nLocal check exceeded '+str(timeout)+' seconds.'

def main():
    source=HERE/'OverlapCertificates.lean'
    result=dict(command=['lake','env','lean','../analysis/taimma_final_professor_validation/OverlapCertificates.lean'],cwd='lean_project',certificate_sha256=hashlib.sha256(source.read_bytes()).hexdigest())
    expected=ROOT/'lean_project/.lake/packages/mathlib/.lake/build/lib/lean/Mathlib/Tactic/Ring.olean'
    if not shutil.which('lake') or not expected.exists():
        result.update(status='unverified: required local executable or cached Mathlib import absent',exit_code=None,stdout='',stderr='No package build/download was attempted.')
    else:
        code,out,err=run(['lake','env','lean',str(source)],45)
        result.update(status='passed' if code==0 else 'unverified: timeout' if code is None else 'unverified: compiler failure',exit_code=code,stdout=out,stderr=err)
        if code==0:
            require_names=['d06_t12_definitional','d06_to_t11','t11_to_t12','t12_to_t11','t13_specializes_to_d07','t07_to_t08','t08_to_t07']
            if not all('ProfessorOverlapAudit.'+name in out for name in require_names):
                result['status']='unverified: incomplete axiom report'
            if 'sorryAx' in out or re.search(r'(?m)^\s*(axiom|constant|opaque)\s+\w+',source.read_text()):
                result['status']='unverified: unsupported axiom or declaration'
            _,version,version_error=run(['lake','env','lean','--version'],15)
            result['lean_version']=version.strip() or version_error.strip()
    for key in ('stdout','stderr','lean_version'):
        if key in result:result[key]=re.sub(r'/Users/[^/\s"\\]+','<HOME>',result[key])
    (HERE/'lean_certificate_check.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=='__main__':main()
