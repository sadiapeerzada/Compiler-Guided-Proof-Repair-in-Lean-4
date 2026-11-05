# Authorized development evidence

This directory extends baseline `83f1d564` without rewriting historical research.
The researcher approved **only phases 1–6 of COMPUTE_PROPOSAL.md**, up to1,084
separately capped calls. These compute-proposal numbers differ from the numbered
research sections of the master task. No confirmatory inference is authorized.
The source of authority is the actual quoted researcher reply in
`resource_authorization.json`, not the proposal or an AI review.

`protocol.json` fixes models, categories, seeds and the development scope.
`preservation_manifest.json` binds6,279 tracked baseline files; the audit also
checks four baseline symlink targets against Git. New manifests under `freezes/`
bind the sources and inputs before each affected phase. Old manifests and failed
prototype diagnostics remain present. `reference_construction_v2.json` was
superseded **before any repair inference** by `reference_construction_v3.json`.
The latter governs base reference construction. After actual malformed repair
outputs, `reference_prompt_v4.json` adds a prospectively frozen Lean4 format
example for unconsumed candidates. The same original ledger,120-call total and
12-hour clock remain in force; no candidate is called twice. New V4 intent keys
additionally contain the V4 freeze hash while the base RunStore binding remains
unchanged. The transition snapshot retains the original ledger prefix, failed
worker status and interrupted charged intent. `reference_repair_v4.py` reconciles
that intent without inference before continuing unconsumed work. The generation
freeze remains unchanged; all31 preliminary passes subsequently passed rigid
revalidation, which still does not constitute AI acceptance.

`reference_resource_v5.json` adds cache release before compilation after a clean
inference-lock checkpoint at40 charged/recorded calls. It adds no calls, no new
deadline and no new unknown intent. The unchanged V4 prompt is used for remaining
candidates, with the additional resource/source hash in their intent keys. Those
keys participate in the already declared seed/context hash; no candidate is
resampled. Each affected call records its cache-release receipt. Runtime
comparisons across these development versions are descriptive, not randomized.

The working run is `runs/20261105T041720Z_development/`. Never reset its phase
clocks, delete reservations or replay a consumed intent. `progress.py` is
read-only. Every model call is reserved in its phase-local `calls/budget.jsonl`;
raw bytes, token streams, pre-inference hashes, model metadata and timestamps are
retained. Exact prompt text is saved in generation/repair records or recoverable
from the immutable prompt function and frozen subject; its intent hash and actual
rendered-chat metadata bind the input. `scientific_audit.actual_prompt` performs
that reconstruction without inference. The C/D/E outer checkpoint ledger and
inner inference ledger describe the same calls; only the inner ledger is added
to consolidated resource use.

The cached Phi snapshot contains Python files. `prepare_model_views.py` recreates
a data-only local view with identical pinned weights, config and tokenizer hashes.
The unchanged local client rejects Python-containing snapshots and uses installed
MLX code with `trust_remote_code=False`; no remote model Python is executed and no
model bytes are downloaded. View provenance is under `model_views/`.

The V4 format example is `True` proved by `trivial`, a real rigid Lean fixture,
not a generated benchmark subject. Its exposure is added to the expanded index
before affected calls; it is ineligible for evaluation. Assistant source concerns
are bound to raw responses and frozen before fresh review, with known concerns
excluded before spending reviewer calls.

From the repository root, use the project's existing `.venv`:

```sh
.venv/bin/python research/ai-confirmatory-study/final-study/prepare_model_views.py
.venv/bin/python research/ai-confirmatory-study/final-study/progress.py
```

An already running generation or continuation worker must not be launched again.
Only when no worker is active, resume permitted unconsumed work within original
limits with the corresponding controller. A `worker_failed` status requires
diagnosis; the continuation script deliberately refuses to advance past it.
Never rerun generation after its recorded status is `finished`. The following
are individual phase launch commands, not a command to restart the whole study.

```sh
.venv/bin/python research/ai-confirmatory-study/final-study/run_stage.py generation
.venv/bin/python research/ai-confirmatory-study/final-study/continue_development.py --wait-generation
```

For the current resource-version5 continuation, use `reference_resource_v5.py run`
only when no worker is active, every previous charged intent has been reconciled,
and unconsumed work remains within the original deadline. After it finishes,
`continue_development.py` skips the finished
repair phase and advances to the separately authorized reviews/data gate. The
transition is not permission to reset clocks or repeat unknown calls.

After the authorized workers stop, regenerate evidence projections and reports,
then run the audit in its own process:

```sh
.venv/bin/python research/ai-confirmatory-study/final-study/export_evidence.py
.venv/bin/python research/ai-confirmatory-study/final-study/report_results.py
.venv/bin/python research/ai-confirmatory-study/final-study/scientific_audit.py --output /tmp/taimma-independent-audit.json
```

These commands spend no model calls. They retain unknowns, separate initial from
repair successes and recompute the frozen paired analysis from actual checkpoints.
The audit fails on recorded integrity violations. Its PASS concerns internal
consistency, not human mathematical review, exhaustive novelty or completion of
unapproved phases. `FINAL_COMPLETED_EXPERIMENTS.md` and
`FINAL_SCIENTIFIC_INTEGRITY_AUDIT.md` live one directory above this file.

`verification_error_taxonomy.jsonl` locates actual errors in the saved trusted
expected-target block, separating target-elaboration errors from other failed
checks. Absence of such an error does not establish a statement's truth or
semantic fidelity. The family/exposure registries retain all extractable current
proposals and explicitly mark unextractable statements unknown; rejected raw
responses remain development exposures.

The two initial V3 candidates received four actual AI reviews, but all four failed
the original typed output contract. They remain unresolved. The fresh review
schema was made explicit prospectively; it cannot turn those old raw ACCEPT words
into approvals. Fresh admission requires real rigid Lean success and two valid,
blinded acceptances from the pinned Phi and Qwen-Coder reviewers, with unresolved
concerns and exposure flags excluded. That remains AI screening, never human
validation. Correlated model ancestry and incomplete equivalence/pretraining
screening are limitations even when the schema and kernel checks succeed.

The private verifier correction is documented by actual Lean fixtures and a
preserved failed negative probe. Explicit `@` fixes unresolved polymorphic
arguments but alone allowed universe specialization. The rigid successor checks
closed declaration types and universe-parameter arity, preserving the historical
axiom/proof-escape restrictions. All newly admitted references and C/D/E proofs
must use it. Header-only recovery extracts only supplied source; actual kernel
verification remains mandatory and original intake outcomes are unchanged.
