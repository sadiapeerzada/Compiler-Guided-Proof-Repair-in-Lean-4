# Release readiness — decision register

[Current paper](../README.md) · [Evidence index](MANUSCRIPT_EVIDENCE_INDEX.md) · [Historical index](HISTORICAL_DOCUMENTS_INDEX.md) · [Rights](../publication/third_party/RIGHTS_AND_ATTRIBUTION.md)

**Overall status: NOT FULLY CLEARED.** This is a review handoff, not a certificate. No independent reviewer identity, signature, supervisor approval, rights clearance or archive privacy sign-off was created for this cleanup.

| Gate | Evidence | Necessary decision | Status |
|---|---|---|---|
| Mathematical and semantic adjudication | [Independent review required](../analysis/taimma_final_professor_validation/HUMAN_ADJUDICATION_REQUIRED.md) and [review packet](../analysis/taimma_supervisor_final/INDEPENDENT_BENCHMARK_REVIEW_PACKET.md) | A qualified independent Lean/mathematics reviewer must inspect source/type fidelity, flagged formal relationships, family overlap and split leakage, then provide signed, dated, source-bound findings | **OPEN** |
| Raw archive privacy | [Warning manifest](../research/study2-raw-v8-v9/PRIVACY_SCAN_WARNINGS.json) | A responsible custodian must inspect actual flagged files, decide permitted release/redaction/restriction and document the decision | **OPEN** |
| Source rights and attribution | [Rights notice](../publication/third_party/RIGHTS_AND_ATTRIBUTION.md) | Responsible authors or rights reviewer must confirm licenses, permissions and required third-party credits for the precise release | **OPEN** |
| Manuscript release decision | [Paper claims](../README.md) and [curated scope](../publication/curated-release-20261107/RELEASE_SCOPE.md) | Authors/supervisor must confirm manuscript version, scientific limits, Table 10 alignment and dissemination scope | **OPEN** |

## What the repository-level audit establishes

The six manuscript Table 10 paths exist, the curated package contains 17 files and its 11 derived CSVs have recorded SHA-256 hashes. The original archive warning manifest identifies **1,220 warning records, totalling 22,882 local-path occurrences**, and requires manual review. A negative high-confidence credential regex result is **not** general privacy clearance.

Historical model identities, experimental input templates, independent-review worksheets, and unfavourable or incomplete outcomes are scientific provenance, not disposable assistant conversation. As of this inspection, 60 tracked repository paths contain the term **prompt**; these include original study inputs and measurements. Renaming or removing them can invalidate pinned hashes, references, or reproduction instructions.

Neither deleting these files nor changing words such as “pending” would resolve the corresponding scientific or legal gate. A cleared decision needs an actual named reviewer/custodian, date, conflicts statement where relevant, exact artifact IDs/hashes, rationale, corrective steps, supporting evidence and approval. The archive is **already public**, so a qualified custodian should assess current exposure as well as any further redistribution; deletion from a branch does not remove Git history.

## Automated reviewer commands

From the repository root:

- `python3 scripts/check_manuscript_evidence.py` — original Table 10 paths and active documentation links
- `python3 scripts/audit_publication_surface.py --scope curated --strict` — limited release-surface wording and identifier screening
- `python3 scripts/audit_publication_surface.py --scope full --report-json /tmp/lean4-audit.json` — inventory of the entire tracked tree
- `python3 publication/curated-release-20261107/verify_release.py` — SHA-256 comparison of copied derivative CSVs

The archive scan is informational. A passing curated scan or checksum check does **not** close any human-reviewed release gate listed above.
