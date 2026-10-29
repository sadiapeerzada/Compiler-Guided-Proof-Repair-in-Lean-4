# Final corrected experimental results

The primary observed and complete-case rates are separated from the internally frozen missing-as-failure sensitivity. There is no autonomous Stage-A or end-to-end accuracy estimate.

| Condition | Success / observed | Rate | Wilson 95% | Known failures | Unavailable |
|---|---:|---:|---|---:|---:|
| A | 0/60 | 0.00% | [0.00, 6.02]% | 60 | 0 |
| B | 1/60 | 1.67% | [0.29, 8.86]% | 59 | 0 |
| C | 1/58 | 1.72% | [0.31, 9.14]% | 57 | 2 |

The primary B/C comparison uses **58 complete pairs**, with B=C=1/58 (1.72%) on the same target, `lib_a_exp_add`. C−B is 0.00 percentage points and there are zero discordant pairs. The frozen helper reports McNemar as `null` / non-informative; conventionally p=1. Neither is evidence of equivalence. Complete-pair problem/family bootstrap intervals [0,0] are conditional on observed pairs, not missingness uncertainty. The matched subset has 52 family clusters; all 60 statements occupy 54.

The frozen protocol explicitly defines full-denominator missing-as-failure **sensitivity**. Under that coding C=1/60 (1.67%), with Wilson interval [0.29,8.86]%; it is not 60 measured C outcomes. Both missing C cases failed in B, so possible full-cohort C−B effects span 0 to +3.33 percentage points. These are identification bounds, not confidence limits or an equivalence margin.

- C_vs_B: 58 matched cases; difference +0.00 percentage points; family-cluster interval [+0.00, +0.00]; exact p=None; Holm p=None.
- C_vs_A: 58 matched cases; difference +1.72 percentage points; family-cluster interval [+0.00, +5.66]; exact p=1.0; Holm p=1.0.
- B_vs_A: 60 matched cases; difference +1.67 percentage points; family-cluster interval [+0.00, +5.45]; exact p=1.0; Holm p=1.0.

There are **410 completed held-out responses**: 60 initial, 178 B repairs and 172 C repairs. The **412 durable logical intents** include one preflight context rejection and one header-only interruption; they are not 412 confirmed completed inference calls. The final frozen pilot has three cases / 21 responses, excluded from test estimates. No new inference was run during this revision.

Known physical completed-response totals: 362,035 input tokens, 130,401 output tokens, 11,233.6 native generation seconds. Shared initials are counted once physically and once per counterfactual condition row. Completed repairs per eligible case: B mean 2.97, C mean 2.87; C consumed-intent mean 2.90; both medians are three. Full resource distributions, including medians, are machine-readable. The same 58 complete cases have 230 completed responses per condition (including initials); paired per-problem resource comparisons are in `paired_resources.json`. No cost or duration is imputed for the unavailable response; completed-only costs are not full-run cost estimates.

One seed (2027), low success, related families, author-assisted AI adjudication, library/pretraining exposure, B-before-C order, cached loads and observed shared-host activity limit inference. No supported superiority, equivalence or causal latency claim is made.

Canonical reconstruction: `data/final_review/20261029_v2/analysis_verified/results.json`. Deterministic repeat: `analysis_repeat/results.json`. Original `data/final_study/v1/analysis/` is unchanged historical evidence. Every revised table/figure uses the canonical reconstruction; qualified old all-60 estimates remain separately labeled rather than overwritten.
