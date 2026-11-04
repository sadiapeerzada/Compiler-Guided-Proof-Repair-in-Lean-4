# Phase 0: audit, preservation and implementation dependencies

Baseline `fcbda552eb734f4539c5a3d65ba263705bcba63b` is main with merged PR22, including PRs19–21 and all three prior scientific audits. New branch: `research/independent-benchmark-causal-confirmatory-study`. Historical files are read-only: `historical_hashes.json` records all 5867 baseline tracked file SHA-256 values; `preservation.py` verifies them and rejects changes outside this new directory. Untracked user files remain untouched.

The audits already establish Study1 A/B/C 0/60,1/60,1/58 with two unknown C outcomes; V7 4/5/10/9/5/5 of72; V8 11/11/11/11/11/14; V9 5/12 versus5/12 development only. Paired theorem/family bootstraps remain inconclusive. PR22 verified E's first-repair matching (all129 comparisons within one token) while later E histories diverge, and locally checked seven explicit overlap certificate declarations. Nothing here replaces those results or replays historical inference.

| Component | Existing evidence / reusable implementation | New implementation / dependency |
| --- | --- | --- |
| Strict verification | `src/verify.py`: fixed-type harness, prohibited proof escapes/declarations, parsed diagnostics and allowed axiom dependencies | Reuse unchanged, bind candidate hash; add gate/integration checks and preserve unknown infrastructure outcomes |
| Local inference | `src/local_llm_client.py`, `src/model_client.py`: immutable snapshots, no fallback, explicit seeds and no automatic replay | Lazy adapter behind real authorization gate; importing/preflight cannot load weights |
| Protocol approval | `src/local_protocol.py`, frozen v0.4.2 source snapshot: exact artifact bindings; human approval cannot be manufactured | New C/D/E protocol, signed evidence references, benchmark/protocol/compute/verification gates and NO_GO until all dependencies exist |
| Historical data | `publication/dataset/`, Study1 manifests, V7 processed/derivative records, V8/V9 indexed ZIP | Historical inventory and exposure fingerprints; never reclassify these exposed items as a new test |
| Benchmark mathematics | Prior independent-review worksheets and `analysis/taimma_final_professor_validation/OverlapCertificates.lean` | Broader lexical/alpha/family screen and semantic reviewer fields; independent human adjudication remains pending |
| First repair | Frozen Study2 shared-initial structure, donor selection and separate RNG streams | Identical rendered-token budget for C/D/E, same failed predecessor, no silent diagnostic truncation, predeclared donor eligibility and counterbalanced planned order |
| Statistics | Existing paired cluster bootstrap and missingness policies | Prospective C−D primary/C−E secondary, preserved theorem/family clusters, Bonferroni simultaneous intervals, explicit missingness bounds and zero-data status |
| Checkpoints/cost | Existing durable intent/completion journals and no-replay policy | Exclusive append-only run store, reserved calls count toward cap, unfinished intents become unknown, resource limits survive resume |
| Fresh data | No new independently validated candidate pool supplied | 0 eligible new dev/test examples. Curator/reviewer must provide disjoint human-reviewed data and opaque sealed test manifest; calibration must not read test statements |

The historical inventory includes all75 published pool subjects, all36 constructed bridge subjects, and earlier recorded seed/curation versions. Full proof availability and provenance vary: missing fields stay unavailable; compact proof-script specifications are not invented completed Lean proofs. Existing source licensing claims and AI semantic labels are observations awaiting independent scope review.

The prospective 240-test/40-development design is a target, not an obtained sample. Three seeds2037/2038/2039 remain dependent repeats of theorem types. A conservative worst-case normal-approximation half-width at240 independent theorem means is12.7percentage points; the earlier assumed-discordance power calculation requires about628 types for a5-point effect. Eligibility loss/dependence can worsen this. No power guarantee or success percentage is promised.

Execution will stop at NO_GO unless independent benchmark decisions, frozen data/protocol/source/model/environment hashes, explicit resource authorization, and executable verification evidence are present. A software consistency check cannot authenticate a reviewer or grant human authorization. No real development or confirmatory inference is currently justified by available approved data.
