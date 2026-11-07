# Clean-release archive decisions (7 November 2026)

This is a supervisor-requested **current-checkout scope classification**, not a history rewrite, independent replication, privacy clearance, or approval of the research.

| Path | Supervisor recommendation | Action in current tree |
| --- | --- | --- |
| `paper/` | Exclude | Already removed by PR #37 |
| `submission_20261031/` | Exclude | Already removed by PR #37 |
| `submission_20261103/` | Exclude | Already removed by PR #37 |
| `publication/paper/` | Exclude | Already removed by PR #37 |
| `publication/post_hoc/paper/` | Exclude | Already removed by PR #37 |
| `RUN_REPORT.md` | Exclude | Removed from current tree; [historical copy](https://github.com/sadiapeerzada/Compiler-Guided-Proof-Repair-in-Lean-4/blob/a201fbd38ff730eacaf0025b874192285debd9ca/RUN_REPORT.md) remains in Git history |
| [`docs/figures/`](figures/README.md) | Review | Reviewed and **archived in place**: four early prototype PNGs, not current manuscript figures |
| [`data/review_packets/`](../data/review_packets/ARCHIVE_STATUS.md) | Archive | **Archived in place**: versioned candidate/review records |
| [`data/analysis/`](../data/analysis/ARCHIVE_STATUS.md) | Archive | **Archived in place**: intermediate and pre-freeze analyses |
| [`research/ai-confirmatory-study/`](../research/ai-confirmatory-study/ARCHIVE_NOTICE.md) | Archive | **Archived in place**: separate historical research stream, not V7/V8 |

## Why the remaining material is archived in place

These data and figures remain publicly tracked at their **original paths**, not physically moved to a new folder. Older scripts, exact source-hash inventories, historical records and references use these filenames. Moving or rewriting thousands of historical files would risk breaking provenance and tests without improving the current paper. Archive notices distinguish them from the current published evidence; this is **classification rather than access control or deletion**.

The removed manual demonstration must not be interpreted as autonomous model output or final pass@1. Its SHA-256 entry in `data/verification/completion_20261027/source_hashes.json` is a historical record referring to an old checkout, not an assertion that the original path still exists.

## What the two-study paper actually relies on

The six Table 10 locations remain intact: [V7 outcomes](../research/study2-v7/test/outcomes.csv), [V7 protocol](../research/study2-v7/test/plan.json), [V8/V9 indexed records](../research/study2-raw-v8-v9/), [current descriptive analysis](../analysis/taimma_20261104/), [supervisor audit](../analysis/taimma_supervisor_final/) and [Lean overlap validation](../analysis/taimma_final_professor_validation/). Study 1 redacted evidence and archives remain in [publication/](../publication/).

**No frozen experimental data, results CSV/JSON, model outputs, verification certificates, raw archive members, inference scripts, or experiment manifests were deleted or modified by this cleanup.**

## Outstanding decisions

Human benchmark adjudication, privacy-warning review and third-party rights verification remain **OPEN**, as documented in [release readiness](RELEASE_READINESS.md). Archive labels do not close those gates, make public distribution automatically safe, or purge old Git commits.

Read-only checks from the repository root:

```bash
python3 scripts/check_clean_release_scope.py
python3 scripts/check_no_manuscript.py
python3 scripts/check_manuscript_evidence.py
```
