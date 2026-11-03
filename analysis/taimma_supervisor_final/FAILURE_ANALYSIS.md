# Failure persistence and non-verifying changes

Across completed guided repairs, V7 repeats the exact predecessor in 111/197 calls; V8 repeats it in 178/183. Shuffled feedback repeats in 116/200 and 180/183, respectively. V7 guided repair changes error category without verification in 16 calls; shuffled repair does so in 11. V8 B/C/D/E retain the same error category throughout recorded repair attempts and add no verified successes. These are descriptive process counts, not independent trials or evidence of repair improvement.

| study | arm | step | completed_repairs | same_error_category | changed_error_category | changed_category_but_unverified | changed_diagnostic_text_but_unverified | repeated_candidates | large_change_unverified | verified |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| V7 | B_neutral | 1 | 68 | 66 | 2 | 2 | 3 | 40 | 3 | 0 |
| V7 | B_neutral | 2 | 68 | 67 | 1 | 0 | 0 | 55 | 0 | 1 |
| V7 | B_neutral | 3 | 67 | 66 | 1 | 1 | 1 | 52 | 1 | 0 |
| V7 | C_real | 1 | 68 | 58 | 10 | 7 | 30 | 19 | 0 | 3 |
| V7 | C_real | 2 | 65 | 56 | 9 | 8 | 13 | 41 | 0 | 1 |
| V7 | C_real | 3 | 64 | 61 | 3 | 1 | 8 | 51 | 1 | 2 |
| V7 | D_shuffled | 1 | 68 | 65 | 3 | 2 | 15 | 35 | 0 | 1 |
| V7 | D_shuffled | 2 | 67 | 60 | 7 | 5 | 17 | 35 | 0 | 2 |
| V7 | D_shuffled | 3 | 65 | 59 | 6 | 4 | 10 | 46 | 0 | 2 |
| V7 | E_token_matched | 1 | 68 | 67 | 1 | 1 | 2 | 40 | 4 | 0 |
| V7 | E_token_matched | 2 | 68 | 68 | 0 | 0 | 0 | 58 | 0 | 0 |
| V7 | E_token_matched | 3 | 68 | 67 | 1 | 0 | 0 | 60 | 0 | 1 |
| V7 | R_resample | 1 | 68 | 56 | 12 | 11 | 34 | 15 | 13 | 1 |
| V7 | R_resample | 2 | 67 | 62 | 5 | 5 | 27 | 25 | 8 | 0 |
| V7 | R_resample | 3 | 67 | 64 | 3 | 3 | 29 | 25 | 6 | 0 |
| V8 | B_neutral | 1 | 61 | 61 | 0 | 0 | 2 | 58 | 0 | 0 |
| V8 | B_neutral | 2 | 61 | 61 | 0 | 0 | 0 | 61 | 0 | 0 |
| V8 | B_neutral | 3 | 61 | 61 | 0 | 0 | 0 | 60 | 0 | 0 |
| V8 | C_real | 1 | 61 | 61 | 0 | 0 | 0 | 59 | 0 | 0 |
| V8 | C_real | 2 | 61 | 61 | 0 | 0 | 0 | 60 | 0 | 0 |
| V8 | C_real | 3 | 61 | 61 | 0 | 0 | 2 | 59 | 0 | 0 |
| V8 | D_shuffled | 1 | 61 | 61 | 0 | 0 | 1 | 60 | 0 | 0 |
| V8 | D_shuffled | 2 | 61 | 61 | 0 | 0 | 1 | 59 | 1 | 0 |
| V8 | D_shuffled | 3 | 61 | 61 | 0 | 0 | 0 | 61 | 0 | 0 |
| V8 | E_token_matched | 1 | 61 | 61 | 0 | 0 | 0 | 59 | 0 | 0 |
| V8 | E_token_matched | 2 | 61 | 61 | 0 | 0 | 0 | 60 | 0 | 0 |
| V8 | E_token_matched | 3 | 61 | 61 | 0 | 0 | 0 | 61 | 0 | 0 |
| V8 | R_resample | 1 | 61 | 57 | 4 | 2 | 42 | 9 | 5 | 2 |
| V8 | R_resample | 2 | 59 | 55 | 4 | 3 | 30 | 14 | 3 | 1 |
| V8 | R_resample | 3 | 58 | 56 | 2 | 2 | 30 | 13 | 3 | 0 |

These are post-hoc completed-attempt denominators, conditional on reaching the step. A category change, a different diagnostic or a large edit is not verified mathematical progress. `large_change` is a predeclared-for-this-analysis threshold of at least 0.5 on one minus Python SequenceMatcher ratio with autojunk disabled; it is not Levenshtein distance and not a semantic similarity score. No synthetic candidate is introduced. Selected authentic excerpts appear in CASE_STUDIES.md.

Initial-error category success and newly verified repair counts are already in PR20 `results/V7_errors.csv`, `V8_errors.csv` and theorem tables; no duplicate category efficacy calculation is introduced. The inherited classification is the frozen runner's `failure_class` function, which maps a multi-error compiler response to ONE priority label using diagnostic strings/failure status. Thus mixed syntax/identifier/unsolved-goal failures may receive only one label; it is not independent expert annotation. Precedence is missing verification, verified success, a recorded non-compiler failure kind, then syntax/parser strings, unknown-name strings, type/elaboration strings, tactic/unsolved-goal strings, and finally other compiler error. A mixed parser/unknown-identifier response is therefore syntax, even if both errors occur. Stored error messages remain available in case excerpts and raw sources. Unknown or other labels are not retrospectively renamed. See `study2_supervisor_suite_v7.py::failure_class` for the exact precedence.

This analysis uses actual previous/new fields in `transitions.csv`, cross-checked against trajectory verification flags; it does not infer repair transitions from initial-error labels. V8 B/C/D/E has zero newly verified repairs, even if errors or candidates change. Histories diverge after step one, selection by previous failure is strong, and no treatment mechanism is identified by these descriptive persistence counts. V7 raw observations depend on locally available untracked snapshots, explicitly listed in SOURCE_HASHES.json; committed sanitized trajectory views make this addition portable while the original CSV transitions remain frozen and authoritative.
