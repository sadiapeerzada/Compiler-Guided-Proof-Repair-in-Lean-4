| scope | excluded_theorem_ids | n_theorem_seed | n_distinct_theorems | counts | C_minus_B_count | C_minus_D_count | C_minus_B_percentage_points | C_minus_D_percentage_points | C_only_vs_B | B_only_vs_C |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Frozen all cases | [] | 72 | 24 | {"B_neutral": 5, "C_real": 10, "D_shuffled": 9, "E_token_matched": 5, "R_resample": 5, "initial_success": 4} | 5 | 1 | 6.9444 | 1.3889 | 6 | 1 |
| Exclude exact cross-split d06/t11-t12 | ["bridge_t11", "bridge_t12"] | 66 | 22 | {"B_neutral": 5, "C_real": 10, "D_shuffled": 9, "E_token_matched": 5, "R_resample": 5, "initial_success": 4} | 5 | 1 | 7.5758 | 1.5152 | 6 | 1 |
| Also exclude d07/t13 specialization | ["bridge_t11", "bridge_t12", "bridge_t13"] | 63 | 21 | {"B_neutral": 5, "C_real": 10, "D_shuffled": 9, "E_token_matched": 5, "R_resample": 5, "initial_success": 4} | 5 | 1 | 7.9365 | 1.5873 | 6 | 1 |
| Also collapse t07/t08 successor relation | ["bridge_t11", "bridge_t12", "bridge_t13", "bridge_t08"] | 60 | 20 | {"B_neutral": 5, "C_real": 10, "D_shuffled": 9, "E_token_matched": 5, "R_resample": 5, "initial_success": 4} | 5 | 1 | 8.3333 | 1.6667 | 6 | 1 |
