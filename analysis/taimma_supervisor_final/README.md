# Final supervisor evidence supplement

This directory adds to merged PR20; it does not rewrite its results or the paper. No model inference, held-out rerun, tokenizer call or Lean replay is needed.

```sh
.venv/bin/python analysis/taimma_supervisor_final/supplement.py
.venv/bin/python analysis/taimma_supervisor_final/verify_reproduction.py
.venv/bin/python -m pytest -q tests analysis/taimma_supervisor_final/test_supplement.py -k 'not real_lean'
```

- [29-point status and outstanding dependencies](SUPERVISOR_29_POINT_STATUS.md)
- [Three authentic cases](CASE_STUDIES.md)
- [Observational context and length analysis](CONTEXT_WINDOW_ANALYSIS.md)
- [Recorded tokens, latency and memory](RESOURCE_ANALYSIS.md)
- [Failure persistence](FAILURE_ANALYSIS.md)
- [Independent benchmark-review worksheet](INDEPENDENT_BENCHMARK_REVIEW_PACKET.md)
- [Primary-source related-work comparison](RELATED_WORK_COMPARISON.md)
- [Final scientific audit](FINAL_SCIENTIFIC_AUDIT.md)
- [Future truncation proposal, not executed](FUTURE_TRUNCATION_PROTOCOL.md)
- [Validation record](VALIDATION.md)

CSV tables contain resource totals, prompt summaries, diagnostic-length bins, failure persistence and the 1,916 completed repair observations. `case_excerpts.json` retains full extracted candidate/diagnostic excerpts. `SOURCE_HASHES.json` identifies source bytes; `integrity_checks.json` records asserted audit counts.

Portable V7 provenance: `sources/v7_trajectory_views.json` is a new minimal derivative of 72 genuine local trajectories, captured during this audit. It retains exact candidate bytes/hash, recorded verification fields, metadata and cap details. It omits raw compiler stdout, personal file paths and other unused content. Original local source paths and SHA-256 are recorded, but those raw files were not part of the independently indexed V8 archive. New hashes do not retroactively authenticate history. The derivative enables clean-checkout reproduction and is not a regenerated experiment. `capture_v7_views.py` documents its one-time creation and refuses to overwrite an existing view. Default analysis only reads the committed view, checking any available local originals against captured digests. V8 sources come directly from the frozen hash-verified ZIP. Study 1 excerpts use already published redacted views.

All generated analyses are post-hoc and descriptive. Existing PR20 paired intervals, seed dependence, repair budgets and overlap sensitivities are reused; no new inferential efficacy claim is made. Independent mathematical/NL review, manuscript integration, bibliography reconciliation and any newly authorized controlled experiment remain separate tasks.
