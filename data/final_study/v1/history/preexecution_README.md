# Compiler-Guided Repair for Natural-Language-to-Lean Formalization

Research target: TAIMMA 2027 / Springer CCIS, submission deadline 5 November 2026.

**The empirical study is not complete.** There are no approved mathematical model pilots, qualifying paired held-out runs, independent semantic reviews or frozen eligible examples. No claim that compiler feedback improves repair is supported yet. No paid inference services are used in the current work.

The current preparation has 96 candidates across arithmetic identities, divisibility, induction, inequalities and modular arithmetic, with 30 proposed development and 66 proposed test assignments. These are unreviewed candidate assignments, not independent eligible benchmark counts. Latest evidence and exact remaining work are in [the M1–M7 compliance report](docs/FINAL_M1_M7_COMPLIANCE_REPORT.md) and [dataset completion report](docs/FINAL_DATASET_COMPLETION.md).

The controlled comparison is:

- **A:** one shared initial candidate, no repair.
- **B:** the same initial candidate, up to three blind repairs without compiler diagnostics.
- **C:** the same initial candidate, up to three repairs using genuine diagnostics from the immediately preceding failure.

B and C use the same reviewed theorem, model, decoding configuration, completion/context limits and Lean environment. The primary comparison is C versus B, using problem-level pairing. First-attempt success, success by repair budget, Wilson intervals, paired bootstrap intervals, exact McNemar tests and Holm adjustment are implemented; no study statistics are available without authentic eligible runs.

## Current local inference proposal

The cached MLX conversion of Qwen2.5-7B-Instruct is pinned to snapshot `c26a38f6a37d0a51b4e9a1eb3026530fa35d9fed`, 4-bit/group-size 64. Exact weights/tokenizer/config/chat-template hashes are recorded in [the model inventory](data/local_model/20261027/model_inventory.json). The free MLX backend passed neutral READY-prompt validation. A neutral backend check is not a mathematical pilot or an A/B/C result.

The [local protocol v0.3.0](configs/repair_experiment_local_v0.3.0.json) is **proposed and disabled**, pending genuine supervisor acceptance of replacing the professor's requested API experiments with local inference. It proposes MLX-LM 0.32.2 / MLX 0.32.4, temperature 0.2, top-p 1, 2000 output tokens, 8192 total context tokens, three repairs and one primary base seed. No automatic generation retry or paid fallback is allowed. The [original Groq protocol](configs/repair_experiment_protocol_v0.2.0.json) is preserved for historical provenance.

Plan without loading a model, generating outputs or invoking a paid service:

```sh
.venv/bin/python scripts/local_experiment.py --plan-only
```

See [local execution evidence](docs/LOCAL_MODEL_EXECUTION_REPORT.md) and the [supervisor decision package](docs/LOCAL_PROTOCOL_SUPERVISOR_APPROVAL.md). Local execution is checked against actual approvals, eligible dataset bytes, model inventory and pinned environment; final held-out execution additionally requires a reviewed freeze, preregistration and an audited genuine development pilot.

## Independent review

Start with the latest [review packet index](data/review_packets/m1_m7_delivery_20261028/README.md). Markdown packets, machine-readable records and blank decision forms contain English, Lean, quantifiers, assumptions, imports/definitions, citations and proof evidence. The importer checks externally human-verified reviewer identities, current content hashes, independence, dates and evidence artifacts. It never signs or approves on behalf of a human. See [semantic review status](docs/SEMANTIC_REVIEW_STATUS.md).

Compilation is not semantic faithfulness. Generated pipeline outputs explicitly distinguish compiler success from end-to-end faithful success, which remains false without genuine independently validated faithful review.

## Verification and reproducibility

Lean remains `leanprover/lean4:v4.32.0`; Mathlib remains pinned to `81a5d257c8e410db227a6665ed08f64fea08e997`. Existing artifacts are preserved. Additional proof overlays are bound to exact statements, source bytes, compiler output and target axiom inspections; expected-statement placeholders never count as candidate proofs.

```sh
.venv/bin/python -m pytest -p no:cacheprovider -q
(cd lean_project && lake build)
.venv/bin/python scripts/research_readiness.py --output-dir /tmp/new-readiness
.venv/bin/python src/semantic_review.py --output-dir /tmp/new-review-packets
.venv/bin/python paper/scripts/generate_inventory_tables.py
git diff --check
```

Use fresh output directories. The readiness command checks structure, source/review/proof metadata, duplicate/family concerns, protocol hashes and freeze rejection reasons. It does not freeze ineligible records. Install local inference dependencies only when needed using `requirements-local.txt`; Groq is optional for local execution. Exact installed dependency snapshots and actual test/build logs are under `data/verification/m1_m7_20261027/` and `data/local_model/20261027/`.

## Paper and historical evidence

The [Springer manuscript](paper/main.tex) remains a pre-results draft. Its pre-results PDF is compiled with the official Springer class using Tectonic; results, authentic model repair examples and author metadata remain incomplete. See [paper readiness](docs/FINAL_PAPER_READINESS.md) and [experiment results status](docs/FINAL_EXPERIMENT_RESULTS.md).

`RUN_REPORT.md`, legacy `data/results/` files, older versioned inventories and earlier completion reports retain their historical scope. Manually authored reference proofs, compiler demonstrations, synthetic tests and neutral smoke checks are never treated as model-generated A/B/C evidence.

The original preparation branch was merged as PR #8 (`d36c6d1`), and the final preparation branch as PR #9 (`386c641`). The follow-up AI audit uses its own branch; no automatic merge into main is authorized. [Remaining human actions](docs/REMAINING_HUMAN_ACTIONS.md) identify the genuine blockers.

## AI-only semantic audit

The follow-up audit is on `research/ai-semantic-audit-20261028`. It preserves the 96 candidate records and all eligibility gates while adding a separate Phi-family model review, coding-assistant assessments, fresh Lean type checks, bounded mathematical probes and an explicit disagreement queue. AI reviews are not independent human reviews or approvals. See the [audit report](docs/AI_SEMANTIC_AUDIT_REPORT.md), [reproduction instructions](docs/AI_AUDIT_REPRODUCIBILITY.md), and [proposed supervisor policy amendment](docs/AI_SEMANTIC_REVIEW_SUPERVISOR_REQUEST.md).
