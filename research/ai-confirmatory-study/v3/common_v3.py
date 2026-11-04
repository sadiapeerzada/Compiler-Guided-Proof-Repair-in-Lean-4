import sys,json,os
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
OLD=HERE.parent
sys.path.insert(0,str(ROOT/'research/confirmatory-study'));sys.path.insert(0,str(ROOT/'src'))
from common import read,dump,sha,content_hash,text_hash,ensure
from checkpoint import RunStore

def rows(path):
    return [json.loads(line) for line in Path(path).read_text().splitlines() if line] if Path(path).exists() else []

def append(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('a') as f:f.write(json.dumps(value,sort_keys=True,ensure_ascii=False)+'\n');f.flush();os.fsync(f.fileno())

def freeze_check():
    p=read(HERE/'protocol_v3.json')
    ensure(sha(HERE/'source_lock_v3.json')==p['source_lock_sha256'],'Source-lock reference changed')
    for rel,h in read(HERE/'source_lock_v3.json')['files'].items():ensure(sha(ROOT/rel)==h,'Frozen source changed: '+rel)
    return p

def authorize(phase):
    a=read(HERE/'resource_authorization_v3.json')
    ensure(a['status']=='AUTHORIZED' and a['source']=='direct_user_authorization' and a['actor_kind']=='researcher_resource_authority' and a['exact_user_instruction'] and not a.get('unit_test_only'),'NO_GO_RESOURCES: genuine explicit V3 permission required')
    ensure(phase in ('generation','reference_repair') and phase in a['phases'],'NO_GO_RESOURCES: no V3 authorization for '+phase)
    s=a['phases'][phase]
    ensure(s==dict(max_calls=10,max_input_tokens=4096,max_output_tokens=1200,max_runtime_seconds=1800),'V3 phase limits differ from explicit user authorization')
    return s,sha(HERE/'resource_authorization_v3.json')

def root():return HERE/'runs'/read(HERE/'protocol_v3.json')['run_id']
