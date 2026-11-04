"""AI-only study helpers; the historical human protocol is never modified."""
import csv
import hashlib
import importlib.util
import json
import os
import sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
LEGACY=ROOT/'research/confirmatory-study'
if str(LEGACY) not in sys.path:sys.path.insert(0,str(LEGACY))

def ensure(value,message):
    if not value:raise ValueError(message)
def canonical(value):return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()
def digest(value):return hashlib.sha256(canonical(value)).hexdigest()
def text_hash(text):return hashlib.sha256(text.encode()).hexdigest()
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read(path):return json.loads(Path(path).read_text())
def save(path,value,exclusive=False):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x' if exclusive else 'w') as f:f.write(json.dumps(value,indent=2,sort_keys=True,ensure_ascii=False)+'\n');f.flush();os.fsync(f.fileno())
def jsonlines(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('a') as f:f.write(json.dumps(value,sort_keys=True,ensure_ascii=False)+'\n');f.flush();os.fsync(f.fileno())
def lines(path):
    if not Path(path).exists():return []
    return [json.loads(line) for line in Path(path).read_text().splitlines() if line]
def table(path,rows,fields):
    with Path(path).open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n');w.writeheader();w.writerows(rows)
def subject_hash(row):return digest({k:row[k] for k in ('id','nl_statement','expected_lean_statement','reference_proof','family','domain','category','generation_provenance')})
def parse_json(text):
    import re
    match=re.search(r'```(?:json)?\s*(.*?)```',text,re.S)
    return json.loads(match.group(1) if match else text)
