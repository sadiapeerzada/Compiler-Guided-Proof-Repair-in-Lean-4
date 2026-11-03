# Validation record — 4 November 2026

New supplement test coverage uses real recorded evidence: candidate hashes and strict recorded outcomes for all three cases; 72-theorem/seed-grid derivative integrity; latency/memory/token normalization; 1,916 unique completed repair observations; zero V8 B/C/D/E newly verified repairs; checksum rejection; publication-view path redaction; and the complete 29-point status table. No invented proof-repair example enters the reports or tests.

| Command | Outcome |
| --- | --- |
| `.venv/bin/python analysis/taimma_supervisor_final/supplement.py` | Passed: archive, lock, source/trace/outcome consistency assertions; three authentic cases and 1,916 observations |
| `.venv/bin/python -m pytest -q analysis/taimma_supervisor_final/test_supplement.py` | 8 passed |
| `.venv/bin/python -m pytest -q tests analysis/taimma_supervisor_final/test_supplement.py -k 'not real_lean'` | 291 passed, 2 deselected, 28 subtests passed |
| `python3 -m pytest -q analysis/tests` from `publication/post_hoc/` | 19 passed |
| `.venv/bin/python analysis/taimma_supervisor_final/verify_reproduction.py` | 14 generated files byte-identical on repeated run and without local V7 originals; home-prefix scan passed |

The two `real_lean` integration tests are explicitly deselected to keep this evidence-only audit free of compiler execution and expensive environment checks. No full real-Lean integration pass is claimed; none is needed to recompute descriptive statistics. No test failed or was interrupted in this supplement's scoped runs. PR20's earlier system-Python/collection/integration limitations are preserved in its own VALIDATION.md, not silently overwritten.

The final checks also cover repeated-run byte identity, clean-checkout-style reproduction without reading local V7 originals, no personal home prefixes in publication-facing derived outputs, and no modifications to pre-existing tracked files. These are consistency/privacy checks for new derivatives, not independent scientific adjudication or a general privacy approval of the original archive.
