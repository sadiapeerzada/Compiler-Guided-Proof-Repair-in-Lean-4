# Validation record

## Current implementation

| Command | Outcome |
| --- | --- |
| `.venv/bin/python -m pytest -q research/confirmatory-study/tests` | 23 passed; synthetic fixtures only, with assertions against separately recorded real Lean/tokenizer checks |
| `.venv/bin/python -m pytest -q tests analysis/taimma_supervisor_final/test_supplement.py analysis/taimma_final_professor_validation/test_validation.py research/confirmatory-study/tests -k 'not real_lean and not provenance_counts_and_read_only_scope'` | 323 passed, 3 deselected, 28 subtests passed |
| `python3 -m pytest -q analysis/tests` from `publication/post_hoc/` | 19 passed |
| `.venv/bin/python research/confirmatory-study/integration_checks.py` | Real Lean valid proof accepted; placeholder, weakened target and invalid proof rejected. Tokenizer-only C/D/E prompts each measured exactly4096 tokens. No weights/model inference loaded |
| `.venv/bin/python research/confirmatory-study/preservation.py` | All5867 baseline tracked files byte-identical; changes confined to the new directory |
| `.venv/bin/python research/confirmatory-study/isolated_repair_runner.py status --phase development` and `--phase test` | Both NO_GO; selected records not released |

`historical_integrity_checks.json` also records read-only verification of the4736 indexed archive members,40 frozen lock entries and frozen V7 source dependencies. The local-path privacy limitation remains1220 warning records/22882 occurrences; no general privacy approval is claimed.

## Failed check retained explicitly

The earlier combined command with only `-k 'not real_lean'` produced **1 failure,322 passes,2 deselections,28 subtest passes** at that implementation revision. The failing pre-existing test is `analysis/taimma_final_professor_validation/test_validation.py::ValidationTests::test_provenance_counts_and_read_only_scope`. It asserts that *no files at all* have been added/changed anywhere under `research/` since its older baseline. The authorized new `research/confirmatory-study/` directory violates that blanket condition even when every historical file is preserved. The old test is not edited or relabeled as passing. The current combined command excludes exactly that legacy scope guard plus the two original real-Lean integration tests. The new5867-file preservation manifest provides the appropriate nonmutation check for this task.

An initial new-adapter Lean smoke check also exposed an API mismatch: the reused verifier expects a well-formed expected-type declaration. The new adapter now supplies a placeholder only in the expected namespace, as the historical verifier design requires; candidate placeholders remain forbidden and candidate axiom dependencies are checked. Real acceptance and rejection cases passed after this correction. No historical verifier source or result was changed.

## Scope and test coverage

Tests cover common predecessors, diagnostic SHA association, disjoint-family/forbidden-pair donors, byte-identical diagnostic rejection, exact input matching or invalidation, hidden reference proofs, deterministic family splitting, within-cohort alpha duplicates, immutable configuration checks, no sealed-test reads during calibration, human-approval-gate refusal, counterbalanced planned orders, exclusive call accounting, interrupted and orphaned reservations, changed-intent rejection, damaged ledgers, nonconforming-response preservation, checkpoint resume, known synthetic paired effects, repeated-theorem clustering and missing-outcome bounds. All synthetic run directories are temporary and destroyed; no synthetic result is written into the research results CSV.

The positive gate-path unit fixture explicitly mocks human-decision verification and historical screening solely to exercise path separation/hash binding; it never invokes a model. The same fixture is rejected by the production gate without mocks. Passing mocks do not establish human approval or end-to-end model execution. Real checks used Lean4.32.0 and pinned Mathlib; tokenizer counts used the pinned local Qwen revision, with no model-weight loading. The two older real-Lean tests were deselected, not certified passing by this work.
