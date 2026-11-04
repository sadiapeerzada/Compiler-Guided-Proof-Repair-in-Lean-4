"""Lazy local model adapter. The production constructor rechecks the real gate."""
import importlib.metadata
import os
import sys
from pathlib import Path
from common import ROOT,ensure,sha

class RenderedTokenizer:
    def __init__(self,tokenizer):self.tokenizer=tokenizer
    def render(self,prompt):return self.tokenizer.apply_chat_template([{'role':'user','content':prompt}],tokenize=False,add_generation_prompt=True)
    def count(self,prompt):return len(self.tokenizer.encode(self.render(prompt),add_special_tokens=False))

class LocalBackend:
    def __init__(self,bundle,phase):
        from isolated_repair_validation import require_go
        self.permit=require_go(bundle,phase)  # Before tokenizer/weight imports or any model initialization.
        sys.path.insert(0,str(ROOT/'src'))
        from local_llm_client import snapshot_inventory
        from transformers import AutoTokenizer
        self.snapshot=Path(os.environ['CONFIRMATORY_MODEL_SNAPSHOT']).resolve()
        pins=self.permit['protocol']['model']
        ensure(self.snapshot.name==pins['revision'],'Wrong local model revision')
        self.inventory=snapshot_inventory(self.snapshot)
        expected=__import__('json').loads((ROOT/pins['inventory_path']).read_text())
        ensure(sha(ROOT/pins['inventory_path'])==pins['inventory_sha256'] and self.inventory==expected,'Frozen model/tokenizer/template/weight files differ')
        for package,version in self.permit['protocol']['runtime_packages'].items():ensure(importlib.metadata.version(package)==version,'Runtime version mismatch: '+package)
        tokenizer=AutoTokenizer.from_pretrained(str(self.snapshot),local_files_only=True,trust_remote_code=False)
        self.tokenizer=RenderedTokenizer(tokenizer);self.clients={}
    def generate(self,prompt,base_seed,context,folder):
        from isolated_repair_validation import require_go
        require_go(self.permit['bundle'],self.permit['phase'])
        from local_llm_client import LocalMLXClient
        p=self.permit['protocol']
        if base_seed not in self.clients:
            self.clients[base_seed]=LocalMLXClient(self.snapshot,self.inventory,model_id=p['model']['model_id'],seed=base_seed,max_context_tokens=p['decoding']['max_context_tokens'])
        client=self.clients[base_seed];client.trace_directory=folder/'stream'
        completion=client(prompt,max_tokens=p['budget']['output_tokens_per_call'],temperature=p['decoding']['temperature'],generation_context=context,retries=1)
        return dict(content=completion.content,metadata=completion.metadata)
