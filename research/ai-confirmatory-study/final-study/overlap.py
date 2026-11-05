"""Conservative exposure checks; no exhaustive mathematical-equivalence claim."""
import re
from study_common import *
from common import normalize

def fingerprint(statement):
    aliases={'Nat':'ℕ','Int':'ℤ','Real':'ℝ'}
    statement=re.sub(r'\b(?:Nat|Int|Real)\b',lambda m:aliases[m.group()],statement)
    return content_hash(normalize(statement,True))

def transitivity_template(statement):
    key=fingerprint(statement)
    return any(key==fingerprint(f'theorem exposure (x y z : {type_}) (h1 : x {op} y) (h2 : y {op} z) : x {op} z') for type_ in ('Nat','Int','Real') for op in ('≤','≥','<','>'))

def flags(c):
    result=[];index=read(run_root()/'expanded_historical_exposure.json')
    applicable=[r for r in index['items'] if not (c['id'].startswith('v3_') and r.get('raw_response_sha256')==c.get('raw_response_sha256'))]
    if fingerprint(c['expected_lean_statement']) in {r['fingerprint'] for r in applicable}:result.append('historical_alias_alpha_statement_overlap')
    if transitivity_template(c['expected_lean_statement']):result.append('standard_scalar_transitivity_previously_exposed')
    return result

def nearest(c,count=5):
    from difflib import SequenceMatcher
    data=read(run_root()/'expanded_historical_exposure.json')['items'];ranked=sorted(data,key=lambda r:SequenceMatcher(None,c['expected_lean_statement'],r['statement'],autojunk=False).ratio(),reverse=True);unique=[];seen=set()
    for r in ranked:
        if r['fingerprint'] in seen:continue
        seen.add(r['fingerprint']);unique.append(r)
        if len(unique)==count:break
    return [dict(id=r['id'],statement=r['statement'],family=r['family'],exposure_only_not_proof_validation=True) for r in unique]
