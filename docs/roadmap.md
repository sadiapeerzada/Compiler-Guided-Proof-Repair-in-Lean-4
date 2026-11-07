# Research roadmap

> **Historical phase document.** This page records an earlier experiment or review stage and is preserved for provenance. For the current two-study research, consult the [evidence index](MANUSCRIPT_EVIDENCE_INDEX.md), [historical classification](HISTORICAL_DOCUMENTS_INDEX.md) and [release readiness](RELEASE_READINESS.md). This note does not imply that any outstanding human decision has been completed.


This roadmap reflects the repository state on 21 October 2026. It supersedes
the original prototype timeline; no deadline or experiment is assumed to have
passed merely because an earlier roadmap listed it.

## Current state

- The curation inventory contains 35 candidates and zero eligible records.
  Proposed splits are not frozen.
- The paired A/B/C protocol is version 0.2.0, proposed for review but not
  independently approved or preregistered.
- The paired experiment runner and fail-closed cost guard have mocked tests.
  API mode remains disabled because model generation access, pricing evidence,
  budget approval, dataset freeze, and protocol approval are unresolved.
- The analysis implementation is in `eval/paired_analysis.py`. It currently
  emits a readiness audit only; no A/B/C tables or figures can be computed.
- `paper/main.tex` is a pre-results Springer LNCS draft, not a submission-ready
  manuscript. The required empirical outputs are explicitly unavailable.

## Dependency-ordered next work

1. **Dataset construction:** archive exact source/page evidence, resolve
   rights, verify theorem statements under the pinned Lean/Mathlib environment,
   and complete independent semantic, statement, assumption, self-containment,
   family, split, and duplicate reviews. Acquire enough distinct problems to
   reach at least 15 development and 60 held-out test examples. Keep related
   theorem families within one split.
2. **Protocol and execution gate:** obtain independent protocol approval and
   preregistration; verify official model-specific pricing and token-bound
   assumptions; verify account generation access and the cost-reservation path.
   Until then, do not make API calls or spend credits.
3. **Freeze before evaluation:** freeze separate development and test files,
   ordered IDs, exact hashes, and approval evidence. Prompt tuning and model
   selection use development only. Do not access test outcomes before the
   preregistered evaluation.
4. **Approved pilot:** after gates 1–3, obtain explicit approval for a fresh
   run directory, fixed problem allowlist, model, and spend cap. Audit raw
   prompts/responses, transport attempts, reservations, Lean diagnostics,
   and paired initial-candidate identity before scaling.
5. **Full paired evaluation and analysis:** run A (one-shot), B (blind retry),
   and C (compiler-guided) with one shared initial candidate, identical fixed
   theorem and environment, and at most three repairs for B/C. Generate all
   metrics, tables, figures, intervals, and tests only from validated saved
   artifacts.
6. **Paper and claims review:** replace unavailable outputs only with
   reproducible analysis outputs. Audit every claim against the frozen
   manifest, raw run hashes, human review records, and source/license evidence.

## Historical artifacts

`RUN_REPORT.md`, `data/results/run1_core_lean.jsonl`, and the legacy figures
are retained for historical context. The report identifies the proof writing
as manual and distinguishes genuine Lean compiler checks from API execution.
Those demonstrations are not autonomous model pass@1 and do not answer the
paired A/B/C research question.
