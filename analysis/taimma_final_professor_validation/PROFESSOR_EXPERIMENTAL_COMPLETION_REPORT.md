# Professor experimental-evidence completion handoff

Audited commit: `a3a709c383ceb016de3e746f962e543bbcc8b2a5` in https://github.com/sadiapeerzada/Compiler-Guided-Proof-Repair-in-Lean-4. Merged PRs #19–21 already provide most requested evidence. This small addition supplies verification, first-repair token reconstruction, explicit control checks and new local overlap certificates. Existing reports/results are cited and preserved; no manuscript or experimental record is edited.

## 1. Lean diagnostics versus trusted verification

Already implemented: strict verifier and PR21's failure/case distinction. Verified now: `src/verify.py` matches the frozen plan hash; recorded candidate/source/verification bindings and accepted-call axiom policies agree. Compiler frontend, elaborator and tactic messages are distinct from kernel checking of proof terms. See EXPERIMENTAL_CONTROL_VERIFICATION.md and `verification_results.json::controls`. Human review is still needed for NL/benchmark meaning.

Factual summary: “Compiler and elaborator diagnostics describe failed candidates; accepted proofs additionally satisfy the fixed-theorem and allowed-axiom verification policy. A changed error is not a verified proof.”

## 2. Novelty and contribution evidence

Already implemented: `analysis/taimma_supervisor_final/RELATED_WORK_COMPARISON.md`, PR20 paired/theorem/cost tables and authentic PR21 cases. Verified now: aggregate counts, coverage implications and controls are grounded in original records. New evidence is the detailed control reconstruction and structural relationship checks, not a new repair algorithm. Literature/bibliographic expert judgment remains separate; the existing APRIL metadata issue is not silently corrected.

Factual summary: “This local quantized-model investigation separates additional attempts, diagnostic-bearing feedback, shuffled feedback and resampling, while reporting their attribution limits, theorem coverage and costs.”

## 3. Controlled and uncontrolled variables

Already implemented: Study1 frozen v0.4.2 protocol and Study2 plans/runner. Verified now: shared initial candidates, fixed targets, maximum calls, deterministic per-arm seed derivation, Study2 rotation and raw prompt/donor bindings. See EXPERIMENTAL_CONTROL_VERIFICATION.md, TOKEN_MATCHING_VERIFICATION.csv and `verification_results.json::study1_controls`/`controls`. Study1 uses fixed B-then-C order and one seed; Study2 rotates five policies across three seeds. No human judgment is needed to read these implementation facts, but benchmark independence still requires it.

Factual summary: “C versus B equalizes maximum repair calls, not realized compute, input tokens, sampling draws or later trajectories. The studies are separate protocols.”

## 4. Statistical conclusions and dependent observations

Already implemented: PR20 clustered intervals; Study1 recovery and missingness accounting. Verified now with independently coded cluster resampling: all paired cells and intervals match PR20. See STATISTICAL_INTEGRITY_REPORT.md and `validate.py::independent_cluster_interval`. Family resampling preserves unequal sizes and uses a row-weighted ratio. No historical interval is replaced. The old handoff discrepancy remains unresolved because its exact pooled recipe is unavailable.

Factual summary: “V7 C−B is +6.94 pp (theorem-cluster 95% −1.39 to +18.06); C−D is +1.39 pp (−5.56 to +9.72). Eight-family sensitivities also include zero. Three seeds repeat 24 nominal theorem types; mathematical overlap may further reduce independence. Inconclusive intervals do not establish equivalence.”

## 5. Benchmark overlap and validity

Already implemented: PR21 signed-review worksheet and archived formal screens. Verified now: all 12 development and 24 test statement/reference hashes match the frozen audit; exclusion denominators and retained successes reproduce. New evidence: OverlapCertificates.lean and lean_certificate_check.json record seven locally checked certificate declarations for the five flagged pairs. BENCHMARK_OVERLAP_EVIDENCE.csv gives exact statements and directional relationships. These checks establish the displayed transports, not independent benchmark approval. HUMAN_ADJUDICATION_REQUIRED.md preserves the independent-review requirement.

Factual summary: “Formal reference acceptance does not establish benchmark independence. Removing overlap-related failures changes denominators 72→66→63→60 while B/C/D successes remain 5/10/9; it creates no new success or untouched held-out benchmark.”

## 6. Token matching and diagnostic attribution

Already implemented: arm E and PR21 observational lengths. Verified now: all 68 V7 and 61 V8 eligible first repairs match actual C prompt lengths within ±1 token, satisfying the recorded ±3 tolerance. Later E targets use E's predecessor and differ from actual C prompt lengths; this does not contradict the own-history matching flags. The recorded feedback-length measure includes the chat wrapper because it uses `MLXModel.count`, unlike plain prefix-cap encoding. See TOKEN_MATCHING_VERIFICATION.csv and EXPERIMENTAL_CONTROL_VERIFICATION.md.

Factual summary: “First-repair matching is supported, but it does not equalize full histories, cumulative costs or sampling. V7 C/D verify 10/9 evaluations while D covers seven theorem types versus C's four; V8 B/C/D/E adds no repair beyond its 11 initial successes.”

## 7. Artifact verification and public reproduction boundaries

Already implemented: PR19 archive, PR20 hash lock and PR21 derivative views. Verified now: frozen V7 outcome/plan/source hashes, all 4736 indexed archive members, all 40 lock entries, source-bound cases and offline tests. See REPRODUCIBILITY_FINAL_VERIFICATION.md and TEST_RESULTS.md. The privacy scan lists 1220 affected-file warning records totaling 22882 local-path occurrences. No manual privacy clearance is asserted. V7 raw history remains locally sourced and weaker than the indexed V8 evidence; model weights/caches/hardware are not reproduced.

Factual summary: “Reproducible summaries and hash consistency are distinct from inference replay, historical Lean-candidate replay and independent expert approval. The new local relationship certificates have their own explicitly bounded check.”

## 8. Technical facts for accurate presentation

Already implemented: PR20 and PR21 scientific handoffs, case studies, resource tables and sourced related-work table. Verified now: Study1 A 0/60, B 1/60, C 1/58 observed, 58 complete B/C pairs sharing one success; V7 A/B/C/D/E/R 4/5/10/9/5/5; V8 11/11/11/11/11/14; V9 development-only 5/12 versus 5/12. Repetition 111/197 and 178/183, V7 16 changed-category/unverified calls and every recorded budget endpoint agree. See DIAGNOSTIC_AND_FAILURE_AUDIT.md. Case selection is post-hoc illustrative, not an efficacy sample.

Factual summary: “Report each study separately, retain unavailable outcomes as unknown, distinguish theorem coverage from aggregate counts, and label additional analyses post-hoc.”

No new experiment is necessary to make the requested conservative manuscript corrections. Independent human benchmark adjudication and any stronger diagnostic-specific causal claim remain unresolved. A stronger efficacy claim would require separately authorized new evidence; it is not produced or needed to accurately report these studies. The author retains all LaTeX, bibliography, figures, PDF and submission work.
