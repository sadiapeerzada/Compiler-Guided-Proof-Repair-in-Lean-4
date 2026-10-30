# Compiler-Guided Proof Repair in Lean 4: A Controlled Local-Model Pilot on Fixed Theorem Types

<!-- POST_HOC_CURRENT -->
The latest [post-hoc manuscript](outputs/post_hoc/manuscript/post_hoc_pilot.pdf) (15 pages) uses the title above. [Post-hoc results and caveats](outputs/post_hoc/SUMMARY.md) include original-data process analyses, calibrated uncertainty and a separately frozen development-only placebo control. The original held-out outcomes are unchanged; Study 2 model execution remains deferred.
<!-- POST_HOC_CURRENT -->


The [final submission review](docs/FINAL_M1_M7_COMPLIANCE_REPORT.md) maps the actual study to the professor’s supplied requirements. **Full-compliance submission: NO-GO** while M1/M2/M3 remain partial. The reduced fixed-theorem empirical pilot is prepared for supervisor review. M4/M5/M6 and the M7 empirical manuscript rewrite are complete in their documented scopes.

Observed results are **A 0/60, B 1/60, C 1/58**, with two unavailable C outcomes. On the **58 complete pairs**, B and C each succeed on the same target (1/58, 1.72%); no advantage or equivalence is established. C=1/60 is the separately planned missing-as-failure sensitivity. The possible full-cohort C−B difference spans 0 to +3.33 percentage points when the missing C outcomes are varied.

The frozen 15-development/60-test dataset contains five mathematical categories with no curated family crossing the split. The study uses one Qwen2.5-7B-Instruct MLX 4-bit snapshot, one seed and a three-case development pilot. It measures proof synthesis for supplied reviewed theorem types, not autonomous NL-to-statement or end-to-end semantic accuracy. Pretest public publication of the final IDs/hash is not evidenced; the internal freeze is preserved.

The revised [14-page Springer manuscript](paper/compiled_final_review_v2.pdf) reports the actual low success, genuine before/after cases, compiler taxonomy, uncertainty, AI-review limitations and public/private reproducibility boundary. See [corrected results](docs/FINAL_EXPERIMENT_RESULTS.md), [pairing audit](docs/PAIRED_COMPARISON_AUDIT.md), [missing outcomes](docs/MISSING_C_OUTCOME_INVESTIGATION.md), and [submission gate](docs/FINAL_SUBMISSION_GATE.md).

All original final-study evidence remains unchanged under `data/final_study/v1/`. New append-only reconstruction and verification artifacts are under `data/final_review/20261029_v2/`; private command logs remain in its ignored `local/` subdirectory. The final revision passed 297 tests / 28 subtests, the Lean build, a fresh reference batch, strict reverification of both model successes, full model/tokenizer hashing and deterministic metric regeneration. No new model inference was executed for that earlier review revision.

The previously approved redacted release was merged into public `main` under `publication/`. This newer revision is on a local review branch and separate publication staging branch; it has not been pushed or merged. Only a newly reviewed, exact file inventory may be approved for publication. Author/contact information is withheld in the proposed public manuscript. Historical manual demonstrations, exploratory pilots and earlier reports remain historical and never enter model accuracy estimates.
