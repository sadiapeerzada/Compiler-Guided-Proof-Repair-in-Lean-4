# Final validation commands and outcomes

All commands below concern frozen records or the new relationship certificates. No model inference, tokenizer execution, original held-out candidate rerun or experimental matrix was launched.

| Exact command | Outcome |
| --- | --- |
| `.venv/bin/python analysis/taimma_final_professor_validation/check_certificates.py` | PASS: seven new certificate declarations compile under recorded Lean 4.32.0; all seven axiom reports present, only standard `propext` where used; source SHA recorded |
| `.venv/bin/python analysis/taimma_final_professor_validation/validate.py` | PASS: independent paired/clustered reconstruction; all 36 statement/reference hashes; shared-initial, budget, seed, donor, prompt/token and classifier checks; all archive members and lock entries |
| `.venv/bin/python analysis/taimma_final_professor_validation/verify_readonly.py` | PASS: 10 generated artifacts byte-identical on repetition; 109 protected tracked evidence files byte-identical; zero prior tracked file modifications; new report home-prefix scan passed |
| `.venv/bin/python -m pytest -q tests analysis/taimma_supervisor_final/test_supplement.py analysis/taimma_final_professor_validation/test_validation.py -k 'not real_lean'` | 301 passed, 2 deselected, 28 subtests passed |
| `python3 -m pytest -q analysis/tests` with working directory `publication/post_hoc/` | 19 passed |

Ten new offline tests are included in the 301 total. They cover actual-C first-repair matching versus own-history later targets, unequal-size family resampling, existing interval reconstruction, unknown Study1 outcomes, checksum rejection, source-bound certificate/axiom evidence, benchmark scope/exclusions, raw-control counts, missing-axiom-report rejection, and protected-file scope.

The two pre-existing `real_lean` integration tests are explicitly deselected: the task is frozen-evidence validation, and the seven new relationship declarations have their own separately recorded Lean command. No full original-verifier integration or inference replay is certified. Final scoped tests have no failures or interruptions. Certificates are locally kernel-checked evidence, not independent human review.

Additional raw checks use all 1006 V7 and 910 V8 completed repairs plus 72 initial calls per model. V7 has local historical provenance; V8 is archive-indexed. Study1 checks 60 common-initial manifests, 178 B and 172 C completed repairs in public redacted views. Reproduction of every local raw check on another machine requires the corresponding original V7 files; absence must be reported, not supplied from aggregate values.
