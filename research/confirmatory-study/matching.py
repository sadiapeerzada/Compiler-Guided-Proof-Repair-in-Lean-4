"""Whole diagnostic preservation and exact rendered-token matching, or invalidity."""
import hashlib
import itertools
from common import ensure,content_hash

ARMS=('C','D','E')
NEUTRAL='No compiler diagnostics are supplied.'
SUFFIXES=('',' ','\n','.',' .','..',' . .','\n\n')

def initial_prompt(row):
    return 'Prove exactly this fixed Lean theorem. Output one Lean code block. Do not change its type or use sorry, admit or new axioms.\n```lean\n'+row['expected_lean_statement']+'\n```\n'

def diagnostic_payload(record,candidate):
    ensure(record.get('candidate_sha256')==hashlib.sha256(candidate.encode()).hexdigest(),'Diagnostics are not bound to this candidate')
    if record.get('success') or record.get('failure_kind')!='compiler_error':return None
    # Preserve every structured error message exactly; only incidental path fields are omitted by fixed schema.
    errors=[{k:d.get(k) for k in ('severity','kind','data','pos')} for d in record.get('diagnostics') or [] if d.get('severity')=='error']
    if not errors:return None
    return __import__('json').dumps(errors,sort_keys=True,ensure_ascii=False,separators=(',',':'))

def repair_prompt(row,previous,payload,padding=''):
    return ('Repair the same failed proof of the fixed Lean theorem below. Return one complete Lean code block. Preserve every binder and assumption. No sorry, admit, new axiom or auxiliary theorem.\nFixed theorem:\n```lean\n'+row['expected_lean_statement']+'\n```\nPrevious candidate:\n```lean\n'+previous+'\n```\nFeedback field:\n'+payload+'\nLength-control markers (not mathematical evidence):'+padding+'\n')

def pad_exact(row,previous,payload,tokenizer,budget):
    base=repair_prompt(row,previous,payload)
    if tokenizer.count(base)>budget:return dict(valid=False,reason='full_payload_exceeds_input_budget',truncated=False)
    def make(n,suffix=''):return repair_prompt(row,previous,payload,' [PAD]'*n+suffix)
    low=0;high=1
    while tokenizer.count(make(high))<budget and high<budget*2:low,high=high,high*2
    for _ in range(32):
        if high-low<=1:break
        mid=(high+low)//2
        if tokenizer.count(make(mid))<budget:low=mid
        else:high=mid
    for n in range(max(0,low-8),min(budget*2,high+8)+1):
        for suffix in SUFFIXES:
            prompt=make(n,suffix);actual=tokenizer.count(prompt)
            if actual==budget:return dict(valid=True,prompt=prompt,prompt_tokens=actual,payload_sha256=content_hash(payload),padding_markers=n,padding_suffix=suffix,truncated=False)
    return dict(valid=False,reason='exact_token_budget_unreachable_by_frozen_padding_search',truncated=False)

def matched_conditions(row,previous,real_record,donor_record,donor_candidate,tokenizer,budget=4096):
    real=diagnostic_payload(real_record,previous);shuffled=diagnostic_payload(donor_record,donor_candidate)
    if real is None or shuffled is None:return dict(valid=False,reason='missing_genuine_or_donor_diagnostic',conditions={})
    if real==shuffled:return dict(valid=False,reason='byte_identical_real_and_donor_diagnostics',conditions={})
    conditions={a:pad_exact(row,previous,p,tokenizer,budget) for a,p in zip(ARMS,(real,shuffled,NEUTRAL))}
    if not all(v['valid'] for v in conditions.values()):return dict(valid=False,reason='at_least_one_arm_cannot_match_without_truncation',conditions=conditions)
    ensure(len({v['prompt_tokens'] for v in conditions.values()})==1,'Matching invariant failed')
    return dict(valid=True,predecessor_sha256=hashlib.sha256(previous.encode()).hexdigest(),diagnostic_sha256=content_hash(real),conditions=conditions)

def donor_order(target,records,seed,forbidden_pairs=()):
    forbidden={frozenset(p) for p in forbidden_pairs}
    return sorted([r['id'] for r in records if r['id']!=target['id'] and r['family']!=target['family'] and frozenset((r['id'],target['id'])) not in forbidden],key=lambda rid:content_hash(['donor',seed,target['id'],rid]))

def planned_orders(records,seeds,order_seed):
    units=[(r['id'],s) for r in records for s in seeds]
    units.sort(key=lambda x:content_hash([order_seed,*x]));permutations=list(itertools.permutations(ARMS))
    return {(rid,seed):list(permutations[i%6]) for i,(rid,seed) in enumerate(units)}
