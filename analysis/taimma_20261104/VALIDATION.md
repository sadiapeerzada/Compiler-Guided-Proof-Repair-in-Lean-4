# Validation record

- `.venv/bin/python -m pytest -q tests -k 'not real_lean'`: **283 passed, 2 deselected, 28 subtests passed**. The eight newly added tests are included.
- `python3 -m pytest -q tests/test_taimma_evidence.py`: **8 passed**. Tests cover full pair grids, duplicate/missing endpoints, denominators, family consistency, outcome/discordance targets, trace matching, checksums and seeded theorem/family bootstrap reproducibility.
- In `publication/post_hoc`, `python3 -m pytest -q analysis/tests`: **19 passed**.
- Repeated analysis runs: all 37 generated artifacts byte-identical; fixed seeds and no timestamp fields.
- Analysis execution validates all 4,736 indexed archive members, ZIP checksum, all 40 V8 frozen-lock records, trace/final-outcome agreement, historical per-seed counts/Wilson/McNemar/family intervals and call/token totals. Historical interval reconstruction is exact.
- All pre-existing tracked files remain unchanged; only new analysis files and one new test file are committed. Pre-existing untracked user files are excluded.

Environment limitations: unrestricted `python3 -m pytest -q` collects archived source-snapshot copies and fails collection (25 errors: duplicate module names, missing archived scripts and package paths). System Python lacks the optional Groq SDK, causing `test_permanent_http_error_is_not_retransmitted` to fail because the fallback namespace has no `BadRequestError`; the project `.venv` run passes that test. Full system-Python unittest/pytest runs were interrupted while waiting on real Lean integration checks; the latter had 270 passes, one missing-SDK failure and 28 subtest passes at interruption. The two real Lean integration tests are not certified passing by this work. No existing production code or frozen evidence was changed to hide these limitations. Tests use mocked model completions; no new model inference was requested or executed.

Coverage limitations: this is a substantial Study 2 evidence addition, not certification of every historical statistic, model-weight hash, original environment or publication artifact. See the explicit inventory and unverified areas in FINDINGS.md.
