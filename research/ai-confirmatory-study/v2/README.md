# V2 delimited generation pilot

This is a new ten-call, generation-only pilot. It cannot spend the old V1 budget
or infer permission for AI review, C/D/E or test inference. Actual outcomes are in
[V2_EXPERIMENTAL_RESULTS.md](../V2_EXPERIMENTAL_RESULTS.md). Passing a parser or
test fixture does not establish theorem validity or experimental success.

The source-only pre-execution commit is `b64aa1d4`. `protocol_v2.json` binds the
model, category schedule, prompts, parser, source hashes, seed, decoding, limits
and development-only designation before V2 responses. The exact resource owner's
instruction is in `resource_authorization_v2.json`. No human mathematical reviewer
approval is synthesized.

Run from the repository root using the existing `.venv`:

```sh
.venv/bin/python -m pytest -q research/ai-confirmatory-study/v2/tests
.venv/bin/python research/ai-confirmatory-study/v2/archived_diagnostics.py
.venv/bin/python research/ai-confirmatory-study/v2/pipeline_v2.py dry-run
.venv/bin/python research/ai-confirmatory-study/v2/run_generation.py
.venv/bin/python research/ai-confirmatory-study/v2/pipeline_v2.py verify
.venv/bin/python research/ai-confirmatory-study/v2/posthoc_field_diagnostic.py
.venv/bin/python research/ai-confirmatory-study/v2/report_v2.py
```

Generation needs local GPU access outside the restricted macOS sandbox. No remote
model service, model download or fallback is permitted. The generation command
has a persisted 30-minute watchdog. Never delete its clock, ledger or intents to
extend an expired/exhausted run. Completed calls are read without regeneration;
unknown consumed calls remain charged and are never replayed. Only unconsumed
indices within the original allocation/deadline can be resumed. Another pilot
requires separate authorization, a new run ID and a new prospectively frozen policy.

The raw responses are exclusive UTF-8 `raw_response.txt` files in each call folder.
They match the local backend's original returned Unicode encoded in UTF-8;
parser whitespace/fence/line-ending handling never overwrites these bytes.
`v2_candidates.jsonl` is the append-only canonical candidate log. The parsed JSONL
and metrics are rebuildable views of that log. Strict reference checks use durable
verification intents. An interrupted verification is unknown, not silently rerun.

The archived-response script is **post-hoc diagnosis only**. Its explicitly recorded
invalid-escape doubling is for inspecting legacy JSON fields, never candidate
admission. Old outcomes and budgets remain untouched. The separate post-hoc field
diagnostic inspects only complete colon-labelled V2 responses, framing their exact
existing field text for a strict Lean check. It never changes the prospective
zero-parse result, fabricates missing English/proofs, or grants AI-screened status.

Automated historical screens operate only on formally verified subjects. They
cannot establish mathematical novelty, semantic fidelity or absence of pretraining
contamination. No candidate is eligible for C/D/E without independently recorded,
blinded AI screening and separately authorized development compute. No V2 output
may later be represented as an untouched confirmatory subject.

Regression command:

```sh
.venv/bin/python -m pytest -q tests research/confirmatory-study/tests research/ai-confirmatory-study/tests research/ai-confirmatory-study/v2/tests analysis/taimma_20261104 analysis/taimma_supervisor_final analysis/taimma_final_professor_validation -k 'not real_lean and not provenance_counts_and_read_only_scope'
.venv/bin/python -m pytest -q tests/test_verify.py -k real_lean
```

The first command passed 347 tests and 28 subtests, with three deselections.
Two are real-Lean fixtures executed separately (both passed); the third is the
historical blanket test prohibiting any new research files, incompatible with
this explicitly requested new study. That test remains unchanged. Actual
preservation is checked against all historical file hashes and symlink targets.
