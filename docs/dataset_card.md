# Final-study dataset card

The approved-method frozen dataset contains **75 eligible statements: 15 development and 60 held-out test examples**. Exact ordered IDs, file hashes, policy and adjudication hashes are in [freeze.json](../data/final_study/v1/freeze.json). Use [the final-study reproduction guide](FINAL_EXECUTION_REPRODUCIBILITY.md) and [completion report](FINAL_DATASET_COMPLETION.md) for validation and delivery status.

The 96-candidate pool comprised 21 original drafts, 16 textbook acquisitions and 59 formal-library adaptations. All 16 textbook and 59 library candidates are retained; one exact duplicate and 20 other source-insufficient originals are excluded. The missing positive-modulus assumption and ambiguous summation endpoints were corrected and checked again, but these corrected original candidates remain excluded for inadequate source provenance. Original records, prior versions and all corrections are preserved.

The 16 textbook items retain CC BY-SA source evidence; 59 library adaptations retain Apache source evidence and attribution. These are AI-assisted license assessments using published notices, not invented publisher permission or independent legal clearance. English paraphrases are author-assisted adaptations, not quotations falsely attributed to the source. See [attribution](../data/final_study/v1/ATTRIBUTION.md).

Development category counts are arithmetic 2, divisibility 3, induction 6, inequalities 1 and modular arithmetic 3. Test counts are 11, 17, 8, 15 and 9 respectively. Development and test occupy five and 54 curated family clusters with no overlap. These counts do not imply 75 independent mathematical topics; family-level dependence, named-lemma exposure and possible training contamination remain limitations.

Eligibility uses the versioned [AI policy](../data/final_study/v1/ai_eligibility_policy.json), content-bound adjudication, strict Lean reference/type checks and archived source evidence. The supervisor's acceptance of AI-assisted review and local MLX is student-reported on 28 October 2026; the original decision date/document and independent verification are unavailable. No record is labeled independently human-reviewed. Historical human-only import and eligibility rules remain intact for that workflow.

Lean is 4.32.0 with Mathlib commit `81a5d257c8e410db227a6665ed08f64fea08e997`. The experiment supplies fixed English plus the reviewed Lean target; its outcome is strict proof synthesis, not unrestricted natural-language-to-statement translation or measured human semantic faithfulness.
