# Post-hoc plan and original-source map

New work is local on `research/post-hoc-diagnostic-sensitivity`, from verified
private research baseline `5ecbe7b`. No new held-out calls, replays, outcomes,
hash bindings or original files will be written. The earlier approved public
branch push had completed before this new request; no new push/merge is planned.

## Original sources and schemas

- `data/final_study/v1/test.json` / `development.json`: ordered 60/15 rows,
  English and fixed Lean types, category/difficulty/source, `study_eligibility.family`.
- `freeze.json` and `configs/repair_experiment_local_v0.4.2.json`: original byte
  bindings, seeds, context/output caps, pinned source/runtime and stop rules.
- `data/local_model/20261027/model_inventory.json`: revision and weight,
  tokenizer and chat-template hashes. Cached original snapshot is available
  through its configured home-relative path; no private path is exported.
- `data/final_study/v1/final_runs/heldout/2027/<id>/manifest.json`: original
  shared initial and A/B/C branches, completed attempts, success/null outcomes,
  original record paths/hashes and checkpoints.
- Each attempt directory: `intent.json`, original `completion.json` containing
  raw model response, rendered prompt/chat, seed/tokens/time; `candidate.lean`;
  `verification.json` containing exact compiled target, verdict, compiler stdout
  and structured diagnostics; generation failures remain separate.
- `streams/<context-hash>.jsonl`: header, token/text frames, finished marker;
  the Bernoulli C1 stream is header-only. A completed stream must reproduce its
  stored raw response exactly before inclusion.
- `eval/paired_analysis.py:classify_compiler_error`: frozen taxonomy, precedence
  parser, unknown name, type/elaboration, tactic/goals, other. Guard/infrastructure
  failures and verified outcomes are separate analysis wrapper states.
- `eval/final_study_analysis.py` and `eval/final_review_analysis.py`: existing
  statistics and family-bootstrap implementations. New analysis uses independent
  post-hoc wrappers and never changes frozen helpers or their stored results.
- `data/final_review/20261029_v2/`: previous independent reconstruction and
  table resource precision, used as a comparison target, not as raw evidence.
- `publication/` / redacted release worktrees are NOT input substitutes.

## Sequence and definitions fixed before new analysis

1. `python -m analysis.reconcile`: original-record reconstruction, CSV mismatch
   report; show reconciliation before Tasks 1–2 and investigate any mismatch.
2. Existing-data analyses only. A repair denominator is a completed response with
   a failed predecessor. Repetition is exact candidate-string equality. Edit
   distance is Levenshtein / maximum length (empty/empty=0), on Unicode characters
   and separately exact frozen Qwen tokenizer token IDs. No whitespace or identifier
   normalization is applied to the candidates.
3. Unknown-name parsing uses the actual structured Lean diagnostic objects.
   Prefer dedicated name fields if present; these originals use
   `lean.unknownIdentifier._namedError` and only a quoted name in `data`, so parse
   that message field, not flattened prose. Removal is syntactic identifier
   occurrence, not proof of mathematical correction. Hallucinated substitution
   additionally requires a different newly introduced name reported unknown by
   the next actual compilation. B diagnostics are analyst-only chance baseline.
4. Distinct diagnostics are unique `(kind, data)` error messages, excluding
   warnings, filenames and locations. Transitions use the frozen primary classifier.
   Stage advance means parser → name → type → tactic; reverse is regression.
   Verified and unranked guard/other states are reported separately, not forced
   into a mathematical-progress score.
5. All main uncertainty resamples whole curated families, 10,000 draws, seed
   20271021, carrying both arms and all their observed repair records. Ratios
   retain completed-repair denominators; missing C outputs are not failures.
   Problem bootstrap is a secondary sensitivity. Prompt-length relationships
   are descriptive; repair attempts are not independent experimental units.
6. Paired score interval: Newcombe paired method 10, Wilson marginals with the
   continuity-adjusted phi coefficient. Source/method and boundary conventions
   will be recorded. McNemar has conventional exact p=1.0 at zero discordance,
   with no equivalence claim. MDE is an assumption-based planning calculation,
   not an observed effect or retrospective power estimate.
7. After Tasks 1–2 pass tests, freeze and commit the NEW dev-only placebo
   protocol, code hashes and filename-metadata normalizer before inference.
   User approved normalization of diagnostic filename metadata only, identically
   for C and placebo; data/severity/positions/order must remain unchanged.
   Export no private absolute paths or identities. Never change original diagnostics.
8. Generate fresh dev initials and up to three repairs per B/C/placebo branch,
   using new phase/condition contexts, identical primary model/settings, genuine
   deterministic donor diagnostics, durable no-replay intents and existing strict
   verifier/weight-release schedule. Interpret n=15 exploratory findings only as
   consistent/inconsistent with diagnostic-content sensitivity, never proof of use.
9. Study 2 model execution is deferred pending separate approval. Only a proposal
   may be prepared; no new test execution is authorized.

All new code is under `analysis/` or `extensions/`; all new data/logs/tables/plots
are under `outputs/post_hoc/`. The requested paper-title change is an explicit
editable-manuscript exception. No existing test output is overwritten.
