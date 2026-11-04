"""One real local generation per durable intent, no provider retries or fallback."""
import gc,time
from v2_common import *
from checkpoint import RunStore

class Generator:
    def __init__(self):
        self.spec,authorization_sha=authorize('generation')
        self.protocol=frozen();self.model=self.protocol['generator'];self.client=None
        self.snapshot=Path.home()/'.cache/huggingface/hub'/self.model['cache_name']/'snapshots'/self.model['revision']
        from local_llm_client import snapshot_inventory
        self.inventory=snapshot_inventory(self.snapshot)
        ensure(self.inventory['snapshot_revision']==self.model['revision'],'Wrong snapshot')
        self.root=HERE/'runs'/self.protocol['run_id'];self.root.mkdir(parents=True,exist_ok=True)
        path=self.root/'model_snapshot_inventory.json'
        if path.exists():ensure(read(path)==self.inventory,'Snapshot changed')
        else:dump(path,self.inventory,exclusive=True)
        limits=dict(max_total_calls=10,max_initial_calls=10,max_repair_calls=0,max_run_calls=10,max_input_tokens=4096,max_output_tokens=1200,max_runtime_seconds=1800)
        self.store=RunStore(self.root/'calls',dict(stage='V2_generation',run_id=self.protocol['run_id'],protocol_sha256=sha(HERE/'protocol_v2.json'),authorization_sha256=authorization_sha),limits)
        from transformers import AutoTokenizer
        self.tokenizer=AutoTokenizer.from_pretrained(str(self.snapshot),local_files_only=True,trust_remote_code=False)

    def generate(self,index,prompt):
        authorize('generation');frozen()
        rendered=self.tokenizer.apply_chat_template([{'role':'user','content':prompt}],tokenize=False,add_generation_prompt=True)
        count=len(self.tokenizer.encode(rendered,add_special_tokens=False))
        ensure(count<=4096,'Prompt exceeds cap; no call issued')
        key=dict(stage='V2_generation',run_id=self.protocol['run_id'],index=index,seed=self.protocol['base_seed'],model_id=self.model['id'],model_revision=self.model['revision'])
        def call(text,folder):
            from local_llm_client import LocalMLXClient
            if self.client is None:self.client=LocalMLXClient(self.snapshot,self.inventory,model_id=self.model['id'],seed=self.protocol['base_seed'],max_context_tokens=8192)
            stream=folder/'stream';stream.mkdir(exist_ok=True)
            self.client.trace_directory=stream
            result=self.client(text,max_tokens=1200,temperature=self.protocol['temperature'],generation_context='V2_generation/'+content_hash(key),retries=1)
            return dict(content=result.content,metadata=result.metadata)
        return self.store.call_once(key,prompt,count,1200,'initial',call)

    def close(self):
        self.client=None;gc.collect()
        # Import only if actually initialized; avoid a second failed MLX import.
        if 'mlx.core' in sys.modules:sys.modules['mlx.core'].clear_cache()
