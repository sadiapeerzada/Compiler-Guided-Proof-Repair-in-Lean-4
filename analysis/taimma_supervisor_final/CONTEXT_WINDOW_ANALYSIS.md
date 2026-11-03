# Observational context-window analysis

Observed test records contain no flagged C/D payload truncation and no context-limit terminal status. Maximum recorded prompt lengths are 513 tokens in V7 and 1489 in V8, below the declared 8192-token context cap even after the 1200-token output allowance. This cohort therefore cannot identify a truncation effect or behavior near the context boundary.

| study | arm | calls | mean_prompt_tokens | median_prompt_tokens | max_prompt_tokens | missing_prompt_tokens | context_statuses |
| --- | --- | --- | --- | --- | --- | --- | --- |
| V7 | A | 72 | 131.95833333333334 | 133.0 | 139.0 | 0 | initial |
| V7 | B_neutral | 203 | 199.4679802955665 | 182.0 | 306.0 | 0 | {"budget_exhausted": 67, "initial_verified": 4, "verified": 1} |
| V7 | C_real | 197 | 273.28934010152284 | 254.0 | 513.0 | 0 | {"budget_exhausted": 62, "initial_verified": 4, "verified": 6} |
| V7 | D_shuffled | 200 | 281.385 | 296.5 | 449.0 | 0 | {"budget_exhausted": 63, "initial_verified": 4, "verified": 5} |
| V7 | E_token_matched | 204 | 275.05392156862746 | 296.0 | 513.0 | 0 | {"budget_exhausted": 67, "initial_verified": 4, "verified": 1} |
| V7 | R_resample | 202 | 147.4851485148515 | 148.0 | 154.0 | 0 | {"budget_exhausted": 67, "initial_verified": 4, "verified": 1} |
| V8 | A | 72 | 131.95833333333334 | 133.0 | 139.0 | 0 | initial |
| V8 | B_neutral | 183 | 222.04918032786884 | 181.0 | 1339.0 | 0 | {"budget_exhausted": 61, "initial_verified": 11} |
| V8 | C_real | 183 | 351.88524590163934 | 326.0 | 1403.0 | 0 | {"budget_exhausted": 61, "initial_verified": 11} |
| V8 | D_shuffled | 183 | 342.5081967213115 | 326.0 | 1489.0 | 0 | {"budget_exhausted": 61, "initial_verified": 11} |
| V8 | E_token_matched | 183 | 352.1857923497268 | 327.0 | 1403.0 | 0 | {"budget_exhausted": 61, "initial_verified": 11} |
| V8 | R_resample | 178 | 147.29775280898878 | 148.0 | 154.0 | 0 | {"budget_exhausted": 58, "initial_verified": 11, "verified": 3} |

| study | arm | original_payload_token_bin | completed_repairs | distinct_theorems | verified | repeated | truncated | first_repairs | first_repair_verified |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| V7 | C_real | (0,128] | 116 | 18 | 3 | 70 | 0 | 35 | 0 |
| V7 | C_real | (128,256] | 78 | 14 | 3 | 39 | 0 | 32 | 3 |
| V7 | C_real | (256,384] | 3 | 1 | 0 | 2 | 0 | 1 | 0 |
| V7 | C_real | (384,inf] | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| V7 | D_shuffled | (0,128] | 103 | 23 | 2 | 65 | 0 | 29 | 0 |
| V7 | D_shuffled | (128,256] | 95 | 23 | 3 | 50 | 0 | 39 | 1 |
| V7 | D_shuffled | (256,384] | 2 | 2 | 0 | 1 | 0 | 0 | 0 |
| V7 | D_shuffled | (384,inf] | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| V8 | C_real | (0,128] | 30 | 4 | 0 | 28 | 0 | 10 | 0 |
| V8 | C_real | (128,256] | 153 | 19 | 0 | 150 | 0 | 51 | 0 |
| V8 | C_real | (256,384] | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| V8 | C_real | (384,inf] | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| V8 | D_shuffled | (0,128] | 36 | 18 | 0 | 36 | 0 | 15 | 0 |
| V8 | D_shuffled | (128,256] | 147 | 21 | 0 | 144 | 0 | 46 | 0 |
| V8 | D_shuffled | (256,384] | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| V8 | D_shuffled | (384,inf] | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

Lengths: prompt/output tokens are historical model-tokenizer counts recorded by the MLX runner, not newly retokenized estimates. `original_feedback_tokens` counts the already extracted diagnostic payload (at most the first three structured compiler errors, with message character limits), before the 384-token prefix cap. It is NOT the entire compiler output. `used_feedback_tokens` is the model-token count of the actual capped payload; for shuffled D it describes its donor's feedback, not the target's compiler output. B has no diagnostic payload; E neutral padding is not a compiler diagnostic. Missing payload fields are unavailable, not zero. `predecessor_diagnostic_characters` measures Unicode characters in stored diagnostic text, not tokens. No tokenizer was loaded.

Binning is fixed post-hoc at 128/256/384 tokens. Rows count completed repair calls, not independent problems. All attempts of a theorem/seed and repeated seeds remain dependent; no p-values or causal length effects are claimed. First-repair columns restrict to identical-predecessor budget one; later rows are selected by prior failure and divergent histories. Repetition is exact candidate-byte equality; changing errors is not proof progress. Inspect `repair_observations.csv` for all measured lengths, truncation flags and verification outcomes. These descriptive relationships may be driven by theorem difficulty, arm, stopping after success, or previous failure.

Context statuses are copied without turning unknown outcomes into failures. The plans declare an 8192-token context and 1200-token output allowance; compare actual prompt maxima to those declared limits, not advertised model limits. Recorded truncation reflects the frozen prefix policy, not a randomized truncation experiment. No absence-of-failure claim extends beyond recorded test trajectories. V7 local raw traces have weaker portable provenance than the indexed V8 archive. Committed sanitized V7 trajectory views permit deterministic reanalysis on a clean checkout; original local digests remain separately recorded and do not authenticate history externally.

For Study 1, the existing missingness recovery identifies `lib_a_trig_unit/C1` as a context-preflight rejection: 9653 recorded rendered input tokens plus a 2000-token output allowance exceed the 8192 cap. `lib_i_bernoulli/C1` instead has 2205 input tokens and a 2000 output allowance, with only a stream header surviving; it is an interrupted generation without a response, not a demonstrated context overflow. Both C outcomes remain unknown. This is reuse of documented recovery evidence, not a new prompt reconstruction or retry. Existing `publication/post_hoc/outputs/post_hoc/post_hoc_task1.json` and `post_hoc_prompt_length_bins.csv` already analyze prompt length descriptively; `publication/results/review_v2/missingness_recovery.json` documents unavailable C trajectories. Those analyses are cited, not rerun here. Missing Study 1 outcomes remain unknown.

A prospective truncation study would require a new independently reviewed held-out benchmark, fixed initial failures, randomized no-feedback / full / 128 / 256 / 384-token prefix conditions, identical call and output caps, padding to match prompt-token budgets, frozen seeds and theorem-clustered verification endpoints. Predeclare incomplete handling, token accounting and stopping limits using a development-only precision study. Do not reuse these inspected test examples for a new confirmatory truncation test. This proposal is not executed and requires separate authorization.
