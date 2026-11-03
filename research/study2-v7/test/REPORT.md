# Study 2 test report

Terminal cases: 72 of 72

**Not results from the original frozen 60-case study.**

Primary endpoint: strict original-type proof verification, case-level B versus C.

The script does NOT provide independent human validation of English–Lean meaning.
Benchmark: bridge; constructed synthetic theorems, possible near-duplicates and training contamination; not independent human semantic review

## Model × seed results

### mlx-community/Qwen2.5-7B-Instruct-4bit / 2027

| Arm | Verified / observed | Missing | Wilson 95% |
|---|---:|---:|---|
| B_neutral | 2/24 | 0 | [0.02315881529704407, 0.2584880219321007] |
| C_real | 3/24 | 0 | [0.043443340801235575, 0.31003881270499467] |
| D_shuffled | 3/24 | 0 | [0.043443340801235575, 0.31003881270499467] |
| E_token_matched | 2/24 | 0 | [0.02315881529704407, 0.2584880219321007] |
| R_resample | 2/24 | 0 | [0.02315881529704407, 0.2584880219321007] |

Complete B/C pairs: 24; B-only 0; C-only 1;
C−B=0.041666666666666664; exact McNemar p=1.0 (NOT an equivalence test).
Full-cohort missingness identification interval: [0.041666666666666664, 0.041666666666666664]

Paired control comparisons (C minus comparator):

| Comparator | Role | Complete pairs | Difference | Exact McNemar p |
|---|---|---:|---:|---:|
| C_real_minus_B_neutral | primary | 24 | 0.041666666666666664 | 1.0 |
| C_real_minus_D_shuffled | secondary_exploratory | 24 | 0.0 | 1.0 |
| C_real_minus_E_token_matched | secondary_exploratory | 24 | 0.041666666666666664 | 1.0 |
| C_real_minus_R_resample | secondary_exploratory | 24 | 0.041666666666666664 | 1.0 |

Token-matched first repairs: 22/22 attempted 
Later repairs do not necessarily share the same previous candidate.

### mlx-community/Qwen2.5-7B-Instruct-4bit / 2028

| Arm | Verified / observed | Missing | Wilson 95% |
|---|---:|---:|---|
| B_neutral | 2/24 | 0 | [0.02315881529704407, 0.2584880219321007] |
| C_real | 3/24 | 0 | [0.043443340801235575, 0.31003881270499467] |
| D_shuffled | 4/24 | 0 | [0.0667867632863311, 0.35853070649698465] |
| E_token_matched | 2/24 | 0 | [0.02315881529704407, 0.2584880219321007] |
| R_resample | 2/24 | 0 | [0.02315881529704407, 0.2584880219321007] |

Complete B/C pairs: 24; B-only 1; C-only 2;
C−B=0.041666666666666664; exact McNemar p=1.0 (NOT an equivalence test).
Full-cohort missingness identification interval: [0.041666666666666664, 0.041666666666666664]

Paired control comparisons (C minus comparator):

| Comparator | Role | Complete pairs | Difference | Exact McNemar p |
|---|---|---:|---:|---:|
| C_real_minus_B_neutral | primary | 24 | 0.041666666666666664 | 1.0 |
| C_real_minus_D_shuffled | secondary_exploratory | 24 | -0.041666666666666664 | 1.0 |
| C_real_minus_E_token_matched | secondary_exploratory | 24 | 0.041666666666666664 | 1.0 |
| C_real_minus_R_resample | secondary_exploratory | 24 | 0.041666666666666664 | 1.0 |

Token-matched first repairs: 23/23 attempted 
Later repairs do not necessarily share the same previous candidate.

### mlx-community/Qwen2.5-7B-Instruct-4bit / 2029

| Arm | Verified / observed | Missing | Wilson 95% |
|---|---:|---:|---|
| B_neutral | 1/24 | 0 | [0.00739345616550606, 0.2024180647865531] |
| C_real | 4/24 | 0 | [0.0667867632863311, 0.35853070649698465] |
| D_shuffled | 2/24 | 0 | [0.02315881529704407, 0.2584880219321007] |
| E_token_matched | 1/24 | 0 | [0.00739345616550606, 0.2024180647865531] |
| R_resample | 1/24 | 0 | [0.00739345616550606, 0.2024180647865531] |

Complete B/C pairs: 24; B-only 0; C-only 3;
C−B=0.125; exact McNemar p=0.25 (NOT an equivalence test).
Full-cohort missingness identification interval: [0.125, 0.125]

Paired control comparisons (C minus comparator):

| Comparator | Role | Complete pairs | Difference | Exact McNemar p |
|---|---|---:|---:|---:|
| C_real_minus_B_neutral | primary | 24 | 0.125 | 0.25 |
| C_real_minus_D_shuffled | secondary_exploratory | 24 | 0.08333333333333333 | 0.5 |
| C_real_minus_E_token_matched | secondary_exploratory | 24 | 0.125 | 0.25 |
| C_real_minus_R_resample | secondary_exploratory | 24 | 0.125 | 0.25 |

Token-matched first repairs: 23/23 attempted 
Later repairs do not necessarily share the same previous candidate.

## Between-seed variability (descriptive)

Same problems repeat across seeds; these rates are not independent task samples.

| Model | Arm | Mean verified rate | SD across seeds |
|---|---|---:|---:|
| mlx-community/Qwen2.5-7B-Instruct-4bit | B_neutral | 0.06944444444444445 | 0.024056261216234404 |
| mlx-community/Qwen2.5-7B-Instruct-4bit | C_real | 0.1388888888888889 | 0.0240562612162344 |
| mlx-community/Qwen2.5-7B-Instruct-4bit | D_shuffled | 0.125 | 0.041666666666666664 |
| mlx-community/Qwen2.5-7B-Instruct-4bit | E_token_matched | 0.06944444444444445 | 0.024056261216234404 |
| mlx-community/Qwen2.5-7B-Instruct-4bit | R_resample | 0.06944444444444445 | 0.024056261216234404 |

## Figures

See repair_success_*.svg for observed-only success-by-budget curves per model and seed.
Each plotted point reports its observed denominator on hover; missing trajectories are excluded.
The figures are an editorial aid, not a significance or equivalence claim.


## Cost and resource accounting

All numeric costs are measured only for completed calls; missing telemetry remains missing.

| Model / seed / arm | Calls | Mean prompt tokens | Mean output tokens | Mean generation seconds |
|---|---:|---:|---:|---:|
| mlx-community/Qwen2.5-7B-Instruct-4bit / 2027 / A | 24 | 132.0 | 72.9 | 4.0 |
| mlx-community/Qwen2.5-7B-Instruct-4bit / 2027 / B_neutral | 66 | 202.9 | 86.9 | 6.0 |
| mlx-community/Qwen2.5-7B-Instruct-4bit / 2027 / C_real | 64 | 284.8 | 78.0 | 6.0 |
| mlx-community/Qwen2.5-7B-Instruct-4bit / 2027 / D_shuffled | 65 | 288.1 | 73.7 | 5.6 |
| mlx-community/Qwen2.5-7B-Instruct-4bit / 2027 / E_token_matched | 66 | 280.2 | 79.9 | 6.4 |
| mlx-community/Qwen2.5-7B-Instruct-4bit / 2027 / R_resample | 66 | 147.6 | 105.7 | 6.1 |
| mlx-community/Qwen2.5-7B-Instruct-4bit / 2028 / A | 24 | 132.0 | 66.2 | 4.3 |
| mlx-community/Qwen2.5-7B-Instruct-4bit / 2028 / B_neutral | 68 | 199.3 | 78.0 | 5.0 |
| mlx-community/Qwen2.5-7B-Instruct-4bit / 2028 / C_real | 67 | 266.3 | 65.7 | 4.9 |
| mlx-community/Qwen2.5-7B-Instruct-4bit / 2028 / D_shuffled | 68 | 286.8 | 80.8 | 5.8 |
| mlx-community/Qwen2.5-7B-Instruct-4bit / 2028 / E_token_matched | 69 | 268.3 | 77.1 | 5.4 |
| mlx-community/Qwen2.5-7B-Instruct-4bit / 2028 / R_resample | 67 | 147.5 | 86.9 | 5.0 |
| mlx-community/Qwen2.5-7B-Instruct-4bit / 2029 / A | 24 | 132.0 | 56.8 | 3.3 |
| mlx-community/Qwen2.5-7B-Instruct-4bit / 2029 / B_neutral | 69 | 196.3 | 90.9 | 5.6 |
| mlx-community/Qwen2.5-7B-Instruct-4bit / 2029 / C_real | 66 | 269.2 | 73.6 | 5.3 |
| mlx-community/Qwen2.5-7B-Instruct-4bit / 2029 / D_shuffled | 67 | 269.3 | 81.5 | 5.6 |
| mlx-community/Qwen2.5-7B-Instruct-4bit / 2029 / E_token_matched | 69 | 276.9 | 91.8 | 6.3 |
| mlx-community/Qwen2.5-7B-Instruct-4bit / 2029 / R_resample | 69 | 147.3 | 120.6 | 6.6 |

## Supervisor review coverage

Experiment automation does not establish causality or guarantee any success-rate improvement.

| Item | Status / work still needed |
|---|---|
| 1 | Run development calibration and separately frozen confirmatory sample; no guaranteed solution rate |
| 2 | Novelty must be argued against Li and Li, APRIL and Baldur (human writing) |
| 3 | Neutral, real, unrelated-diagnostic, token-matched, and independent-resampling arms |
| 4 | Original and coding-specialized models when both snapshots are supplied |
| 5 | At least three independent declared seeds by default |
| 6 | Statement/elaboration screening and source/proof metadata inventory; human semantic review remains required |
| 7 | Token-matched neutral controls measured and explicit token mismatches reported |
| 8 | Per-target shared initial, independent condition PRNG streams, rotating arm order |
| 9 | Failure taxonomy and transition counts |
| 10 | Automatic case-study packet with raw candidates and compiler diagnostics |
| 11 | Explicit missing, operational-failure, and full-cohort bounds |
| 12 | Declared diagnostic cap and context truncation tracking |
| 13 | Paired McNemar, Wilson and clustered bootstrap with limitations |
| 14 | Original post hoc findings not reclassified as confirmatory |
| 15 | Generation/compiler latency, tokens and available peak-memory records |
| 16 | Per-step success-at-budget curves |
| 17 | Category and family denominators with zero-success caveats |
| 18 | Manuscript abstract must be rewritten after results (human writing) |
| 19 | Motivation for small offline local model must be written (human writing) |
| 20 | Related-work table requires literature review (human writing) |
| 21 | Novelty framing depends on actual results (human writing) |
| 22 | Machine-readable prompts, seeds, model revisions, toolchain and stop rules |
| 23 | Figure needs manuscript-specific revision (human writing) |
| 24 | Results CSV and raw denominators produced for tables (human writing) |
| 25 | String/error/verification endpoints kept separate |
| 26 | Floor effect, reuse of old test items and confounding documented |
| 27 | Local append-only checkpoints, exact script and model revision hash inventory |
| 28 | References require manual verification (human writing) |
| 29 | Venue template and page-limit must be checked separately (human writing) |

## Limitations

- The frozen original experiment used full import Mathlib; Study 2 uses predeclared scoped imports when selected. Theorems and kernel checks are retained, but library visibility/tactics change; treat as a new experimental environment.
- Original test material was already seen in pilot analysis, so follow-up is not an entirely new untouched benchmark.
- Real, unrelated and neutral prompts differ in content; matched tokens alone do not remove all semantic confounding.
- Developer-selected model/benchmark and exploratory tuning must be disclosed; do not label original results as Study 2.
- Bootstrap conditions on complete cases and does not account for missing outcomes; report bounds separately.
- Follow-up results are only defensible after all declared model–seed–case cells are complete, and human review.
- Report memory only if the MLX backend exposes telemetry, never impute it.

See outcomes.csv, calls.csv, transitions.csv, success_by_budget.csv and summary.json.
