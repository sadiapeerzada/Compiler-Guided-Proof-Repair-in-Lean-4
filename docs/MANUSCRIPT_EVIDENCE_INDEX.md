# Manuscript evidence index

**Paper:** *Compiler Feedback Versus Retry Controls in Lean 4 Proof Repair: Two Local-Model Studies* · Faraz Masood and Sadia Peerzada · TAIMMA 2027 manuscript companion.

[Return to main README](../README.md) · [Repository guide](REPOSITORY_GUIDE.md) · [Research diagrams](RESEARCH_DIAGRAMS.md)

> This is a **navigation and interpretation index**, not a new experimental result, a provenance upgrade, a privacy clearance, or a claim that the final manuscript has been reproduced end-to-end. The paths listed as Table 10 correspond to the uploaded 14-page manuscript. The six paths below were present on the public default branch during the November 2026 documentation audit. Preserve original numbers and use their cited snapshots.

## A. Table 10 — six manuscript evidence locations

| Manuscript Table 10 entry | Exact relative path | Reader's entry point | Scope and caution |
|---|---|---|---|
| V7 outcomes (CSV) | [`research/study2-v7/test/outcomes.csv`](../research/study2-v7/test/outcomes.csv) | [Frozen test report](../research/study2-v7/test/REPORT.md), [summary](../research/study2-v7/test/summary.json) | The base-model **24 types × 3 reused seeds**, not 72 independent types |
| V7 protocol | [`research/study2-v7/test/plan.json`](../research/study2-v7/test/plan.json) | [Study 2 README](../research/study2-v7/README.md) and [development lineage](../research/study2-v7/test/DEVELOPMENT_LINEAGE.md) | V7 C–B is the named primary comparison; do not upgrade other contrasts to preregistered |
| V8/V9 indexed journals | [`research/study2-raw-v8-v9/`](../research/study2-raw-v8-v9/) | [Archive README](../research/study2-raw-v8-v9/README.md), [index](../research/study2-raw-v8-v9/ARCHIVE_INDEX.json) | V8 exploratory **test** run versus V9 **development only**; archive checks are not inference replay |
| Paired post-hoc analysis | [`analysis/taimma_20261104/`](../analysis/taimma_20261104/) | [FINDINGS.md](../analysis/taimma_20261104/FINDINGS.md), [analysis README](../analysis/taimma_20261104/README.md) | Bootstrap, theorem coverage, budgets, costs, semantic flags; exploratory and dependent |
| Integrity audit | [`analysis/taimma_supervisor_final/`](../analysis/taimma_supervisor_final/) | [Scientific audit](../analysis/taimma_supervisor_final/FINAL_SCIENTIFIC_AUDIT.md), [cases](../analysis/taimma_supervisor_final/CASE_STUDIES.md) | Descriptive supplement and sanitized views; V7 originals not independently indexed |
| Lean overlap certificates | [`analysis/taimma_final_professor_validation/`](../analysis/taimma_final_professor_validation/) | [Benchmark verification](../analysis/taimma_final_professor_validation/BENCHMARK_VALIDITY_VERIFICATION.md), [Lean file](../analysis/taimma_final_professor_validation/OverlapCertificates.lean) | Demonstrates scoped relationships among types; not benchmark independence or independent human adjudication |

**Presence check:** From the repository root, run `python3 scripts/check_manuscript_evidence.py`. Its checks establish path and documentation-link presence only.

## B. Follow the reported results to their backing artifacts

| Claim or manuscript component | Relevant versioned evidence | Important interpretive boundary |
|---|---|---|
| Study 1 A 0/60, B 1/60, C 1/58 with two missing C outcomes | [Historical public release](../publication/README.md), [Study 1 analysis docs](../publication/docs/PAIRED_COMPARISON_AUDIT.md), [missingness investigation](../publication/docs/MISSING_C_OUTCOME_INVESTIGATION.md) | C is *observed* on 58 only. Never silently convert missing endpoints into failures |
| Study 1 strict theorem checking, original study constraints | [Publication release](../publication/README.md), [public release manifest](../publication/PUBLIC_RELEASE_MANIFEST.json) | Fixed-theorem proof synthesis, not NL-to-Lean statement translation |
| Study 2 V7 verified A/B/C/D/E/R = 4/5/10/9/5/5 | [V7 outcomes](../research/study2-v7/test/outcomes.csv), [V7 report](../research/study2-v7/test/REPORT.md), [V7 summary](../research/study2-v7/test/summary.json) | Each arm's successes include the same initial A opportunities |
| Study 2 V8 verified A/B/C/D/E/R = 11/11/11/11/11/14 | [V8 archive](../research/study2-raw-v8-v9/), [V8 paired comparison](../analysis/taimma_20261104/results/V8_paired.md) | B–E show zero *rescued* verified cells, despite 11 total successes each |
| V7 paired C–B +6.94 pp and C–D +1.39 pp; intervals crossing zero | [Paired table](../analysis/taimma_20261104/results/V7_paired.md), [full results JSON](../analysis/taimma_20261104/results/results.json) | Theorem-level bootstrap with three seeds kept together; exploratory post-hoc uncertainty |
| 10 C successes across 4 theorem types vs 9 D across 7 | [Theorem coverage table](../analysis/taimma_20261104/results/V7_theorems.md) | Evaluation counts and distinct theorem coverage are different outcomes |
| V7 C repair input 53,838 vs B 40,492 | [V7 costs](../analysis/taimma_20261104/results/V7_costs.md) | **Repair-only** token totals, not full compute-matched budgets |
| Failure categories and case studies | [Error analysis](../analysis/taimma_20261104/results/V7_errors.md), [authentic cases](../analysis/taimma_supervisor_final/CASE_STUDIES.md) | Qualitative post-hoc examples are not frequency estimates |
| Suspicious mathematical relationships among constructed types | [Overlap evidence](../analysis/taimma_final_professor_validation/BENCHMARK_OVERLAP_EVIDENCE.csv), [certificates](../analysis/taimma_final_professor_validation/OverlapCertificates.lean), [human-review notice](../analysis/taimma_final_professor_validation/HUMAN_ADJUDICATION_REQUIRED.md) | Formal transport checks cannot rule out leakage or certify the informal descriptions |
| Evidence-integrity and reproducibility limitations | [Read-only scope statement](../analysis/taimma_final_professor_validation/REPRODUCIBILITY_FINAL_VERIFICATION.md), [scientific audit](../analysis/taimma_supervisor_final/FINAL_SCIENTIFIC_AUDIT.md) | Hash verification is narrower than original candidate replay, model inference or independent validation |

## C. Results-level distinctions reviewers should retain

### Units and denominators

- **Study 1:** 60 held-out formal types, one model and one seed. A and B have 60 known outcomes; C has 58 observed and two unavailable. There are 58 complete B/C pairs.
- **Study 2 V7:** 24 constructed formal types, three seeds each, **72 dependent theorem–seed evaluations** per arm with the same Qwen base model.
- **Study 2 V8:** The same 24 constructed types × three seeds, but a different exploratory Coder model. Do **not** sum V7 and V8 as independent theorem cohorts.
- **Study 2 V9:** Development-only 12-case strategy comparison; **not** new held-out evaluation.
- **Strict success:** Proof acceptance for the *original fixed theorem type* without forbidden placeholders/axioms. A change to error class or proof text is insufficient.

### Controls

- **A:** one-shot initial proof only; zero repairs.
- **B:** neutral/blind retry (up to three).
- **C:** genuine compiler diagnostics from its own preceding failed attempt (up to three).
- **D:** shuffled diagnostics from a different family (up to three, potentially still useful generic advice).
- **E:** approximately length-matched neutral text (up to three; not full-budget matching).
- **R:** independent resampling without predecessor display (up to three generation opportunities after initial failure).

**C–B** compares policies with equal *maximum calls*, not equal realized input/output tokens, exact later predecessor histories, or compute. **C–D** is explicitly post hoc in the paper. V8 is exploratory. A positive count difference with a cluster interval crossing zero is **not evidence of statistically established improvement**; a zero or small difference is **not an equivalence result**.

### Manuscript figures

- **Figure 1:** bounded fixed-type verifier/retry protocol; diagrams here are documentation reconstructions, *not* newly analyzed outcomes.
- **Figure 2:** V7 verified evaluations vs distinct theorem coverage; source [V7 theorem table](../analysis/taimma_20261104/results/V7_theorems.md).
- **Figure 3:** V7 cumulative success by allowed repair attempt; consult [V7 analysis](../analysis/taimma_20261104/FINDINGS.md) and underlying [V7 outcomes](../research/study2-v7/test/outcomes.csv). The README does not substitute invented plot points for the reported chart.

## D. Integrity boundaries and versioning

The manuscript distinguishes a frozen pre-supplement evidence snapshot (`a3a709c383ce`) from later formal/control-integrity supplement (`aae97d197f63`). Links to those snapshots:

- [Earlier frozen evidence commit](https://github.com/sadiapeerzada/Compiler-Guided-Proof-Repair-in-Lean-4/commit/a3a709c383ce)
- [Later supplement commit](https://github.com/sadiapeerzada/Compiler-Guided-Proof-Repair-in-Lean-4/commit/aae97d197f63)

Their contents should **not be attributed interchangeably**. Historical file names and old repository identifiers inside immutable protocol artifacts may be correct for the frozen run. Do not rewrite them merely to harmonize naming.

The [archive index](../research/study2-raw-v8-v9/ARCHIVE_INDEX.json) and published audit describe **4,736 archive members** and **40 lock entries** verified in their documented scope. V7 sanitized derivatives of original local trajectories have weaker historical custody than the V8 indexed ZIP, and newer indices do not retroactively authenticate old untracked originals.

### Privacy and distribution

The final validation document clarifies **1,220 local-path warning records** totaling **22,882 detected occurrences**. These quantities must not be confused. [Warning details](../research/study2-raw-v8-v9/PRIVACY_SCAN_WARNINGS.json) require manual review; a tool passing credential regexes is not general privacy/license clearance. This index does **not** authorize releasing additional unreviewed raw material. Do not upload original local paths, private journals or model caches in pursuit of a tidier repository.

## E. Read-only verification recipes

```bash
# 1. Check Table 10 path and local documentation links:
python3 scripts/check_manuscript_evidence.py

# 2. Recalculate the published post-hoc statistics from stored artifacts:
#    Use a disposable clone if scripts regenerate output files.
python3 analysis/taimma_20261104/analyze.py

# 3. See the archive's own verification instructions:
cat research/study2-raw-v8-v9/README.md

# 4. See scoped mathematical/control verification:
cat analysis/taimma_final_professor_validation/README.md
```

**Confidence levels are different:** path present ≠ checksum verified ≠ analysis recomputed ≠ Lean certificate checked ≠ original candidates replayed ≠ new model inference ≠ independent human mathematical adjudication.

This table/index is intended as a reviewer-friendly map, not a substitute for the evidence and limitations in the manuscript.