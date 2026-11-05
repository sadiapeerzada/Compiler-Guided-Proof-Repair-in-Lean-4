CATEGORIES=('integer cubic factorization','real quartic identities','integer linear inequalities','natural-number arithmetic constraints','finite-set membership identities','list reversal and concatenation','real quadratic inequalities','integer divisibility relations','finite sums with constant coefficients','propositional distributive equivalences')

def prompt(index):
    return f'''Generate ONE nontrivial theorem in {CATEGORIES[index]} for Lean 4.32.0 with import Mathlib already provided. Use name v3_gen_{index:03d}. Choose a true statement with a short complete proof using Lean 4 tactics such as ring, omega, simp, aesop or nlinarith. Give all quantifiers and assumptions in English. Avoid reflexivity, commutativity/zero laws, elementary distributivity, binomial squares, successor addition and divisibility transitivity. No imports, extra declarations, sorry, admit, placeholders, JSON, LaTeX escapes or explanations. Use by syntax and · for case bullets; never begin/end or dash bullets. At most1200 output tokens.
Return exactly three sections, in this format:
STATEMENT: your precise English statement
LEAN:
```lean
theorem v3_gen_{index:03d} ... := by
  ...
```
FAMILY: a concise mathematical relation label
Replace the schematic dots with actual complete mathematics and proof.''' 

def repair_prompt(candidate,diagnostics):
    return '''Repair this generated reference proof using its actual Lean diagnostics. This is development benchmark construction, NOT a C/D/E evaluation. Keep the theorem target exactly fixed. Output ONLY a complete Lean 4 `by` block, optionally in a lean fence. No theorem declaration, imports, sorry, admit or extra commands. Do not invent hypotheses. At most1200 tokens.\nFIXED TARGET:\n'''+candidate['expected_lean_statement']+'\nFAILED SOURCE:\n'+candidate['reference_proof']+'\nACTUAL COMPILER RECORD:\n'+diagnostics
