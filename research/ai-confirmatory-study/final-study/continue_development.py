"""Run the already authorized remaining development phases sequentially.

This does not generate or evaluate any confirmatory subjects. Failed workers stop
the chain for diagnosis. Re-entry skips completed phases without resetting clocks.
"""
import subprocess,time,argparse
from study_common import *

def command(args):
    result=subprocess.run([sys.executable,*[str(a) for a in args]])
    ensure(result.returncode==0,'Authorized phase command failed: '+str(args))

def stage(name,script):
    spec,_=authorize(name);folder=run_root()/name;status=folder/'status.json'
    if status.exists():
        state=read(status)
        if state['status']=='finished':print(name,'already finished',flush=True);return
        ensure(state['status']!='worker_failed','Worker needs diagnosis before resume: '+name)
        if state['status']=='authorized_deadline_expired':print(name,'deadline already expired; no further inference',flush=True);return
    c=clock(name);remaining=c['started_epoch']+c['max_runtime_seconds']-time.time()
    with (folder/'stdout.log').open('a') as stdout,(folder/'stderr.log').open('a') as stderr:
        child=subprocess.Popen([sys.executable,str(HERE/script),name],stdout=stdout,stderr=stderr,start_new_session=True)
        try:code=child.wait(timeout=remaining);state='finished' if code==0 else 'worker_failed'
        except subprocess.TimeoutExpired:
            import signal
            os.killpg(child.pid,signal.SIGKILL);child.wait();code=None;state='authorized_deadline_expired'
    dump(status,dict(status=state,exit_code=code,original_clock_preserved=True));print(name,state,code,flush=True)
    ensure(state!='worker_failed','Worker needs diagnosis: '+name)

def main(wait_generation):
    authorize('generation');status=run_root()/'generation/status.json'
    while not status.exists():
        ensure(wait_generation,'Generation has not completed')
        time.sleep(5)
    ensure(read(status)['status'] in ('finished','authorized_deadline_expired'),'Generation needs diagnosis before advancing')
    stage('reference_repair','reference_construction_v2.py')
    if not (run_root()/'fresh_verified.json').exists():command([HERE/'prepare_cohorts.py','fresh-review'])
    stage('development_review_1','fresh_review.py');stage('development_review_2','fresh_review.py')
    command([HERE/'adjudication.py','development'])
    if not (run_root()/'accepted_development.json').exists():command([HERE/'prepare_cohorts.py','development'])
    if not (HERE/'freezes/development_CDE_v1.json').exists():command([HERE/'freeze_development.py'])
    command([HERE/'development_experiment.py','run'])
    dump(run_root()/'development_chain_status.json',dict(status='AUTHORIZED_DEVELOPMENT_CHAIN_FINISHED',confirmatory_inference=False))
    print('Authorized development chain finished; inspect actual stage results, not code existence',flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--wait-generation',action='store_true');main(p.parse_args().wait_generation)
