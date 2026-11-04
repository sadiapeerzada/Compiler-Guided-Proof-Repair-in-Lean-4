"""Exclusive, append-only calls. Interrupted intents consume budget and never replay."""
import fcntl
import json
import os
import time
from contextlib import contextmanager
from pathlib import Path
from common import content_hash,text_hash,dump,read,ensure

class RunStore:
    def __init__(self,root,binding,limits,global_root=None):
        self.root=Path(root);self.root.mkdir(parents=True,exist_ok=True)
        self.global_root=Path(global_root or root);self.global_root.mkdir(parents=True,exist_ok=True)
        self.binding=binding;self.limits=limits
        with self.lock():
            meta=self.root/'run.json'
            if meta.exists():ensure(read(meta)['binding']==binding,'Run inputs changed; refusing cross-protocol resume')
            else:dump(meta,dict(binding=binding,started_epoch=time.time()),exclusive=True)
    @contextmanager
    def lock(self):
        with (self.global_root/'.execution.lock').open('a+') as f:
            fcntl.flock(f,fcntl.LOCK_EX)
            try:yield
            finally:fcntl.flock(f,fcntl.LOCK_UN)
    def events(self):
        path=self.global_root/'budget.jsonl'
        if not path.exists():return []
        events=[]
        for line in path.read_text().splitlines():
            try:events.append(json.loads(line))
            except json.JSONDecodeError:raise ValueError('Damaged append-only ledger; manual audit required')
        return events
    def append(self,event):
        with (self.global_root/'budget.jsonl').open('a') as f:f.write(json.dumps(event,sort_keys=True)+'\n');f.flush();os.fsync(f.fileno())
    def remaining_preflight(self,initial,repair):
        with self.lock():
            events=self.events();mine=[e for e in events if e['run_binding']==content_hash(self.binding)]
            for kind,needed,limit in [('initial',initial,self.limits['max_initial_calls']),('repair',repair,self.limits['max_repair_calls'])]:
                already=sum(e['kind']==kind for e in mine)
                ensure(max(0,needed-already)<=limit-sum(e['kind']==kind for e in events),'Insufficient remaining '+kind+' resource allocation; authorize/amend before starting')
            ensure(max(0,initial+repair-len(mine))<=self.limits['max_total_calls']-len(events),'Insufficient shared allocation (calibration consumes budget)')
    def elapsed_ok(self):
        start=read(self.root/'run.json')['started_epoch'];now=time.time()
        ensure(now>=start and now-start<=self.limits['max_runtime_seconds'],'Wall-clock allocation exhausted or clock moved backwards')
    def call_once(self,key,prompt,prompt_tokens,max_output,kind,generate):
        ensure(kind in ('initial','repair'),'Invalid call kind')
        folder=self.root/'calls'/content_hash(key);folder.mkdir(parents=True,exist_ok=True)
        intent=dict(key=key,prompt_sha256=text_hash(prompt),prompt_tokens_reserved=prompt_tokens,output_tokens_reserved=max_output,kind=kind,binding=self.binding)
        # Hold a single-writer lock through inference: no concurrent duplicate calls/reservations.
        with self.lock():
            if (folder/'intent.json').exists():
                ensure(read(folder/'intent.json')==intent,'Intent changed; refusing replay')
                if (folder/'completion.json').exists():return read(folder/'completion.json'),folder
                return dict(status='unknown_consumed_intent',content=None,metadata=None,resumed=True),folder
            ensure(not (folder/'completion.json').exists(),'Orphaned completion without intent')
            events=self.events()
            orphan=[e for e in events if e['key']==key and e['run_binding']==content_hash(self.binding)]
            if orphan:
                ensure(orphan[0]['intent_sha256']==content_hash(intent),'Reserved intent changed')
                return dict(status='unknown_consumed_intent',content=None,metadata=None,resumed=True),folder
            self.elapsed_ok()
            cap=self.limits['max_initial_calls'] if kind=='initial' else self.limits['max_repair_calls']
            ensure(sum(e['run_binding']==content_hash(self.binding) for e in events)<self.limits.get('max_run_calls',self.limits['max_total_calls']),'Authorized per-run allocation exhausted')
            ensure(len(events)<self.limits['max_total_calls'] and sum(e['kind']==kind for e in events)<cap,'Call allocation exhausted')
            ensure(0<prompt_tokens<=self.limits['max_input_tokens'] and 0<max_output<=self.limits['max_output_tokens'],'Per-call token allocation exceeded')
            # Ledger first: a crash before intent may over-reserve, but never undercounts consumption.
            self.append(dict(key=key,kind=kind,run_binding=content_hash(self.binding),intent_sha256=content_hash(intent),input_reserved=prompt_tokens,output_reserved=max_output))
            dump(folder/'intent.json',intent,exclusive=True)
            completion=None
            try:
                completion=generate(prompt,folder)
                metadata=completion['metadata']
                ensure(type(metadata['prompt_tokens']) is int and metadata['prompt_tokens']==prompt_tokens,'Actual input tokenizer count mismatch')
                ensure(type(metadata['completion_tokens']) is int and 0<=metadata['completion_tokens']<=max_output,'Actual output count missing/exceeds cap')
                if isinstance(key,dict):
                    for k,m in [('model_revision','snapshot_revision'),('model_id','model'),('seed','base_seed')]:
                        if k in key:ensure(metadata.get(m)==key[k],'Backend model/seed metadata mismatch')
                if 'prompt_sha256' in metadata:ensure(metadata['prompt_sha256']==text_hash(prompt),'Backend prompt hash mismatch')
                result=dict(status='completed',content=completion['content'],metadata=metadata)
                dump(folder/'completion.json',result,exclusive=True)
                return result,folder
            except BaseException as error:
                if completion is not None:dump(folder/'nonconforming_generation.json',completion,exclusive=True)
                # Includes interruption; no next run is allowed to silently re-generate.
                dump(folder/'generation_unavailable.json',dict(status='unknown_consumed_intent',error_type=type(error).__name__,message=str(error)),exclusive=True)
                if isinstance(error,(KeyboardInterrupt,SystemExit)):raise
                return dict(status='unknown_consumed_intent',content=None,metadata=None),folder
    def verify_once(self,folder,candidate,target,verify):
        binding=dict(candidate_sha256=text_hash(candidate),target_sha256=text_hash(target))
        with self.lock():
            path=folder/'verification.json'
            if (folder/'verification_intent.json').exists():
                ensure(read(folder/'verification_intent.json')==binding,'Verification inputs changed')
                return read(path) if path.exists() else dict(success=None,failure_kind='interrupted_verification')
            ensure(not path.exists(),'Orphaned verification')
            dump(folder/'verification_intent.json',binding,exclusive=True)
            try:result=verify(candidate,target,str(folder.name))
            except BaseException as error:
                result=dict(success=None,failure_kind='verification_infrastructure_error',error_type=type(error).__name__)
                dump(path,result,exclusive=True)
                if isinstance(error,(KeyboardInterrupt,SystemExit)):raise
                return result
            dump(path,result,exclusive=True);return result
