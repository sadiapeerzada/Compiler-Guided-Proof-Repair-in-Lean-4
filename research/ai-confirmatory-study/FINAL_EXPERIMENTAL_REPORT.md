# Actual experimental evidence — AI-only pilot v1

This pilot produced **22 durable real local model completions**
from **24 charged generation intents**. It did not complete the
requested confirmatory study. No human approval or confirmatory result is claimed.

| Stage | Actual result |
|---|---|
| Generation | 24 recorded attempts; 0 schema-valid candidates |
| Generation failures | {'UNAVAILABLE_GENERATION': 2, 'REJECTED_PARSE': 22} |
| Strict reference verification | 0 verified; 0 failed/unavailable among parsed candidates |
| Blinded AI review | 0 reviewer-1 records; 0 reviewer-2 records |
| AI acceptance | 0 AI_SCREENED_FORMALLY_VERIFIED |
| Frozen cohorts | 0 development types; 0 confirmatory types |
| Development C/D/E | NOT EXECUTED: no eligible frozen development cohort |
| Confirmatory C/D/E | NOT EXECUTED; no test authorization |

The actual approved limits were 24 generation calls, 48 combined review calls,
and 48 development calls; each call allows at most 4,096 input and 1,200 output
tokens. Each phase has a 30-minute watchdog; both reviewers share one review
deadline. These limits supersede the larger planning ceilings. Generation is not
extended to reach a quota. All pilot proposals were designated development-only
before model output; none may become an untouched confirmatory subject.

Recorded generation expenditure was 4829 input tokens,
11755 output tokens, and 654.084
seconds inside completed generation calls. Both reviewers reserved zero calls.
Detailed accounting is in `runs/generation/generation_resource_usage.json` and
`runs/reviews/reviewer_*/resource_usage.json`; generation throughput and MLX-reported
peak memory are in `runs/generation/measured_runtime_memory.json`.
Unknown consumed intents remain charged; their unrecorded token costs are unknown,
not zero. The first attempt encountered sandbox Metal unavailability and the second
encountered a missing trace directory. GPU availability was verified outside the
sandbox; trace directories were prepared without editing frozen code or prompts.
Neither failed intent was replayed. Raw errors and all model outputs are retained.

No schema failure was silently repaired. Unparsed responses were excluded before
Lean checking, not counted as formal failures or semantic rejections. Only real
strict-verifier successes could reach AI review. Review agreement is not truth,
and the Qwen generator/reviewer ancestry prevents any claim of independent errors.
Pretraining contamination and exhaustive mathematical equivalence remain unassessed.
Recorded failure groups: `{'unavailable_generation': 2, 'invalid_JSON_escape': 15, 'non_bare_theorem_declaration': 5, 'other_JSON_parse_failure': 2}`. A changed generation prompt or
parser must be a new versioned pilot, rather than retroactive admission here.

The development gate is `NO_GO_DATA`; the test gate is
`NO_GO_RESOURCES`. The requested 40 development and 240 test types remain
unmet. With no completed eligible experiment, verification rates for C/D/E, paired
discordance, C−D/C−E effects, category effects, cluster confidence intervals and
multiplicity-adjusted intervals are not estimable. Zero completed evaluations is
not evidence of zero benefit or equality. No throughput estimate for development
or peak-memory measurement is substituted with generation timing or a planning cap.

Evidence paths relative to this directory:

- `runs/generation/`: prompts, raw responses, stream traces, charged intent ledger,
  candidate generation manifest, failed attempts and measured resource usage.
- `runs/formal_verification/`: verified/rejected candidate lists, reference manifest
  and actual compiler records when a parse-valid candidate exists.
- `runs/reviews/`: actual reviewer logs, acceptance/quarantine decisions, agreement,
  historical overlap screen, family and exclusion registries, validation report.
- `runs/dataset_*.json`, `runs/development.json`, `runs/test_sealed.json`: frozen
  pilot partition evidence. The ignored private encryption key is never published.
- `runs/preservation_validation.json`: 5911 historical files
  hash checked; 0 changed. Historical studies, human gate and manuscript
  remain unchanged from `adf16acee82cad915a2012c1a7856cbbadc20a13`.
- `runs/execution_gate_status.json`, `runs/stage_completion.json`: explicit stage
  status; absent experiment rows are not fabricated as failed model outcomes.

Validation: 332 tests passed, 3 deselected, 28 subtests passed in the combined
offline regression command recorded in `VALIDATION.md`. The deselections exclude
two opt-in real-Lean fixtures and the legacy blanket prohibition on any new
research files, which conflicts with this explicitly requested separate study.
The new policy tests are included; no synthetic test approvals enable inference.
Separately, both real-Lean fixtures passed (2 passed, 29 deselected, 454.89 seconds),
and the archived post-hoc analysis checks passed (19 passed). These fixtures are
not generated benchmark candidates or experimental outcomes.

Use the exact commands in `README.md` to inspect or resume existing phases.
Checkpoint replay never regenerates consumed intents. An exhausted allocation or
expired persisted deadline cannot be reset to extend this run. A further pilot
requires a new, separately authorized and versioned run. Confirmatory evaluation
also requires fresh accepted data and separate test authorization.
