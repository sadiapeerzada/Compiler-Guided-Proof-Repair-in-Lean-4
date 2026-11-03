# MANUSCRIPT_CHANGES — 2026-10-30

Source: publication/paper/main.tex; manuscript-only update. Frozen artifacts and existing outputs unchanged.

1. Unknown-name removal B 12/76 and C 14/70 is not evidence of diagnostic use; B is an analyst-only chance baseline. Dev C 3/19 vs placebo 2/17 differs by one event; removed higher-name-removal interpretation.
2. First repair B 17/60 (28.3%), C 10/58 (17.2%); C-B -11.09 pp, whole-family 95% CI [-22.00,-0.86] with 10,000 resamples and seed 20271021. Two unavailable C first repairs excluded. Later B 73/118 (61.9%), C 60/114 (52.6%) have divergent predecessors.
3. Dev B repetition 22/45 (48.9%), C 23/45 (51.1%), C_placebo 32/45 (71.1%). Dev B name removal 1/18 (analyst-only). Mismatched diagnostics may increase copying, making the placebo ambiguous. Fifteen problems, five families, one seed, no hypothesis test.
4. Pooled test repetition 90/178 vs 70/172 and -9.86 pp family CI [-19.77,-0.50] preserved. Called suggestive and exploratory; upper endpoint barely below zero and no multiplicity correction.
5. Promoted process diagnostics to new top-level section after taxonomy, before qualitative cases, labelled exploratory and defined after observing outcomes.
6. Shortened abstract; added one exploratory sentence; distinguished 3-case pre-test protocol pilot from 15-case post-hoc placebo.
7. Revised conclusion with correct percentages, uncertainty and no robust success advantage.
8. Fixed-theorem synthesis framing; conventional exact McNemar p=1.0 is non-informative for equivalence. No frozen-study reported success, Wilson/Newcombe/bootstrap intervals or resource counts changed.
9. Proper captioned table float wrappers for existing generated resources (those generated fragments untouched); moved provenance detail, Table 4, and reproducibility detail to appendices. Short main-text dataset and hashes retained. Local standalone build 15 pages total, references end page 12; **repository/BibTeX build not verified locally**. Venue appendix page-count exemption not independently verified.
10. Internal freeze (not external preregistration), privacy-limited replay, authorization caveat and AI-assisted review without human labels preserved.

Old abstract: “We report genuine outputs, compiler errors, resource usage and failure cases rather than a demonstrated feedback benefit.”
New abstract: “Exploratorily, compiler diagnostics were associated with fewer byte-identical retries (70/172 = 40.7% versus 90/178 = 50.6%), and a separate 15-problem development placebo pointed in the same direction, but neither comparison yielded more verified proofs.”
Old conclusion: “The recorded experiment does not establish a robust advantage for compiler feedback; a non-significant test is not evidence of equivalence.”
New conclusion: “On 58 complete paired test trajectories, B and C each verified 1/58, with no robust verified-success advantage or equivalence established. Exploratorily, C was associated with fewer byte-identical retries than B (70/172, 40.7%, versus 90/178, 50.6%; C-minus-B -9.86 percentage points, whole-family 95% bootstrap CI [-19.77,-0.50]); the development placebo also had lower repetition under real than mismatched diagnostics, but neither produced more verified proofs.”

TODO placeholders: none; all new numbers computed from stored post-hoc CSVs by analysis/manuscript_update_numbers.py. Repository build not run in the connector environment; compile the exact repository source before submission.
