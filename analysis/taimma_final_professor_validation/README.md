# Final professor experimental validation

This is a focused addition to merged PRs #19–21 at audited commit `a3a709c383ceb016de3e746f962e543bbcc8b2a5`. It adds control-integrity verification and small formal overlap certificates, independently checks prior statistics, and cites existing reports instead of reproducing them. No manuscript or old evidence is changed.

Start with [the eight-concern completion handoff](PROFESSOR_EXPERIMENTAL_COMPLETION_REPORT.md) and [the evidence-gap matrix](EVIDENCE_GAP_MATRIX.md).

```sh
# Only the new relationship certificates; no held-out candidate replay:
.venv/bin/python analysis/taimma_final_professor_validation/check_certificates.py
# Frozen-record checks and reports; no inference/tokenizer execution:
.venv/bin/python analysis/taimma_final_professor_validation/validate.py
.venv/bin/python analysis/taimma_final_professor_validation/verify_readonly.py
.venv/bin/python -m pytest -q tests analysis/taimma_supervisor_final/test_supplement.py analysis/taimma_final_professor_validation/test_validation.py -k 'not real_lean'
```

- [Control verification](EXPERIMENTAL_CONTROL_VERIFICATION.md) and [new token-matching reconstruction](TOKEN_MATCHING_VERIFICATION.csv).
- [Independent statistical cross-check](STATISTICAL_INTEGRITY_REPORT.md).
- [Benchmark validation](BENCHMARK_VALIDITY_VERIFICATION.md), [pair evidence](BENCHMARK_OVERLAP_EVIDENCE.csv), [all 36 statement hashes](STATEMENT_INVENTORY.csv), [certificates](OverlapCertificates.lean), and [actual local check result](lean_certificate_check.json).
- [Human adjudication still required](HUMAN_ADJUDICATION_REQUIRED.md).
- [Diagnostic and case audit](DIAGNOSTIC_AND_FAILURE_AUDIT.md).
- [Reproducibility scope](REPRODUCIBILITY_FINAL_VERIFICATION.md), [machine-readable checks](verification_results.json), and [tests](TEST_RESULTS.md).

V8 raw inputs are in the frozen indexed ZIP. V7 descriptive records use PR21's committed minimal views; further raw prompt/seed/donor checks use locally available originals and report unavailable calls if absent. Their local hash-inventory digest checks consistency without upgrading external historical provenance. No model weights or new responses are generated. A fresh checkout can reproduce the existing descriptive analyses from PR21; it must not claim all additional local V7 raw-journal checks without those originals.

The new Lean command checks seven audit declarations relating the five suspected pairs. This is permitted local mathematical verification, not new model evaluation or independent human adjudication. Its result remains tied to the certificate SHA and actual Lean version. If cached imports or Lean are absent, it reports unverified and does not build/download dependencies. None of the scripts invokes a model, tokenizer, experiment runner or manuscript generator.
