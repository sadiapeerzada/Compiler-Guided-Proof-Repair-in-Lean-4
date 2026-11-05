import sys,json,os,time,hashlib
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
OLD=HERE.parent
LEGACY=ROOT/'research/confirmatory-study'
sys.path.insert(0,str(LEGACY));sys.path.insert(0,str(ROOT/'src'))
from common import read,dump,sha,content_hash,text_hash,ensure
from checkpoint import RunStore

def rows(path):
    return [json.loads(line) for line in Path(path).read_text().splitlines() if line] if Path(path).exists() else []

def append(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('a') as stream:stream.write(json.dumps(value,sort_keys=True,ensure_ascii=False)+'\n');stream.flush();os.fsync(stream.fileno())

def protocol():return read(HERE/'protocol.json')
def run_root():return HERE/'runs'/protocol()['run_id']

def authorize(stage):
    a=read(HERE/'resource_authorization.json')
    ensure(a['status']=='AUTHORIZED' and a['source']=='direct_user_authorization' and a['actor_kind']=='researcher_resource_authority' and not a.get('unit_test_only'),'NO_GO_RESOURCES: genuine researcher instruction required')
    ensure(a['exact_user_instruction']=='Approve phases 1–6 only (development subset)','NO_GO_RESOURCES: authorization scope changed')
    ensure(a['proposal_sha256']==sha(HERE/'COMPUTE_PROPOSAL.md'),'NO_GO_RESOURCES: approved proposal changed')
    ensure(stage in a['stages'],'NO_GO_RESOURCES: stage not authorized: '+stage)
    spec=a['stages'][stage]
    ensure(spec['max_input_tokens']==4096 and spec['max_output_tokens']==1200,'Token authorization mismatch')
    return spec,sha(HERE/'resource_authorization.json')

def frozen(name):
    manifest=read(HERE/'freezes'/name)
    for rel,h in manifest['files'].items():ensure(sha(ROOT/rel)==h,'Frozen source/input changed: '+rel)
    return manifest

def clock(stage):
    spec,_=authorize(stage);folder=run_root()/stage;folder.mkdir(parents=True,exist_ok=True);path=folder/'phase_clock.json'
    if not path.exists():dump(path,dict(started_epoch=time.time(),max_runtime_seconds=spec['max_runtime_seconds']),exclusive=True)
    record=read(path);ensure(record['max_runtime_seconds']==spec['max_runtime_seconds'],'Phase clock limits changed')
    ensure(time.time()<record['started_epoch']+record['max_runtime_seconds'],'Phase deadline expired; never reset: '+stage)
    return record

def raw_write(path,raw):
    path=Path(path)
    if path.exists():ensure(path.read_bytes()==raw,'Raw bytes changed')
    else:
        with path.open('xb') as stream:stream.write(raw);stream.flush();os.fsync(stream.fileno())

def subject_hash(c):return content_hash({k:c[k] for k in ('id','nl_statement','expected_lean_statement','reference_proof','family','category','generation_provenance')})
