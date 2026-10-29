# Final M1–M7 compliance report

The frozen single-seed study reached terminal records for all 60 cases, with 58 complete A/B/C comparisons and two unavailable C outcomes. Technical delivery does not imply full completion of every requested experiment. The student-reported substitutions and explicit execution instruction cover M1–M6; no further experiment approval is required. Negative or unverified model outputs are retained as outcomes, not repaired manually. No automatic merge or submission occurred.

The user directly reported supervisor approval of AI-assisted semantic review replacing independent human semantic review, and free local MLX replacing Groq. Report date: **28 October 2026**. Actual supervisor decision date is unknown. Evidence is the student's direct report, **not independently verified**; no supervisor document, identity, signature or original date has been invented. Exact implementation choices were made under the user's explicit execution authorization.

| Requirement | Status | Delivered evidence | Exact remaining work / limit; approval needed |
|---|---|---|---|
| M1 genuine generation | COMPLETE | 60 frozen held-out cases, actual MLX generations and Lean checks | One planned seed, not three-seed robustness |
| M2 dataset | COMPLETE | 15 development / 60 test, five categories, source evidence, ordered hashes, no cross-split curated family overlap | AI-policy eligibility; 54 test families, not 60 independent families |
| M3 A/B/C | PARTIAL | One shared initial, matched model/environment/output budgets, at most three B/C repairs, no B diagnostics, latest genuine C diagnostics | 58 complete pairs; two unavailable C outcomes retained without replay; final pilot covers 3 of 15 development items |
| M4 semantics | COMPLETE | 75 source-eligible AI-adjudicated references, corrected/reviewed original pairs preserved, zero invented human reviews | AI adjudication is not measured human semantic accuracy |
| M5 analysis | COMPLETE | Actual rates, intervals, exact McNemar/Holm, family sensitivity, calls/tokens/timing, error outcomes and authentic examples | No unsupported significance or equivalence claim |
| M6 verification | PARTIAL | 293 Python tests and 28 subtests; Lean build; dataset/result validators; source/evidence hashes | Full diff whitespace check flags preserved evidence; tests, Lean and scientific artifact validation pass. Reproduction remains backend/hardware scoped |
| M7 paper | PARTIAL | Actual empirical methods/results, four required numbered tables, two figures, qualitative examples, compiled PDF | No institutional affiliation supplied; venue-specific final submission checks remain; separate submission authorization needed |

| Condition | Verified | Rate | Wilson 95% (%) | Missing | Repair attempts |
|---|---:|---:|---|---:|---:|
| A | 0/60 | 0.0% | [0.0, 6.0] | 0 | 0 |
| B | 1/60 | 1.7% | [0.3, 8.9] | 0 | 178 |
| C | 1/60 | 1.7% | [0.3, 8.9] | 2 | 174 |

`data/final_study/v1/` contains the frozen datasets, policy, reported approval, corrections, pilot audit, launch record, actual runs, analysis and final verification. The final protocol is `configs/repair_experiment_local_v0.4.2.json`.

Final protocol SHA-256: `a032110d7afbc367c2daa820bd17511c6ff5dba2d1164e0130ea5d1c4b693317`. Final PDF: `paper/compiled_final_manuscript.pdf`, SHA-256 `58eaadcc2680bbd1c787dee3ca821b513fffe664af6a705748d36d117974d7ac`. Source implementation was committed before held-out generation at `fe8fbee15d8d96a9f0d6512f4d0e568f00a957b3`. Original Groq, pre-results artifacts and exploratory protocols/runs are preserved and excluded from empirical estimates.

Limits: one primary seed (2027), one general instruction model and quantization; 60 test statements in 54 curated family clusters, rather than 60 independent topic families; five development clusters; author-assisted AI adjudication and unreliable independent-model judgments; named-lemma/pretraining exposure; fixed-theorem proof synthesis rather than unrestricted NL translation; B-before-C order and host/cache effects on timings. These limits remain explicit rather than being concealed as completed multi-seed or independent-human validation.
