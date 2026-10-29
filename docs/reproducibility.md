# Current final-study reproduction

Use [the final local-study reproduction guide](FINAL_EXECUTION_REPRODUCIBILITY.md) for the approved AI-review dataset, frozen MLX protocol, actual execution/resume and reporting. The following historical Groq/preparation instructions are retained for provenance and do not describe the final study.

# Reproducibility package

## Current evidence state

The paired analysis is currently blocked: the dataset manifest is draft,
there are 37 candidates and zero eligible records, and there are no paired
API experiment manifests. Thus the only valid current analysis output is a
readiness audit; it does not contain study results. See
[`paper/claims_to_evidence.md`](../paper/claims_to_evidence.md).

## Repository and input identity

Record the commit and exact working-tree state used for any reproduction:

```sh
git rev-parse HEAD
git status --short
shasum -a 256 configs/repair_experiment_protocol_v0.2.0.json
shasum -a 256 prompts/repair_experiment_initial.txt prompts/repair_experiment_blind.txt prompts/repair_experiment_compiler_guided.txt
shasum -a 256 data/research_dataset_draft_v0.1.0.json data/research_dataset_manifest_v0.1.0.json
```

The protocol references each prompt's SHA-256 and records the Lean/Mathlib
configuration. Do not infer exact model weights from the configured
`openai/gpt-oss-120b` provider alias; its revision and account generation
access remain unverified. No API call is authorized by this guide.

At the current protocol v0.2.0, the protocol SHA-256 is
`ced0e392772700181188bddf3b59e67a5794980a28a0deaa4e03f5110e280861`.
The initial prompt hash is
`00ec7bc08fdf14274d021a308ebc27a51e17e46198b4dbc29002b958a1e04990`;
blind and compiler-guided template file hashes are each
`98f5f2ca17094874da1b89f5b4cfc4f7eff00753dc56ac8d8cb7161fdaa57745`.
The Lean toolchain is `leanprover/lean4:v4.32.0`; Mathlib is pinned to
`81a5d257c8e410db227a6665ed08f64fea08e997` in the lockfile.

## Python environment and tests

Use the repository's declared Python dependencies and local environment:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m pytest -q -k 'not test_real_lean'
```

The excluded tests are explicitly marked to run actual Lean integration. The
full suite may include those integration checks; report commands and outcomes
without treating a timeout or interruption as a passing suite.

## Lean and Mathlib

The pinned inputs are `lean_project/lean-toolchain` and
`lean_project/lake-manifest.json`. From a machine with the required toolchain
and dependencies installed:

```sh
cd lean_project
lake --version
lake build
```

To verify an individual theorem or candidate under that project environment,
use the documented verifier (`src/verify.py`) or run the exact verification
command stored with its evidence. Preserve the compiler output, command,
return code, toolchain and theorem/source hashes. Lean acceptance is not a
semantic-fidelity decision.

## Dataset validation and inventory

The present draft-only structural audit is:

```sh
.venv/bin/python src/dataset_validation.py \
  data/research_dataset_draft_v0.1.0.json --validate-curation-draft
```

Regenerate the candidate-only composition and semantic-review tables and the
manual trace illustrations included with the pre-results paper:

```sh
.venv/bin/python paper/scripts/generate_inventory_tables.py
```

These tables are sourced from versioned candidate records and legacy manual
attempt logs. They are not A/B/C metrics. The current held-out split is not
frozen. Once a legitimate freeze exists, validate exact bytes, ordered IDs,
family separation, duplicate dispositions, source/legal evidence, theorem
hashes, and review records using the frozen-curation validator before any
test evaluation.

## Readiness and paired analysis

Generate a readiness audit in a new output directory without overwriting
existing research artifacts:

```sh
.venv/bin/python eval/paired_analysis.py --audit-current \
  --output-dir /tmp/nl2lean-analysis-readiness
```

After a dataset is frozen and the protocol/run prerequisites are met, generate
study outputs into a new analysis directory:

```sh
.venv/bin/python eval/paired_analysis.py \
  --test-dataset data/frozen/test.json \
  --development-dataset data/frozen/development.json \
  --freeze-manifest data/frozen/manifest.json \
  --runs-dir data/experiments \
  --output-dir data/analysis/<new-analysis-id>
```

The pipeline validates frozen inputs before producing tables or figures. It
records input/output hashes, analysis script hash, protocol/configuration
hashes, Wilson interval settings, bootstrap seed/resamples, McNemar tests, and
Holm comparisons. Use a fresh output directory because outputs are
append-only. Do not run prompt/model selection against the held-out test set.

## Paper build

`paper/main.tex` uses Springer LNCS (`llncs.cls`) and `splncs04.bst`. Obtain
these files from the official [Springer LNCS proceedings author
resources](https://www.springer.com/gp/computer-science/lncs/forthcoming-proceedings);
they are not vendored. Then follow `paper/README.md`. Current results sections
are explicitly unavailable and must be populated only from a validated
analysis output, never by copying values from historical charts or manually
authored proofs.

Current completion evidence (27 October 2026): [final readiness audit](../data/analysis/verified_readiness_20261027/readiness.json) and [completion report](FINAL_COMPLETION_REPORT.md). The pool has 37 candidates (29 proposed development, 8 proposed test), zero eligible records, and 95 review warnings. Exact source bytes are now archived separately under `data/source_archives/20261027_curl/`; source compatibility and independent semantic reviews remain pending.


## Final local-study revision (after PR #8)

The preferred proposed inference path is now local MLX, not a paid API. See `configs/repair_experiment_local_v0.3.0.json`, `docs/LOCAL_MODEL_EXECUTION_REPORT.md`, and `docs/FINAL_M1_M7_COMPLIANCE_REPORT.md`. The original protocol and historical inventories above remain as dated evidence. Local mode requires real approval, exact eligible input bytes and the frozen model inventory; `scripts/local_experiment.py --plan-only` makes no generations. Current proof overlays are loaded through `src/candidate_inventory.py` without rewriting historical candidate files. Markdown review packets and the latest readiness report are linked from the final dataset report.

The pre-results paper builds with the official Springer class 2.25 and Tectonic 0.17.0; exact release/template hashes and actual build logs are in `data/verification/m1_m7_20261027/`. The binaries/template are obtained from their official sources, not vendored without redistribution review. Reproduce using a temporary copy of `paper/`, place matching `llncs.cls` and `splncs04.bst` in that temporary source directory, then run `tectonic --untrusted --keep-logs --outdir <fresh-output> <temporary-source>/main.tex`. First-run TeX resource downloads require network access. Successful typesetting does not turn unavailable results into findings.
