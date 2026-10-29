# Final dataset preparation — completed 28 October 2026

Status: PARTIAL. Independent review/eligibility/freeze: BLOCKED.

| Measure | Actual count |
|---|---:|
| Candidates | 96 |
| Proposed development / test | 30 / 66 |
| Strict proof-verified candidates | 96 |
| Independent semantic reviews completed | 0 |
| Eligible development / test | 0 / 0 |
| Frozen examples | 0 |
| Categories | 5 |
| Structural errors | 0 |
| Review warnings | 192 |

Machine evidence: `data/analysis/m1_m7_delivery_20261028/{summary,readiness}.json`.

Added 59 library-derived candidates across all five categories, with explicit English paraphrases, exact Lean signatures and reference code, assumptions/imports, provisional difficulty/families, pinned source-item citations, original source bytes/copyright notices and Apache-2.0 license evidence. The batches of 52 and seven verified in `data/curation_batches/v0.2.0/references_expanded.lean` and `v0.2.1/references_expanded.lean`, compiler exit 0, with complete diagnostics and an approved axiom list for every target theorem. Earlier failed authoring checks are preserved. These are authored reference proofs, not model experiment outputs.

Twenty original statements gained additional exact-statement proof evidence through `data/reference_verification/v0.1.0/proof_overlay.json`; five further statements are covered by `v0.2.0/proof_overlay.json`, including an explicit candidate-definition module for the previously undefined geometric sum. The overlay preserves historical records, checks all evidence hashes and compares the actual theorem types in Lean. Expected-statement placeholders are used only for type comparison; the candidate proofs contain no forbidden shortcuts, and none of the twenty target axiom lists contains sorryAx. The validator now recognizes the actual structured compiler argv as well as legacy command strings, with malformed/empty argv rejected.

Remaining reference-proof gaps: none in the prepared 96-record inventory. The original geometric-sum context was incomplete; its historical statement is preserved, and the current prepared version explicitly imports and displays the hash-pinned definition. All original source, semantic, family and rights review issues still require genuine decisions. Compilation does not resolve them.

Current category counts: arithmetic identities 18; divisibility 26; induction 18; inequalities 19; modular arithmetic 15. Sixty-six proposed test records is a candidate count, not sixty independent eligible held-out problems. Whole-family review may merge or exclude generalizations; source overlap/pretraining exposure and direct named-lemma retrieval must be assessed. Unique family identifiers do not establish independence. No candidate in the new batch was used for mathematical model inference or prompt/model selection.

Review-ready Markdown, JSON packets and blank decision forms for all 96 candidates: `data/review_packets/m1_m7_delivery_20261028/README.md`. Source-sensitive and mathematical decisions remain pending. There are 75 item-cited candidates; the original 21 still lack adequate item-level provenance. Archived licenses are not fabricated rights-review approvals.

No freeze was attempted as a workaround. Frozen validation records 14 rejection reasons, including missing approval, exact split-manifest requirements and zero eligible counts. Still required: at least 60 genuinely independent eligible test examples and 15–20 separate eligible development examples; independently select whole development families from the 30 candidates, resolve exclusions and expand the pool if needed. Then freeze ordered IDs, exact bytes and approvals before any held-out run.

The final prepared geometric-sum source imports `Nl2Lean.CandidateDefinitions` and displays the exact definition for review/model prompts. Its source hash is included in the proposed local protocol and review binding. No independent review is inferred from this preparation. Evidence directories retain the collection start date, 27 October 2026.

The final seven sourced candidates add one provisional development family and six provisional test families, bringing item-cited assignments to 15 development and 60 test before exclusions/review. Archimedean/floor examples were screened out to avoid padding the rational-density family. All 75 cited candidates still require genuine independent review; these assignments do not establish eligible counts.
