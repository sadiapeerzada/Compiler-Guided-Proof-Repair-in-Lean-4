# Final C/D/E completion sprint: PARTIAL, data gate BLOCKED

The authorized construction attempt completed, but the actual eligible development
cohort did not satisfy the gate for C/D/E. No C/D/E or untouched-test inference ran.
This is a negative construction result, not evidence of a repair treatment effect.

## Recorded outcomes

- Fresh generation calls: 120; structurally valid: 42;
  strictly kernel-verified reference proofs: 3.
- Raw valid dual-AI acceptances: 1; eligible fresh candidates after
  unresolved critical concerns: 0. Frozen development cohort:
  1 subject in 1 independent family, including unchanged old development
  evidence where explicitly marked. No new human mathematical approval is claimed.
- Actual gate reason: `NO_GO_DATA: two distinct accepted families required; no relabeling`.
- Initial-solve and C/D/E attempts: zero. Paired cases, repair rates, differences,
  confidence intervals, significance tests and power estimates: **not estimable**.
- Untouched-test construction/evaluation: **NOT_STARTED**. No test outcomes were
  inspected, no test target was reduced, and no inference was substituted for a
  missing development comparison.

## Fresh authorization and actual usage

The researcher explicitly approved **Expanded exploratory — 1,728 calls**.
`completion-sprint/resource_authorization.json` binds the actual reply, proposal,
exact revisions and separate phase ceilings. This was a maximum allocation,
not a requirement to spend calls when mathematical eligibility fails. Old V1/V2/V3
and final-study budgets remain closed. No unused phase allocation was transferred.
Reference-proof repair calls were not authorized for this sprint and none ran.

| Phase | Charged | Completed | Unknown | Approved cap |
| --- | ---: | ---: | ---: | ---: |
| development_generation | 120 | 120 | 0 | 128 |
| development_initial | 0 | 0 | 0 | 48 |
| development_repairs | 0 | 0 | 0 | 144 |
| development_review_1 | 3 | 3 | 0 | 128 |
| development_review_2 | 3 | 3 | 0 | 128 |
| test_generation | 0 | 0 | 0 | 256 |
| test_initial | 0 | 0 | 0 | 96 |
| test_repairs | 0 | 0 | 0 | 288 |
| test_review_1 | 0 | 0 | 0 | 256 |
| test_review_2 | 0 | 0 | 0 | 256 |

Total actual charged calls: **126**. Observed prompt tokens: **88053**;
completion tokens: **33365**. Per-call ceilings were 4,096/1,200 tokens.
Summed observed model-call latency: **2087.9 seconds**; maximum reported
MLX peak memory: **5.087543708 GB** (allocator-reported, not whole-machine RSS).
Original phase clocks, actual per-phase call spans, and call start/finish
timestamps are retained in the audit and run; no deadline was restarted. Summed
model-call latency is not wall-clock phase duration and excludes Lean checks.

| Executed phase | First-to-last call span, seconds | Summed call latency, seconds | Reported MLX peak, GB |
| --- | ---: | ---: | ---: |
| development_generation | 15357.0 | 1992.8 | 4.919 |
| development_review_1 | 37.8 | 34.9 | 3.021 |
| development_review_2 | 65.3 | 60.2 | 5.088 |

The generation span includes the interval between prompt versions. Eight of the
128 scheduled positions remained unconsumed under recorded family retirement;
they were not replayed or replaced to pursue a favorable outcome.

## Scientific interpretation and rejection evidence

The first 60 responses failed the mandatory three-section format. Their raw bytes,
historical outcomes and charged IDs remain unchanged. A prospective mandatory
FAMILY-footer clarification was source-frozen for unconsumed slots under the same
128-call cap and original eight-hour clock. No missing field or proof was filled
by the assistant. Both prompt versions, retirement decisions and skipped slots
are retained. Structural rejections by exact parser reason: `{'missing_or_reordered_sections': 56, 'truncated_response': 12, 'Lean_syntax: <input>:4:34: expected end of input': 1, 'Lean_syntax: <input>:3:17: unknown tactic': 1, 'Lean_syntax: <input>:2:17: unknown tactic': 2, 'Lean_syntax: <input>:6:2: expected end of input': 2, "Lean_syntax: <input>:1:90: expected ':=', 'where' or '|'": 1, 'Lean_syntax: <input>:4:21: unknown tactic': 1, "Lean_syntax: <input>:2:11: expected ')'": 1, "Lean_syntax: <input>:2:5: expected '['": 1}`.

Successful parsing did not imply proof success or English/Lean equivalence.
Every parsed reference was submitted unchanged to the rigid declaration-type
and universe checker using Lean 4.32.0 and pinned Mathlib
`81a5d257c8e410db227a6665ed08f64fea08e997`. Compiler diagnostics, failed source,
actual axiom dependencies and verification checkpoints remain available. A
compiler-verified reference still required two qualified blinded reviews under
the unchanged Boolean policy; invalid or uncertain reviews were quarantined.
See the raw review records for substantive rejection reasons rather than
interpreting all review failures as the same mathematical defect.
`completion-sprint/mathematical_concerns.json` records exact-subject assistant
concerns: two verified interval-product references describe shifted intervals
in English but prove an endpoint splitting identity; a third reference states
only a forward implication in English while Lean asserts an iff. All three
remain ineligible even if both reviewers accept. These are source-bound assistant
exclusions, not human approval. `completion-sprint/review_outcomes.json` preserves
actual raw qualified decisions separately from final eligibility.

| Strictly verified reference | Phi decision | Qwen decision | Final status |
| --- | --- | --- | --- |
| sprint_development_0086 | UNCERTAIN | ACCEPT | Excluded: source-bound statement concern |
| sprint_development_0094 | UNCERTAIN | ACCEPT | Excluded: source-bound statement concern |
| sprint_development_0078 | ACCEPT | ACCEPT | Excluded: source-bound statement concern |

The two UNCERTAIN Phi results omitted the mandatory `historical_explanation`
field; they were not retroactively reinterpreted or retried. Both reviewers gave
a schema-valid ACCEPT to `sprint_development_0078`, even though the English
describes a shift involving c and the Lean declaration proves endpoint splitting
without using c. Thus actual dual-model agreement failed to establish statement
alignment on this subject. This is an observed screening limitation, not a
C/D/E treatment result or an estimate of the reviewers' general error rate.

Models used or reserved by the approved proposal:

- G: `mlx-community/Qwen2.5-Coder-7B-Instruct-4bit` at `019cc73c45c770444708a6dd8690c66243cc5c80`.
- R1: `mlx-community/Phi-4-mini-instruct-4bit` at `ac1c269cb4222a4e136a3d09edad301056c1f36a`.
- R2: `mlx-community/Qwen2.5-7B-Instruct-4bit` at `c26a38f6a37d0a51b4e9a1eb3026530fa35d9fed`.
- X: `mlx-community/Qwen2.5-7B-Instruct-4bit` at `c26a38f6a37d0a51b4e9a1eb3026530fa35d9fed`.

Only stages with charged calls above actually used a model. The reviewers belong
to Phi and Qwen families; this does not establish independent errors. Generation,
the second reviewer and evaluation share Qwen ancestry; the second reviewer and
evaluation use identical weights. No unseen-test generalization, adequately
powered confirmatory result, human validation or external replication is claimed.

## Evidence and validation

- `completion-sprint/generation_outcomes.csv`: every charged generation outcome.
- `completion-sprint/runs/expanded_v1/`: exact prompts, raw responses, hashes,
  streaming traces, usage, checkpoints, compiler diagnostics, reviews and gates.
- `completion-sprint/final_recorded_consistency_audit.json`: separate-process
  consistency audit, **PASS_RECORDED_CONSISTENCY**, 0 failures;
  all 9,734 starting-main files and four symlink targets preserved.
- `completion-sprint/regression_validation.json`: actual offline regression runs;
  **62 parser, review, overlap and policy tests passed** in the broader run.
  The 42 actual Lean reference checks above are separate from offline tests.
- `completion-sprint/previous_31_audit.csv`: prior references and exclusion rules;
  27 excluded, four already reviewed, two qualified in one family and zero
  eligible unreviewed subjects. None were silently rescued or rereviewed.

Branch starts at merged main `9be2360b`; all changes are scoped to the new sprint
and this report. No manuscript claim or old experiment record was edited. The
remaining research objective is blocked by insufficient genuine eligible data;
infrastructure passing is not a substitute for mathematical evidence.
