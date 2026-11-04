# Prospective isolated Lean repair infrastructure

**NO_GO. No new model inference has run.** Independent benchmark adjudication is pending; new eligible development/test counts are0/0. This package implements and tests the workflow, but does not claim to have created an untouched approved benchmark or completed a confirmatory experiment.

Start with [the completion report](FINAL_EXPERIMENTAL_COMPLETION_REPORT.md), [phase0 audit](PHASE0_AUDIT.md), and [human approval/freeze requirements](APPROVAL_AND_FREEZE.md).

Safe commands:

```sh
.venv/bin/python research/confirmatory-study/preservation.py
.venv/bin/python research/confirmatory-study/isolated_repair_runner.py status --phase test
.venv/bin/python -m pytest -q research/confirmatory-study/tests
# Real Lean safety fixtures and tokenizer assets only; no weights or model generation:
.venv/bin/python research/confirmatory-study/integration_checks.py
```

Implemented:

- Historical inventory of193 subject versions, source hashes, automated lexical/alpha/family candidates, prior generated-candidate fingerprints, and unsigned human semantic/adjudication packets.
- Candidate intake/quarantine and deterministic whole-family partitions, including alpha-duplicate checks within and across prospective partitions. No historical example is promoted to a fresh test.
- Shared-predecessor one-repair C/D/E prompts, exact tokenizer/template input budgets, whole diagnostic preservation, deterministic eligible donor mapping, counterbalanced planned order and model/environment pins.
- Independent human/protocol/data/compute/verification gates, with no model/tokenizer initialization before authorization.
- Exclusive append-only intent/completion/verification journals, no replay after interrupted intent, persistent call/runtime accounting and immutable versioned full-grid exports.
- C−D primary/C−E secondary paired analyses with theorem clusters, unequal-family sensitivity, nominal Bonferroni simultaneous intervals, initial-eligibility and missing-outcome bounds, categories, source manifests and recorded costs.

`isolated_repair_results.csv` is header-only. Temporary synthetic test results never enter it. `offline_integration_results.json` contains safety fixtures and tokenizer-only checks, not research outcomes. `readiness_status.json` records current gates and owners. `historical_hashes.json` protects all5867 baseline tracked files.

If real human-approved input becomes available, a curator must prepare a new versioned bundle following APPROVAL_AND_FREEZE.md. Only then is the explicit `isolated_repair_runner.py run --bundle ... --phase development|test` entry point relevant. It rechecks the production gate and refuses unauthorized execution. Do not manually change pending fields to simulate approvals. CLI status or a passing test suite is not authorization.
