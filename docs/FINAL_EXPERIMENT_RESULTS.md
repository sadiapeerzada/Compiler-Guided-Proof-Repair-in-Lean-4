# Final genuine experimental results

The user directly reported supervisor approval of AI-assisted semantic review replacing independent human semantic review, and free local MLX replacing Groq. Report date: **28 October 2026**. Actual supervisor decision date is unknown. Evidence is the student's direct report, **not independently verified**; no supervisor document, identity, signature or original date has been invented. Exact implementation choices were made under the user's explicit execution authorization.

All 60 frozen eligible held-out statements were processed under one seed, 2027, using the exact cached Qwen2.5-7B-Instruct 4-bit snapshot. The final development pilot and actual no-new-generation resume check passed control/provenance validation. Pilot model failures were not counted as held-out results.

| Condition | Verified | Rate | Wilson 95% (%) | Missing | Repair attempts |
|---|---:|---:|---|---:|---:|
| A | 0/60 | 0.0% | [0.0, 6.0] | 0 | 0 |
| B | 1/60 | 1.7% | [0.3, 8.9] | 0 | 178 |
| C | 1/60 | 1.7% | [0.3, 8.9] | 2 | 174 |

Full-denominator rates and Wilson intervals count missing outcomes as failures for sensitivity; paired tests use complete matched outcomes. Incomplete trajectories: **2**. Individual/problem-level inference assumes independence; family-cluster intervals address the recorded related-target grouping. `None` McNemar p-values mean no informative discordant-pair test, not equivalence.

- C_vs_B: +0.0 pp; family-cluster 95% [+0.0, +0.0] pp; complete pairs 58; exact McNemar p=None; Holm p=None.
- C_vs_A: +1.7 pp; family-cluster 95% [+0.0, +5.5] pp; complete pairs 58; exact McNemar p=1.0; Holm p=1.0.
- B_vs_A: +1.7 pp; family-cluster 95% [+0.0, +5.5] pp; complete pairs 60; exact McNemar p=1.0; Holm p=1.0.

Actual generation attempts: **412**; completed generations: **410**. Known completed-call prompt tokens: **362,035**; completion tokens: **130,401**. Physical totals count the shared initial once, while each condition's counterfactual resource row includes it. Complete native generation seconds: **11233.6**; recorded trajectory wall seconds: **108797.3**. Unknown interrupted-call endpoints are not invented.

Actual outputs: `analysis/results.json`, `condition_results.csv`, `initial_failure_outcomes.csv`, `rendered_evidence.json`, `selected_qualitative_examples.json`; all relative to `data/final_study/v1/`. Figures and four main tables are under `paper/generated/final_*`. The selected authentic examples are lib_a_exp_add, div_007, lib_a_trig_unit, div_008, div_011; their display-only snippets are truncated/transliterated, while original Unicode outputs remain unchanged.

Limits: one primary seed (2027), one general instruction model and quantization; 60 test statements in 54 curated family clusters, rather than 60 independent topic families; five development clusters; author-assisted AI adjudication and unreliable independent-model judgments; named-lemma/pretraining exposure; fixed-theorem proof synthesis rather than unrestricted NL translation; B-before-C order and host/cache effects on timings. These limits remain explicit rather than being concealed as completed multi-seed or independent-human validation.

No paid inference, fabricated score, manual proof counted as model output, hidden retry or retrospective protocol change was used.

Repair calls per eligible problem (60-case denominator, including zeros and consumed interrupted intents):

- A: mean 0.00; median 0.0.
- B: mean 2.97; median 3.0.
- C: mean 2.90; median 3.0.

A read-only process sample identified another local MLX workload on the host during execution. Its duration and overhead were not measured; timing is observed shared-host performance, not an isolated-hardware benchmark. See `runtime_observations.json`.

Incomplete generation streams additionally preserve **0** observed output tokens. These are retained partial tokens, not completed responses or an invented exact total beyond the durable stream; completed-call totals above exclude them.

Unavailable condition outcomes and recorded causes:

- `lib_a_trig_unit` / C: Context budget exceeded; incomplete_interrupted_generation.
- `lib_i_bernoulli` / C: Interrupted generation; incomplete_interrupted_generation.

Checkpoint recovery preserved an interrupted generation without replay. Its trajectory elapsed wall time includes the inactive interval before recovery and must not be read as uninterrupted compute time. Exact recovery records and hashes are in `data/final_study/v1/resume_history/`.
