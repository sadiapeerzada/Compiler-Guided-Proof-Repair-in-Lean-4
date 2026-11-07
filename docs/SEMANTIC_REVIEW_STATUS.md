# Semantic review status

> **Historical phase document.** This page records an earlier experiment or review stage and is preserved for provenance. For the current two-study research, consult the [evidence index](MANUSCRIPT_EVIDENCE_INDEX.md), [historical classification](HISTORICAL_DOCUMENTS_INDEX.md) and [release readiness](RELEASE_READINESS.md). This note does not imply that any outstanding human decision has been completed.


Status: BLOCKED for review outcomes; workflow implementation is available.

All 96 candidates remain pending independent semantic review. No reviewer ID, date, decision, signature, source permission or supervisor approval has been invented.

Start at `data/review_packets/m1_m7_delivery_20261028/README.md`. Each Markdown packet includes English, Lean, exact binders/quantifiers, assumptions/imports, source, category/difficulty/family/split, complete proof-verification status and reviewer instructions. Companion JSON and `.decision.json` files bind decisions to English, Lean, imports and assumptions using SHA-256. Labels are faithful / not faithful / uncertain, initially blank.

`src/semantic_review.py` imports authentic human decisions only with an externally supplied human-verified qualified Lean reviewer registry, actual reviewer identity/date, independence attestation, substantive explanation, and matching evidence-artifact bytes. It rejects unknown/self reviewers, stale statements, future dates, changed evidence, duplicates and conflicting completed decisions needing adjudication. Import writes a fresh candidate snapshot and receipt; historical records and unrelated license, family, split and eligibility statuses are not promoted. Hashes establish binding, not human identity: a qualified human must actually verify the registry/evidence; these records cannot be supplied by an agent pretending to be a reviewer.

Example commands, after real decisions and registry exist:

```sh
.venv/bin/python src/semantic_review.py --output-dir /tmp/new-review-packets
.venv/bin/python src/semantic_review.py --decisions <actual-decisions.json> \
  --reviewer-registry <human-verified-registry.json> --output-dir <fresh-import-dir>
```

The `semantic_success` function requires successful compilation plus a current independently validated faithful decision. Compilation alone, an uncertain/not-faithful label, or missing registry/evidence yields false. Tests cover Lean-compiling but unfaithful formalizations and changed English/Lean bindings. The primary A/B/C runner independently requires an eligible fixed reviewed reference theorem, identical for all conditions. It cannot substitute a generated unreviewed statement for that reference.

Actual generated statement results can be prepared separately with `--generated-results <actual-pipeline-results.jsonl>`. Each generated subject gets a distinct run-bound ID, preserves its English/reference comparison and raw result hash, and resets semantic decisions to pending. It never inherits a reference's faithful label or treats `solved: true` as semantic success. This path was tested synthetically; there are no genuine mathematical generated subjects to review yet.
