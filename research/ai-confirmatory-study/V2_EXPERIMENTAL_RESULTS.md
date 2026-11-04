# Generation V2 — actual experimental results

**The authorized pilot ran; the experimental objective remains unmet.**
It used 10 charged new generation intents and produced
10 durable real responses, 0 structurally
valid candidates and 0 strictly verified candidates. AI review
and C/D/E inference were not run. They were explicitly deferred by the researcher.
No new test inference or independent human validation is claimed.

## Previous failure diagnosis

The 22 V1 responses remain unchanged. Their original failures were 15 invalid JSON
escapes, five non-bare theorem declarations and two other JSON parse failures.
Inspection found 5 length-capped outputs. All 22 stream
reconstructions match the saved response. There is no evidence of lost stream text.
Fourteen responses had a JSON Markdown fence, which the old parser already accepted;
fencing alone did not explain the original rejections. A separately disclosed,
diagnostic-only escape-doubling pass exposed fields in 17
responses. All 17 inspectable targets included an assignment; ten proofs used Lean 3
begin/end syntax, two included imports and two contained placeholders. Flags overlap.
None was admitted to V2 or relabeled as a new successful generation.

Source-backed records: `v2/offline/archived_response_diagnostics.json` includes each
original call path, completion-file hash, raw-response hash, token limit and flags.

## Parser V2 validation and prospective freeze

The parser requires ordered ID/STATEMENT/TARGET/PROOF/CATEGORY/FAMILY/END markers.
It separates a bare target from a `by` block and assembles their exact concatenation
for the unchanged strict verifier. It invents no statement, target, proof or family.
Only outer whitespace, documented Markdown fences and source line endings are
normalized; original UTF-8 response bytes remain independently stored and hashed.
Invalid UTF-8, non-NFC text, duplicate IDs, missing/conflicting fields, reserved
delimiter collisions, over-budget output and length-capped responses are rejected.
Fifteen parser tests passed. Strict replay of the old JSON responses under V2 yields
0/22 parses, as expected for a different output protocol.
That replay is offline post-hoc diagnosis, not prospective benchmark evidence.

The no-inference dry run passed for all ten prompts. The pinned coding-specialized
generator is `mlx-community/Qwen2.5-Coder-7B-Instruct-4bit` at `019cc73c45c770444708a6dd8690c66243cc5c80`. It was chosen
before V2 responses. Temperature is 0.2, base seed 3038001.
Prompt source SHA-256: `24aa5ce2fe5cd577a713b214c858f3da3e5b10176510d455dac7cbca53cb99d2`.
Parser source SHA-256: `c22c7586045e143cbf83e1ca604516373e98392db187a95792986b97028c3463`.
Source lock SHA-256: `41d5e6aac29d0b7f7990694a90f346f792502484a7acb665cca95bb2c3485499`.
The ten-category schedule and complete prompts are frozen in the dry-run evidence.
Source/protocol commit: `b64aa1d4`. No prompt, parser, source lock or acceptance rule
was changed in response to V2 outputs.

## New generation and formal results

| Measure | Actual result |
|---|---|
| Charged new intents | 10/10 |
| Durable responses | 10 |
| Unknown consumed intents | 0 |
| Structurally valid candidates | 0 |
| Strictly checked / verified / failed / unknown | 0 / 0 / 0 / 0 |
| Parsed alpha-duplicate candidates | 0 (no estimate of duplication among unparsed text) |
| Response rate / parse rate per response | 1.0 / 0.0 |
| Strict verification rate per parsed candidate | None |

Formal stage: **NOT EXECUTED: zero structurally eligible candidates**. No parser rejection is recoded as a Lean compiler
failure. Successful real-Lean fixtures are not generated candidate successes.
Where subjects exist, the fixed environment is Lean 4.32.0 and Mathlib revision
`81a5d257c8e410db227a6665ed08f64fea08e997`, with import Mathlib, exact target
checking, a 180-second reference timeout and the unchanged strict axiom policy.

Exact V2 failure counts: `{'missing_duplicate_or_out_of_order_delimiter': 7, 'output_truncated_at_allocation': 2, 'ambiguous_or_incomplete_outer_fence': 1}`.
`v2_output_bound_failure_diagnostics.json` records missing markers, alternative
literal header lines, finish reasons, output tokens and hashes for every response.
The original responses and stream traces are retained in each `calls/calls/` folder.
There is no post-hoc rescue of missing English, reordered fields, truncated proof
text, combined declarations or arbitrary header variants into the frozen cohort.

A separate post-hoc diagnostic extracted all six explicit colon-labelled fields from 1 rejected response(s), without changing mathematical text. It submitted only that supplied theorem to the strict verifier: 0 verified, 1 compiler/policy failures, 0 unknown. The original prospective parse count remains zero. Exact source, target, original-response binding and full compiler records are in `posthoc_alternate_labels/`. For v2_gen_003 the compiler reported unknown `exact` identifiers and an application type mismatch; elapsed verification time was 26.878 seconds. These are actual compiler diagnostics, not an AI mathematical adjudication or a new prospective success.

## AI review, historical overlap and development C/D/E

AI review calls: 0. AI-screened accepted candidates: 0. Reviewer agreement is not
estimable. No model is relabeled as an independent human. The automated historical
screen uses the inherited 193-version inventory and generated-candidate exposure
registry for formally verified subjects; actual screen records are in
`automated_historical_screen.json`. No exhaustive semantic or pretraining
contamination clearance is claimed.

Development theorem types eligible for C/D/E: 0. Initial model calls and C/D/E
repair calls: 0. Paired comparisons, discordance, C−D/C−E effects, missingness
bounds and confidence intervals are not estimable. No claim of equality, causal
benefit or inferential superiority is supported. Reference proofs have not been
sent to any repair model. This is a development-generation pilot, not untouched
confirmatory testing and not a completed C/D/E evaluation.

## Resource accounting

Actual user instruction: “10 generation calls only; defer review and development
authorization.” The recorded question context caps each call at 4,096 input and
1,200 output tokens and the generation phase at 30 minutes. This is a new run;
the earlier 24 exhausted intents and deadlines are unchanged and never replayed.
No unused old allocation or deferred review/development allocation is transferred.

Completed calls record 3740 input tokens,
3144 output tokens and 179.603
generation seconds. Maximum reported MLX peak memory is
4.720849806 GB; this is not an independently sampled RSS
series. Unknown consumed compute is not estimated. No cloud model calls were made.
Review, development and test gates each report NO_GO_RESOURCES for this V2 run.

## Next justified revision and confirmatory readiness

The immediate observed technical failure is failure to follow the multi-field
delimiter contract. A next version should test a smaller response contract:
one verbatim English statement, one fenced full Lean theorem, and one family label,
with ID and category assigned by the controller. Derive the unproved target by
parsing the single supplied declaration at its top-level assignment, without
inventing or modifying mathematical text. Define all accepted header/fence forms
and ambiguity rejection before another response. Add fixtures based on these exact
V2 failures. Keep completeness, exact-type checks, proof policy and semantic review
requirements unchanged. This is a proposed revision, not an executed V3 pilot.
The concrete proposed contract and boundary cases are in `v2/NEXT_REVISION.md`.

Another inference pilot needs fresh, explicit resource authorization; no positive
result is pursued by looping past the ten-call ceiling. AI review and C/D/E also
need separately authorized limits, genuinely verified subjects and two blinded
review processes. Diagnostic donors require distinct eligible families. A separate
test stream must use fresh families/subjects, a prospectively frozen generation,
screening and analysis policy, a feasible sample/compute calculation, and separate
test authorization. No inspected V1 or V2 output may become an untouched test.

## Reproducibility and validation

Run ID: `20261104T161647Z_v2_generation`; evidence directory: `v2/runs/20261104T161647Z_v2_generation/`.
Raw responses are exclusive `raw_response.txt` files alongside durable intents,
completions, prompt/token metadata and per-token traces. The new ledger is
append-only. Completed calls may be re-read, but consumed unknown calls are never
regenerated. The persisted generation deadline cannot be reset.

All 6058 historical file hashes and 4 historical
symlink targets match `1ac2e624`. Old pilot records, human protocol, experiments,
manuscript and pre-existing untracked user files were left unchanged.
Validation results: `{'offline_regression': {'deselected': 3, 'passed': 347, 'seconds': 11.41, 'subtests_passed': 28}, 'parser_tests': {'passed': 15}, 'real_lean_integration': {'deselected': 29, 'passed': 2, 'seconds': 194.51}, 'tests_are_not_benchmark_successes': True}`. See `v2/README.md` for exact commands and the
legacy exclusion explanation. Scripts/tests passing does not establish candidate
validity, AI acceptance, experimental inference or completion of this research goal.
