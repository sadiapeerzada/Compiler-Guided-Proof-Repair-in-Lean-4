import subprocess,signal,time,argparse
from study_common import *

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('stage');a=p.parse_args();spec,_=authorize(a.stage);ensure(spec['kind']=='review','Review only');c=clock(a.stage);out=run_root()/a.stage
    with (out/'stdout_v2.log').open('a') as stdout,(out/'stderr_v2.log').open('a') as stderr:
        child=subprocess.Popen([sys.executable,str(HERE/'review_worker_v2.py'),a.stage],stdout=stdout,stderr=stderr,start_new_session=True)
        try:code=child.wait(timeout=c['started_epoch']+c['max_runtime_seconds']-time.time());status='finished' if code==0 else 'worker_failed'
        except subprocess.TimeoutExpired:os.killpg(child.pid,signal.SIGKILL);child.wait();code=None;status='original_deadline_expired'
    dump(out/'status_v2.json',dict(status=status,exit_code=code,original_clock_preserved=True));print(a.stage,status,code)
