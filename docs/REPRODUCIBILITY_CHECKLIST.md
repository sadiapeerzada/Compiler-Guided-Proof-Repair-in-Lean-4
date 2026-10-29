# Reproducibility verification

**M6: COMPLETE for the exact local professor requirement.** Complete does not mean all private original prompt bytes are publicly disclosed.

- Stable Lean 4.32.0 and Mathlib `81a5d257c8e410db227a6665ed08f64fea08e997` match frozen and live environment checks.
- Every model, weight, tokenizer and native chat-template file matches the frozen inventory. Qwen2.5-7B-Instruct 4-bit revision `c26a38f6a37d0a51b4e9a1eb3026530fa35d9fed`; runtime MLX 0.32.4 / MLX-LM 0.32.2 / Transformers 5.21.0 / NumPy 2.5.4 validated.
- Dataset manifest `de0850197b821ca4c519737c4cffb16d78e2a329d15be6c7f3c6a7f5487db67f` and protocol `a032110d7afbc367c2daa820bd17511c6ff5dba2d1164e0130ea5d1c4b693317` recalculate exactly. All frozen pinned source/template/environment files validate.
- The operative AI-review/freeze validator passes for 15 development / 60 test examples. Legacy human-review gates remain intact; AI records are not imported as human reviews.
- All 410 raw response/stream/prompt/target/verification bindings and 60 pairings validate. All 96 reference proofs freshly compile in the pinned environment. Both claimed final model successes freshly compile against exact targets with only allowed axioms; no `sorry`, `admit`, `sorryAx` or added assumptions are accepted as successes.
- 297 Python tests and 28 subtests passed; Lean build passed (8,658 jobs). Actual output/exit statuses: `data/final_review/20261029_v2/verification_steps.json` and its log paths.
- Metric regeneration is byte-identical in a fresh output directory. All 2394 original final-study artifacts retain their hashes. No inference was performed during verification.
- Editable source-file whitespace is checked separately. Original generated `.lean` evidence and CSV exports retain historical trailing whitespace/CRLF. They are immutable data, not source to normalize; old raw diff-check findings remain preserved, not relabeled as passing source checks.

Public evidence is a labeled redacted view. All candidate proof texts preserve original hashes, and aggregate/pairing reanalysis is public, but 172 C prompt byte strings differ because home paths in diagnostics are redacted. Original hashes/seeds/token counts still describe original bytes. Exact prompt replay and complete private source-evidence validation require the preserved original checkout; model weights and backend can be restored from pinned public revisions, but private exact paths cannot be reconstructed from the redacted bundle alone. No bit-identical cross-hardware generation claim is made.

Core evidence: `environment_verification.json`, `reproducibility_verification.json`, `reference_axiom_validation.json`, `verification_steps.json`, `analysis_verified/results.json`, and `analysis_repeat/results.json`, under `data/final_review/20261029_v2/`.
