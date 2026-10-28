"""New-policy invariants and synthetic checkpoint/control unit tests; no model calls."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import sys
import pytest
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from final_study import BASE,validate_freeze,sha
from model_client import CompletionResult
from verify import VerificationResult

def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def copied(tmp_path):
    for file in ['freeze.json','ai_eligibility_policy.json','adjudications.json','development.json','test.json','approvals/student_reported.json']:
        target=tmp_path/file;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(BASE/file,target)
    return tmp_path

def test_ai_policy_validates_without_inventing_human_reviews():
    report=validate_freeze();assert report['eligible_counts']=={'development':15,'test':60};assert report['independent_human_reviews']==0

@pytest.mark.parametrize('field,value',[('semantic_label','uncertain'),('human_review_completed',True),('family','binomial_identities')])
def test_policy_rejects_uncertainty_human_mislabel_and_family_leakage(tmp_path,field,value):
    base=copied(tmp_path);p=base/'test.json';r=json.loads(p.read_text());r[0]['study_eligibility'][field]=value;p.write_text(json.dumps(r))
    freeze=json.loads((base/'freeze.json').read_text());freeze['splits']['test']['sha256']=sha(p);(base/'freeze.json').write_text(json.dumps(freeze))
    with pytest.raises(ValueError):validate_freeze(base)

def test_checkpoint_reuses_initial_and_keeps_blind_guided_feedback_isolated(tmp_path,monkeypatch):
    runner=module('synthetic_final_runner',ROOT/'scripts/run_final_study.py');monkeypatch.setattr(runner,'ROOT',tmp_path)
    for name in ['initial','blind','guided']:
        (tmp_path/(name+'.txt')).write_text('{nl_statement}\n{theorem_statement}' if name=='initial' else '{theorem_statement}\n{previous_candidate}\n{feedback}')
    calls=[]
    class Client:
        def __call__(self,prompt,**kw):
            calls.append((prompt,kw['generation_context']));return CompletionResult('theorem test : True := by trivial',{'prompt_tokens':1,'completion_tokens':1,'latency_seconds':0.01})
    n=[0]
    def verify(code,*args,**kwargs):
        n[0]+=1;ok=n[0] in [3,5]
        return VerificationResult(ok,errors=[] if ok else ['SYNTHETIC_DIAGNOSTIC_'+str(n[0])],exit_code=0 if ok else 1,
            candidate_sha256=hashlib.sha256(code.encode()).hexdigest(),diagnostic_state='available',diagnostics=[{'severity':'error','kind':'test_fixture','data':'SYNTHETIC_DIAGNOSTIC_'+str(n[0])}])
    monkeypatch.setattr(runner,'check_lean_file_detailed',verify)
    p={'_sha256':'SYNTHETIC','dataset_sha256':{'development_pilot':'SYNTHETIC'},'prompts':{k:k+'.txt' for k in ['initial','blind','guided']},'verifier_timeout_seconds':180}
    r={'id':'synthetic','nl_statement':'Synthetic test','expected_lean_statement':'theorem test : True'}
    result=runner.trajectory(Client(),p,r,'development_pilot',2027,tmp_path/'runs')
    assert result['conditions']['A']['success'] is False and result['conditions']['B']['success'] and result['conditions']['C']['success']
    assert all('SYNTHETIC_DIAGNOSTIC' not in prompt for prompt,context in calls if '/B' in context)
    guided=[prompt for prompt,context in calls if '/C' in context]
    assert 'SYNTHETIC_DIAGNOSTIC_1' in guided[0] and 'SYNTHETIC_DIAGNOSTIC_4' in guided[1]
    count=len(calls);runner.trajectory(Client(),p,r,'development_pilot',2027,tmp_path/'runs');assert len(calls)==count

def test_generation_intent_without_completion_is_never_replayed(tmp_path,monkeypatch):
    runner=module('synthetic_intent_runner',ROOT/'scripts/run_final_study.py');monkeypatch.setattr(runner,'ROOT',tmp_path)
    run=tmp_path/'run';folder=run/'initial';folder.mkdir(parents=True);(folder/'intent.json').write_text('{}')
    def forbidden(*args,**kwargs):raise AssertionError('Interrupted call was replayed')
    with pytest.raises(runner.InterruptedGeneration):runner.step(forbidden,{'_sha256':'SYNTHETIC'},run,{'id':'synthetic'},'development_pilot',2027,'initial','Synthetic prompt')
