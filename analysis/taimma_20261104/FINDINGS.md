# TAIMMA evidence audit — 4 November 2026

All new inferential results below are exploratory post-hoc reanalyses. Frozen originals, experiment protocols and manuscript are unchanged. No inference or Lean replay was run. Execute `python3 analysis/taimma_20261104/analyze.py` from any directory; outputs are deterministic standard-library JSON/CSV/Markdown.

## Manuscript-ready findings

“In the frozen V7 cohort of 24 theorem types evaluated under three seeds, correct diagnostics verified 10/72 evaluations versus 5/72 with blind retry. Six evaluations succeeded only with correct diagnostics and one only with blind retry. The paired difference was 6.94 percentage points (post-hoc theorem-cluster percentile bootstrap 95% interval −1.39 to 18.06 points). Against shuffled diagnostics, four evaluations succeeded only with correct diagnostics and three only with shuffled diagnostics, for a difference of 1.39 points (−5.56 to 9.72). These intervals are inconclusive and do not establish equivalence or a diagnostic-specific benefit.”

“Blind retry, correct diagnostics and shuffled diagnostics solved 3, 4 and 7 distinct theorem types, respectively. More successful theorem–seed evaluations therefore did not imply broader theorem coverage. All three arms included four shared initially verified evaluations. Correct diagnostics added six verified evaluations beyond initial generation; shuffled diagnostics added five and blind retry added one.”

“V7 correct-diagnostic success at repair budgets 0, 1, 2 and 3 was 4, 7, 8 and 10 of 72. Among the six verified repairs, 50%, 16.7% and 33.3% first succeeded on steps 1, 2 and 3. Correct-diagnostic repair consumed 197 recorded calls, 53,838 input tokens and 14,256 output tokens. The shared initial generation consumed 72 calls, 9,501 input tokens and 4,701 output tokens, counted once.”

“The separate exploratory V8 Coder study had 11 initial verified evaluations. Blind, correct-diagnostic, shuffled and token-matched repair each remained at 11/72, with no new verified repair in these arms. Independent resampling reached 14/72. V8 provides no observed diagnostic-specific rescue and is not an identically conducted confirmatory replication.”

Use the generated paired, theorem, seed, budget, cost and error tables for exact denominators. Differences and intervals in tables are proportions; multiply by 100 for percentage points. The initial-A row in cost tables is initial generation, and its ratio counts initial tokens only; other rows contain repair costs only. Repair input tokens per final verified evaluation include initially solved evaluations in the denominator. They are resource ratios, not prices or causal efficiency estimates. Do not sum initial costs across arms. The separate marginal cost per newly repaired evaluation is undefined for V8 non-resampling arms with zero repairs.

## Methods and uncertainty

Primary new intervals resample 24 theorem clusters with replacement, preserving all three dependent seeds and pairing of arms. Family sensitivity resamples eight recorded family clusters, retaining their theorem–seed rows. Unequal family sizes use a row-weighted ratio in each resample. Both use 10,000 percentile replicates, Python `random.Random(20261104)`, and order-statistic endpoints at floor(p×9999). Family labels are supplied experimental labels, not independent mathematical adjudications. Overlap can violate independence even across nominal theorem clusters. Eight families and sparse successes make these intervals fragile.

Three new pooled contrasts are exploratory. No new p-values or significance claims are made. Error-category tables report recorded initial labels, denominators, distinct theorem counts, successes, new successes and theorem-cluster intervals for C minus each arm. Small/constant strata may give degenerate intervals; these are empirical bootstrap limitations, not proof of zero effect. Initially verified rows are included under their recorded initial label and must not be described as failed-proof repairs. Categories are observational strata, not randomized treatments. No category transition is inferred from an initial label: repair-budget reconstruction uses explicit `verified` transition fields and checks them against final outcomes.

## Historical statistical verification and discrepancies

Generated historical-verification tables reproduce each V7 and V8 seed-specific historical paired family bootstrap exactly (10,000 draws, seed 20271102), arm counts, Wilson intervals and exact McNemar values; recorded per-seed call counts and token totals also match their historical summaries. These historical per-seed McNemar values are verification targets, not newly endorsed pooled independent-row inference. Historical Wilson intervals do not account for related theorem families. New pooled intervals have a different resampling unit/seed/scope and must not silently replace historical intervals.

The handoff quotes pooled family intervals C−B [−1.67,+15.39] and C−D [−2.78,+6.41] percentage points without an executable pooled recipe in that document. Our explicitly specified pooled family bootstrap gives [−1.52,+15.38] and [−3.03,+6.67]. These do not exactly reconstruct the handoff numbers; report this discrepancy and retain the original. The qualitative conclusion is unchanged. No equivalence is established.

V8 aggregate “C 11/72 versus base C 10/72” hides that every V8 C success was already initially verified. It cannot substantiate improved repair. Two review CSVs contain pasted-sheet wrapper text before their headers; the analysis strips only that wrapper in memory, preserving original bytes.

## Evidence inventory and coverage

| Frozen evidence | Existing analyses | Added or reproduced here | Limitations |
|---|---|---|---|
| `research/study2-v7/test/{plan,summary,outcomes,calls,transitions}` | Per-seed counts, costs, Wilson, McNemar, family bootstrap | Pooled paired concordance, theorem/family coverage, seed and initial-error strata, budget curves, token tables, historical verification | Processed V7 records; not a full independent raw Lean replay |
| `study2_supervisor_suite_v7.py` | Plan, arm semantics, reporting and bootstrap implementation | Read-only import of statistical functions to reconstruct historical statistics | Import does not execute CLI or model inference |
| `research/study2-v7/development` and test lineage | V5 development evidence used for V7 | Inspected plan lineage; kept separate | Not a uniformly rerun V7 development study |
| `research/study2-raw-v8-v9/ARCHIVE_INDEX.json` and ZIP | 4,736 member release with hashes; frozen V8 lock; V9 dev records and raw journals | Every indexed archive/member checksum, all resolvable V8 lock hashes; V8 test row-level analyses | Hash consistency is not external authentication or proof of scientific correctness; absent model weights/caches cannot be verified here |
| `research/study2-final/study2_sensitivity.py` and review CSVs | Four overlap exclusion scopes and 31 provisional decisions plus five additional flags | Reproduced exclusion counts; consolidated all 36 review rows with reference-evidence paths | Exclusions selected post-hoc; independent signed review still outstanding |
| `publication/post_hoc/analysis` and archived Study 1 | Existing process/transition, placebo, cluster and precision analyses | Inventory plus Study 1 descriptive row reconstruction; existing repository test suite run | This addition does not claim to recalculate every Study 1/publication statistic or validate every historical environment hash |

Archive-member verification and the 40-entry frozen-lock status are machine-readable in `results/results.json` and `lock_checks.csv`. Plan hashes referring to absent model weights, cached tokenizer assets or the historical Lean environment are not newly verified by a successful archive hash check. This audit's hash claim is limited to the files explicitly listed as verified. Do not describe it as verification of every hash anywhere in this repository.

## Benchmark-overlap audit

`results/benchmark_review.{csv,md,json}` retains all original reasons/proposed dispositions and adds theorem identifiers, recorded families, available reference proof text from the frozen V7 constructor, archived reference-screen paths and outstanding review requirements. `reference_evidence.json` indexes additional archived validation records. Reference-screen files attest recorded formal proof success, not independent benchmark validity. No automated Lean equivalence claim was added.

Critical pairs remain d06/t11, d06/t12 and t11/t12 (Nat binomial-square variants), d07/t13 (distributivity specialization), and t07/t08 (successor/addition relation). Available rationale is provisional. Require independent signed/dated inspection of exact statements, reference proofs, family grouping and development/test reuse. AI reviewer self-duplicates or similarity flags do not establish logical identity. Placeholder English cannot establish NL-to-Lean fidelity; training overlap remains unknown.

The reproduced exclusions yield 72, 66, 63 and 60 evaluation denominators (24, 22, 21 and 20 theorem types). B/C/D success counts remain 5/10/9 in every scope: excluded cases contribute no successes. The resulting larger percentages reflect denominator removal, not new verified proofs. Original outcomes remain authoritative. Family exclusions cannot retroactively create a fresh held-out benchmark.

## Safe manuscript changes and remaining evidence gaps

Add paired discordance and theorem coverage alongside aggregate rates; show initial versus newly repaired successes, resource totals and budget curves; distinguish V8 initial successes from repair rescues. Label added analyses post-hoc and state cluster units and uncertainty. Preserve Study 1 as a separate experiment: the handoff reports B and C sharing one success on 58 complete pairs with two missing C trajectories; archived case rows independently reproduce these counts (60 theorem types, 54 recorded families), but this report has not newly revalidated its full raw provenance.

No observed V7/V8 test endpoint is missing in the analyzed outcome tables. Status counts are included per arm, rather than reclassifying incomplete trajectories as failure. Available token fields permit recorded-call totals; they do not prove that an unjournaled interrupted call consumed no compute. No monetary costs are estimated. Later repair histories diverge, so multi-step C−D or C−E is a comparison of full policies, not isolated diagnostic content.

The requested full-repository statistical and environment-hash audit is broader than this Study 2 addition; inventory-only areas above remain explicitly unverified. No paper edits, inference, benchmark edits, independent adjudication, submission or deployment occurred.
