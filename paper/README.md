# TAIMMA 2027 manuscript

The final-study paper is generated from validated actual local MLX experiment artifacts. The historical `compiled_pre_results.pdf` and earlier inventory/illustration scripts retain their historical scope; manual traces and neutral backend checks are excluded from study results.

The frozen final protocol is `configs/repair_experiment_local_v0.4.2.json`. Dataset eligibility uses the supervisor-approved AI-assisted method as reported by the student on 28 October 2026, with no original approval document or independent verification invented. The dataset has 15 development and 60 held-out examples in disjoint curated family clusters. The final experiment uses seed 2027, a fixed reviewed Lean target and the same initial proof for A/B/C.

After genuine held-out execution and analysis complete, `scripts/render_final_study.py` generates actual tables/figures/examples, `paper/scripts/write_final_manuscript.py` writes `main.tex` and a claims manifest, and `paper/scripts/build_final_manuscript.py` compiles `compiled_final_manuscript.pdf` using official Springer LNCS files and Tectonic. `scripts/finalize_completed_study.py` coordinates this automatically with the full tests, Lean build and result validation; it never generates results or commits/merges code.

Exact runtime, template/archive hashes, actual build logs and final PDF/source hashes are recorded under `data/final_study/v1/`. See [reproduction](../docs/FINAL_EXECUTION_REPRODUCIBILITY.md), [paper readiness](../docs/FINAL_PAPER_READINESS.md), and [claims/evidence](claims_to_evidence.md). The agent executes the pipeline; these commands document reproduction rather than requesting manual work from the student.

Author metadata is Sadia Peerzada, `sadiapeerzada2006@gmail.com`. No affiliation was supplied. Conference-specific submission constraints and final submission remain external decisions.
