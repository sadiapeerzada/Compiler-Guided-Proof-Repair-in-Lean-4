"""Read original artifacts only; privacy-safe, append-only derived outputs."""
from collections import Counter
import csv
import datetime as dt
import json
from pathlib import Path
import re
import sys

ROOT=Path(__file__).resolve().parents[1]
STUDY=ROOT/'data/final_study/v1'
OUT=ROOT/'outputs/post_hoc'
sys.path.insert(0,str(ROOT/'eval'))
from paired_analysis import classify_compiler_error as frozen_classifier
from .metrics import completed_repair_pairs


def read(path):return json.loads(Path(path).read_text())


def private_text(text):
    return bool(re.search(r'(?:/Users/|/home/)[^/\s]+|(?i:sadiapeerzada|Sadia Peerzada)|[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}',text))


def sanitize(text):
    text=re.sub(r'(?:/Users/|/home/)[^\s\"\x27<>]+','[PRIVATE_PATH]',str(text))
    text=re.sub(r'(?i)sadiapeerzada(?:2006)?|Sadia Peerzada','[PRIVATE_IDENTITY]',text)
    text=re.sub(r'[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}','[PRIVATE_CONTACT]',text)
    return text


def write_json(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    text=json.dumps(value,ensure_ascii=False,indent=2)+'\n'
    if private_text(text):raise ValueError('Private information detected in derived JSON; export stopped')
    if path.exists():raise FileExistsError('Refusing to overwrite derived output: '+path.name)
    path.write_text(text)


def write_csv(path,rows,fields=None):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists():raise FileExistsError('Refusing to overwrite derived output: '+path.name)
    if not rows:return
    fields=fields or list(rows[0]);buffer=__import__('io').StringIO();writer=csv.DictWriter(buffer,fieldnames=fields,lineterminator='\n');writer.writeheader();writer.writerows(rows)
    text=buffer.getvalue()
    if private_text(text):raise ValueError('Private information detected in derived CSV; export stopped')
    path.write_text(text)


def category(v):
    if v['success']:return 'verified'
    if v.get('failure_kind') not in {None,'compiler_error'}:return 'guard/infra/incomplete'
    return frozen_classifier('\n'.join(v.get('errors',[])))


def load_originals():
    """Never fall back to publication/ or a derived/redacted dataset."""
    required=[STUDY/'freeze.json',STUDY/'test.json',STUDY/'development.json',ROOT/'data/local_model/20261027/model_inventory.json']
    missing=[str(p.relative_to(ROOT)) for p in required if not p.is_file()]
    if missing:raise FileNotFoundError('Original sources missing: '+', '.join(missing))
    rows=read(STUDY/'test.json');cases=[];repairs=[];calls=[]
    for row in rows:
        folder=STUDY/'final_runs/heldout/2027'/row['id'];mp=folder/'manifest.json'
        if not mp.is_file():raise FileNotFoundError('Original checkpoint missing for '+row['id'])
        m=read(mp);initial=m['initial'];family=row['study_eligibility']['family']
        c={'id':row['id'],'family':family,'initial_category':category(initial['verification']),
           'outcomes':{n:m['conditions'][n]['success'] for n in ['A','B','C']},'manifest':m,'folder':folder,'row':row,
           'intents':list(folder.glob('*/intent.json'))}
        for condition,index,prior,after in completed_repair_pairs(m):
            repairs.append({'id':row['id'],'family':family,'condition':condition,'repair_index':index,
                            'initial_category':c['initial_category'],'before':prior,'after':after,'folder':folder})
        steps=[initial]+[a for n in ['B','C'] for a in m['conditions'][n]['attempts']]
        for step in steps:
            cp=ROOT/step['completion_path'];vp=ROOT/step['verification_path']
            if not cp.is_file() or not vp.is_file():raise FileNotFoundError('Original completion/verification missing for '+row['id']+'/'+step['key'])
            completion=read(cp);intent=read(cp.parent/'intent.json');md=completion['metadata']
            if completion['raw_response'] is None or read(vp)!=step['verification']:raise ValueError('Original completion/verifier inconsistency')
            stream=folder/'streams'/(__import__('hashlib').sha256(completion['context'].encode()).hexdigest()+'.jsonl')
            if not stream.is_file():raise FileNotFoundError('Original token journal missing: '+row['id']+'/'+step['key'])
            frames=[json.loads(line) for line in stream.read_text().splitlines()]
            if ''.join(f.get('text','') for f in frames)!=completion['raw_response']:raise ValueError('Token journal differs from original raw response')
            calls.append({'id':row['id'],'family':family,'key':step['key'],'condition':'A' if step['key']=='initial' else step['key'][0],
                          'prompt_tokens':md['prompt_tokens'],'completion_tokens':md['completion_tokens'],
                          'generation_seconds':md['latency_seconds'],
                          'wall_seconds':(dt.datetime.fromisoformat(completion['finished_at'])-dt.datetime.fromisoformat(intent['started_at'])).total_seconds(),
                          'compiler_seconds':step['verification']['elapsed_seconds'],'raw':completion,'step':step})
        cases.append(c)
    return cases,repairs,calls
