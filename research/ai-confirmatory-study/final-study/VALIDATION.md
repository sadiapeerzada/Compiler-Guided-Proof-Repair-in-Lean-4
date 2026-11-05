# Validation of the development implementation

These checks validate infrastructure and strict verification; they are not
generated benchmark subjects or C/D/E model outcomes. They spend zero inference
calls. Actual experiment counts remain in run-local ledgers and final reports.

The expanded working-suite command passed **388 tests and28 subtests**,
with four deselections, in11.43s:

```sh
.venv/bin/python -m pytest tests research/confirmatory-study/tests research/ai-confirmatory-study/tests research/ai-confirmatory-study/v2/tests research/ai-confirmatory-study/v3/tests research/ai-confirmatory-study/final-study/tests analysis/taimma_supervisor_final/test_supplement.py analysis/taimma_final_professor_validation/test_validation.py submission_20261031/tests -q -k 'not real_lean and not no_real_research_rows_manufactured and not provenance_counts_and_read_only_scope'
```

Two unchanged legacy assertions are incompatible with this requested extension:
`no_real_research_rows_manufactured` rejects new research files;
`test_provenance_counts_and_read_only_scope` requires an empty research-tree Git
diff against an older analysis baseline. The latter failed solely on that scope
assertion when the historical-analysis tests were first included; its preceding
frozen-data/provenance assertions passed. The other17 historical-analysis tests
and all four public-release tests pass in the command above. Neither test was
weakened to accept changed historical data. All6,279 baseline file hashes and four
symlink targets are checked independently. The two actual Lean tests were run
separately:

```sh
.venv/bin/python -m pytest tests/test_verify.py -q -k real_lean
```

Result: **2 passed,29 deselected in252.74s**. Final-study tests alone passed
**24 tests**, already included in the388-test count.
A mistakenly unscoped pytest invocation also collected archived
publication snapshots and failed collection with missing snapshot dependencies
and duplicate module names. The explicit working-suite command above avoids
those archived copies; historical files were not altered to hide their state.

Actual versioned Lean/parser fixture artifacts are under
`runs/20261105T041720Z_development/`:

- `offline_integration/`: explicit-all-arguments harness checks, including
  polymorphism and negative target/assumption/placeholder checks. The later
  `universe_specialization_probe.json` records a **failed negative probe**:
  that first harness accepted universe specialization. It is preserved as a
  discovered defect, not counted as a passing control.
- `rigid_verifier_fixtures/results.json`: **four actual Lean checks passed**,
  including polymorphic and monomorphic positives, weaker-target rejection and
  rejection of the same universe specialization. Rigid source/fixture hashes
  were frozen before reference-repair inference. All newly admitted references
  must have a successful actual check with this stronger variant.
- `reference_prompt_v4_syntax_fixture.json`: the `True`/`trivial` format example
  passed an additional actual rigid Lean check before V4 repair inference. It is
  a development-exposed syntax example, not a generated evaluation subject.
- `header_parser_fixture_checks_v2/`: four native Lean parser cases passed.
  Invalid tactic bodies may supply an exact header for later compiler-guided
  repair, but are not considered verified. The actual invalid-body kernel
  check rejected that proof. Earlier failed header-parser prototypes remain
  separately archived.

`scientific_audit.py` runs without inference in a separate process. An interim
run checked6,279 baseline file hashes, four baseline symlink targets, used source
freezes, phase-local ledgers, exact raw/stream hashes, original clocks, model
identities and independently recounted rendered input tokens with the pinned
tokenizers. An in-flight call was recorded as pending/unknown in that snapshot.
Final audit results must be regenerated after the permitted workers stop; this
document does not predict their outcome or imply completed experimental phases.
