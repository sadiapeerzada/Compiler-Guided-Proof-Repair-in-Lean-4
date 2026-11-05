"""AI-screened development gate and unchanged shared-predecessor C/D/E core."""
import copy,importlib.util,time,subprocess,signal
from study_common import *
from strict_verifier import StrictVerifier
from cde_verifier import CDEVerifier
from runtime_v2 import PhaseModelV2
from backend import RenderedTokenizer
from lean_adapter import live_environment

def gate():
    try:
        authorize('development_initial');authorize('development_repairs');frozen('development_CDE_v1.json')
        manifest=read(run_root()/'development_dataset_freeze.json');dataset=read(run_root()/'accepted_development.json')
        ensure(sha(run_root()/'accepted_development.json')==manifest['dataset_sha256'],'NO_GO_FREEZE: cohort changed')
        ensure(2<=len(dataset)<=20 and len({r['family'] for r in dataset})==len(dataset),'NO_GO_DATA: at least two distinct accepted canonical families required')
        accepted={r['id']:r for name in ('v3_ai_accepted_candidates.json','development_ai_accepted_candidates.json') for r in read(run_root()/name)}
        all_reviews={}
        for stage in ('v3_review_1','v3_review_2','development_review_1','development_review_2'):
            all_reviews[stage]={r['id']:r for r in rows(run_root()/stage/'reviews.jsonl')}
        formal=rows(run_root()/'strict_reference_verification.jsonl');v3_checks=rows(OLD/'v3/runs/20261104T163622Z_v3/generation/records.jsonl')
        for c in dataset:
            a=accepted[c['id']];ensure(a['status']=='AI_SCREENED_FORMALLY_VERIFIED','NO_GO_VALIDATION: missing AI acceptance');ensure(c['review_subject_sha256']==subject_hash(a),'NO_GO_VALIDATION: review subject mismatch')
            for key in ('nl_statement','expected_lean_statement','reference_proof','category','generation_provenance'):ensure(c[key]==a[key],'NO_GO_VALIDATION: mathematical subject changed')
            ensure(c['family']==a['canonical_family'],'NO_GO_VALIDATION: canonical donor family changed')
            ensure(text_hash(c['reference_proof'])==c['proof_sha256'],'NO_GO_VALIDATION: reference hash mismatch')
            check=any(r.get('candidate',{}).get('id')==c['id'] and r.get('verification',{}).get('success') is True and r['verification']['candidate_sha256']==c['proof_sha256'] for r in v3_checks) if c['id'].startswith('v3_') else any(r['id']==c['id'] and r['source_sha256']==c['proof_sha256'] and r['target_sha256']==c['statement_sha256'] and r['result']['success'] is True and r['result']['candidate_sha256']==c['proof_sha256'] for r in formal)
            ensure(check,'NO_GO_VALIDATION: no actual strict success')
            stages=('v3_review_1','v3_review_2') if c['id'].startswith('v3_') else ('development_review_1','development_review_2');evidence=[all_reviews[s][c['id']] for s in stages]
            ensure(evidence[0]['model']['family']!=evidence[1]['model']['family'],'NO_GO_VALIDATION: review families identical')
            for r in evidence:
                ensure(r['decision']=='ACCEPT' and r['subject_sha256']==subject_hash(a) and not r.get('parse_error'),'NO_GO_VALIDATION: unresolved review')
                ensure(read(HERE/r['source_call']/'completion.json')==r['record'],'NO_GO_VALIDATION: review not backed by actual completion')
                expected_model=protocol()['models']['R1' if r['reviewer']==1 else 'R2'];ensure(r['model']==expected_model and r['record']['metadata']['model']==expected_model['id'] and r['record']['metadata']['snapshot_revision']==expected_model['revision'],'NO_GO_VALIDATION: reviewer checkpoint identity changed')
                if c['id'].startswith('v3_'):
                    from review_protocol import parse_review
                else:
                    from fresh_review import parse_review
                actual=parse_review(r['record']);ensure(actual==r['review'] and actual['decision']=='ACCEPT','NO_GO_VALIDATION: raw review does not substantiate acceptance')
            from dataset_tools import screen
            flags=screen(dict(a,source_url='Local AI generation',license='Unassessed upstream rights',library_dependencies=[]))['automated_flags'];ensure(not flags,'NO_GO_VALIDATION: historical overlap flag')
            concerns=run_root()/'assistant_audit_concerns.json'
            if concerns.exists():ensure(not any(x['id']==c['id'] for x in read(concerns)),'NO_GO_VALIDATION: unresolved source-bound audit concern')
        return dict(status='READY_FOR_DEVELOPMENT',records=dataset,manifest=manifest)
    except (ValueError,FileNotFoundError,KeyError) as error:
        reason=str(error);status=next((x for x in ('NO_GO_DATA','NO_GO_VALIDATION','NO_GO_RESOURCES','NO_GO_FREEZE') if x in reason),'NO_GO_FREEZE');return dict(status=status,reason=reason)

class Backend:
    def __init__(self):
        state=gate();ensure(state['status']=='READY_FOR_DEVELOPMENT',state.get('reason','Development gate closed'));self.clients={};self.records=state['records'];self.tokenizer=None
        # Tokenizer only after the data/resource gate; no reference proofs in prompts.
        model=protocol()['models']['X'];path=Path.home()/'.cache/huggingface/hub'/model['cache_name']/'snapshots'/model['revision']
        from transformers import AutoTokenizer
        self.tokenizer=RenderedTokenizer(AutoTokenizer.from_pretrained(str(path),local_files_only=True,trust_remote_code=False))
    def generate(self,prompt,base_seed,context,folder):
        ensure(gate()['status']=='READY_FOR_DEVELOPMENT','Development gate changed')
        key=read(folder/'intent.json')['key'];stage='development_initial' if key['arm']=='A' else 'development_repairs'
        for c in self.records:ensure(c['reference_proof'] not in prompt,'Reference proof entered model prompt')
        if stage not in self.clients:
            for old in self.clients.values():old.close()
            self.clients[stage]=PhaseModelV2(stage,'development_CDE_v1.json')
        dump(run_root()/'development_active_stage.json',dict(stage=stage))
        record,inner=self.clients[stage].call(prompt,dict(outer_key=key,context=context),base_seed)
        dump(folder/'inner_call_binding.json',dict(stage=stage,inner_call=str(inner.relative_to(HERE)),model_generations=1 if record['status']=='completed' else None))
        ensure(record['status']=='completed','New unavailable model completion')
        return dict(content=record['content'],metadata=record['metadata'])
    def close(self):
        for client in self.clients.values():client.close()

def worker():
    state=gate();ensure(state['status']=='READY_FOR_DEVELOPMENT',state.get('reason','Gate closed'));p=read(run_root()/'development_protocol.json');live_environment(protocol()['environment']);out=run_root()/'development_experiment';out.mkdir(exist_ok=True)
    # Private module instance: add a strict leak exclusion without altering old files.
    spec=importlib.util.spec_from_file_location('final_development_core',LEGACY/'isolated_repair_runner.py');core=importlib.util.module_from_spec(spec);spec.loader.exec_module(core);original=core.matched_conditions
    def matched(row,*args,**kwargs):
        result=original(row,*args,**kwargs)
        if result['valid'] and any(row['reference_proof'] in item['prompt'] for item in result['conditions'].values()):return dict(valid=False,reason='reference_proof_leak_excluded',conditions={})
        return result
    core.matched_conditions=matched
    permit=dict(phase='development',protocol=p,protocol_sha256=sha(run_root()/'development_protocol.json'),source_lock_sha256=sha(HERE/'freezes/development_CDE_v1.json'),records=state['records'],authorization=dict(actor_kind='researcher_resource_authority',source='actual consolidated phases1–6 approval; not human mathematical adjudication',resource_limits=dict(max_calls=240,max_runtime_seconds=64800)),manifest={'development':{'sha256':state['manifest']['dataset_sha256']}})
    backend=Backend()
    try:core.run_core(permit,backend,CDEVerifier(),out,out)
    finally:backend.close()

def run():
    state=gate();dump(run_root()/'development_gate_status.json',{k:v for k,v in state.items() if k!='records'})
    if state['status']!='READY_FOR_DEVELOPMENT':print(state);return
    out=run_root()/'development_experiment';out.mkdir(exist_ok=True);clock_path=out/'overall_clock.json'
    if not clock_path.exists():dump(clock_path,dict(started_epoch=time.time(),max_runtime_seconds=64800),exclusive=True)
    with (out/'stdout.log').open('a') as stdout,(out/'stderr.log').open('a') as stderr:
        child=subprocess.Popen([sys.executable,str(HERE/'development_experiment.py'),'worker'],stdout=stdout,stderr=stderr,start_new_session=True)
        expired=None
        while child.poll() is None:
            deadline=read(clock_path)['started_epoch']+64800
            active=run_root()/'development_active_stage.json'
            if active.exists():
                stage=read(active)['stage'];c=read(run_root()/stage/'phase_clock.json');deadline=min(deadline,c['started_epoch']+c['max_runtime_seconds'])
            if time.time()>=deadline:os.killpg(child.pid,signal.SIGKILL);child.wait();expired='authorized_deadline_expired';break
            time.sleep(.5)
        dump(out/'status.json',dict(status=expired or ('finished' if child.returncode==0 else 'worker_failed'),exit_code=child.returncode))
    print(read(out/'status.json'))

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['status','run','worker']);a=p.parse_args()
    if a.mode=='status':print(gate())
    elif a.mode=='run':run()
    else:worker()
