# Reproducibility checklist

Verified delivery on 29 October 2026; historic checklist preserved in `data/final_study/v1/history/`.

- COMPLETE: 15 development / 60 test examples validated under the versioned AI policy; no cross-split curated family overlap; ordered IDs and hashes in `freeze.json`.
- COMPLETE: original dataset, correction history, excluded records, raw AI disagreements and student-reported approval provenance retained.
- COMPLETE: primary model snapshot, weights/tokenizer hashes, Lean/Mathlib, prompts, seed and decoding pinned before held-out execution.
- PARTIAL: final development pilot covers 3 of 15 development examples; one primary seed; 60 terminal held-out cases include 58 complete A/B/C pairs and two unavailable C outcomes. No hidden replay is permitted.
- COMPLETE: 410 completed held-out inference calls; 412 logical intents; raw prompts, streams, candidates, genuine diagnostics, control checks and checkpoint recovery preserved.
- COMPLETE: artifact validator, paired analysis, Wilson intervals, problem/family bootstrap sensitivity, McNemar/Holm and resource distributions verified. No C-over-B benefit established.
- COMPLETE: 293 Python tests and 28 subtests passed in the fresh delivery check (`pytest_delivery_20261029.log`); Lean build passed (8658 jobs).
- COMPLETE: 12-page Springer manuscript compiled, actual PDF text/results checked; four numbered tables, two figures and five authentic examples included.
- PARTIAL: author affiliation was not supplied; final submission category and publication review remain. No automatic merge or submission.

Evidence root: `data/final_study/v1/`. Exact reproduction commands and runtime limits: [reproduction guide](FINAL_EXECUTION_REPRODUCIBILITY.md). Historical human-only gates are retained; AI eligibility is not mislabeled as human review.

- PARTIAL: full staged `git diff --check` reports whitespace in preserved raw model candidates, development prototypes and CSV exports. Findings and exit code are retained in `git_diff_check.json`; original evidence was not rewritten to clear this formatting check.
