"""Audit real final-protocol pilot checkpoints, then autonomously execute held-out."""
import argparse
import datetime
import json
from pathlib import Path
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'eval'))
from final_study import BASE,read,sha,validate_protocol
from final_study_analysis import validate_run

def main(path):
    p=validate_protocol(path);p['_sha256']=sha(path);root=ROOT/p['output_root'];pilotroot=root/'development_pilot'/'2027'
    started=time.monotonic()
    while True:
        paths=[pilotroot/i/'manifest.json' for i in p['pilot_ids']]
        if all(x.exists() and read(x)['status'] in ('completed','incomplete') for x in paths):break
        if time.monotonic()-started>7200:raise RuntimeError('Pilot not finished within two hours; no held-out generation started.')
        time.sleep(5)
    audited=[]
    for mp in paths:
        m=read(mp);validate_run(m,p,expected_phase='development_pilot')
        if m['initial'] is None or not m['local_generation_confirmed'] or m['dataset_sha256']!=p['dataset_sha256']['development_pilot']:
            raise ValueError('Pilot lacks genuine local initial generation on the eligible development dataset')
        audited.append({'problem_id':m['problem_id'],'status':m['status'],'outcomes':{k:c['success'] for k,c in m['conditions'].items()},
                        'manifest':str(mp.relative_to(ROOT)),'sha256':sha(mp)})
    before={str(x):sha(x) for x in pilotroot.glob('*/*/intent.json')}
    # Actual resume invocation: finished checkpoints must not generate again.
    result=subprocess.run([str(ROOT/'.venv/bin/python'),str(ROOT/'scripts/run_final_study.py'),'--protocol',str(path),'--phase','development_pilot'],cwd=ROOT,capture_output=True,text=True)
    (BASE/'actual_pilot_resume_check.log').write_text(result.stdout+result.stderr)
    after={str(x):sha(x) for x in pilotroot.glob('*/*/intent.json')}
    if result.returncode or before!=after:raise ValueError('Actual pilot resume replayed a generation or failed')
    audit={'kind':'actual_ai_engineering_control_audit_not_supervisor_approval','phase':'development_pilot',
        'protocol_sha256':p['_sha256'],'controls_passed':True,'independent_human_audit':False,
        'approval_provenance':'student_reported_supervisor_substitutions; user_authorized_execution',
        'audited_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'actual_resume_generated_no_new_calls':True,
        'trajectories':audited,'meaning':'Controls/provenance passed, not a claim that all model proofs succeeded.'}
    (BASE/'pilot_audit.json').write_text(json.dumps(audit,indent=2)+'\n')
    launch={'kind':'preheldout_launch_record','protocol_sha256':p['_sha256'],'freeze_sha256':p['freeze_sha256'],
        'source_git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        'launched_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'expected_cases':60,'seeds':p['seeds'],
        'no_protocol_changes_after_heldout_start':True}
    if not (BASE/'heldout_launch.json').exists():(BASE/'heldout_launch.json').write_text(json.dumps(launch,indent=2)+'\n')
    print('Pilot controls and actual resume passed. Starting all frozen held-out cases.',flush=True)
    result=subprocess.run([str(ROOT/'.venv/bin/python'),str(ROOT/'scripts/run_final_study.py'),'--protocol',str(path),'--phase','heldout'],cwd=ROOT)
    if result.returncode:raise SystemExit(result.returncode)
    print('All held-out trajectories finished. Starting validated paired analysis.',flush=True)
    result=subprocess.run([str(ROOT/'.venv/bin/python'),str(ROOT/'eval/final_study_analysis.py'),'--protocol',str(path),'--output',str(BASE/'analysis')],cwd=ROOT)
    raise SystemExit(result.returncode)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--protocol',type=Path,required=True);main(p.parse_args().protocol.resolve())
