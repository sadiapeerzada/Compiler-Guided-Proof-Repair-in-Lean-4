# Preservation and reuse

Starting commit: `adf16acee82cad915a2012c1a7856cbbadc20a13`.
New branch: `research/ai-validated-lean-confirmatory-experiments`.
The pre-existing human-gated study remains a separate study. Its source files are
also bound into this pilot's source lock; AI review cannot satisfy its human gate.

The baseline hash inventory covers every tracked file at the starting commit,
including the three historical study directories, the three TAIMMA analysis
directories, `src/verify.py`, `src/local_llm_client.py`, and manuscripts. The final
preservation validation checks actual file bytes rather than asserting that no
new research directory may exist. Pre-existing untracked user files are left alone.

The inherited `research/confirmatory-study/` audit, 193-version historical
inventory, exposure screens, strict Lean adapter, pinned environment checks,
append-only checkpoints, exact-token prompt matching, shared-predecessor runner,
and paired analysis are reused. The local client is used unchanged. No historical
experiment is rerun or relabeled as new data; old reporting mains that rewrite
historical reports are not invoked.

Historical results remain descriptive context: Study 1 A 0/60, B 1/60, C 1/58
with two unknown C outcomes; V7 A/B/C/D/E/R 4/5/10/9/5/5 of 72; V8
11/11/11/11/11/14 of 72; V9 development 5/12 versus 5/12. They do not supply
fresh eligible subjects or confirmatory evidence for this pilot.

The new implementation is frozen by `source_lock.json` before model outputs.
The source-only commit is `22a17e61`. Mathematical statements, acceptance rules,
and prompts are not edited in response to pilot outcomes. Operational trace
directory preparation and dependency installation are recorded separately.
Consumed failed intents remain in the original ledger and count against the
24-call ceiling. No additional inference budget is inferred from planning targets.
