import sys,json,hashlib
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
OLD=HERE.parent
LEGACY=ROOT/'research/confirmatory-study'
sys.path.insert(0,str(LEGACY));sys.path.insert(0,str(ROOT/'src'))
from common import read,dump,sha,content_hash,text_hash,ensure

def rows(path):
    path=Path(path)
    return [json.loads(line) for line in path.read_text().splitlines() if line] if path.exists() else []

def append(path,record):
    import os
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('a') as f:f.write(json.dumps(record,sort_keys=True,ensure_ascii=False)+'\n');f.flush();os.fsync(f.fileno())

def frozen():
    protocol=read(HERE/'protocol_v2.json')
    ensure(sha(HERE/'source_lock_v2.json')==protocol['source_lock_sha256'],'Frozen source-lock reference changed')
    for rel,expected in read(HERE/'source_lock_v2.json')['files'].items():ensure(sha(ROOT/rel)==expected,'Frozen source changed: '+rel)
    return protocol

def authorize(stage):
    auth=read(HERE/'resource_authorization_v2.json')
    ensure(auth['status']=='AUTHORIZED' and auth['actor_kind']=='researcher_resource_authority' and auth['source']=='direct_user_authorization' and not auth.get('unit_test_only'),'NO_GO_RESOURCES: real user authorization required')
    spec=auth['phases'].get(stage)
    ensure(spec is not None,'NO_GO_RESOURCES: '+stage+' has no V2 resource authorization')
    ensure(stage=='generation' and spec['max_calls']==10 and spec['max_input_tokens']==4096 and spec['max_output_tokens']==1200 and spec['max_runtime_seconds']==1800,'NO_GO_RESOURCES: this run only permits the approved ten-call generation pilot')
    return spec,sha(HERE/'resource_authorization_v2.json')
