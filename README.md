# Compiler-Guided Repair for Natural-Language-to-Lean Formalization

Research target: TAIMMA 2027 / Springer CCIS. The final study uses genuine free local MLX inference and strict Lean verification. Current execution and delivery status are recorded in [the final results report](docs/FINAL_EXPERIMENT_RESULTS.md) and [M1–M7 report](docs/FINAL_M1_M7_COMPLIANCE_REPORT.md); no improvement or significance is assumed before actual analysis.

The frozen approved-method dataset contains **15 development and 60 held-out examples**, selected from 96 audited candidates. One exact duplicate and 20 other source-insufficient originals are excluded. The splits have no curated theorem-family overlap; they contain five and 54 family clusters respectively, not 75 independent topics. See [dataset card](docs/dataset_card.md), [freeze](data/final_study/v1/freeze.json) and [AI review status](docs/SEMANTIC_REVIEW_STATUS.md).

The student directly reported supervisor acceptance of AI-assisted semantic review and local MLX on 28 October 2026. The [approval record](data/final_study/v1/approvals/student_reported.json) identifies that evidence status: actual decision date, original document/signature and independent verification were not supplied. AI reviews are never labeled independent human reviews. Historical human-only gates remain intact; the final versioned AI policy uses separate eligibility fields.

The controlled comparison is:

- **A:** one initial candidate, no repair.
- **B:** that identical initial candidate, up to three blind repairs without compiler diagnostics.
- **C:** that identical initial candidate, up to three repairs using the immediately preceding genuine compiler diagnostics.

All conditions use the same fixed English/reviewed Lean target, immutable Qwen2.5-7B-Instruct MLX snapshot, decoding limits and Lean environment. The task measures proof synthesis for a supplied reference type, not unrestricted English-to-statement translation. The [final protocol v0.4.2](configs/repair_experiment_local_v0.4.2.json) was frozen before held-out generation; [the original Groq protocol](configs/repair_experiment_protocol_v0.2.0.json) remains historical provenance. One primary seed, 2027, limits robustness claims.

## Execution and reproducibility

The agent executes the full study automatically. `scripts/audit_and_execute_final_study.py` audits the actual pilot and zero-call resume, then runs all held-out trajectories and validated paired analysis. `scripts/finalize_completed_study.py` waits for genuine analysis before rendering actual tables/figures, writing the manuscript, running tests/Lean/result validation, compiling the PDF and writing the four FINAL reports. Neither script commits, merges or submits a paper.

Raw output, per-token streams, every repair, diagnostics, hashes, token counts and timing are preserved under `data/final_study/v1/final_runs/`. Durable interrupted attempts consume their budget; missing output is never silently regenerated. See [the reproduction guide](docs/FINAL_EXECUTION_REPRODUCIBILITY.md) for exact commands, runtime and resume behavior. At most one model worker may run.

Lean is 4.32.0 and Mathlib is `81a5d257c8e410db227a6665ed08f64fea08e997`. The primary model snapshot and every weight/tokenizer/template file are hash-bound in [the inventory](data/local_model/20261027/model_inventory.json). Model weights and TeX binaries are not committed; no paid inference or API fallback is used.

## Manuscript and limitations

The [manuscript workflow](paper/README.md) produces `paper/compiled_final_manuscript.pdf` only from actual validated results. The [pre-results PDF](paper/compiled_pre_results.pdf), manual historical traces, neutral checks and development prototypes retain their historical scope and never enter study estimates. [Claims and evidence](paper/claims_to_evidence.md) distinguish measured proof success from semantic accuracy, AI adjudication from human review, and published license evidence from independent legal clearance.

The author is Sadia Peerzada, correspondence `sadiapeerzada2006@gmail.com`; no affiliation was supplied. Named-library-lemma exposure, possible pretraining contamination, one seed and correlated family clusters remain limitations. See [remaining publication actions](docs/REMAINING_HUMAN_ACTIONS.md).

Delivery is on `research/taimma2027-complete-study`; automatic merge into `main` and conference submission are not authorized. Historical preparation/audit snapshots and previous reports remain in version control and the final-study history directory.
