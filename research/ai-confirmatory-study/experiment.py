"""AI-only approval adapter reusing the unchanged shared-predecessor runner."""
from pathlib import Path
from ai_common import HERE,read,save,sha,digest,ensure
from ai_gate import require_ready
from model_runtime import AuthorizedLocalModel
from backend import RenderedTokenizer
from isolated_repair_runner import run_core
from lean_adapter import LeanVerifier,live_environment

class AIExperimentBackend:
    def __init__(self,phase,root):
        state=require_ready(phase)
        self.phase=phase;self.model=AuthorizedLocalModel(phase,'experiment',root/'model_calls')
        from transformers import AutoTokenizer
        self.tokenizer=RenderedTokenizer(AutoTokenizer.from_pretrained(str(self.model.snapshot),local_files_only=True,trust_remote_code=False))
    def generate(self,prompt,base_seed,context,folder):
        require_ready(self.phase)
        record,_=self.model.generate(prompt,base_seed,['experiment',context])
        ensure(record['status']=='completed','Real model call unavailable; no replacement inference')
        return dict(content=record['content'],metadata=record['metadata'])

def execute(phase):
    state=require_ready(phase);root=HERE/'runs'/phase
    protocol=state['protocol']['experiment'];live_environment(protocol)
    permit=dict(phase=phase,protocol=protocol,protocol_sha256=sha(HERE/'ai_protocol_v1.json'),source_lock_sha256=sha(HERE/'source_lock.json'),records=state['records'],authorization=dict(actor_kind='researcher_resource_authority',source='actual session authorization; not human benchmark adjudication',resource_limits=dict(max_calls=state['resource_limits']['max_calls'],max_runtime_seconds=state['resource_limits']['max_runtime_seconds'])),manifest={phase:dict(sha256=digest(state['records']))})
    backend=AIExperimentBackend(phase,root)
    try:return run_core(permit,backend,LeanVerifier(['Mathlib'],timeout=45),root/'experiment',root/'experiment')
    finally:backend.model.close()
