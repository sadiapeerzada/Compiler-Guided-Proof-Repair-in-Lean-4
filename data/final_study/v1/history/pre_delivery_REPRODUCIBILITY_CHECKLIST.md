# Reproducibility checklist

Status: PARTIALLY COMPLETE. Run from repository root, using `.venv/bin/python` because unqualified `python` is absent from this shell.

- [x] Record starting SHA `648ec7b9f025eb76e13f273b34055243890c9ea1` and dedicated branch `research/taimma2027-completion`.
- [x] Preserve historical result files and versioned candidate records.
- [x] Save environment package snapshot in `data/verification/completion_20261027/python_packages.txt`.
- [x] Full suite: 228 tests / 24 subtests passed; later offline suite: 228 passed, 2 real-Lean tests deselected / 24 subtests passed. Logs preserve command boundaries.
- [x] Verify installed Lean version and pinned `lake build`; logs alongside the package snapshot.
- [x] Validate protocol, environment-file and prompt hashes through `scripts/research_readiness.py`.
- [x] Save full combined candidate validation, review queue and exact input hashes.
- [x] Attempt frozen validation and preserve its 14 rejection reasons; no false freeze.
- [x] Archive publisher sources and official provider-page hashes; leave rights review pending.
- [x] Generate pre-results paper inventory tables; preserve unavailable study outputs.
- [ ] Eligible and independently reviewed development/test sets frozen with exact ordered IDs/hashes.
- [ ] Independent protocol/preregistration and spend/access/quota approvals.
- [ ] Genuine paired pilot, audited interruptions/recovery and full study.
- [ ] Reproducible statistics/figures and five authentic repair examples.
- [ ] Successful LaTeX/PDF build and final claims review.

Commands (use fresh output directories):

```sh
.venv/bin/python -m pytest -p no:cacheprovider -q
(cd lean_project && lake build)
.venv/bin/python scripts/research_readiness.py --output-dir /tmp/nl2lean-new-readiness
.venv/bin/python eval/paired_analysis.py --audit-current --output-dir /tmp/nl2lean-new-analysis
.venv/bin/python paper/scripts/generate_inventory_tables.py
git diff --check
```

The readiness command creates development/test *candidate* snapshots and independently rejects their draft freeze status. It does not create eligible splits, invoke the API or tune on held-out outcomes. Identical B/C template-file hashes are intentional; rendered feedback and rendered prompt hashes differ. Groq's mutable alias does not guarantee immutable model weights. Machine evidence is scoped to the source files and environment actually tested, not an empirical research result.
