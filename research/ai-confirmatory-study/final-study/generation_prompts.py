import json
from families import FAMILIES

def generation_prompt(index):
    group,category=FAMILIES[index%len(FAMILIES)];name=f'final_dev_{index:04d}'
    return f'''Create one true, nontrivial theorem about {category}. Lean4.32.0, pinned Mathlib81a5d257c8e410db227a6665ed08f64fea08e997; import Mathlib is provided. Use theorem name {name}. Choose a compact statement whose complete proof you can supply, preferably a short Lean4 by-block using ring, omega, simp, aesop, norm_num, induction or nlinarith as appropriate. No tautologies, plain transitivity, commutativity/zero laws, binomial-square identities, successor addition or renamed repetitions. Avoid unnecessary premises and contradictory hypotheses. English must state every quantifier, domain and assumption. No helper declarations, imports, sorry, admit, placeholders or explanations. Use Lean4 syntax and · case bullets, never begin/end or dash bullets. Stay below1200 tokens. Return only three sections:
STATEMENT: precise English theorem
LEAN:
```lean
theorem {name} ... := by
  ...
```
FAMILY: the mathematical relation, not an arbitrary unique label
Replace the schematic dots with actual complete mathematics. This request is for one theorem, not a proof template. Category occurrence {index//len(FAMILIES)+1}: vary the mathematical relation within the stated group, never just variable names. The family label does not itself prove independence.'''

def repair_prompt(c,verification):
    errors=[{k:d[k] for k in ('severity','kind','data','pos','endPos') if k in d} for d in verification['diagnostics'] if d.get('severity')=='error']
    if not errors:raise ValueError('No complete compiler errors for reference repair')
    return '''Correct the failed reference proof using the actual Lean4 compiler errors. The target is fixed: do not change, add or remove any binder, assumption or conclusion. Output only a complete by-block, optionally fenced as lean. Do not repeat the declaration, copy the known failed proof unchanged, use sorry/admit or invent hypotheses. There is at most one repair. If the fixed target cannot be proved, do not pretend it is valid. At most1200 output tokens.\nFIXED TARGET:\n'''+c['expected_lean_statement']+'\nFAILED PROOF:\n'+c['reference_proof']+'\nCOMPLETE COMPILER ERRORS:\n'+json.dumps(errors,ensure_ascii=False)
