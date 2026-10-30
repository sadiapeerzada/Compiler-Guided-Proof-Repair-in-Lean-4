"""Complete test/build checks after model execution, with privacy-safe logs."""
import subprocess
import time
from .common import ROOT,OUT,sanitize,write_json


def main():
    if not (OUT/'dev_placebo/execution_finished.json').exists():raise ValueError('Do not compete with the active model worker')
    if (OUT/'post_hoc_final_checks.json').exists():raise ValueError('Preserve prior check results')
    results=[]
    for name,command,cwd in [('python_suite',['.venv/bin/python','-m','pytest','-q','tests','analysis/tests'],ROOT),
                              ('lean_build',['lake','build'],ROOT/'lean_project')]:
        print('Running',name,flush=True);start=time.monotonic()
        result=subprocess.run(command,cwd=cwd,capture_output=True,text=True)
        text=sanitize(result.stdout+result.stderr);log=OUT/('post_hoc_'+name+'.log')
        if log.exists():raise ValueError('Preserve prior check log')
        log.write_text(text)
        results.append({'check':name,'command':command,'working_directory':'.' if cwd==ROOT else 'lean_project',
                        'exit_code':result.returncode,'elapsed_seconds':time.monotonic()-start,'log':str(log.relative_to(ROOT))})
        print(name,'exit',result.returncode,flush=True)
    write_json(OUT/'post_hoc_final_checks.json',{'post_hoc':True,'checks':results,'all_passed':all(r['exit_code']==0 for r in results),'new_model_calls':0})
    if any(r['exit_code'] for r in results):raise SystemExit(1)


if __name__=='__main__':main()
