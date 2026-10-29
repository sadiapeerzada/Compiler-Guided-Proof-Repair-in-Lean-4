# Missing C outcome investigation

The two exact prompts were reconstructed from the correct predecessor and retokenized offline; both match their original intent hashes. No model weights were loaded for generation, no inference occurred, and no historical output or checkpoint was modified.

- `lib_a_trig_unit` / C1: context_preflight_rejection; input 9,653 + output reservation 2,000, context cap 8,192. Durable frames: 0; durable generated tokens: 0. Exact input already exceeds the frozen total context cap; truncation would change the prompt. Intent: `data/final_study/v1/final_runs/heldout/2027/lib_a_trig_unit/C1/intent.json`.
- `lib_i_bernoulli` / C1: interrupted_generation_without_response; input 2,205 + output reservation 2,000, context cap 8,192. Durable frames: 1; durable generated tokens: 0. Only a stream header survives; no response tokens or persisted generator state can be continued. Terminal no-replay policy forbids a replacement call. Intent: `data/final_study/v1/final_runs/heldout/2027/lib_i_bernoulli/C1/intent.json`.

Neither logical context has a durable completed response anywhere in the final-run artifacts. The context failure is a generation preflight resource failure, not a Lean timeout. The interrupted case has only a header, not a partial proof or resumable KV/RNG state. Its interruption cause is unknown. Both are terminal under the frozen runner and consume their intent.

**Recovery status: unavailable, not safely recoverable under the frozen protocol.** Repeating a seed is still a replay; altering caps, prompts, diagnostics or terminal statuses would change the study. New experiments require a separately versioned follow-up and cannot replace these records. Machine-readable evidence: `data/final_review/20261029_v2/missingness_recovery.json`.
