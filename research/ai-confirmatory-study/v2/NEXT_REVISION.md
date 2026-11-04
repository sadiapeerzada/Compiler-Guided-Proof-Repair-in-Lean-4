# Proposed generation revision — not authorized or executed

V2 generated 10 complete durable responses but zero acceptable records. Seven
failed delimiter ordering/completeness, two hit the token cap, and one used an
unsupported `plaintext` fence and lacked required fields. Stream reconstruction
matches every response. This is output-contract noncompliance, not transport loss.

The model often returns a full theorem with its assignment instead of a separate
bare type. One complete six-field colon-labelled response can be extracted without
inventing content; its supplied proof fails actual Lean checking. Simplifying
formatting alone therefore does not establish mathematical or Lean correctness.

Proposed smaller prompt contract, to freeze and test before another model call:

````text
Generate one nontrivial theorem in [controller-assigned category] for Lean 4.32.0
and the pinned Mathlib. Import Mathlib is already provided. Use theorem name
[controller-assigned ID]. Give a short complete Lean 4 proof; use · for tactic
case bullets, not Lean 3 begin/end or dash bullets. Do not include sorry, imports,
extra declarations, explanations or LaTeX escapes. Avoid the frozen historical
exclusion families, trivial identities and duplicate theorem templates.
Return exactly three sections:
STATEMENT: [precise English including every quantifier and assumption]
LEAN:
```lean
[one complete theorem declaration with its proof]
```
FAMILY: [mathematical relation/family, not an arbitrary unique label]
````

The displayed contract is a draft instruction, not a generated candidate. A next
version must pin its actual category schedule, exact prompts, generator revision,
parser, seeds, limits and acceptance rules before responses. No V3 model or sample
size is selected based on a future test result. No new call is authorized here.

Parser requirements for the next version:

- Document accepted literal header and Markdown fence variants beforehand,
  including whether `plaintext` wrappers are supported.
- Require all English, Lean and family content explicitly. Controller-provided
  IDs and categories are provenance, not invented mathematical descriptions.
- Use Lean-aware parsing to identify a single declaration's top-level assignment
  and derive its exact unproved type. Reject ambiguous assignments, multiple
  declarations and incomplete input; never strip a proof with a naive split that
  could cross a `let` or nested expression.
- Preserve original bytes and record any framing normalization separately. Never
  reconstruct missing proof text or weaken targets.
- Keep all truncations and missing-English responses rejected. V2 indices 0, 4,
  5 and 7 cannot become complete benchmark records by inventing statements.
- Add fixtures from all ten V2 failures before generation; test the colon-labelled
  index 3 as structurally extractable but **not** a valid proof fixture.
- Keep strict formal verification and blinded semantic/historical review separate.
  Simpler source formatting does not confer semantic fidelity or novelty.

Any further generation needs a new authorized allocation and a new versioned run.
The researcher explicitly deferred AI review and development inference. Those
phases remain closed even if a future generator produces a valid theorem.
