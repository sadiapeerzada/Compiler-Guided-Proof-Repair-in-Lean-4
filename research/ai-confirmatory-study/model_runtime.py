"""Pinned real local clients. Construction checks authorization before any weights."""
import gc
import os
import sys
import time
from pathlib import Path
from ai_common import HERE,ROOT,read,save,sha,ensure,digest
from resource_gate import authorize
from checkpoint import RunStore

class AuthorizedLocalModel:
    def __init__(self,stage,model_key,run_root):
        spec,auth_sha=authorize(stage)
        protocol=read(HERE/'ai_protocol_v1.json');model=protocol['models'][model_key]
        ensure(protocol['source_lock_sha256']==sha(HERE/'source_lock.json'),'AI source lock reference changed')
        for rel,expected in read(HERE/'source_lock.json')['files'].items():ensure(sha(ROOT/rel)==expected,'Frozen AI implementation changed')
        self.stage,self.spec,self.model,self.protocol=stage,spec,model,protocol
        self.snapshot=Path.home()/'.cache/huggingface/hub'/model['cache_name']/'snapshots'/model['revision']
        sys.path.insert(0,str(ROOT/'src'))
        from local_llm_client import snapshot_inventory,LocalMLXClient
        actual=snapshot_inventory(self.snapshot)
        ensure(actual['snapshot_revision']==model['revision'],'Wrong cached model')
        # The first authorized stage captures every actual weight/tokenizer hash before generating.
        manifest=run_root/(model_key+'_snapshot_inventory.json')
        if manifest.exists():ensure(read(manifest)==actual,'Snapshot bytes changed during the run')
        else:save(manifest,actual,exclusive=True)
        self.inventory=actual;self.client=None;self.started=time.time();self.run_root=run_root
        limits=dict(max_total_calls=spec['max_calls'],max_initial_calls=spec['max_calls'],max_repair_calls=spec['max_calls'],max_input_tokens=spec['max_input_tokens'],max_output_tokens=spec['max_output_tokens'],max_runtime_seconds=spec['max_runtime_seconds'],max_run_calls=spec['max_calls'])
        self.store=RunStore(run_root/'calls',dict(stage=stage,model=model['id'],revision=model['revision'],protocol_sha256=sha(HERE/'ai_protocol_v1.json'),authorization_sha256=auth_sha),limits)
    def generate(self,prompt,seed,key):
        authorize(self.stage)
        from transformers import AutoTokenizer
        tok=AutoTokenizer.from_pretrained(str(self.snapshot),local_files_only=True,trust_remote_code=False)
        rendered=tok.apply_chat_template([{'role':'user','content':prompt}],tokenize=False,add_generation_prompt=True)
        count=len(tok.encode(rendered,add_special_tokens=False))
        ensure(count<=self.spec['max_input_tokens'],'Prompt exceeds authorized budget; no inference issued')
        def real_call(text,folder):
            from local_llm_client import LocalMLXClient
            if self.client is None or self.client.seed!=seed:
                self.close();self.client=LocalMLXClient(self.snapshot,self.inventory,model_id=self.model['id'],seed=seed,max_context_tokens=8192)
            self.client.trace_directory=folder/'stream'
            r=self.client(text,max_tokens=self.spec['max_output_tokens'],temperature=self.protocol['temperature'],generation_context='ai-study/'+digest([self.stage,key]),retries=1)
            return dict(content=r.content,metadata=r.metadata)
        record,folder=self.store.call_once(dict(stage=self.stage,key=key,seed=seed,model_id=self.model['id'],model_revision=self.model['revision']),prompt,count,self.spec['max_output_tokens'],'initial',real_call)
        return record,folder
    def close(self):
        self.client=None;gc.collect()
        try:
            import mlx.core as mx
            mx.clear_cache()
        except ImportError:pass
