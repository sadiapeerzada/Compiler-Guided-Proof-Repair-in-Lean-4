"""Automatically perform reporting/QA/PDF work after genuine analysis is ready.

No generation, data selection, protocol amendment, commit or merge occurs here.
The agent reviews the resulting artifacts before the final Git delivery.
"""
from pathlib import Path
import datetime
import json
import os
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'data/final_study/v1';PYTHON=str(ROOT/'.venv/bin/python')

def main():
    while not all((BASE/'analysis'/name).exists() for name in ['results.json','qualitative_examples.json','condition_results.csv']):
        log=(BASE/'automatic_execution.log').read_text() if (BASE/'automatic_execution.log').exists() else ''
        if 'Traceback (most recent call last)' in log:raise RuntimeError('Actual experiment/analysis failed; final results cannot be invented.')
        time.sleep(10)
    protocol='configs/repair_experiment_local_v0.4.2.json'
    steps=[
        ('render',[PYTHON,'scripts/render_final_study.py','--protocol',protocol],ROOT,'render_final.log'),
        ('manuscript',[PYTHON,'paper/scripts/write_final_manuscript.py'],ROOT,'write_manuscript.log'),
        ('python_tests',[PYTHON,'-m','pytest','-q'],ROOT,'pytest_final.log'),
        ('lean_build',['lake','build'],ROOT/'lean_project','lake_build_final.log'),
        ('result_validation',[PYTHON,'scripts/verify_final_study_artifacts.py'],ROOT,'final_result_validation.log'),
        ('latex',[PYTHON,'paper/scripts/build_final_manuscript.py'],ROOT,'build_final_pdf.log'),
        ('reports',[PYTHON,'scripts/write_final_delivery_reports.py'],ROOT,'write_final_reports.log')]
    events=[]
    for name,command,cwd,filename in steps:
        log=BASE/filename
        if log.exists():raise ValueError('Refusing to replace prior finalization log: '+str(log))
        print('START',name,datetime.datetime.now(datetime.timezone.utc).isoformat(),flush=True)
        with log.open('w') as stream:result=subprocess.run(command,cwd=cwd,stdout=stream,stderr=subprocess.STDOUT)
        events.append({'step':name,'returncode':result.returncode,'log':str(log.relative_to(ROOT)),'finished_at':datetime.datetime.now(datetime.timezone.utc).isoformat()})
        (BASE/'finalization_steps.json').write_text(json.dumps(events,indent=2)+'\n')
        print('END',name,'exit',result.returncode,flush=True)
        if result.returncode:raise RuntimeError('Finalization failed: '+name+'; original log preserved.')
    print('TECHNICAL FINALIZATION COMPLETE; source/PDF review and final Git delivery remain.',flush=True)

if __name__=='__main__':main()
