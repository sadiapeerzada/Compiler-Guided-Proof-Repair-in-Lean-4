"""Shared serialization and integrity helpers; importing never starts inference."""
import csv
import hashlib
import json
import os
import re
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
STATUS='PENDING_INDEPENDENT_HUMAN_ADJUDICATION'

def canonical(value):return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()
def content_hash(value):return hashlib.sha256(canonical(value)).hexdigest()
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def ensure(condition,message):
    if not condition:raise ValueError(message)
def read(path):return json.loads(Path(path).read_text())
def clean(text):return re.sub(r'/(?:Users|home)/[^/\s"\\]+','<HOME>',text)
def dump(path,value,exclusive=False):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x' if exclusive else 'w') as f:
        f.write(json.dumps(value,indent=2,sort_keys=True,ensure_ascii=False)+'\n');f.flush();os.fsync(f.fileno())
def csv_write(path,rows,fields=None):
    fields=fields or (list(rows[0]) if rows else [])
    with Path(path).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n');w.writeheader();w.writerows(rows)
def source_rows(value):
    if isinstance(value,dict):
        if isinstance(value.get('id'),str) and isinstance(value.get('expected_lean_statement'),str):yield value
        else:
            for item in value.values():yield from source_rows(item)
    elif isinstance(value,list):
        for item in value:yield from source_rows(item)
def normalize(statement,alpha=False):
    statement=re.sub(r'(?m)^\s*(?:import|open scoped) [^\n]*\n?', '',statement)
    statement=re.sub(r'\b(?:theorem|lemma)\s+[\w.\u0080-\uffff]+', '',statement,count=1)
    if alpha:
        names=[]
        for binder in re.findall(r'\(([^()]*)\)',statement):
            if ':' in binder:names.extend(binder.split(':',1)[0].split())
        names={n:'v'+str(i) for i,n in enumerate(dict.fromkeys(names))}
        statement=re.sub(r'\b\w+\b',lambda m:names.get(m.group(),m.group()),statement)
    return ' '.join(re.findall(r'\w+|[^\w\s]',statement))
