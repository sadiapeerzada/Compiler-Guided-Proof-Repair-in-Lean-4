# Local model execution report

Status: PARTIAL. Neutral backend validation succeeded; genuine mathematical pilot is BLOCKED.

Hardware inspection confirmed Apple M4 / arm64, 16 GiB unified RAM, approximately 22 GiB available disk at inspection. MLX-LM was absent from this repository's environment, so the free backend was installed locally. The selected cached `mlx-community/Qwen2.5-7B-Instruct-4bit` snapshot is `c26a38f6a37d0a51b4e9a1eb3026530fa35d9fed`: approximately 4.28 GB weights, 4-bit quantization, group size 64. No new weights or API credits were purchased/downloaded. The cached 3B alternative lacked a corresponding instruction-model card; no mathematical performance comparison was made.

Exact file/weight/tokenizer hashes and the chat template: `data/local_model/20261027/model_inventory.json`. Pinned model card, upstream license bytes, source URLs/hashes, selected configuration and dependency snapshot are alongside it. Model card identifies Apache-2.0; independent compatibility review is still pending. MLX 0.32.4, MLX-LM 0.32.2 and Transformers 5.21.0 are recorded. Groq is optional; tests import and plan local execution with Groq unavailable. Existing Groq code and protocol remain intact and disabled for study use.

Three neutral READY-prompt checks returned genuine local outputs; earlier source versions remain preserved. The final trace in `final_backend/manifest.json` records 36 input / 2 output tokens, exact rendered chat and template hashes, seed/context, latency and approximately 4.43 GB peak model memory. These are backend checks, not mathematical examples, a supervised pilot, A/B/C results or evidence for M1's empirical claim. The sandboxed Metal import failed; host-authorized Metal access succeeded. These checks used no paid inference service and no dataset problem.

`src/local_llm_client.py` validates snapshot bytes, rejects model/decoding/context drift, uses stateless per-call KV/conversation contexts, records tokenizer counts and seeds, persists streamed tokens, and rejects automatic replay of a logical context. Seeds depend on the base seed, problem/condition/attempt context and prompt hash, so unchanged blind prompts get distinct streams and B stopping does not shift C's RNG state. Interrupted streams are retained; recovery means preserving the incomplete call, not silently regenerating it. Backend failures are identified separately from paid/API failures.

The shared A/B/C runner now supports genuine local mode; it does not disguise local calls as API, manual or mock generations. `src/local_protocol.py` checks genuine approval artifacts, dataset eligibility, fixed theorem bytes, model inventory, backend versions, protocol/prompt/environment hashes and generation budgets before a study call. Held-out execution additionally requires frozen eligible splits, preregistration and an audited genuine local pilot. These gates remain closed: zero eligible examples and no approval exist.

Plan without loading weights or generating:

```sh
.venv/bin/python scripts/local_experiment.py --plan-only
```

The local proposal is `configs/repair_experiment_local_v0.3.0.json`. Supervisor substitution request: `docs/LOCAL_PROTOCOL_SUPERVISOR_APPROVAL.md`. One primary seed is proposed; three-seed replication is not implemented or claimed. No mathematical local generation, genuine pilot or held-out model execution occurred.

The final protocol also binds implementation-source hashes, the candidate-definition module and the exact supervisor approval record/evidence. The original NL pipeline stages accept the common completion interface; compiler-only outputs explicitly keep `end_to_end_faithful_success` false until authentic independent semantic review. No local mathematical case was run through those stages.
