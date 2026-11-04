# Final experimental completion handoff

**Status: SAFE IMPLEMENTATION COMPLETED; DEVELOPMENT AND CONFIRMATORY EXECUTION NO_GO.** No new model inference ran. No new independently approved test or development examples exist. Independent benchmark adjudication is **PENDING_INDEPENDENT_HUMAN_ADJUDICATION**. No unexecuted experiment is called complete.

## A. Implemented components and commits

Baseline: `fcbda552eb734f4539c5a3d65ba263705bcba63b`, main including merged PR22 and the earlier PR19–21 evidence. Branch: `research/independent-benchmark-causal-confirmatory-study`.

- `7b03be898ebb70aaf65bd4bb9acc33fdcdf1baf0`: phase0 audit/preservation and historical inventory/reviewer infrastructure.
- `95eb9c94ae3e39e746d7f5a17e684230fea4e990`: isolated runner, approval/source locks, real offline checks, prospective analysis and regression tests. Later handoff documentation is the branch tip; use `git rev-parse HEAD` for its final exact SHA.

| Component | Exact implementation |
| --- | --- |
| Inventory, overlap and semantic packets | `benchmark_inventory.py::records/main`; `benchmark_inventory.csv`, `overlap_candidates.csv`, `semantic_review_packet.json`, `human_adjudication_template.csv`, `benchmark_validation_manifest.json`, `historical_exposure_index.json` |
| Candidate intake and partitions | `dataset_tools.py::screen/cohort_flags/partition/intake`; historical quarantine, within-cohort alpha-duplicate flags, deterministic whole-family assignments and exclusion registry |
| Strict offline references | `reference_check.py`; `lean_adapter.py::LeanVerifier/live_environment`, reusing unchanged `src/verify.py` with the fixed expected-type scaffold and frozen scoped imports |
| Matched C/D/E controls | `matching.py::diagnostic_payload/pad_exact/matched_conditions/donor_order/planned_orders`; fixed predecessor/theorem, whole error messages, exact rendered4096-token budget or invalid comparison |
| Real execution gates | `isolated_repair_validation.py::gate/require_go/check_source_lock/human`; exact artifact/subject/model/code/data bindings and independent-review/resource/freeze requirements |
| Inference and runner | `backend.py::LocalBackend/RenderedTokenizer`; `isolated_repair_runner.py::execute/run_core/perform/collect/export`; production gate before tokenizer/weight initialization and again before generation |
| Safe checkpoint/cost handling | `checkpoint.py::RunStore`; exclusive append-only intent/ledger/result files, no replay, reserved calls consumed, actual metadata separated from intended budgets and unknown costs |
| Statistics | `paired_analysis.py::validate_rows/bootstrap/analyze`; C−D primary, C−E secondary; theorem/family clusters, nominal Bonferroni simultaneous intervals, full-grid/phase/model checks, initial-eligibility and missingness bounds, categories and recorded costs |
| Integrity and evidence | `preservation.py`, `historical_hashes.json`, `historical_integrity_checks.json`, `offline_integration_results.json`, `implementation_lock.v2.json`, `verification_evidence.v2.json`, `readiness_status.json` |

The prospective protocol and current engineering source lock are auditable candidates, **not human preregistration**. V1 is retained as an intermediate nonexecuted engineering snapshot; the execution bundle points to v2. Actual preregistration and test freeze cannot be completed before genuine reviewed data and human decisions exist.

## B. Validation

See TEST_RESULTS.md for exact commands, passed/excluded/failed checks and limitations. The current scoped suite passed323 tests plus28 subtests, with three explicit deselections; archived post-hoc tests passed19. All23 new tests passed. One older blanket scope test failed because it forbids any new research directory, not because historical evidence changed; it remains unmodified and the failure is disclosed. Do not call the unrestricted suite fully passing.

Real Lean accepted the valid integration fixture and rejected placeholder, weakened-target and invalid-proof fixtures. The tokenizer-only check measured4096 rendered input tokens for each C/D/E condition, using the pinned tokenizer/template without loading weights. This is real compiler/tokenizer integration, not real-model generation or an end-to-end experimental result. Offline testing caught and corrected the new adapter's expected-type scaffold before the current lock.

All5867 baseline tracked artifacts remain byte-identical. Read-only archive verification passed all4736 indexed members and40 frozen lock entries. Existing experiments, manuscripts, data, prompts, outputs, analysis scripts and historical hashes were not rewritten. Original V7 raw history remains weaker than the indexed V8 release; local-path privacy warnings remain unresolved.

## C. Benchmark adjudication

The inventory contains193 distinct ID/statement/English **versions**, not193 independent new problems. It includes all75 published Study1 pool items, all36 bridge examples and earlier seed/curation records. Automated screening produces170 flagged/referenced record-version pairs, including the five already certified bridge relationships. Exact lexical/family matches, implications, specialization and explicit Lean transport are kept distinct from exclusion decisions.

Human identity, qualifications, semantic gold labels and signatures are not fabricated. Every review remains pending. Missing standalone reference proofs, licensing or difficulty evidence is explicitly unavailable/provisional; recorded compact tactic specifications are not invented completed proof outcomes. Semantic packets request quantifiers, domains, assumptions, boundaries/operators, premises, ambiguity and strengthening/weakening judgments.

New independently eligible development count: **0**. New independently eligible test count: **0**. No historical/inspected item is promoted to an untouched test. External independently reviewed candidates are required; a lexical screen cannot rule out mathematical relatedness or model pretraining contamination.

## D. Execution status

| Milestone | Actual state |
| --- | --- |
| Infrastructure and prospective analysis | Implemented and offline-tested |
| Synthetic fixture tests | Passed; temporary outputs only, never research data |
| Real Lean integration | Passed within the recorded safety-fixture/import scope |
| Real tokenizer accounting | Passed: C/D/E each4096 input tokens |
| Model inference/backend execution | NOT RUN; no performance, latency or device feasibility claim |
| Development inference/calibration | NOT RUN,0 calls; no approved fresh development data/resource authorization |
| Confirmatory benchmark constructed and approved | NOT COMPLETED;0 eligible new subjects |
| Genuine preregistration/test freeze | NOT COMPLETED; only an engineering candidate lock exists |
| Confirmatory inference/analysis | NOT RUN,0 calls; NO_GO |

`isolated_repair_results.csv` is header-only. It contains no success/failure rows and no fabricated rates. Run exports, if later authorized, will preserve unknown/not-started rows and actual strict outcomes separately from invalid comparison endpoints.

## E. Experimental results

There are **no new model-evaluation results**. Historical Study1/V7/V8/V9 results remain exactly as documented in the prior audits. Do not interpret synthetic test effects, real Lean safety fixtures or successful token matching as evidence that diagnostics improve repair success. No statistical significance or equivalence claim is made.

## F. Scientific limits and resource feasibility

A first-repair shared-predecessor design removes later-history divergence, but equal input-token counts/output caps do not force equal output expenditure, latency or all semantic/attention effects. Shuffled donors from different declared families may still be mathematically related; independent review and frozen prohibited-pair decisions remain necessary. Whole diagnostics are preserved; an oversize/unmatchable comparison is incomplete, not manipulated to fit. Byte-identical real/donor payloads are ineligible under the frozen rank rule.

The target240 types ×three seeds is not an obtained or adequately powered sample by assertion. Dependence, family overlap, initial successes, invalid comparisons and unknown eligibility can reduce effective precision. The prior12.7pp worst-case normal-approximation half-width is a planning assumption, not a guarantee. Reassess actual eligible counts and precision before a genuine freeze.

The2880-call allocation covers the full proposed test worst case (720 initials+2160 repairs), but40×three-seed development cases could add480 calls. The shared ledger refuses to silently exceed the allocation. A separately explicit prior resource/protocol amendment or a smaller approved design is required; do not start calibration and later pretend the full test worst case remains funded.

## G. Outstanding owners and exact next steps

| Blocked action | Owner/dependency | Required next action |
| --- | --- | --- |
| Fresh data construction | Independent curator/source owner | Supply new licensed/source-traceable candidates with genuine NL, formal types, references and families; keep test statements away from calibration/protocol selection |
| Mathematical and semantic approval | Qualified independent Lean/mathematics reviewer | Inspect exact subjects, relationships and source evidence; sign bound mathematics/NL/family/split/licensing decisions with independence/conflicts disclosed |
| Reference validation | Curator/Lean expert | Run the offline reference checker under the exact intended imports/pins and bind real results to every subject |
| Actual sample and precision | Research lead/statistical reviewer | Assess eligible independent types/families and freeze defensible counts/analyses before inspecting test outcomes; do not fill a240 target with invalid duplicates |
| Genuine preregistration | Research lead | Create a separately signed pre-outcome/test-access freeze binding approved protocol, subject manifests, implementation/environment and analysis hashes |
| Compute authorization | Resource authority | Sign phase-specific call/runtime approval and resolve the calibration-versus-test allocation conflict before execution |
| Development/confirmatory run | Authorized operator | Verify actual pins, GO and available remaining resources, then execute only the approved phase; no automatic substitution, retry, model fallback or outcome-dependent tuning |

APPROVAL_AND_FREEZE.md specifies the required fields/artifacts. Software checks consistency of genuine decisions; they cannot authenticate a person or turn a readiness score into human authorization. No reviewer or execution authorization is currently supplied.

## H. Reproducibility and delivery

Use README.md for safe commands and the bundle layout. `preservation.py` verifies history without private model caches. The inventory, source lock, signed-review templates, results schema, offline check logs, prospective code and missingness rules are committed. Tokenizer-only checks require local tokenizer assets; actual inference additionally requires the exact weight cache, runtime and real approvals. Running status is safe and returns NO_GO without releasing test records. Do not invoke an unapproved full matrix.

The branch is pushed for review without force-push, merge or submission. Final commit SHA and branch URL are reported at delivery. Completion here means concrete, tested infrastructure and transparent blockers; it does not claim independent human adjudication, fresh approved test construction or an unexecuted confirmatory experiment has been completed.
