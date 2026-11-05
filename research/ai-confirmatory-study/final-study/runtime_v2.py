"""Same pinned weights/config; optional frozen data-only snapshot view.

No remote Python is loaded. The unchanged strict local client still checks the
view contains no .py files and uses trust_remote_code=False and built-in MLX.
"""
from study_common import *
from local_runtime import PhaseModel

class PhaseModelV2(PhaseModel):
    def __init__(self,stage,freeze):
        spec,_=authorize(stage);model=protocol()['models'][spec['model_key']]
        view_manifest=HERE/'model_views'/f"{model['revision']}.json"
        if not view_manifest.exists():
            super().__init__(stage,freeze);return
        self.spec,auth=authorize(stage);frozen(freeze);self.freeze=freeze;self.stage=stage;self.p=protocol();self.model=model;self.client=None
        view=read(view_manifest);ensure(view['revision']==model['revision'] and view['model_id']==model['id'],'Wrong approved model view')
        self.clock=clock(stage);self.root=run_root()/stage
        self.snapshot=HERE/view['view_path']
        from local_llm_client import snapshot_inventory
        self.inventory=snapshot_inventory(self.snapshot)
        for name,entry in self.inventory['files'].items():ensure(entry['sha256']==view['included_files'][name]['sha256'],'View bytes differ from pinned original')
        path=self.root/'snapshot_inventory.json'
        if path.exists():ensure(read(path)==self.inventory,'Cached model view changed')
        else:dump(path,self.inventory,exclusive=True)
        limits=dict(max_total_calls=self.spec['max_calls'],max_initial_calls=self.spec['max_calls'],max_repair_calls=self.spec['max_calls'],max_run_calls=self.spec['max_calls'],max_input_tokens=4096,max_output_tokens=1200,max_runtime_seconds=self.spec['max_runtime_seconds'])
        self.store=RunStore(self.root/'calls',dict(stage=stage,run_id=self.p['run_id'],authorization_sha256=auth,freeze_sha256=sha(HERE/'freezes'/freeze)),limits)
        from transformers import AutoTokenizer
        self.tokenizer=AutoTokenizer.from_pretrained(str(self.snapshot),local_files_only=True,trust_remote_code=False)
