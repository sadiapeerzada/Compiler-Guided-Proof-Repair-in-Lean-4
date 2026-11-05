"""One persisted deadline per new phase; no retries or clock renewal."""
import subprocess,signal,argparse
from sprint_common import *
def run(stage,script,args):
    c=clock(stage);out=RUN/stage;status=out/'status.json'
    if status.exists():
        previous=read(status)
        if previous['status']=='finished':print(stage,'already finished');return
        ensure(previous['status']!='worker_failed','Diagnose worker failure before explicit resume')
        ensure(previous['status']!='authorized_deadline_expired','Deadline expired; no more calls')
    with (out/'stdout.log').open('a') as stdout,(out/'stderr.log').open('a') as stderr:
        child=subprocess.Popen([sys.executable,str(HERE/script),*args],stdout=stdout,stderr=stderr,start_new_session=True)
        try:code=child.wait(timeout=c['started_epoch']+c['max_runtime_seconds']-time.time());state='finished' if code==0 else 'worker_failed'
        except subprocess.TimeoutExpired:os.killpg(child.pid,signal.SIGKILL);child.wait();code=None;state='authorized_deadline_expired'
    dump(status,dict(status=state,exit_code=code,original_clock_preserved=True));print(stage,state,code,flush=True);ensure(state!='worker_failed','Worker needs diagnosis: '+stage)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('stage');p.add_argument('script');p.add_argument('args',nargs='*');a=p.parse_args();run(a.stage,a.script,a.args)
