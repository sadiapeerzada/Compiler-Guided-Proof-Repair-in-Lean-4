"""Advance permitted stages only from actual eligibility/evaluation evidence."""
import subprocess,argparse
from sprint_common import *
def command(*args):subprocess.run([sys.executable,*map(str,args)],check=True)
def main(wait=False):
    status=RUN/'development_generation/status.json'
    while not status.exists() or read(status)['status']=='running':
        ensure(wait,'Development construction still running');time.sleep(2)
    ensure(read(status)['status'] in ('finished','authorized_deadline_expired'),'Diagnose generation worker failure first')
    if not (HERE/'freezes/development_reviews.json').exists():command(HERE/'reviews.py','prepare','development')
    subjects=read(RUN/'development_review_input/fresh_verified.json')
    if subjects:
        for i in (1,2):command(HERE/'run_phase.py',f'development_review_{i}','reviews.py','review','development',i)
    command(HERE/'reviews.py','adjudicate','development')
    if not (RUN/'development_selected.json').exists():command(HERE/'reviews.py','select','development')
    command(HERE/'evaluate.py','run','development')
    gate=read(RUN/'development_evaluation_gate.json')
    if gate['status']!='GO':dump(RUN/'chain_status.json',dict(status='BLOCKED',reason=gate['reason'],test_inference_calls=0));print('Sprint blocked at genuine development-data gate',flush=True);return
    out=RUN/'development_experiment';ensure(read(out/'status.json')['status']=='finished','Development execution needs diagnosis')
    # Construction of the test stream is a separate prospective step after real
    # paired development data; never manufacture a GO or run it from code alone.
    exports=list((out/'exports').glob('*/analysis.json'));ensure(exports,'No actual development export');analysis=read(max(exports,key=lambda p:p.stat().st_mtime))
    if not any(c['complete_pairs'] for c in analysis.get('comparisons',[])):
        dump(RUN/'chain_status.json',dict(status='BLOCKED',reason='No genuine matched development C/D/E comparisons; test-side protocol not validated',test_inference_calls=0));return
    dump(RUN/'development_ready_for_locked_test.json',dict(status='REAL_DEVELOPMENT_COMPARISONS_RECORDED',analysis=analysis,requires_prospective_disjoint_test_construction=True));print('Real development comparisons recorded; finalize the locked test-side stream',flush=True)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--wait',action='store_true');a=p.parse_args();main(a.wait)
