# Generation V3 — actual mathematical evidence and remaining limits

V3 used **7 generation intents** and **4 separately
counted reference-repair intents**, producing **6 structurally
valid initial candidates** and **2 unique strictly verified reference
proofs**. Initial strict successes: 2; additional repaired
successes: 0. No AI adjudication, C/D/E or confirmatory inference
ran. Formal success alone is not semantic fidelity, novelty or benchmark eligibility.

## Prospective protocol and authorization

Starting commit: `14e9a450`; pre-inference implementation commit: `1b3b85c8`.
Run: `20261104T163622Z_v3`. The user explicitly authorized “10 generation calls and up
to 10 reference-proof repair calls,” each at most 4,096 input/1,200 output tokens,
with a 30-minute generation phase and a separate 30-minute repair phase. At most one
repair is allowed per candidate. No V1/V2 budget or expired deadline was reused.
Generation was interrupted before a worker completion status was saved. Its
original 30-minute window had expired by the continuation, so the remaining
3 generation slots were not launched and no clock was reset.
The cause of interruption is not established. A durable seventh completion was
reconciled offline using the unchanged parser and verifier, with zero additional
model calls. The separately authorized repair phase had not started; its own
original phase clock began only when that phase was actually launched. See
`generation/interruption_reconciliation.json`. Unlaunched slots are not failures
or missing model outcomes. This run was not a completed ten-generation sample.

Protocol SHA-256: `af7cfb59ed33f942978250f78447d53e2e85ff2b2efd6ad27e767757a9412d93`.
Source lock SHA-256: `d43285db49637e13cd14e092441388364a6efc2088bbbd657e3bc1acb819e09c`.
Generation model: `mlx-community/Qwen2.5-7B-Instruct-4bit` at
`c26a38f6a37d0a51b4e9a1eb3026530fa35d9fed`. Repair model:
`mlx-community/Qwen2.5-Coder-7B-Instruct-4bit` at
`019cc73c45c770444708a6dd8690c66243cc5c80`. No reviewer independence is claimed.
Temperature .2, seed 3039001; complete prompts, categories, models and
decoding metadata are retained. All outputs are development-only, never untouched test.

## Parser and offline validation

Three explicit sections replace six-field serialization: STATEMENT, LEAN and FAMILY.
IDs and categories come from the controller; mathematical content always comes from
the actual response. Documented heading/fence variants are accepted, but missing
content, ambiguity, truncation, invalid UTF-8 and non-NFC text are rejected.
Raw bytes are independently preserved; no JSON escaping or reconstructed English is
needed. Lean's native command parser consumes the complete command and locates the
theorem's own assignment in its direct declValSimple syntax node. It does not split
at an assignment inside a let, string or comment. Supplied syntax is not elaborated
or executed by this parser. The unchanged strict adapter cannot handle assignments
inside an unproved target; such targets are explicitly rejected, never mis-split.

All ten archived V2 responses were replayed offline: 0 parsed under
the frozen V3 contract. These are post-hoc diagnostics, not new prospective results.
V2 outcomes and ledgers remain unchanged. Four real native-parser checks passed,
including a proof-local let, comment delimiters, multiple-command rejection and a
correctly located but unsupported nested-let target. Fourteen parser unit tests
passed. Validation: `{'native_Lean_parser_checks': {'evidence': 'offline/native_parser_checks.json', 'passed': 4}, 'offline_regression': {'deselected': 3, 'passed': 361, 'seconds': 10.5, 'subtests_passed': 28}, 'parser_unit_tests': {'passed': 14}, 'real_Lean_integration_before_pilot': {'deselected': 29, 'passed': 2, 'seconds': 93.83}, 'test_fixtures_are_not_generation_successes': True}`. The broader regression excludes the two real
Lean tests run separately and the unchanged historical blanket test forbidding new
research files. Synthetic fixtures never count as benchmark candidates.

## Actual generation and repair outcomes

| Index | Initial structure | Initial strict result | Repair structure | Repair strict result |
|---|---|---|---|---|
| 0 | STRUCTURE_REJECTED | None | NOT_ATTEMPTED | None |
| 1 | STRUCTURALLY_VALID | True | NOT_ATTEMPTED | None |
| 2 | STRUCTURALLY_VALID | True | NOT_ATTEMPTED | None |
| 3 | STRUCTURALLY_VALID | False | STRUCTURALLY_VALID | False |
| 4 | STRUCTURALLY_VALID | False | STRUCTURALLY_VALID | False |
| 5 | STRUCTURALLY_VALID | False | STRUCTURALLY_VALID | False |
| 6 | STRUCTURALLY_VALID | False | STRUCTURALLY_VALID | False |

`None` means not checked or unknown, never false. Phase metrics distinguish these
cases. No repair is attempted for a missing/truncated candidate or an unknown
initial verification. Only structurally valid, known failed references can receive
one repair. Full initial compiler diagnostics, failed source and immutable target
are passed to the repair model. The repair model supplies only a by-block; joining
it to the original exact declaration is recorded explicitly. Each resulting proof
is parsed and strictly checked again. No reference from a different theorem is
substituted, and no assumption or theorem target is weakened.

Initial structure/verification rejections: `[{'failure_kind': None, 'index': 0, 'reason': 'truncated_response', 'status': 'STRUCTURE_REJECTED'}, {'failure_kind': 'compiler_error', 'index': 3, 'reason': None, 'status': 'STRUCTURALLY_VALID'}, {'failure_kind': 'compiler_error', 'index': 4, 'reason': None, 'status': 'STRUCTURALLY_VALID'}, {'failure_kind': 'compiler_error', 'index': 5, 'reason': None, 'status': 'STRUCTURALLY_VALID'}, {'failure_kind': 'compiler_error', 'index': 6, 'reason': None, 'status': 'STRUCTURALLY_VALID'}]`.
Repair rejections: `[{'index': 3, 'status': 'STRUCTURALLY_VALID', 'reason': None, 'failure_kind': 'compiler_error'}, {'index': 4, 'status': 'STRUCTURALLY_VALID', 'reason': None, 'failure_kind': 'compiler_error'}, {'index': 5, 'status': 'STRUCTURALLY_VALID', 'reason': None, 'failure_kind': 'compiler_error'}, {'index': 6, 'status': 'STRUCTURALLY_VALID', 'reason': None, 'failure_kind': 'compiler_error'}]`.

Of 4 structurally valid repair responses,
3 repeat the original proof
block exactly after boundary-whitespace removal. See repair_change_audit.json.
An additional response is not counted as an improvement without strict verification.

The original repair prompt serialized the entire verifier record. After one
actual failed repair, three other indices were skipped before inference because
that record exceeded the input cap. A separately frozen development-only prompt
amendment projected complete structured error messages (data, kind, severity and
positions), omitting duplicated stdout, verifier harness source and warnings.
No error message was truncated. Offline token checks were 854/909/908 for the three
prompts, with exact preservation of every error message. This was an explicitly
recorded technical change after original outcomes, not a prospective unchanged
prompt comparison. Original source locks and skip records remain untouched.
Only previously unattempted indices4/5/6 were eligible. The amended calls used the
same original ledger, ten-call cap, per-candidate one-call limit and original
30-minute repair deadline; index3 was not retried. See repair_prompt_amendment/.
Merged outcome views include amended records; original_prompt_variant_summary.json
preserves the separate original prompt variant summary. Rebuild using this report
script after pipeline summarization, not the original summarizer alone.


Strict verification uses pinned Lean4.32.0/Mathlib
`81a5d257c8e410db227a6665ed08f64fea08e997`, import Mathlib, the unchanged
exact-type harness and axiom policy, and a 180-second check timeout. Syntax acceptance
alone is not kernel acceptance. Every exported proof is labelled
FORMALLY_VERIFIED_PENDING_AI_REVIEW; repaired proofs retain their construction path.

First real verified example, `v3_gen_001` (initial):

For any real numbers \(a\), \(b\), \(c\), and \(d\), the following identity holds: \((a^2 + b^2)(c^2 + d^2) = (ac + bd)^2 + (ad - bc)^2\).

```lean
theorem v3_gen_001 (a b c d : ℝ) : (a^2 + b^2) * (c^2 + d^2) = (a*c + b*d)^2 + (a*d - b*c)^2 := by
  ring
```

Proof SHA-256: `98be24b76dafa14a9f021f656094140fb9427e79b39b2a1c0762236702ddc4e5`. This is a formal proof, not AI semantic or originality acceptance.

## Actual resource accounting

| Phase | Charged | Durable | Unknown consumed | Input tokens | Output tokens | Model generation seconds |
|---|---|---|---|---|---|---|
| Generation | 7 | 7 | 0 | 1630 | 2243 | 111.358 |
| Reference repair | 4 | 4 | 0 | 5467 | 352 | 46.126 |

Recorded total tokens: 9692; recorded compiler-check seconds:
514.863. Native-parser startup time is separate from compiler and
model metadata and is not estimated here. MLX-reported peaks are
4.677169208GB for generation and 5.105407948GB for
repair, not a whole-process RSS time series. Unknown consumed compute is not zero
and is not estimated. Over-budget repair prompts are skipped without truncation or
inference. Separate ledgers prevent transferring or replaying exhausted calls.

## Remaining scientific and authorization conditions

Automated historical/exposure/cohort flags for actual verified subjects are in
automated_historical_screen.json. This is not exhaustive equivalence screening,
semantic validation or pretraining contamination clearance. No candidate is yet
AI_SCREENED_FORMALLY_VERIFIED or independently human-approved. Two blinded model
reviews, conservative overlap adjudication and separately authorized compute are
still required. No AI-review inference is inferred from this generation budget.

C/D/E needs accepted subjects, eligible diagnostics from distinct families, a
frozen execution protocol and separate authorization. Its calls, paired outcomes,
effects and confidence intervals are absent, not fabricated as zero benefit. A
future untouched test needs a fresh separately frozen stream and authorization;
no inspected V1, V2 or V3 output may be promoted to it. The immediate formal-proof
objective is met for 2 development candidates; the larger benchmark
and C/D/E study remain incomplete. Reference repair added no verified proofs in
this run. Failed/truncated responses and exact compiler records define any next
version rather than an unlimited generation or repair loop.

## Reproducibility and preservation

All raw responses, prompts, seed/model metadata, token traces, native parser
offsets/errors, strict compiler diagnostics, checkpoints and source hashes are in
`v3/runs/20261104T163622Z_v3/`. `metrics.json` and `verified_candidates.json` are rebuildable
views of canonical phase records. `formal_checks/` preserves consumed verification
intents. `response_integrity.json` confirms 11 actual completions
match raw response bytes and stream reconstruction. Existing outcomes are never
silently repaired or recoded. Expired clocks cannot be reset; unfinished consumed
calls/checks remain unknown on resume.

All 6143 historical file hashes and 4 historical
symlink targets match `14e9a450`. Historical manuscripts, studies and human approval
protocol remain unchanged. Exact commands are in `v3/README.md`. The branch is pushed
without merging; passing scripts/tests alone is not completion of the scientific study.
