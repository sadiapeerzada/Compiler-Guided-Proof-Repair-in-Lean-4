# Exploratory post-hoc analyses (original records only)

Use the existing project Python environment. The original raw records under
`data/final_study/v1/` and the exact local Qwen tokenizer are required. Do not
replace missing originals with `publication/` views. All outputs are post hoc.

Initial commands, each writing its own outputs without overwriting old records:

```sh
.venv/bin/python -m analysis.reconcile
.venv/bin/python -m analysis.task1
.venv/bin/python -m analysis.task2
.venv/bin/python -m analysis.render
.venv/bin/python -m pytest -q analysis/tests
```

To reproduce all tables/figures into a fresh directory in one command:

```sh
.venv/bin/python -m analysis.reproduce --output outputs/post_hoc/reproduced_run1
```

`post_hoc_repair_metrics.csv` is the per-completed-repair source table for exact
repetition, Unicode-character/frozen-Qwen-token normalized Levenshtein distance,
unknown-name removal/substitution, primary error transitions, distinct error
counts, and prompt length. Ratios use their explicit eligible denominators.
`post_hoc_task1.json` includes 10,000-draw family bootstrap intervals (primary)
and whole-problem intervals (secondary), seed 20271021, with all observations
from a sampled family carried together. No repair-level independence is assumed.

`post_hoc_calibrated_null.json` and `post_hoc_MDE_sensitivity.csv` separate
complete-pair differences, Newcombe paired method 10 (independent-pair score
sensitivity), conventional exact McNemar p=1 at zero discordance, degenerate
family-bootstrap intervals, missingness identification bounds, and explicitly
assumption-based approximate/exact discrete power calculations. See method URLs
in the JSON. The Newcombe implementation is checked against the official
statsmodels documented example; statsmodels/SciPy are not runtime dependencies.

Character/token distances are exact Myers bit-vector Levenshtein divided by
maximum sequence length, empty/empty=0; candidates are never normalized. Unknown
names come from structured compiler objects (dedicated fields preferred, with
quoted `data` fallback for the actual Lean `_namedError` schema). All 282 original
unknown-name diagnostics were parsed. Name disappearance is not a verified fix.
B's own preceding diagnostics are analyst-only chance baseline; they were never
fed to B. New hallucinated substitution requires a different name newly present
in the next source and reported unknown by its actual compilation.

`latex/` contains booktabs tables and figure snippets; `figures/` contains
grayscale-safe PDFs. `POST_HOC_PROSE.md` and `SUMMARY.md` state observed numbers,
denominators and limitations. Context-failed/header-only C intents never become
completed repairs or observed failures. Synthetic tests are isolated under
`analysis/tests/fixtures/` and never enter research estimates.

The separate dev-only extension is documented under `extensions/`; no existing
held-out condition can be replayed by these scripts. Study 2 model execution is
explicitly deferred until separately approved.

After the approved dev worker reaches its durable end marker, run:

```sh
.venv/bin/python -m analysis.validate_dev
.venv/bin/python -m analysis.dev_placebo
.venv/bin/python -m analysis.dev_figures
.venv/bin/python -m analysis.check_public_dev
.venv/bin/python -m analysis.paper_additions
.venv/bin/python -m analysis.update_paper
.venv/bin/python -m analysis.restore_build_assets
.venv/bin/python -m analysis.compile_paper
```

The dev analyzer writes explicit completed-repair denominators, category/index
repetition groups, transitions, donor ancestry, physical-call resources and
descriptive success intervals. Its nominal Wilson intervals treat problems as
independent and are labeled accordingly; only five dev families exist. It makes
no hypothesis-test claim. The new manuscript goes to
`outputs/post_hoc/manuscript/post_hoc_pilot.pdf`; existing PDFs are retained.
These commands do not regenerate model responses. Do not rerun an analyzer into
an existing output path; preserve its first outputs and use a fresh location for
any subsequent reproduction.

`analysis.check_public_dev` is a non-inference, non-tokenizer check that can also
run from the reviewed public source view. It checks stored response/journal and
candidate bindings, seeds/budgets, shared initials, reported success denominators
and deterministic donor selection using recorded token counts. It does not claim
fresh kernel verification, original-donor authenticity, or tokenizer recomputation.

Reproduce the completed dev analysis/plots into a fresh directory, referencing
the original new dev records through a relative read-only-use link:

```sh
.venv/bin/python -m analysis.reproduce_dev --output outputs/post_hoc/dev_reproduced_run1
```

This checks numerical JSON/CSV outputs byte-for-byte. PDF metadata timestamps
are not claimed identical. It never reruns inference or overwrites a record.
