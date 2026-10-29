# Current final-study claims and evidence

The final manuscript is generated only from `data/final_study/v1/analysis/results.json` and validated raw held-out trajectories. `paper/generated/final_claims_manifest.json` binds quantitative claims to their source hashes; `final_result_validation.json` checks all raw prompts, candidates, diagnostics, budgets and provenance. These artifacts become available only after actual execution, never as placeholders.

| Claim | Authoritative evidence | Scope |
|---|---|---|
| 15 development / 60 held-out eligible examples | `data/final_study/v1/freeze.json`, `dataset_validation.json` | Approved AI policy; no human-review claim |
| Supervisor acceptance of AI review and MLX | `approvals/student_reported.json` | Student report dated 28 October; actual decision date/document unknown, not independently verified |
| Exact primary model and controls | `configs/repair_experiment_local_v0.4.2.json`, model inventory, `heldout_launch.json` | Frozen before held-out generation, one seed |
| Strict A/B/C success and paired statistics | Actual `analysis/results.json`, raw `final_runs/heldout/2027/` | Fixed English/reference target proof synthesis; no unrestricted translation or human semantic-accuracy estimate |
| Tokens, latency and compiler outcomes | Native completions, durable intents, genuine raw verification JSON, rendered evidence | Shared initial counted once physically; reload overhead disclosed |
| Five qualitative examples and repeated-output diagnostics | Actual selected raw trajectories and `analysis/selected_qualitative_examples.json` | Post-hoc descriptive selection; no extra confirmatory tests |
| Compiled manuscript | `paper_build_manifest.json`, `paper/compiled_final_manuscript.pdf` | Actual build only; no venue acceptance claim |

The automatically generated FINAL reports state actual completion and failures. No statistical advantage, significance or equivalence is assumed in advance.

## Historical claims audits (superseded snapshots)

# Paper claims-to-evidence audit

This audit records what can be supported from the repository at the Phase 6
draft. `Unavailable` means the evidence needed to make the claim does not
exist; it is not a zero-valued experimental result.

| Manuscript statement or required claim | Evidence inspected | Status / allowed wording |
|---|---|---|
| Dataset size and composition | `data/analysis/verified_readiness_20261027/readiness.json`, baseline draft, nine `candidate_records.json` batch files | 37 candidates; 29 proposed development / 8 proposed test; 5 categories; 0 eligible. Do not call these benchmark or frozen-split counts. |
| Lean verification coverage | Research inventory and candidate verification metadata | 12 candidates have recorded strict theorem-proof verification; four additional propositions have only statement-type elaboration checks with `sorry` placeholders. This does not imply eligibility or semantic faithfulness. |
| Source provenance and rights | Source ledger; candidate records; DMOI3 source/license statement | 14 item citations point to DMOI3; 21 baseline records lack item-level citations. Rights review and source-byte archival are incomplete. No record is declared cleared for redistribution. |
| A/B/C design | Protocol v0.2.0 and `src/repair_experiment.py` | A/B/C design is implemented/proposed. Protocol is not approved or preregistered. No measured condition outcome. |
| Primary model | Protocol v0.2.0 and historical run manifests | Proposed mutable alias `openai/gpt-oss-120b`; generation access and immutable revision unverified. Historical model strings do not establish API execution. |
| Dataset freeze / held-out test | `data/research_dataset_manifest_v0.1.0.json`; validator inventory | Manifest status is draft; eligible count is 0; no frozen test set exists. No held-out evaluation claim. |
| First-attempt or repair success | `data/analysis/analysis_readiness_v0.1.0.json`; `data/experiments/` inventory | No paired API run manifests; metrics unavailable. Legacy pipeline/pilot outcomes are excluded. |
| Pass@1 from historical demonstrations | `RUN_REPORT.md`, `data/results/run1_core_lean.jsonl`, legacy attempts | Candidate proofs were manually authored and compiler-checked. They are not autonomous model pass@1. |
| Compiler taxonomy effect | Paired experiment manifests and raw matched outcomes | No qualifying A/B/C traces. Taxonomy effect unavailable. |
| Semantic faithfulness | Candidate review fields and review records | All 37 candidates are pending/unreviewed for semantic fidelity; there is no test-set faithfulness estimate. |
| Qualitative examples | Five selected attempt 1/2 pairs from `data/results/attempts/*.jsonl` | Manual compiler-checking examples only. Saved attempt outcomes are failures; legacy records do not preserve exit codes. They are not API or A/B/C examples. |
| Cost, tokens, and latency | Cost guard, run manifests, protocol and raw artifacts | No paired-run aggregates. Pricing remains unverified; no cost estimate or model-run resource total is reported. |
| Statistical evidence | No frozen denominator or matched pairs | Confidence intervals, McNemar tests, Holm-adjusted p-values, and power statements unavailable. |
| Reproduction | Toolchain and Mathlib lock, prompt hashes, scripts, run schemas | Configuration is recorded, but the paper cannot be empirically reproduced until frozen data and raw paired API runs exist. LNCS PDF build also requires Springer class files not present in this repository. |

## Claims excluded from the draft

- No A/B/C success rate, effect size, significance, category effect, or
  semantic accuracy.
- No claim that Lean compilation proves the English translation is correct.
- No claim that requested model metadata proves provider generation occurred.
- No claim that public access to a source establishes redistribution rights.
- No autonomous LLM pass@1 claim from historical manual demonstrations.
- No assertion that the protocol, dataset, pricing, or submission gate is
  approved, frozen, or complete.


27 October 2026 completion update: candidate pool now 37 (29 proposed development, 8 proposed test), still zero eligible; 95 review warnings. Latest machine evidence is `data/analysis/verified_readiness_20261027/readiness.json`. Publisher source bytes were archived with attribution; independent rights and semantic reviews remain pending. New greatest-modulus and Diophantine reference proofs passed strict checks after initial timeouts; both attempts are preserved. Verifier and eligibility defects are detailed in `docs/FINAL_RESEARCH_AUDIT.md`. No A/B/C findings or authentic API examples have become available.

Citation checks on 27 October 2026: miniF2F and ProofNet titles/authors matched their arXiv records; LeanDojo matched the NeurIPS proceedings page; Lean 4 matched Springer DOI 10.1007/978-3-030-79876-5_37; APRIL matched arXiv:2602.02990 (including ICLR VerifAI workshop reference); Beyond Compilation matched arXiv:2606.31002v4. Direct ACM DOI retrieval for Mathlib returned HTTP 403, so publisher-page verification remains unresolved rather than inferred from a successful lookup. Levin's publisher colophon states CC BY-SA 4.0. These are bibliographic checks, not validation of this manuscript's results or venue acceptance.

Mathlib citation follow-up: the project-maintained citation page https://leanprover-community.github.io/cite.html and author manuscript https://arxiv.org/abs/1910.09336 provide primary-source confirmation of the publication. The direct ACM page still returned 403.

## Final local-study revision (completed 28 October 2026)

Current construction evidence: `data/analysis/m1_m7_delivery_20261028/summary.json` and `readiness.json`: 96 candidates (30 proposed development, 66 proposed test), 96 strict reference proofs, zero independent reviews/eligible/frozen examples, 192 review warnings. Source records and exact proof overlays are traceable under `data/curation_batches/v0.2.0/`, `v0.2.1/` and `data/reference_verification/`. Earlier inventory rows above describe previous snapshots.

Actual local evidence is limited to three neutral READY backend checks. There are no genuine mathematical A/B/C pilot or held-out outcomes. Local substitution, model/protocol approval and dataset eligibility remain unresolved. No inferential/semantic advantage claim is supported. The official Springer/Tectonic pre-results PDF builds; author metadata, authentic model examples and empirical results remain missing.
