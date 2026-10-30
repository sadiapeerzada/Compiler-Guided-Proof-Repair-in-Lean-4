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
