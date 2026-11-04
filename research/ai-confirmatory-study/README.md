# AI-screened development pilot, protocol v1

This separate study uses real local candidate generation, strict pinned Lean checks,
and two blinded model reviews. The historical independent-human protocol remains
unchanged. AI acceptance is named `AI_SCREENED_FORMALLY_VERIFIED`, never human
approval. Formal validity does not establish faithful English semantics.

The user authorized at most 24 generation calls, 48 combined review calls, and
48 development calls, with 4,096 input tokens and 1,200 output tokens per call.
Each phase has a 30-minute limit; both reviewers share one review deadline.
Confirmatory inference is not authorized. All pilot proposals are development-only;
the 40-development/240-test targets cannot be met by this allocation.

Models are pinned in `ai_protocol_v1.json`. Phi and Qwen are the two review
families. The generator and second reviewer share the Qwen family, so correlated
errors remain possible. Five lexical historical neighbors are supplied to each
reviewer; separate automated screens inspect the historical inventory. This is
not exhaustive mathematical equivalence detection or proof of originality.

Run from the repository root using `.venv/bin/python`. Local MLX needs GPU access;
the restricted macOS sandbox cannot expose the GPU. Each consumed intent remains
charged even if no durable completion was produced. Never delete or replay intents.
The existing local client requires trace directories to exist before invocation;
directory preparation is recorded in `runs/stream_directory_preparation.json`.
The additional sealing dependency is pinned in `requirements-encryption.txt`;
install with `.venv/bin/python -m pip install -r research/ai-confirmatory-study/requirements-encryption.txt`.

Commands, in order:

```sh
.venv/bin/python research/ai-confirmatory-study/prepare_stream_directories.py generation
.venv/bin/python research/ai-confirmatory-study/run_phase.py generation
.venv/bin/python research/ai-confirmatory-study/pipeline.py verify
.venv/bin/python research/ai-confirmatory-study/prepare_stream_directories.py reviewer_1
.venv/bin/python research/ai-confirmatory-study/prepare_stream_directories.py reviewer_2
.venv/bin/python research/ai-confirmatory-study/run_phase.py reviews
.venv/bin/python research/ai-confirmatory-study/freeze_dataset.py
.venv/bin/python research/ai-confirmatory-study/prepare_stream_directories.py development
.venv/bin/python research/ai-confirmatory-study/run_phase.py development
.venv/bin/python research/ai-confirmatory-study/finalize_evidence.py
```

The gate must accept the actual evidence before development runs. The separate
test gate rejects unauthorized access before reading the encrypted payload/key.
The encryption key stays local under ignored `.private/`; the pilot contains zero
confirmatory subjects. Repository-level role checks are not an operating-system
security boundary against a user who controls this checkout.

Raw prompts, responses, token metadata, compiler diagnostics, checkpoints and
decisions are retained under `runs/`. Read `FINAL_EXPERIMENTAL_REPORT.md` for
actual results and limitations; the commands above are not claims of completion.
