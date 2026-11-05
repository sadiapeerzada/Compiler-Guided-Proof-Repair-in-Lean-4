"""New scope only; reuse existing serialization/checkpoint/client primitives."""
import sys,os,json,time,hashlib
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];OLD=HERE.parent/'final-study';LEGACY=ROOT/'research/confirmatory-study'
sys.path.insert(0,str(OLD));sys.path.insert(0,str(LEGACY));sys.path.insert(0,str(ROOT/'src'))
from common import read,dump,sha,text_hash,content_hash,ensure
from checkpoint import RunStore
RUN=HERE/'runs'/'expanded_v1'
def rows(path):return [json.loads(x) for x in Path(path).read_text().splitlines() if x] if Path(path).exists() else []
def append(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('a') as f:f.write(json.dumps(value,sort_keys=True,ensure_ascii=False)+'\n');f.flush();os.fsync(f.fileno())
def authorize(stage):
    a=read(HERE/'resource_authorization.json');ensure(a['status']=='AUTHORIZED' and a['source']=='direct_user_reply' and a['exact_user_instruction']=='Expanded exploratory — 1,728 calls (Recommended)','NO_GO_RESOURCES')
    ensure(a['proposal_sha256']==sha(HERE/'COMPUTE_PROPOSAL.md'),'Approved proposal changed');ensure(stage in a['stages'],'Stage not approved')
    planned=read(HERE/'proposal_options.json');option=planned['options'][a['selected_option']]
    ensure(a['stages']==option['stages'] and a['models']==planned['models'] and sum(s['max_calls'] for s in a['stages'].values())==1728,'Approved scope/model caps changed')
    if stage.startswith('test_'):ensure((RUN/'test_construction_go.json').exists() and read(RUN/'test_construction_go.json')['status']=='GO','NO_GO_TEST: development comparisons/prospective test freeze required')
    if stage.endswith(('_initial','_repairs')):
        scope=stage.split('_')[0];p=RUN/(scope+'_evaluation_gate.json');ensure(p.exists() and read(p)['status']=='GO','NO_GO_DATA: evaluation gate closed')
    return a['stages'][stage],a
def clock(stage):
    spec,_=authorize(stage);p=RUN/stage/'phase_clock.json'
    if not p.exists():dump(p,dict(started_epoch=time.time(),max_runtime_seconds=spec['max_runtime_seconds']),exclusive=True)
    c=read(p);ensure(c['max_runtime_seconds']==spec['max_runtime_seconds'] and time.time()<c['started_epoch']+c['max_runtime_seconds'],'Original phase deadline expired; do not reset');return c
def frozen(name):
    m=read(HERE/'freezes'/name)
    for rel,h in m['files'].items():ensure(sha(ROOT/rel)==h,'Frozen source/input changed: '+rel)
    return m
def freeze(name,paths,**extra):
    dump(HERE/'freezes'/name,dict(files={str(Path(p).relative_to(ROOT)):sha(p) for p in paths},**extra),exclusive=True)

class Model:
    def __init__(self,stage,lock):
        self.spec,a=authorize(stage);frozen(lock);self.stage=stage;self.lock=lock;self.model=a['models'][self.spec['model_key']];self.client=None;self.c=clock(stage);self.out=RUN/stage
        model=self.model;view=OLD/'model_views'/(model['revision']+'.json')
        self.snapshot=OLD/read(view)['view_path'] if view.exists() else Path.home()/'.cache/huggingface/hub'/model['cache_name']/'snapshots'/model['revision']
        from local_llm_client import snapshot_inventory
        self.inventory=snapshot_inventory(self.snapshot)
        if view.exists():
            for name,item in self.inventory['files'].items():ensure(item['sha256']==read(view)['included_files'][name]['sha256'],'Model view bytes changed')
        inventory=self.out/'snapshot_inventory.json'
        if inventory.exists():ensure(read(inventory)==self.inventory,'Model bytes changed')
        else:dump(inventory,self.inventory,exclusive=True)
        cap=self.spec['max_calls'];self.store=RunStore(self.out/'calls',dict(stage=stage,authorization_sha256=sha(HERE/'resource_authorization.json'),source_freeze_sha256=sha(HERE/'freezes'/lock)),dict(max_total_calls=cap,max_initial_calls=cap,max_repair_calls=cap,max_run_calls=cap,max_input_tokens=4096,max_output_tokens=1200,max_runtime_seconds=self.spec['max_runtime_seconds']))
        from transformers import AutoTokenizer
        self.tokenizer=AutoTokenizer.from_pretrained(str(self.snapshot),local_files_only=True,trust_remote_code=False)
    def call(self,prompt,key,seed,release=False):
        authorize(self.stage);frozen(self.lock);clock(self.stage)
        rendered=self.tokenizer.apply_chat_template([{'role':'user','content':prompt}],tokenize=False,add_generation_prompt=True);count=len(self.tokenizer.encode(rendered,add_special_tokens=False));ensure(count<=4096,'PROMPT_OVER_CAP_NO_CALL')
        call_key=dict(stage=self.stage,key=key,seed=seed,model_id=self.model['id'],model_revision=self.model['revision'])
        def invoke(text,folder):
            dump(folder/'call_started.json',dict(epoch=time.time(),phase_clock=self.c),exclusive=True)
            from local_llm_client import LocalMLXClient
            if self.client is None or self.client.seed!=seed:self.close();self.client=LocalMLXClient(self.snapshot,self.inventory,model_id=self.model['id'],seed=seed,max_context_tokens=8192)
            (folder/'stream').mkdir(exist_ok=True);self.client.trace_directory=folder/'stream'
            r=self.client(text,max_tokens=1200,temperature=.2,generation_context='completion-sprint/'+content_hash(call_key),retries=1)
            dump(folder/'call_finished.json',dict(epoch=time.time()),exclusive=True);return dict(content=r.content,metadata=r.metadata)
        cp,folder=self.store.call_once(call_key,prompt,count,1200,'initial',invoke)
        if cp['status']=='completed':
            p=folder/'raw_response.txt'
            if p.exists():ensure(p.read_bytes()==cp['content'].encode(),'Raw response changed')
            else:p.write_bytes(cp['content'].encode())
        if release:self.close()
        return cp,folder
    def close(self):
        import gc
        self.client=None;gc.collect()
        if 'mlx.core' in sys.modules:sys.modules['mlx.core'].clear_cache()
