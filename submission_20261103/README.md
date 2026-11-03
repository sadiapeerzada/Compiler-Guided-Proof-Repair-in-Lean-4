# TAIMMA 2027: two-study revision for supervisor review (3 November 2026)

This directory contains a **separately versioned manuscript**. It does not replace the six-page author-supplied original study or the historical 31 October candidate. Its source is `main.tex` and its short title is *Controlled Lean 4 Proof Repair Pilots*.

## Build and status

The authoring environment compiled this source with the Springer `llncs` class using two passes of:

```sh
cd submission_20261103
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdfinfo main.pdf | grep Pages
```

**Observed at creation: 5 A4 pages**, no overfull-box or unresolved-reference messages in the second build. This is a local build check, not venue or supervisor approval. The compiled PDF was delivered separately to the requester; this GitHub branch stores the editable LaTeX source, not a new binary PDF.

## What the paper reports

- **Original Study 1:** A 0/60, B 1/60, C 1/58 observed, 2 unavailable C outcomes. Both B and C verify the same single target on 58 complete pairs. Do not treat missing C outcomes as failures.
- **Separate constructed Study 2 V7:** 24 elementary types across three seeds; A 4/72, B 5/72, C 10/72, D shuffled 9/72, E matched 5/72, R resampling 5/72. Correct diagnostics are *not* demonstrably superior to shuffled diagnostics.
- **Study 2 V8 Coder:** A/B/C/D/E each 11/72; R 14/72; separately run and exploratory. The V8 lock does not represent a preregistered second-model study.
- **Study 2 V9 development only:** new error-aware repair 5/12, previous Coder-guided 5/12. No new held-out test result was created.
- **Benchmark caveat:** 24/24 reference proofs checked, 40 V8 manifest entries checked locally, nine AI flags and multiple family-overlap candidates remain subject to independent adjudication. Synthetic English descriptions cannot measure NL-to-Lean semantic faithfulness.
- **Post-hoc sensitivity:** reported as a *separate descriptive audit*, not as a replacement denominator. See `research/study2-final/V7_POST_HOC_SENSITIVITY.csv` and its read-only script.

## Release gate

**For supervisor review only. Not all 29 requested revisions have been independently approved.** In particular, there is no demonstrated general compiler-feedback advantage, no independent semantic gold validation for constructed English placeholders, no clear pretest-freeze repair for discovered overlap, and no proof of full raw journal replay from the publicly committed files. Author/category/anonymity details and venue-specific submission requirements still need approval.

The historic source `submission_20261031/main.tex`, frozen Study 1 evidence under `publication/`, and frozen V7 inputs/results are intentionally not rewritten.
