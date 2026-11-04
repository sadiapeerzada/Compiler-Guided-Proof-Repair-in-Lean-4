"""Persisted single generation-phase deadline; kills the entire worker on expiry."""
import os,signal,subprocess,sys,time
from v2_common import *
from pipeline_v2 import root,metrics

if __name__=='__main__':
    authorize('generation');p=frozen();out=root();out.mkdir(parents=True,exist_ok=True);clock=out/'generation_phase_clock.json'
    if not clock.exists():dump(clock,dict(started_epoch=time.time(),max_runtime_seconds=1800),exclusive=True)
    remaining=read(clock)['started_epoch']+1800-time.time();ensure(remaining>0,'Generation deadline exhausted; no reset permitted')
    with (out/'generation_stdout.log').open('a') as stdout,(out/'generation_stderr.log').open('a') as stderr:
        child=subprocess.Popen([sys.executable,str(HERE/'pipeline_v2.py'),'generate'],stdout=stdout,stderr=stderr,start_new_session=True)
        try:code=child.wait(timeout=remaining);status='finished' if code==0 else 'worker_failed'
        except subprocess.TimeoutExpired:os.killpg(child.pid,signal.SIGKILL);child.wait();code=None;status='authorized_deadline_exhausted'
    metrics();dump(out/'generation_phase_status.json',dict(status=status,exit_code=code));print(status,code)
