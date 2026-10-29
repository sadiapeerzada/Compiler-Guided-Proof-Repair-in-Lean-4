# Reproducing the final local study

The executed protocol is `configs/repair_experiment_local_v0.4.2.json`, SHA-256 `a032110d7afbc367c2daa820bd17511c6ff5dba2d1164e0130ea5d1c4b693317`. Scientific source and frozen inputs were committed at `fe8fbee` before any held-out generation. The final delivery commit additionally contains the resulting evidence and reporting code. This is an internally frozen, hash-bound protocol, not a claim of external preregistration.

The approval record is `data/final_study/v1/approvals/student_reported.json`: direct student-reported supervisor approval of AI-assisted semantic review and local MLX, reported 28 October 2026. The actual supervisor decision date and original document/signature were not supplied. No independent verification or supervisor-authored artifact is invented. The user separately authorized automatic dataset/protocol finalization and execution.

## Dataset and eligibility

The new versioned AI policy and validator are in `data/final_study/v1/ai_eligibility_policy.json` and `src/final_study.py`. All 75 eligible rows have a content-bound faithful AI adjudication, source and license evidence, strict reference/type proof evidence and a whole-family split assignment. Exact duplicate and source-insufficient originals are excluded. Two corrected originals retain fresh proof checks and repeated separate-model reviews but remain excluded for missing source provenance.

Fifteen development statements and 60 held-out statements occupy five and 54 curated family clusters, respectively; the family sets are disjoint. These are not 75 independent topic families. The analysis retains this limitation and includes family-cluster bootstrap sensitivity. Dataset ordering and bytes are fixed in `freeze.json`; historical human-review/curation fields are preserved, not relabeled as human decisions. The operative approved-method eligibility is the separate `study_eligibility` field. The historical human-only validator/importer remains strict and is not falsely represented as passing AI records.

## Model and runtime

The exact primary snapshot is `mlx-community/Qwen2.5-7B-Instruct-4bit` at `c26a38f6a37d0a51b4e9a1eb3026530fa35d9fed`. `data/local_model/20261027/model_inventory.json` binds every weight, tokenizer, quantization and chat-template file. Restore these exact public bytes in the declared local Hugging Face cache path before reproduction; model weights are not committed. Custom remote model Python code and fallback models are disallowed. The client uses offline loading and checks the snapshot again at each reload.

The recorded host is Apple M4, 16 GiB RAM; exact observations are in `hardware_runtime.json`. Runtime package versions are frozen in the protocol and checked before execution. Lean is 4.32.0, Mathlib is clean at `81a5d257c8e410db227a6665ed08f64fea08e997`; the lockfile and actual executable/checkout are checked separately. Model weights are released during memory-heavy Lean checks and reloaded unchanged for the next independent call. Full trajectory/model-call wall times include reload overhead; native generation telemetry excludes loading. A read-only process sample during the held-out run identified another local MLX workload on the host (`runtime_observations.json`). Its duration and attributable overhead were not measured. Timings therefore describe observed shared-host execution, not an isolated-hardware benchmark; no other workload was modified.

There is one primary seed, 2027, temperature 0.2, top-p 1, a 2,000-token output cap and 8,192-token context cap. Per-call RNG derives from the base seed, logical phase/problem/step context and exact prompt SHA-256. This prevents B stopping from shifting C's stream. Reproducibility is scoped to the recorded backend/hardware; identical outputs on another platform are not guaranteed.

## Actual execution and resume

The agent executed these commands; they are documented for reproduction, not a request for the student to run the study manually:

```sh
.venv/bin/python scripts/run_final_study.py \
  --protocol configs/repair_experiment_local_v0.4.2.json \
  --phase development_pilot
.venv/bin/python scripts/audit_and_execute_final_study.py \
  --protocol configs/repair_experiment_local_v0.4.2.json
```

The second command audits real pilot output/provenance and performs an actual pilot resume with no new generation calls. Only after that check does it automatically launch all frozen held-out cases and paired analysis. `pilot_audit.json` records an AI engineering/control audit, not a human or supervisor signature. Model failure is an observed outcome rather than proof that a control failed.

The final run path is `data/final_study/v1/final_runs/{phase}/2027/{problem_id}/`. Each initial/B1–B3/C1–C3 step stores durable intent, raw completion and native metadata, candidate bytes, strict verification and raw compiler JSON. Per-token streams retain interrupted output. Each trajectory manifest binds its protocol, dataset, initial SHA-256, branch states, actual attempts and verification hashes.

Use at most one active worker. After a genuine interruption, the same `run_final_study.py --phase heldout` command resumes completed outputs and verifications; completed/incomplete terminal cases are not regenerated. An intent without a durable completed response consumes its call and remains incomplete. Do not delete intents or silently regenerate a preferred answer. A new generation attempt beyond the declared budget belongs in a separately documented study, not a hidden retry. The automated phase launcher is not intended to be started concurrently with an existing worker.

The original Groq protocol, proposed local protocol, two exploratory pilot versions, development format diagnostic and all raw failures are preserved. `protocol_history/prototype_dispositions.json` identifies deliberately interrupted development prototypes; their original `running` checkpoints are not fabricated into completed results. Only final-protocol held-out manifests enter the empirical analysis.

## Analysis and reporting

The frozen analysis source validates model/seed/prompt/response/verification provenance, shared initial candidates, B isolation and C's latest real feedback. It reports observed success, missingness, Wilson intervals, paired differences, exact McNemar tests and Holm adjustment, plus 10,000-resample problem and family-cluster bootstrap intervals using seed 20271021. Physical resource totals count the shared initial only once; per-condition counterfactual totals include it once in each row.

`scripts/render_final_study.py` creates the required four numbered tables, two scientific figures, resource/paired-test matrices and at least five authentic examples when available. Qualitative selection and repeated-candidate counts are explicitly post-hoc descriptive diagnostics, not extra hypothesis tests. Display-only code transliteration/truncation never changes raw output. `paper/scripts/write_final_manuscript.py` fills the manuscript from validated artifacts and writes a quantitative-claims manifest. It does not invent significance, equivalence, semantic ground truth or missing model success.

The official Springer template and Tectonic engine are restored outside the repository; URLs and exact archive/class hashes are in `tex_toolchain.json`. The actual final build log and PDF/source hashes are retained in `paper_build_manifest.json`. Source licenses and attribution stay with the dataset; no model weights, TeX binaries or API credentials are published.

## Recorded checkpoint recovery

On 29 October, the prior worker processes were absent and 29 trajectories were terminal (28 complete and one with a context-budget failure). The next case had a durable C1 intent without a complete response. `scripts/resume_final_study.py` resumes the unchanged frozen runner, preserving that call as incomplete and checking that all prior durable responses, verifications, intents, streams and terminal manifests retain their hashes. The termination cause is not established. `resume_history/` retains the observed state and commands. The interrupted trajectory's recorded wall elapsed time includes the inactive interval before recovery and is not uninterrupted compute time. The coordinator runs analysis and technical finalization after all remaining cases reach terminal states.
