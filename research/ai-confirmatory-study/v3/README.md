# V3: three sections, native Lean parsing, bounded reference repair

This new development-only run has explicit authorization for at most ten generation
calls and ten reference-proof repair calls, each at most 4,096 input and 1,200 output
tokens. Generation and repair each have a persisted 30-minute deadline. There is at
most one repair per candidate. V1/V2 budgets are not reused. AI adjudication, C/D/E
and test inference have no authorization and are not implemented as executable phases.

From the repository root:

```sh
.venv/bin/python -m pytest -q research/ai-confirmatory-study/v3/tests
.venv/bin/python research/ai-confirmatory-study/v3/offline_v3.py archived
.venv/bin/python research/ai-confirmatory-study/v3/offline_v3.py native
.venv/bin/python research/ai-confirmatory-study/v3/offline_v3.py dry
.venv/bin/python research/ai-confirmatory-study/v3/pipeline_v3.py run generation
.venv/bin/python research/ai-confirmatory-study/v3/pipeline_v3.py run reference_repair
.venv/bin/python research/ai-confirmatory-study/v3/pipeline_v3.py summarize
.venv/bin/python research/ai-confirmatory-study/v3/report_v3.py
```

GPU inference requires access outside the macOS sandbox. There are no remote calls
or model downloads. These commands resume only within the original persisted phase
window and allocation. Never delete clocks, intents or ledgers to extend a run.
Consumed unknown generations and interrupted verification checks are not replayed.
Completed responses may be re-read for deterministic parsing, without regeneration.

`STATEMENT`, `LEAN` and `FAMILY` must contain actual model-supplied content. The
controller supplies only ID and category. Accepted formatting is frozen: uppercase
colon headers, standalone names, bold header/colon variants, or `###` headings;
optional whole text/plaintext wrapper and one lean/lean4 code fence. No missing
English, family, target or proof is inferred. Original response bytes are retained
separately from whitespace, fence and line-ending handling. Truncated, non-NFC or
invalid-UTF8 responses are rejected.

`ParseTheorem.lean` imports the pinned Mathlib parser extensions, parses one whole
Lean command and reads the theorem's direct `declValSimple` assignment byte range.
Nested assignments, comments and strings are not scanned with a regex. The helper
does not elaborate or execute the supplied source. Its `unsafe` qualifier is solely
for Lean's trusted extension-loader initialization; candidate proofs still use the
unchanged strict kernel verifier. Multiple commands and malformed syntax are rejected.
Targets containing nested assignments are explicitly unsupported by the unchanged
strict adapter and rejected after the correct outer assignment is found.

Only structurally valid initial candidates with a known strict verification failure
receive a repair attempt. The repair prompt includes the actual failed source and
compiler record. It requests only a `by` block. The controller joins this supplied
proof to the exact frozen target, parses it again and strictly verifies it. A repair
never substitutes a theorem from another source or changes assumptions. Over-budget
prompts are skipped without inference; diagnostics are never silently truncated.

Every generated/repair response, prompt, token count, hash and per-token stream is
retained in its phase's separate append-only call ledger. Formal checking has its
own durable intents. `records.jsonl` is canonical; `metrics.json` and
`verified_candidates.json` are rebuildable views. Repaired proofs are labelled as
one-step compiler-guided reference construction, never original-generation success
or C/D/E evaluation. Even successful proofs remain
`FORMALLY_VERIFIED_PENDING_AI_REVIEW`, not accepted or human-approved.

All archived V2 replay is post-hoc diagnosis only. Original V1/V2 outcomes, ledgers,
models and source locks remain unchanged. The final report distinguishes initial
proofs, repaired proofs, structural failures, compiler failures and unknown outcomes.

If a generation worker was interrupted and its phase window has expired,
`reconcile_generation.py` can finish deterministic parsing/checking of saved durable
responses. It cannot initialize a model, issue inference, replay verification
intents, or reset a deadline. It records reconciliation explicitly. For this run:

```sh
.venv/bin/python research/ai-confirmatory-study/v3/reconcile_generation.py
```

Reconciliation is a one-time audit command; its initial audit record should be
preserved. Inspect the saved record on subsequent checkouts rather than overwriting
that original interruption audit.

For this run, the initial repair prompt exceeded the input cap on three candidates
before any call was reserved. A separately frozen diagnostic-projection amendment
retains every complete compiler error while omitting redundant verifier metadata.
It is limited to previously unattempted candidates and shares the original repair
ledger and deadline. Its preparation and execution commands were:

```sh
.venv/bin/python research/ai-confirmatory-study/v3/repair_prompt_amendment.py prepare
.venv/bin/python research/ai-confirmatory-study/v3/repair_prompt_amendment.py run
```

Preparation is exclusive and refuses to overwrite an existing amendment. Do not
reset or recreate it after expiration. `report_v3.py` merges its canonical outcomes
with the original prompt variant, while preserving that variant's separate summary.
Run the report after `pipeline_v3.py summarize` to restore the complete merged view.

Validation commands executed from the repository root:

```sh
.venv/bin/python -m pytest -q tests research/confirmatory-study/tests research/ai-confirmatory-study/tests research/ai-confirmatory-study/v2/tests research/ai-confirmatory-study/v3/tests analysis/taimma_20261104 analysis/taimma_supervisor_final analysis/taimma_final_professor_validation -k 'not real_lean and not provenance_counts_and_read_only_scope'
.venv/bin/python -m pytest -q tests/test_verify.py -k real_lean
```

The regression run passed 361 tests and 28 subtests, with three deselections. Two
real-Lean fixtures were executed separately and both passed. The third exclusion
is the unchanged historical blanket assertion prohibiting any new research files,
which conflicts with this explicitly requested study. Preservation is independently
checked against historical file hashes and symlink targets. Actual generation and
repair verification records are separate from these synthetic test fixtures.
