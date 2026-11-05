"""Release the pinned inference model before Lean compilation, without extra calls.

The V4 prompt is unchanged. V5 is an additive resource/source version inside the
original repair phase, with the original clock, ledger and120-call total.
"""
import argparse,subprocess,signal
from study_common import *
from runtime_v2 import PhaseModelV2
import reference_repair_v4 as base

FREEZE='reference_resource_v5.json'

class ReleasingModel(PhaseModelV2):
    def __init__(self,*args,**kwargs):
        frozen(FREEZE);super().__init__(*args,**kwargs)
    def call(self,prompt,key,seed):
        frozen(FREEZE)
        key=dict(key,resource_version='release_before_compiler_v5',resource_source_freeze_sha256=sha(HERE/'freezes'/FREEZE))
        record,folder=super().call(prompt,key,seed)
        self.close()
        dump(folder/'resource_release_before_compiler.json',dict(epoch=time.time(),resource_version='release_before_compiler_v5',source_freeze_sha256=key['resource_source_freeze_sha256'],model_client_closed=True,MLX_allocator_cache_cleared=True),exclusive=True)
        return record,folder

def worker():
    authorize('reference_repair');clock('reference_repair');frozen(FREEZE);frozen(base.FREEZE)
    out=run_root()/'reference_repair';events=rows(out/'calls/budget.jsonl');done={r['index'] for r in rows(out/'records.jsonl')}
    ensure({e['key']['key']['index'] for e in events}<=done,'Unrecorded existing intent needs explicit zero-inference reconciliation; do not replay')
    base.PhaseModelV2=ReleasingModel
    original=base.entry_from_record
    def entry(*args,**kwargs):
        result=original(*args,**kwargs);result.update(resource_version='release_before_compiler_v5',resource_source_freeze_sha256=sha(HERE/'freezes'/FREEZE));return result
    base.entry_from_record=entry
    base.worker()

def run():
    authorize('reference_repair');frozen(FREEZE);c=clock('reference_repair');out=run_root()/'reference_repair'
    dump(out/'status.json',dict(status='running',prompt_version='v4',resource_version='v5',original_clock_preserved=True))
    remaining=c['started_epoch']+c['max_runtime_seconds']-time.time()
    with (out/'stdout_v5.log').open('a') as stdout,(out/'stderr_v5.log').open('a') as stderr:
        child=subprocess.Popen([sys.executable,str(HERE/'reference_resource_v5.py'),'worker'],stdout=stdout,stderr=stderr,start_new_session=True)
        try:code=child.wait(timeout=remaining);status='finished' if code==0 else 'worker_failed'
        except subprocess.TimeoutExpired:os.killpg(child.pid,signal.SIGKILL);child.wait();code=None;status='authorized_deadline_expired'
    dump(out/'status.json',dict(status=status,exit_code=code,prompt_version='v4',resource_version='v5',original_clock_preserved=True,original_total_call_cap_preserved=True));print(read(out/'status.json'));ensure(status!='worker_failed','V5 worker needs diagnosis')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['run','worker']);a=p.parse_args();run() if a.mode=='run' else worker()
