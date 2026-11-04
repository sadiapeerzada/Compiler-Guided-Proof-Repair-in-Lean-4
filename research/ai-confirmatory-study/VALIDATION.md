# Validation commands

Executed from the repository root:

```sh
.venv/bin/python -m pytest -q tests research/confirmatory-study/tests research/ai-confirmatory-study/tests analysis/taimma_20261104 analysis/taimma_supervisor_final analysis/taimma_final_professor_validation -k 'not real_lean and not provenance_counts_and_read_only_scope'
```

Result: **332 passed, 3 deselected, 28 subtests passed** in 13.69 seconds.
The two real-Lean integration tests were excluded from this offline regression
command. The third excluded test is the old blanket assertion that no new
`research/` files exist after its earlier baseline; it conflicts with the requested
new study directory. Its code and historical baseline were not edited. Preservation
of actual historical bytes is checked independently against all tracked files at
`adf16acee82cad915a2012c1a7856cbbadc20a13`.

The 9 new offline tests cover explicit resource limits, no unauthorized test
inference, rejection of simulated resource approvals, development/test access
restrictions, blinded prompt contents, distinct review families, frozen source
hashes, and preservation of the existing human protocol. Mocked negative tests
do not create production approval records or model outcomes.

Actual model-dependent generation is recorded separately under `runs/generation/`.
Test success is not evidence that a generated proof compiled or a reviewer accepted
it. Such claims require the corresponding real durable artifacts.

The separate real-compiler command also completed:

```sh
.venv/bin/python -m pytest -q tests/test_verify.py -k real_lean
```

Result: **2 passed, 29 deselected**, in 454.89 seconds. These fixtures check valid
Lean acceptance, exact target matching and a mismatched target rejection. They are
fixtures, not new benchmark subjects.

The archived post-hoc checks also passed: **19 passed** in 0.48 seconds, using
`../../.venv/bin/python -m pytest -q analysis/tests` from `publication/post_hoc/`.
