# Semantic review status

The operative final-study method is **AI-assisted semantic review**, approved according to the student's direct report on 28 October 2026. The actual supervisor decision date and original approval document/signature were not supplied; the report has not been independently verified. See [the approval record](../data/final_study/v1/approvals/student_reported.json).

All 96 candidate records were inspected through the [AI audit](AI_SEMANTIC_AUDIT_REPORT.md), including separate Phi-family reviews, coding-assistant adjudication, Lean proof/type checks and bounded mathematical probes. The final adjudicator is the authoring coding assistant, not an independent human. Raw model disagreements, malformed responses and specific resolutions remain inspectable; unreliable responses are not silently counted as faithful votes.

The versioned [AI eligibility policy](../data/final_study/v1/ai_eligibility_policy.json) admits 75 source-supported statements: 15 development and 60 held-out, in five and 54 curated family clusters with no cross-split cluster overlap. Each row binds its English, Lean target, source/license evidence, strict reference proof, AI adjudication and split assignment. One exact duplicate and 20 other source-insufficient candidates are excluded. Corrected modulus and summation examples retain correction history, fresh proofs and repeated model reviews; both remain excluded for source provenance. See [the frozen dataset](../data/final_study/v1/freeze.json).

This establishes eligibility under the approved AI policy, not measured human semantic accuracy. Compilation alone does not establish English/Lean equivalence. The final experiment fixes the reviewed reference target and measures proof synthesis, not unrestricted statement translation.

Historical human-review fields and blank decisions are preserved. `src/semantic_review.py` still requires actual externally verified human reviewer identity, independence and evidence. AI decisions are never imported as human reviews. The final study uses the separate `study_eligibility` field and `src/final_study.py`; a historical human-only readiness failure does not constitute failure of that explicitly different policy.

The earlier [supervisor request](AI_SEMANTIC_REVIEW_SUPERVISOR_REQUEST.md) remains a historical proposal, not the approval document. Current approval provenance is only the student-reported record above.
