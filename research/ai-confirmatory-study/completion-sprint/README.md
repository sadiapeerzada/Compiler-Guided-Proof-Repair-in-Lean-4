# Completion sprint — authorized expanded exploratory run

Started from fetched `main` at9be2360b on
`research/final-cde-confirmatory-completion`. Fresh inference is running under the
explicit expanded allocation recorded in `resource_authorization.json`.
The previous development run is permanently closed; its files, clocks, ledgers,
rejections and qualified decisions are preserved.

`previous_31_audit.csv` audits every prior verified reference against actual rigid
verification checkpoints and recorded exclusions/reviews. Results:27 excluded,
four previously reviewed, two qualified acceptances in one family, zero eligible
unreviewed subjects. Exclusion-rule bindings match the recorded rules; this is
not an independent human mathematical validation or exhaustive novelty claim.
The original selected representative `final_dev_0146` may be reused unchanged
for development only. Rejected/uncertain or schema-invalid responses are not
rescued, and excluded alpha variants are not rereviewed to fish for approval.

`preservation_manifest.json` binds all tracked starting-main files and symlink
targets. `previous_run_closed.json` records old clock hashes and prohibited reuse.
`previous_run_independent_audit.json` reruns the existing checker read-only and
retains the one known interrupted intent as unknown. All audit preparation
uses zero model calls.

`COMPUTE_PROPOSAL.md` is the single consolidated fresh request. Its exact model,
token, phase-call and deadline ceilings are mirrored in `proposal_options.json`.
`resource_authorization.json` records the actual researcher reply authorizing
the expanded exploratory allocation: at most 1,728 calls, with separate fixed
phase ceilings and original deadlines. Unused budgets cannot be transferred. Both proposed full-stream options are exploratory, not claimed powered
confirmatory studies. Existing parser/verifier, Boolean review policy, C/D/E core,
checkpoint primitives and statistical scripts will be reused in the new scope;
no old experiment is reopened or altered.

Reproduce the read-only fast-path audit from the repository root:

```sh
.venv/bin/python research/ai-confirmatory-study/completion-sprint/audit_previous_candidates.py
```

Run the existing independent checker with a new output path; never overwrite the
closed run's audit or outputs. No model inference is performed by this command:

```sh
.venv/bin/python research/ai-confirmatory-study/final-study/scientific_audit.py --output /tmp/completion-sprint-baseline-audit.json
```

The eventual evidence-backed sprint report will be
`research/ai-confirmatory-study/FINAL_CDE_CONFIRMATORY_RESULTS.md`, after permitted
execution or a documented gate/deadline blocker. Only recorded outcomes will appear in that report; a compiler-verified proof
is still ineligible until its English statement and novelty pass both reviewers.

The original 60 responses failed the three-section contract. Their raw bytes,
rejections and charged calls remain unchanged. `prompt_v2_transition.json` and
`freezes/development_prompt_v2.json` prospectively bind the mandatory-footer
clarification used only for unconsumed candidate IDs, within the same original
128-call cap and clock. No response is repaired by filling missing fields.

Read-only source/data audit (does not run model inference):

```sh
.venv/bin/python research/ai-confirmatory-study/completion-sprint/audit_sprint.py --output /tmp/completion-sprint-audit.json
```

`continue_sprint.py --wait` advances genuine verified candidates through the
unchanged strict Boolean review policy and invokes C/D/E only if eligible
distinct families exist. Held-out inference remains gated on actual paired
development results and a prospectively frozen, disjoint test stream.
