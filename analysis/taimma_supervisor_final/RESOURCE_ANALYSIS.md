# Recorded computational resources

Exploratory extension of PR #20; no new experiment. Token totals are cross-checked against its existing cost tables, not presented as a new finding. Added quantities are per-cohort-evaluation normalization, recorded elapsed generation/compiler durations and maximum observed memory.

| study | model | arm | cohort_evaluations | completed_calls | input_tokens | output_tokens | input_tokens_per_cohort_evaluation | output_tokens_per_cohort_evaluation | generation_elapsed_seconds | generation_missing | compiler_elapsed_seconds | compiler_missing | max_recorded_peak_memory_gb | memory_observed | memory_missing | input_per_new_verified_repair |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| V7 | mlx-community/Qwen2.5-7B-Instruct-4bit | A | 72 | 72 | 9501.0 | 4701.0 | 131.95833333333334 | 65.29166666666667 | 277.782370749017 | 0 | 119.489 | 0 | 4.77981581 | 72 | 0 | undefined |
| V7 | mlx-community/Qwen2.5-7B-Instruct-4bit | B_neutral | 72 | 203 | 40492.0 | 17312.0 | 562.3888888888889 | 240.44444444444446 | 1121.2421680848638 | 0 | 312.999 | 0 | 4.77981581 | 203 | 0 | 40492.0 |
| V7 | mlx-community/Qwen2.5-7B-Instruct-4bit | C_real | 72 | 197 | 53838.0 | 14256.0 | 747.75 | 198.0 | 1061.7029009649996 | 0 | 309.46 | 0 | 4.77981581 | 197 | 0 | 8973.0 |
| V7 | mlx-community/Qwen2.5-7B-Instruct-4bit | D_shuffled | 72 | 200 | 56277.0 | 15744.0 | 781.625 | 218.66666666666666 | 1133.5439450441045 | 0 | 321.491 | 0 | 4.77981581 | 200 | 0 | 11255.4 |
| V7 | mlx-community/Qwen2.5-7B-Instruct-4bit | E_token_matched | 72 | 204 | 56111.0 | 16924.0 | 779.3194444444445 | 235.05555555555554 | 1234.715155251819 | 0 | 347.319 | 0 | 4.77981581 | 204 | 0 | 56111.0 |
| V7 | mlx-community/Qwen2.5-7B-Instruct-4bit | R_resample | 72 | 202 | 29792.0 | 21121.0 | 413.77777777777777 | 293.34722222222223 | 1186.8816148319747 | 0 | 316.326 | 0 | 4.77981581 | 202 | 0 | 29792.0 |
| V8 | mlx-community/Qwen2.5-Coder-7B-Instruct-4bit | A | 72 | 72 | 9501.0 | 5794.0 | 131.95833333333334 | 80.47222222222223 | 404.9875912901771 | 0 | 154.878 | 0 | 5.073061982 | 72 | 0 | undefined |
| V8 | mlx-community/Qwen2.5-Coder-7B-Instruct-4bit | B_neutral | 72 | 183 | 40635.0 | 16201.0 | 564.375 | 225.01388888888889 | 1567.5247830828303 | 0 | 487.913 | 0 | 5.073061982 | 183 | 0 | undefined |
| V8 | mlx-community/Qwen2.5-Coder-7B-Instruct-4bit | C_real | 72 | 183 | 64395.0 | 16277.0 | 894.375 | 226.06944444444446 | 1520.721230459807 | 0 | 361.364 | 0 | 5.073061982 | 183 | 0 | undefined |
| V8 | mlx-community/Qwen2.5-Coder-7B-Instruct-4bit | D_shuffled | 72 | 183 | 62679.0 | 13902.0 | 870.5416666666666 | 193.08333333333334 | 1278.9594416757172 | 0 | 408.771 | 0 | 5.073061982 | 183 | 0 | undefined |
| V8 | mlx-community/Qwen2.5-Coder-7B-Instruct-4bit | E_token_matched | 72 | 183 | 64450.0 | 16224.0 | 895.1388888888889 | 225.33333333333334 | 1528.8332280858303 | 0 | 430.241 | 0 | 5.073061982 | 183 | 0 | undefined |
| V8 | mlx-community/Qwen2.5-Coder-7B-Instruct-4bit | R_resample | 72 | 178 | 26219.0 | 15409.0 | 364.15277777777777 | 214.01388888888889 | 1144.6001027830935 | 0 | 456.098 | 0 | 5.073061982 | 178 | 0 | 8739.666666666666 |

A is shared initial generation, charged once across all policies. Other rows are repair-only. Per-evaluation values divide by all 72 theorem–seed evaluations, including those requiring no repair. The PR20 marginal input-token ratio divides repair input tokens by NEW verified evaluations beyond initial successes; zero new repairs makes it undefined. No currency conversion or unlogged compute is estimated.

`seconds` is the runner's monotonic elapsed interval around streaming generation and token-journal writes. It includes streaming and journal I/O overhead; it is not pure accelerator kernel time. `compiler_seconds` is the verifier's recorded elapsed time per call, including its subprocess/setup work. Their sum is not experiment wall time: orchestration, loading, reference screening, development, idle periods and interrupted/unrecorded work are excluded. No total wall time is inferred by summing them.

`memory_gb` copies MLX's last streamed `peak_memory` field under the runner's `peak_memory_gb` label. We report its maximum, never a sum or an estimate. It may be a process-cumulative high-water mark and is not incremental per-arm allocation or OS total RAM. The backend's units and scope are not independently calibrated here. Missing counts remain explicit. V7 and V8 share this reporting implementation; they are separate model snapshots/runs and elapsed times are not controlled hardware-speed comparisons.

Success at cumulative repair budgets and newly verified repair token ratios already appear in `../taimma_20261104/results/{V7,V8}_budgets.csv` and `{V7,V8}_costs.csv`; those frozen derived tables are reused unchanged. In particular, V8 B/C/D/E has zero newly verified repairs; none receives a finite marginal token-per-new-success claim.
