"""Hard phase watchdog; original start/expiration persists across interruptions."""
import subprocess,signal,time,argparse
from study_common import *

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('stage');a=p.parse_args();spec,_=authorize(a.stage);c=clock(a.stage);out=run_root()/a.stage
    module='review_protocol.py' if spec['kind']=='review' else 'generation.py'
    command=[sys.executable,str(HERE/module),a.stage];remaining=c['started_epoch']+c['max_runtime_seconds']-time.time();ensure(remaining>0,'Deadline expired')
    with (out/'stdout.log').open('a') as stdout,(out/'stderr.log').open('a') as stderr:
        process=subprocess.Popen(command,stdout=stdout,stderr=stderr,start_new_session=True)
        try:code=process.wait(timeout=remaining);status='finished' if code==0 else 'worker_failed'
        except subprocess.TimeoutExpired:os.killpg(process.pid,signal.SIGKILL);process.wait();code=None;status='authorized_deadline_expired'
    dump(out/'status.json',dict(status=status,exit_code=code,clock_unchanged=True));print(a.stage,status,code)
