"""Predeclared V2 categories; no supplied mathematical statements or proofs."""
CATEGORIES=('integer polynomial identities','real polynomial identities','natural-number inequalities','integer linear arithmetic','finite-set identities','list concatenation and length','real polynomial inequalities','divisibility in natural numbers','finite sums','propositional equivalences')

def generation_prompt(index):
    name=f'v2_gen_{index:03d}'
    return f'''Create ONE mathematical theorem in {CATEGORIES[index]}. Environment: Lean 4.32.0, Mathlib revision 81a5d257c8e410db227a6665ed08f64fea08e997, import Mathlib already provided. Choose a compact, valid theorem and a complete Lean 4 proof using available tactics (for example ring, omega, simp, aesop or nlinarith as appropriate). Avoid trivial reflexivity, commutativity/zero laws, binomial-square or successor-addition examples, standard divisibility transitivity, and renamed repetitions. Do not include imports, definitions, extra lemmas, sorry, admit, placeholders, explanations, JSON or LaTeX escapes. Use Lean 4 `by` syntax, never Lean 3 begin/end. Stay under 1200 output tokens.
Return exactly these delimiters on separate lines, replacing every bracketed instruction with actual content. ID must be {name}; TARGET must start `theorem {name}` and contain only its full declaration and type WITHOUT := or a proof. PROOF must contain ONLY a complete `by` tactic block, without repeating the declaration. Give the precise English quantifiers and assumptions. Family must describe the mathematical relation, not just an arbitrary unique name.
<<<ID>>>
{name}
<<<STATEMENT>>>
[precise English mathematical statement]
<<<TARGET>>>
[bare Lean theorem declaration]
<<<PROOF>>>
[by block]
<<<CATEGORY>>>
{CATEGORIES[index]}
<<<FAMILY>>>
[concise mathematical-family label]
<<<END>>>'''
