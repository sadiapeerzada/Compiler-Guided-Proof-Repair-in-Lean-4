"""Correct two candidates, reverify proofs and request a real separate-model audit."""
from pathlib import Path
import datetime
import hashlib
import json
import sys

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from candidate_inventory import load_candidates
from local_llm_client import LocalMLXClient
from verify import check_lean_file_detailed
from ai_semantic_audit import subject,digest

BASE=ROOT/'data/final_study/v1/corrections'

def main():
    originals={r['id']:r for r in load_candidates(ROOT)}
    changed=[]
    for ident in ['mod_001','ind_001']:
        r=json.loads(json.dumps(originals[ident]));before=subject(r)
        if ident=='mod_001':
            r['expected_lean_statement']=r['expected_lean_statement'].replace('(h :','(_hm : 0 < m) (h :')
            proof='exact h.add (Int.ModEq.refl 1)'
            reason='Restore the positive integer modulus restriction explicitly required by the English.'
        else:
            r['nl_statement']='For every natural number n, the sum of the integers from 1 through n (the empty sum when n=0) equals n(n+1)/2.'
            proof='simpa [Nat.mul_comm] using Finset.sum_range_id_mul_two (n + 1)'
            reason='Specify inclusive endpoints 1..n, eliminating the zero-based first-n ambiguity.'
        code='import Mathlib\n'+r['expected_lean_statement']+' := by\n  '+proof+'\n'
        (BASE/(ident+'.lean')).write_text(code)
        result=check_lean_file_detailed(code,ROOT/'lean_project','final_correction_'+ident,
            expected_statement=r['expected_lean_statement']+' := by sorry')
        (BASE/(ident+'.verification.json')).write_text(json.dumps(result.to_record(),ensure_ascii=False,indent=2)+'\n')
        if not result.success:raise RuntimeError('Correction proof failed: '+ident)
        r['correction_history']=[{'record_kind':'authoring_ai_correction_not_human_approval',
            'on':'2026-10-28','reason':reason,'before':before,'before_binding':digest(before),
            'after_binding':digest(subject(r)),'verification_file':str((BASE/(ident+'.verification.json')).relative_to(ROOT))}]
        r['reference_lean_code']=code
        changed.append(r)
    (BASE/'corrected_candidates.json').write_text(json.dumps(changed,ensure_ascii=False,indent=2)+'\n')
    modeldir=ROOT/'data/ai_semantic_audit/20261028/model_phi4'
    client=LocalMLXClient(Path((modeldir/'local_snapshot_path.txt').read_text().strip()),
        json.loads((modeldir/'inventory.json').read_text()),model_id='mlx-community/Phi-4-mini-instruct-4bit',seed=284730,max_context_tokens=8192)
    streams=BASE/'streams';streams.mkdir(exist_ok=False);client.trace_directory=streams
    for r in changed:
        prompt=('Compare this English statement and Lean theorem type as a mathematical auditor. '
            'Check quantifiers, domains, hypotheses, endpoints, equivalence and strength. '
            'Different equivalent algebraic encodings are allowed. Give your own concrete reasoning, '
            'not generic placeholders. Output a verdict FAITHFUL, NOT FAITHFUL or UNCERTAIN, '
            'then explain all checks and try a boundary case. Do not claim human review or tool execution.\n'
            +json.dumps(subject(r),ensure_ascii=False,indent=2))
        (BASE/(r['id']+'.prompt.txt')).write_text(prompt)
        result=client(prompt,max_tokens=900,temperature=0.0,generation_context='corrected-review/'+r['id'])
        (BASE/(r['id']+'.ai_review.json')).write_text(json.dumps({'kind':'ai_only_not_human',
            'subject_sha256':digest(subject(r)),'response':result.content,'metadata':result.metadata},ensure_ascii=False,indent=2)+'\n')
        print(r['id'],result.content,flush=True)

if __name__=='__main__':main()
