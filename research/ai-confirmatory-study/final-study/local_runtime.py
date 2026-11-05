"""Fresh phase-local budgets; permission and freeze checked before model loading."""
import gc
from study_common import *

class PhaseModel:
    def __init__(self,stage,freeze):
        self.spec,auth=authorize(stage);frozen(freeze);self.freeze=freeze;self.stage=stage;self.p=protocol();self.model=self.p['models'][self.spec['model_key']];self.client=None
        self.clock=clock(stage);self.root=run_root()/stage
        self.snapshot=Path.home()/'.cache/huggingface/hub'/self.model['cache_name']/'snapshots'/self.model['revision']
        from local_llm_client import snapshot_inventory
        self.inventory=snapshot_inventory(self.snapshot)
        path=self.root/'snapshot_inventory.json'
        if path.exists():ensure(read(path)==self.inventory,'Cached model bytes changed')
        else:dump(path,self.inventory,exclusive=True)
        limits=dict(max_total_calls=self.spec['max_calls'],max_initial_calls=self.spec['max_calls'],max_repair_calls=self.spec['max_calls'],max_run_calls=self.spec['max_calls'],max_input_tokens=4096,max_output_tokens=1200,max_runtime_seconds=self.spec['max_runtime_seconds'])
        self.store=RunStore(self.root/'calls',dict(stage=stage,run_id=self.p['run_id'],authorization_sha256=auth,freeze_sha256=sha(HERE/'freezes'/freeze)),limits)
        from transformers import AutoTokenizer
        self.tokenizer=AutoTokenizer.from_pretrained(str(self.snapshot),local_files_only=True,trust_remote_code=False)

    def call(self,prompt,key,seed):
        authorize(self.stage);frozen(self.freeze);clock(self.stage)
        rendered=self.tokenizer.apply_chat_template([{'role':'user','content':prompt}],tokenize=False,add_generation_prompt=True);count=len(self.tokenizer.encode(rendered,add_special_tokens=False))
        ensure(count<=4096,'PROMPT_OVER_CAP_NO_CALL')
        call_key=dict(stage=self.stage,key=key,seed=seed,model_id=self.model['id'],model_revision=self.model['revision'])
        def invoke(text,folder):
            dump(folder/'call_started.json',dict(epoch=time.time(),phase_clock=self.clock,stage=self.stage),exclusive=True)
            from local_llm_client import LocalMLXClient
            if self.client is None or self.client.seed!=seed:
                self.close();self.client=LocalMLXClient(self.snapshot,self.inventory,model_id=self.model['id'],seed=seed,max_context_tokens=8192)
            (folder/'stream').mkdir(exist_ok=True);self.client.trace_directory=folder/'stream'
            result=self.client(text,max_tokens=1200,temperature=.2,generation_context='final-study/'+content_hash(call_key),retries=1)
            dump(folder/'call_finished.json',dict(epoch=time.time(),stage=self.stage),exclusive=True)
            return dict(content=result.content,metadata=result.metadata)
        record,folder=self.store.call_once(call_key,prompt,count,1200,'initial',invoke)
        if record['status']=='completed':raw_write(folder/'raw_response.txt',record['content'].encode())
        return record,folder

    def close(self):
        self.client=None;gc.collect()
        if 'mlx.core' in sys.modules:sys.modules['mlx.core'].clear_cache()
