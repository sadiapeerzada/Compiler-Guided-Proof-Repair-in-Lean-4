# Compiler-Guided Repair for Natural-Language-to-Lean Formalization

Provenance: controlling checklist supplied directly by the user in this conversation on 29 October 2026. The report identifies its review date as 20 October 2026. This repository transcription records the supplied requirements; it is not independently authenticated supervisor correspondence. AI-review and local-MLX substitutions remain separately student-reported approvals.

For the research student | Target: TAIMMA 2027 (Springer CCIS) | Review date: 20 October 2026

## 1. Overall decision

Decision: MAJOR REVISION. The proposed topic fits the conference, and the software provides a useful technical foundation. However, the present evidence is inadequate for a defensible empirical research paper. Submission is recommended only after the mandatory experiments and reporting corrections below are completed.

Acceptance is not guaranteed by completing a checklist. The objective is to remove the principal reasons a reviewer would reject the study: unvalidated performance claims, missing controlled baselines, insufficient test data and uncertainty about semantic correctness.

## 2. Findings from the existing repository

- **Positive:** A four-stage NL-to-Lean pipeline, Lean verification, repair prompts, automated tests, run metadata and support for several configurations are already implemented.
- **Major validity issue:** The historical 20/20 successful core-Lean proofs were compiler-checked, but proof generation and repairs in that run were performed manually, not by the configured API-driven LLM. They are demonstrations, not autonomous model accuracy.
- **Very limited real-run evidence:** The separate Mathlib results file contains only two cases (one successful after repair, one unsuccessful). These cannot support a general empirical conclusion.
- **Missing causal comparison:** The current no-sketch and fast-model variants do not establish whether compiler error feedback helps more than repeated attempts without feedback.
- **Formal correctness is not semantic correctness:** Lean accepting a proof does not show that the generated theorem expresses the original natural-language claim. Stage A needs independent evaluation.
- **Dataset and reporting gaps:** The seed set is small, includes closely related tasks, and lacks a frozen independent research split and complete provenance. The README must not label historical final solved rate as model pass@1.
- **Environment mismatch:** Historical run documentation refers to Lean 4.14.0, while the present toolchain file selects v4.33.0-rc1. Final comparisons must use a single documented environment.

## 3. Minimum changes required before submission (mandatory)

**M1. Execute genuine automated runs.** Run the present pipeline with a real model API from the input NL statement to the final compiler verdict. Save the complete per-attempt records, initial outputs, compiler diagnostics, final outcomes, model identifiers, token consumption, timings and experiment configuration. Do not use manually written proofs in the reported experimental results.

**M2. Build a frozen independent test set.** Prepare at least 60 distinct held-out test statements, preferably 100, spanning at least five existing categories. Keep 15–20 separate development items for debugging. Avoid duplicate or near-duplicate theorem families across development/test. Record problem source, reference Lean statement, category, and difficulty. Publish the fixed IDs and dataset hash before running the test experiments.

**M3. Add the critical feedback baseline.** Implement and compare (i) no-repair one-shot, (ii) retry/repair without compiler errors, and (iii) repair using real compiler errors. Use the SAME first failed candidate, SAME model, SAME formal theorem, SAME prompt budget and SAME maximum number of retries for the paired repair conditions. Limit all repaired conditions to three repair calls unless pre-registered otherwise.

**M4. Check semantic faithfulness.** Have a competent Lean reviewer inspect the NL-to-Lean statements for the held-out dataset and label faithful / not faithful / uncertain. For the principal repair comparison, use the identical fixed human-reviewed Lean theorem in all conditions; report end-to-end NL-to-Lean success separately. A compiling but mistranslated theorem is not an end-to-end success.

**M5. Repair the metric definitions.** Report first-attempt verified success, success within the repair budget, improvement over no-feedback repair, success by error type, number of repair calls, total tokens, and time. Include denominators and uncertainty intervals. Do not present final manually achieved success as pass@1; report at least one paired significance test (e.g., McNemar test for matched success/failure outcomes).

**M6. Reproduce results under one pinned environment.** Choose a stable Lean and compatible Mathlib version, then run all comparison methods under the same pinned commit/toolchain. Check every claimed final proof against forbidden shortcuts (including sorry/admit and unapproved assumptions), and preserve the run manifest and artifact hashes.

**M7. Rewrite the paper around an empirical finding.** The contribution is not that a repair loop was built. Frame it as: “Does compiler diagnostic feedback improve repair compared with equally budgeted retries, and for which errors?” Include recent related work, baselines, failure analysis, limitations, and complete reproducibility details.

## 4. Minimum experimental protocol

Use one primary LLM across all conditions. Three repeated runs with fixed, documented random seeds are preferred; if resources limit repetitions, disclose this as a limitation rather than overstating statistical certainty. The central comparison must be paired at the problem/candidate level.

| Condition | Input after the same initial failure | Retries |
|---|---|---|
| A. One-shot | Initial model output; no repair | 0 |
| B. Blind retry (baseline) | Previous candidate plus generic retry instruction; no compiler diagnostics | Up to 3 |
| C. Compiler-guided (proposed) | Previous candidate plus genuine Lean diagnostic message | Up to 3 |

Optional, only after A–C are completed: compare full diagnostic output against a concise error summary, or run a second model. These are valuable extensions but should not displace the basic controlled experiment.

## 5. Minimum figures and tables required in the manuscript

**Table 1.** Dataset composition: number of problems by category and difficulty, source/provenance, development/test counts.

**Table 2.** Head-to-head results for A/B/C: initial success, post-repair success, improvement, average repair attempts, tokens and wall-clock time.

**Figure 1.** Verified success versus allowed number of repair calls (0, 1, 2, 3), using consistent denominators.

**Figure 2 / Table 3.** Compiler-error taxonomy and success rate after repair for each sufficiently represented category.

**Table 4.** Semantic faithfulness: correct/incorrect/uncertain statement translations, with examples of failure.

Include a small qualitative error analysis with at least five representative examples, both successful and unsuccessful, showing the compiler message and the actual change in the proof.

## 6. Paper structure and writing corrections

Use the conference-prescribed Springer format. Recommended sections: Introduction and research questions; Related work; Pipeline and verification safeguards; Dataset and experimental protocol; Results and statistical analysis; Error analysis and semantic faithfulness; Threats to validity; Conclusion. Cite directly relevant Lean autoformalization and proof-repair systems; explain precisely what the present controlled comparison adds beyond them.

The current README and historical charts must explicitly identify manual demonstrations as historical. Do not state “20/20 LLM pass@1” or “compiler verification guarantees NL meaning.” Use only numbers computed from independently reproducible API-run logs.

## 7. Required delivery schedule

| Deadline | Required evidence to submit for review |
|---|---|
| 22 Oct | Final questions, frozen protocol, primary model, toolchain and baseline implementation plan |
| 25 Oct | Successful end-to-end API pilot; complete per-attempt traces and proof checks |
| 29 Oct | Frozen dataset; paired A/B/C runs completed; raw results and summary script |
| 31 Oct | Tables, uncertainty estimates, semantic audit and failure taxonomy |
| 03 Nov | Complete conference-format manuscript with references and limitations |
| 04 Nov | Rechecked results, claims and final independent manuscript review |
| 05 Nov | TAIMMA submission deadline in the attached CFP |

## 8. Final submission gate

Do not submit until each of the following is demonstrably complete: (1) genuine API-generated results; (2) a frozen, independently checked test set; (3) a valid no-feedback retry baseline; (4) comparable budgets across methods; (5) semantic evaluation; (6) correctly named metrics and reproducible evidence; and (7) a manuscript whose claims match its results. If these cannot be completed by the deadline, reduce the claims and consider a short empirical pilot rather than presenting unvalidated results as a full study.

Expected outcome: With these minimum corrections, the work becomes a credible conference submission rather than only a promising software demonstration. Whether it is accepted will depend on the observed results, their novelty relative to current literature, reviewer evaluation and venue standards.
