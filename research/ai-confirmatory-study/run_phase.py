"""Hard phase wall-clock watchdog. Child intents persist after timeout/crash."""
import argparse
import os
import signal
import subprocess
import sys
import time
from ai_common import HERE,save,read
from pipeline import deadline,summarize_resources

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('phase',choices=['generation','reviews','development']);a=p.parse_args()
    end=deadline(a.phase);remaining=end-time.time()
    if remaining<=0:raise SystemExit('Authorized phase wall-clock window exhausted')
    command=[sys.executable,str(HERE/'pipeline.py'),'generate' if a.phase=='generation' else 'reviews'] if a.phase!='development' else [sys.executable,'-c',"import sys;sys.path.insert(0,"+repr(str(HERE))+");from experiment import execute;execute('development')"]
    root=HERE/'runs'/a.phase;root.mkdir(parents=True,exist_ok=True)
    with (root/'worker_stdout.log').open('a') as out,(root/'worker_stderr.log').open('a') as err:
        process=subprocess.Popen(command,cwd=HERE,stdout=out,stderr=err,start_new_session=True)
        try:code=process.wait(timeout=remaining);status='finished' if code==0 else 'worker_failed'
        except subprocess.TimeoutExpired:os.killpg(process.pid,signal.SIGKILL);process.wait();code=None;status='authorized_runtime_exhausted'
    save(root/'phase_execution_status.json',dict(status=status,exit_code=code,authorized_wall_clock_limit_seconds=1800,actual_model_inference_not_implied_by_status=True))
    print(status,code)
