# Study 2 — final evidence and supervisor handoff

**Prepared 3 November 2026. Scope: report and archive completed studies, not approve all supervisor revisions.** The repository branch is based on the clean one-commit V7 experiment branch; nothing in its frozen CSV, plan, script, or source datasets has been modified.

## Measured outcomes

| Condition | V7 base Qwen2.5-7B (72) | V8 Coder Qwen2.5-7B (72) |
|---|---:|---:|
| A initial | 4 | 11 |
| B neutral | 5 | 11 |
| C correct compiler diagnostics | 10 | 11 |
| D shuffled diagnostics | 9 | 11 |
| E token-matched neutral | 5 | 11 |
| R independent resampling | 5 | 14 |

These are 24 theorem types observed under three seeds, not 72 independent mathematics problems per model. V7's C–B difference is +5/72 (6.94 percentage points), exploratory family-cluster 95% interval [−1.67,+15.39]. C–D is +1/72 (+1.39 points), interval [−2.78,+6.41]. Both intervals cross zero. The Coder study is a separate exploratory test run and did not yield a C-specific rescue. In a post-hoc V9 development-only check, the novel repair prompt and Coder baseline each verified 5/12.

**Study 1 is different:** A 0/60, B 1/60, C 1/58 observed, two C trajectories unavailable; on 58 complete pairs B and C both verified exactly the same one theorem. There was no demonstrated C benefit.

## Verification and benchmark validity

The Mac audit reported 24/24 strict Lean reference checks, 40 locally hashed V8 evidence entries, 24 independent-model AI-review calls, nine flagged references, 12 heuristic within-test similarities, and 10 cross-split similarities. A separate review identified exact development d06 vs test t11/t12 binomial-square identity equivalence, test t11/t12 equivalence, development d07 as a specialization of t13, and related successor test t07/t08. These adjudications are **provisional**, not signed independent semantic review.

See `BENCHMARK_ADJUDICATION_NOTES.md`, `PROPOSED_VALIDATION_DECISIONS.csv`, and `ADDITIONAL_BENCHMARK_OVERLAPS.csv`. A validation label `ACCEPT_FORMAL_ONLY` does not imply a unique, independent, uncontaminated theorem or English-to-Lean fidelity. The V7 data stay frozen. The deterministic post-hoc exclusion audit is `study2_sensitivity.py`; its outputs are summarized in `V7_POST_HOC_SENSITIVITY.csv`. Exclusions were chosen after inspecting outcomes, so they are exploratory and cannot retroactively cleanse the originally examined test cohort.

## Supervisor's 29-point revisions — evidence-based status

| Items | Current assessment | Outstanding issue |
|---|---|---|
| 1 proof success | **Partial** | V9 has no improvement over Coder guided dev (5/12 vs 5/12); no robust diagnostic-specific advantage |
| 2 novelty | **Argument drafted** | Independent source-by-source literature and novelty sign-off |
| 3 strong baselines | **Implemented in V7/V8** | Controls do not fully isolate token/history differences |
| 4 multiple models | **Implemented** | Base and Coder observed in separate plans; V8 exploratory |
| 5 multiple seeds | **Implemented in Study 2** | Three seeds reuse theorem types and are dependent |
| 6 benchmark validation | **Partial** | Formal proof checking passes; suspected family duplicates and no true NL labels |
| 7–8 matched tokens/feedback streams | **Implemented with limitations** | Unequal histories and semantic differences remain |
| 9–17 analysis | **Substantially implemented** | Small family count, low power, raw verification limits |
| 18–19 abstract/motivation | **Revised in new draft** | Editorial approval |
| 20–21 related work/novelty | **Revised with restrained claims** | Independent primary-paper citation verification |
| 22 reproducibility | **Partial** | Public processed records, but not full private raw model/reviewer trajectories |
| 23–26 figures/tables/interpretation | **Revised in new five-page draft** | Supervisor/venue review; post-hoc analyses labelled |
| 27 code/evidence archive | **Partial** | V7 script/results public; V8 lock report documents local uncommitted raw evidence |
| 28 citations | **Review required** | Not all final bibliography entries independently verified in this handoff |
| 29 venue formatting/submission | **Draft build passed** | Editorial, anonymity, supervisor and category approval pending |

## Reproducibility gate

Run the Python standard-library hash-verified checker from the repository root:

```sh
python research/study2-final/study2_sensitivity.py
```

It refuses a modified V7 source file and reports exclusion cohorts while retaining the original 72-case numbers. The original 60-case dataset, V7 and local V8/V9 experimental records must not be overwritten. No fabricated hypothesis acceptance, fixed theorem proof, AI reviewer sign-off, new model call or submission approval is claimed.

## Current decision

**Freeze experimental runs. Send manuscript and this handoff to supervisor for reduced-scope approval.** Do not describe corrections 1 and 6 as fully satisfied; these have limited evidence and unresolved validation. The draft pull request should not be merged or submitted before reviewing the flagged cases and author/venue release requirements.
