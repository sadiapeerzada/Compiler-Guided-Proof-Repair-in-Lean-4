# Historical research documentation index

[Current research overview](../README.md) · [Clean-release archive scope](ARCHIVE_SCOPE.md) · [Paper evidence](MANUSCRIPT_EVIDENCE_INDEX.md) · [Release readiness](RELEASE_READINESS.md)

The root README and its [manuscript evidence index](MANUSCRIPT_EVIDENCE_INDEX.md) describe the **current two-study paper**. The [17-file curated package](../publication/curated-release-20261107/) is a compact reader-facing companion, not the underlying complete research archive.

| Earlier artifact | Classification | Reader guidance |
|---|---|---|
| [Research roadmap](roadmap.md) | October 2026 planning | Not current experiment status |
| [Implementation plan](implementation_plan.md) | Previous engineering and protocol stage | Treat worktree observations as dated |
| [Final paper readiness](FINAL_PAPER_READINESS.md) | Earlier pre-results manuscript | Do not apply its zero-run state to V7/V8 |
| [Remaining human actions](REMAINING_HUMAN_ACTIONS.md) | Earlier revision and reviewer handoff | Evidence for those decisions is separate from an authentic sign-off |
| [Semantic review status](SEMANTIC_REVIEW_STATUS.md) | Earlier dataset/96-candidate review | Do not treat as completed independent benchmark adjudication |
| Prior paper drafts (removed from current tree) | Earlier manuscript versions | Consult separately retained copies; Git history still contains old commits |
| [Earlier release snapshots](../publication/) | Versioned Study 1 and post-hoc artifacts | Preserve version identity and third-party notices |
| [Early demonstration (historical Git commit)](https://github.com/sadiapeerzada/Compiler-Guided-Proof-Repair-in-Lean-4/blob/a201fbd38ff730eacaf0025b874192285debd9ca/RUN_REPORT.md) | Removed from current tree | Not held-out model evidence |
| [Prototype figures](figures/README.md) | Four archived-in-place historical PNGs | Not the current manuscript figures |
| [Historical review packets](../data/review_packets/ARCHIVE_STATUS.md) | Versioned curation records | Preserve paths and actual review statuses |
| [Intermediate analyses](../data/analysis/ARCHIVE_STATUS.md) | Previous readiness/analysis snapshots | Not the current two-study results |
| [Separate AI research stream](../research/ai-confirmatory-study/ARCHIVE_NOTICE.md) | Historical independent project stream | Not V7/V8 evidence |
| [Experimental input templates](../prompts/) | Real methodology and reproduction inputs | Preserve exact bytes and archived identities |

The original six Table 10 evidence locations remain in place; see [the manuscript index](MANUSCRIPT_EVIDENCE_INDEX.md). Historical documentation is retained rather than mass-moved because links, frozen manifests, source hashes and external citations may rely on the present paths. Git would also retain moved or deleted content in history.

A full tracked-file audit is available through `python3 scripts/audit_publication_surface.py --scope full`. Results must be interpreted by artifact class: a literal term match in a real experimental template is not proof of an unnecessary assistant instruction. The curated set can be tested separately with `--scope curated --strict`.
