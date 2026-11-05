"""Strong AI-only scoped gate; reuse the unchanged shared-predecessor C/D/E core."""
import copy,importlib.util,subprocess,signal,argparse
from sprint_common import *
from reviews import evidence
from study_common import subject_hash
from fresh_review import parse_review
from cde_verifier import CDEVerifier
from backend import RenderedTokenizer
from lean_adapter import live_environment

def gate(scope):
    data=read(RUN/(scope+'_selected.json'));manifest=read(RUN/(scope+'_dataset_freeze.json'));target=16 if scope=='development' else 32
    ensure(sha(RUN/(scope+'_selected.json'))==manifest['dataset_sha256'],'Cohort changed')
    ensure(2<=len(data)<=target and len({c['canonical_family'] for c in data})==len(data),'NO_GO_DATA: two distinct accepted families required; no relabeling')
    if scope=='test':ensure(len(data)==32,'NO_GO_SAMPLE: locked32-family test target unmet')
    reviews=[{r['id']:r for r in rows(RUN/f'{scope}_review_{i}/reviews.jsonl')} for i in (1,2)]
    for c in data:
        ensure(not any(x['id']==c['id'] for x in read(HERE/'mathematical_concerns.json')['items']),'Unresolved source-bound critical mathematical concern')
        ensure(c['status']=='AI_SCREENED_FORMALLY_VERIFIED' and evidence(scope,c),'No genuine proof/acceptance evidence')
        ensure(text_hash(c['reference_proof'])==c['proof_sha256'],'Reference source changed')
        if c.get('reused_qualified_development'):continue
        rs=[m[c['id']] for m in reviews];ensure(rs[0]['model']['family']!=rs[1]['model']['family'],'Same review family')
        for r in rs:ensure(r['subject_sha256']==subject_hash(c) and r['decision']=='ACCEPT' and not r.get('parse_error') and read(HERE/r['source_call']/'completion.json')==r['record'] and parse_review(r['record'])==r['review'],'No two actual qualified reviews')
    return data,manifest

def prepare(scope):
    try:data,manifest=gate(scope)
    except (ValueError,KeyError,FileNotFoundError) as error:
        dump(RUN/(scope+'_evaluation_gate.json'),dict(status='BLOCKED',reason=str(error)));print(scope,'evaluation BLOCKED:',error,flush=True);return False
    a=read(HERE/'resource_authorization.json');p=copy.deepcopy(read(OLD/'protocol.json')['legacy_CDE_protocol']);initial=a['stages'][scope+'_initial'];repair=a['stages'][scope+'_repairs'];model=a['models']['X'];p['model'].update(model_id=model['id'],revision=model['revision']);p['seeds']=read(HERE/'family_schedule.json')['seeds'][scope+'_eval'];p['budget'].update(max_total_calls=initial['max_calls']+repair['max_calls'],max_initial_calls=initial['max_calls'],max_repair_calls=repair['max_calls'],input_tokens_per_call=4096,output_tokens_per_call=1200,max_runtime_seconds=initial['max_runtime_seconds']+repair['max_runtime_seconds']);p['lean']['timeout_seconds']=180;p['study']='New completion sprint '+scope;p['status']='FROZEN_BEFORE_EVALUATION';p['sample_size']={scope:len(data)};p['statistics']['sample_precision']='Exploratory actual theorem/family count; no power guarantee';p['validation_gate']='Genuine dual-AI/rigid-check gate; never human approval';p['source_control']='Model cache released uniformly before every Lean check; actual derived RNG streams differ across prompts/arms'
    dump(RUN/(scope+'_protocol.json'),p,exclusive=True)
    files=[HERE/x for x in ('evaluate.py','reviews.py','sprint_common.py','resource_authorization.json','proposal_options.json','COMPUTE_PROPOSAL.md','family_schedule.json','mathematical_concerns.json')]+[RUN/(scope+'_selected.json'),RUN/(scope+'_dataset_freeze.json'),RUN/(scope+'_protocol.json'),RUN/(scope+'_review_input/formal_checks_snapshot.json'),RUN/(scope+'_ai_accepted.json')]+[LEGACY/x for x in ('isolated_repair_runner.py','matching.py','paired_analysis.py','checkpoint.py','common.py','lean_adapter.py','backend.py')]+[OLD/x for x in ('cde_verifier.py','rigid_verifier.py','strict_verifier.py','study_common.py','fresh_review.py','review_protocol.py')]+[ROOT/'src/verify.py',ROOT/'src/local_llm_client.py']
    for i in (1,2):
        path=RUN/f'{scope}_review_{i}/reviews.jsonl'
        if path.exists():files.append(path)
    freeze(scope+'_evaluation.json',files,status='FROZEN_BEFORE_ANY_EVALUATION_OUTCOME',scope=scope,actual_types=len(data),independent_families=len(data),gold_proofs_not_model_inputs=True)
    dump(RUN/(scope+'_evaluation_gate.json'),dict(status='GO',scope=scope,dataset_sha256=manifest['dataset_sha256'],source_freeze_sha256=sha(HERE/'freezes'/(scope+'_evaluation.json'))),exclusive=True);return True

def core_module():
    spec=importlib.util.spec_from_file_location('sprint_private_CDE_core',LEGACY/'isolated_repair_runner.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def permit(scope):
    data,manifest=gate(scope);frozen(scope+'_evaluation.json');p=read(RUN/(scope+'_protocol.json'));a=read(HERE/'resource_authorization.json')
    return dict(phase=scope,protocol=p,protocol_sha256=sha(RUN/(scope+'_protocol.json')),source_lock_sha256=sha(HERE/'freezes'/(scope+'_evaluation.json')),records=[dict(c,family=c['canonical_family']) for c in data],manifest={scope:{'sha256':manifest['dataset_sha256']}},authorization=dict(actor_kind='researcher_resource_authority',source='actual fresh expanded1728-call approval; AI-only mathematical gate',resource_limits=dict(max_calls=a['stages'][scope+'_initial']['max_calls']+a['stages'][scope+'_repairs']['max_calls'],max_runtime_seconds=a['stages'][scope+'_initial']['max_runtime_seconds']+a['stages'][scope+'_repairs']['max_runtime_seconds'])))

class Backend:
    def __init__(self,scope):
        self.scope=scope;self.p=permit(scope);self.clients={};m=read(HERE/'resource_authorization.json')['models']['X']
        from transformers import AutoTokenizer
        self.tokenizer=RenderedTokenizer(AutoTokenizer.from_pretrained(str(Path.home()/'.cache/huggingface/hub'/m['cache_name']/'snapshots'/m['revision']),local_files_only=True,trust_remote_code=False))
    def generate(self,prompt,seed,context,folder):
        permit(self.scope);key=read(folder/'intent.json')['key'];stage=self.scope+('_initial' if key['arm']=='A' else '_repairs')
        for c in self.p['records']:ensure(c['reference_proof'] not in prompt,'Gold proof leak')
        if stage not in self.clients:
            for old in self.clients.values():old.close()
            self.clients[stage]=Model(stage,self.scope+'_evaluation.json')
        dump(RUN/(self.scope+'_active_evaluation_stage.json'),dict(stage=stage));r,inner=self.clients[stage].call(prompt,dict(outer_key=key,context=context),seed,release=True)
        dump(folder/'inner_call_binding.json',dict(stage=stage,inner_call=str(inner.relative_to(HERE))))
        ensure(r['status']=='completed','New unavailable evaluation generation');return dict(content=r['content'],metadata=r['metadata'])
    def close(self):
        for m in self.clients.values():m.close()

def worker(scope):
    p=permit(scope);live_environment(read(OLD/'protocol.json')['environment']);core=core_module();original=core.matched_conditions
    def matched(row,*args,**kwargs):
        r=original(row,*args,**kwargs)
        if r['valid'] and any(c['reference_proof'] in item['prompt'] for c in p['records'] for item in r['conditions'].values()):return dict(valid=False,reason='gold_reference_leak_excluded',conditions={})
        return r
    def diagnostic(record,candidate):
        if record.get('success') is not False or record.get('failure_kind')!='compiler_error':return None
        from matching import diagnostic_payload
        return diagnostic_payload(record,candidate)
    core.matched_conditions=matched;core.diagnostic_payload=diagnostic;backend=Backend(scope);out=RUN/(scope+'_experiment')
    try:core.run_core(p,backend,CDEVerifier(),out,out)
    finally:backend.close()

def run(scope):
    if not (RUN/(scope+'_evaluation_gate.json')).exists():
        if not prepare(scope):return
    if read(RUN/(scope+'_evaluation_gate.json'))['status']!='GO':return
    p=permit(scope);out=RUN/(scope+'_experiment');out.mkdir(exist_ok=True);cp=out/'overall_clock.json';limit=p['authorization']['resource_limits']['max_runtime_seconds']
    if not cp.exists():dump(cp,dict(started_epoch=time.time(),max_runtime_seconds=limit),exclusive=True)
    with (out/'stdout.log').open('a') as stdout,(out/'stderr.log').open('a') as stderr:
        child=subprocess.Popen([sys.executable,str(HERE/'evaluate.py'),'worker',scope],stdout=stdout,stderr=stderr,start_new_session=True);state=None
        while child.poll() is None:
            deadline=read(cp)['started_epoch']+limit;active=RUN/(scope+'_active_evaluation_stage.json')
            if active.exists():
                s=read(active)['stage'];c=read(RUN/s/'phase_clock.json');deadline=min(deadline,c['started_epoch']+c['max_runtime_seconds'])
            if time.time()>=deadline:os.killpg(child.pid,signal.SIGKILL);child.wait();state='authorized_deadline_expired';break
            time.sleep(.5)
        dump(out/'status.json',dict(status=state or ('finished' if child.returncode==0 else 'worker_failed'),exit_code=child.returncode))
    print(scope,'evaluation',read(out/'status.json'),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['run','worker']);p.add_argument('scope',choices=['development','test']);a=p.parse_args();worker(a.scope) if a.action=='worker' else run(a.scope)
