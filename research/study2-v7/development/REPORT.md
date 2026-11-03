# Study 2 development report

Terminal cases: 12 of 12

**Not results from the original frozen 60-case study.**

Primary endpoint: strict original-type proof verification, case-level B versus C.

The script does NOT provide independent human validation of English–Lean meaning.
Benchmark: bridge; constructed synthetic theorems, possible near-duplicates and training contamination; not independent human semantic review

## Model × seed results

### mlx-community/Qwen2.5-7B-Instruct-4bit / 2027

| Arm | Verified / observed | Missing | Wilson 95% |
|---|---:|---:|---|
| B_neutral | 3/12 | 0 | [0.08894166839405718, 0.5323053349335582] |
| C_real | 5/12 | 0 | [0.19326031365876087, 0.6804886874504443] |
| D_shuffled | 4/12 | 0 | [0.13812009109121645, 0.6093779111271937] |
| E_token_matched | 3/12 | 0 | [0.08894166839405718, 0.5323053349335582] |
| R_resample | 3/12 | 0 | [0.08894166839405718, 0.5323053349335582] |

Complete B/C pairs: 12; B-only 0; C-only 2;
C−B=0.16666666666666666; exact McNemar p=0.5 (NOT an equivalence test).
Full-cohort missingness identification interval: [0.16666666666666666, 0.16666666666666666]

Paired control comparisons (C minus comparator):

| Comparator | Role | Complete pairs | Difference | Exact McNemar p |
|---|---|---:|---:|---:|
| C_real_minus_B_neutral | primary | 12 | 0.16666666666666666 | 0.5 |
| C_real_minus_D_shuffled | secondary_exploratory | 12 | 0.08333333333333333 | 1.0 |
| C_real_minus_E_token_matched | secondary_exploratory | 12 | 0.16666666666666666 | 0.5 |
| C_real_minus_R_resample | secondary_exploratory | 12 | 0.16666666666666666 | 0.5 |

Token-matched first repairs: 9/9 attempted 
Later repairs do not necessarily share the same previous candidate.

## Between-seed variability (descriptive)

Same problems repeat across seeds; these rates are not independent task samples.

| Model | Arm | Mean verified rate | SD across seeds |
|---|---|---:|---:|
| mlx-community/Qwen2.5-7B-Instruct-4bit | B_neutral | 0.25 | NA |
| mlx-community/Qwen2.5-7B-Instruct-4bit | C_real | 0.4166666666666667 | NA |
| mlx-community/Qwen2.5-7B-Instruct-4bit | D_shuffled | 0.3333333333333333 | NA |
| mlx-community/Qwen2.5-7B-Instruct-4bit | E_token_matched | 0.25 | NA |
| mlx-community/Qwen2.5-7B-Instruct-4bit | R_resample | 0.25 | NA |

## Figures

See repair_success_*.svg for observed-only success-by-budget curves per model and seed.
Each plotted point reports its observed denominator on hover; missing trajectories are excluded.
The figures are an editorial aid, not a significance or equivalence claim.


## Cost and resource accounting

All numeric costs are measured only for completed calls; missing telemetry remains missing.

| Model / seed / arm | Calls | Mean prompt tokens | Mean output tokens | Mean generation seconds |
|---|---:|---:|---:|---:|
| mlx-community/Qwen2.5-7B-Instruct-4bit / 2027 / A | 12 | 130.3 | 56.1 | 15.6 |
| mlx-community/Qwen2.5-7B-Instruct-4bit / 2027 / B_neutral | 27 | 190.3 | 56.0 | 12.1 |
| mlx-community/Qwen2.5-7B-Instruct-4bit / 2027 / C_real | 24 | 291.0 | 70.9 | 16.4 |
| mlx-community/Qwen2.5-7B-Instruct-4bit / 2027 / D_shuffled | 27 | 304.6 | 61.7 | 15.3 |
| mlx-community/Qwen2.5-7B-Instruct-4bit / 2027 / E_token_matched | 27 | 299.7 | 54.4 | 12.2 |
| mlx-community/Qwen2.5-7B-Instruct-4bit / 2027 / R_resample | 27 | 146.6 | 62.1 | 11.9 |

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
