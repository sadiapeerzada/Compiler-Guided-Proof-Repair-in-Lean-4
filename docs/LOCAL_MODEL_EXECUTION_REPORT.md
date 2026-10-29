# Final local model execution report

The genuine development pilot and full 60-case held-out study ran with free local MLX inference. The user directly reported supervisor approval of AI-assisted semantic review replacing independent human semantic review, and free local MLX replacing Groq. Report date: **28 October 2026**. Actual supervisor decision date is unknown. Evidence is the student's direct report, **not independently verified**; no supervisor document, identity, signature or original date has been invented. Exact implementation choices were made under the user's explicit execution authorization.

Exact protocol: `configs/repair_experiment_local_v0.4.2.json`; Qwen2.5-7B-Instruct 4-bit snapshot `c26a38f6a37d0a51b4e9a1eb3026530fa35d9fed`. Every model/tokenizer/template file is bound by `data/local_model/20261027/model_inventory.json`. Runtime: MLX 0.32.4, MLX-LM 0.32.2, Transformers 5.21.0; Apple M4, 16 GiB. The frozen configuration uses one seed 2027, temperature 0.2, top-p 1, 2000 output tokens, 8192 context tokens and at most three repairs per branch. Exact environment/source checks occur before execution.

| Condition | Verified | Rate | Wilson 95% (%) | Missing | Repair attempts |
|---|---:|---:|---|---:|---:|
| A | 0/60 | 0.0% | [0.0, 6.0] | 0 | 0 |
| B | 1/60 | 1.7% | [0.3, 8.9] | 0 | 178 |
| C | 1/60 | 1.7% | [0.3, 8.9] | 2 | 174 |

Actual held-out generation attempts: 412; completed generations: 410; incomplete trajectories: 2. Native model responses, streams, prompts, per-call seeds, timing, strict compiler diagnostics and manifests are preserved in `data/final_study/v1/final_runs/heldout/2027/`. Pilot and interrupted developmental prototypes are retained separately and excluded from study estimates. The actual final pilot resume generated no additional calls.

Model weights are released before Lean and reloaded from identical verified bytes for each independent generation. The actual common initial is counted once physically. A separate MLX workload was observed on the host during execution; its contribution to latency was not measured. Wall times describe this host, not isolated hardware or a causal speed comparison.

No paid API, fallback provider, manually supplied proof counted as model output, hidden replay, or retrospective protocol amendment was used. The earlier Groq and disabled local proposal remain historical artifacts; the final study uses the explicit new AI-policy validator and does not relabel human-review fields.

See `docs/FINAL_EXPERIMENT_RESULTS.md`, `docs/FINAL_EXECUTION_REPRODUCIBILITY.md`, and the raw artifact directory for exact statistics, source hashes and reproduction.
