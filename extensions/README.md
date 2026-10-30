# Exploratory development-only placebo control

Protocol: `placebo_protocol.json`; SHA-256 recorded in `placebo_protocol.sha256`
and `outputs/post_hoc/dev_placebo/protocol_freeze.json`. The implementation,
configuration, normalized donor pool, and filename-only normalizer were frozen
and committed before the first new generation. The user explicitly approved
normalizing only diagnostic filename metadata for both real and placebo arms.

The agent executes the approved control; these commands are reproducibility
documentation, not a request for the student to run the experiment manually:

```sh
.venv/bin/python -m extensions.run_placebo --execute-dev
.venv/bin/python -m analysis.validate_dev
.venv/bin/python -m analysis.dev_placebo
```

Inference needs the actual pinned local snapshot and Metal/GPU access. All 15
original dev items get a fresh shared initial in a new phase. B, real C and
C_placebo use independent new condition/step contexts, the original primary
model and decoding caps, up to three repairs, fresh KV state, original weight
release/reload schedule, and the unmodified strict Lean verifier/type/axiom policy.
The same initial bytes are referenced by A and all repair arms. Existing dev
pilot/test calls are never reused or replayed as new model generations.

Placebo pool: only genuine original test shared-initial failure diagnostics and
family/category metadata. No repaired test outcome is read for donor selection.
Same problem/family is excluded; same primary error category is preferred,
then closest diagnostic-payload token length, then the exact committed hash tie
rule. A category fallback is logged. Nothing is truncated, synthesized, or
selected to improve a score. Selection is repeated relative to the current own
failed predecessor, including steps two/three. The matching rule itself reveals
category/length and unrelated diagnostics can contain generally useful tactics.

Normalization deep-copies each actual structured message, changing only
`fileName` to a repository-relative POSIX path. Message text, severity, ordering,
kind, positions and every other field must compare equal. Actual compiler JSON
can be reserialized after that metadata-only transformation. Original frozen
diagnostics are never rewritten. Unexpected private data outside filename
metadata or filenames outside the repository stop execution without silently
editing the message. The original feedback function's `hasSorry` filtering is
retained; complete new verifier records preserve those genuine warnings.

New raw model responses/token journals, normalized compiler JSON, intents,
checkpoints, donor selection records, timings, cumulative peak RSS and native
MLX peak-memory telemetry are under `outputs/post_hoc/dev_placebo/`. The verifier
uses its existing transient scratch namespace with new, noncolliding names.
No new held-out condition is executed. Failed and incomplete calls remain
recorded; context overflows do not trigger retry or truncation.

Completed responses and verifier checkpoints are reused on a legitimate resume;
an intent with no completed response is consumed and not regenerated. A stale
worker lock requires inspection, not an automatic second worker. Keep any new
resume log separate from the original execution log. At most one model worker
may run. Do not modify pinned code or protocol after inference starts.

After all cases reach terminal states, analyze only observed outcomes/completed
repairs. Report descriptive counts, nominal problem-level Wilson intervals and
the five-family/one-seed limitation; no repair-level independence or hypothesis
test is claimed. Interpret only consistency/inconsistency with diagnostic-content
sensitivity, never proof that content is used/ignored. Study 2 model execution
is deferred until separately approved, including dev execution.
