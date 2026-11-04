import gc
from common_v3 import *

class LocalPhase:
    def __init__(self,phase):
        self.spec,auth=authorize(phase);self.p=freeze_check();self.phase=phase
        self.model=self.p['models'][phase];self.client=None
        self.path=Path.home()/'.cache/huggingface/hub'/self.model['cache_name']/'snapshots'/self.model['revision']
        from local_llm_client import snapshot_inventory
        self.inventory=snapshot_inventory(self.path)
        out=root()/phase;out.mkdir(parents=True,exist_ok=True);inv=out/'snapshot_inventory.json'
        if inv.exists():ensure(read(inv)==self.inventory,'Model snapshot changed')
        else:dump(inv,self.inventory,exclusive=True)
        self.store=RunStore(out/'calls',dict(phase=phase,protocol_sha256=sha(HERE/'protocol_v3.json'),authorization_sha256=auth),dict(max_total_calls=10,max_initial_calls=10,max_repair_calls=10,max_run_calls=10,max_input_tokens=4096,max_output_tokens=1200,max_runtime_seconds=1800))
        from transformers import AutoTokenizer
        self.tokenizer=AutoTokenizer.from_pretrained(str(self.path),local_files_only=True,trust_remote_code=False)

    def call(self,index,prompt):
        authorize(self.phase);freeze_check()
        rendered=self.tokenizer.apply_chat_template([{'role':'user','content':prompt}],tokenize=False,add_generation_prompt=True)
        tokens=len(self.tokenizer.encode(rendered,add_special_tokens=False));ensure(tokens<=4096,'PROMPT_OVER_CAP_NO_CALL')
        key=dict(phase=self.phase,index=index,model_id=self.model['id'],model_revision=self.model['revision'],seed=self.p['base_seed'])
        def invoke(text,folder):
            from local_llm_client import LocalMLXClient
            if self.client is None:self.client=LocalMLXClient(self.path,self.inventory,model_id=self.model['id'],seed=self.p['base_seed'],max_context_tokens=8192)
            (folder/'stream').mkdir(exist_ok=True);self.client.trace_directory=folder/'stream'
            r=self.client(text,max_tokens=1200,temperature=.2,generation_context='V3/'+content_hash(key),retries=1)
            return dict(content=r.content,metadata=r.metadata)
        record,folder=self.store.call_once(key,prompt,tokens,1200,'initial' if self.phase=='generation' else 'repair',invoke)
        if record['status']=='completed':
            raw=record['content'].encode();path=folder/'raw_response.txt'
            if path.exists():ensure(path.read_bytes()==raw,'Raw response changed')
            else:
                with path.open('xb') as stream:stream.write(raw);stream.flush();os.fsync(stream.fileno())
        return record,folder

    def close(self):
        self.client=None;gc.collect()
        if 'mlx.core' in sys.modules:sys.modules['mlx.core'].clear_cache()
