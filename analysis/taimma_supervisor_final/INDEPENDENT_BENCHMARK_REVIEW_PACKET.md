# Independent benchmark review worksheet

UNAPPROVED: AI-assisted preparation for a mathematician/Lean expert. No signed independent adjudication is asserted. Exact source statements/reference proofs below come from the frozen V7 constructor; recorded outcomes come from frozen test CSVs. Reference checking establishes formal acceptance only. PR20 retains all 36 provisional review rows and all overlap-exclusion counts unchanged.

## bridge_d06 / bridge_t11

Relationship to examine: Binomial square with multiplication notation; exact/rewritten identity needs expert confirmation.

Potential development/test leakage: cross-split pair.

`bridge_d06`; family `bridge_nat_ring_squares`.

Exact statement:
```lean
theorem bridge_d06 (a b : Nat) : (a+b)^2 = a^2 + 2*a*b + b^2
```
Available reference proof:
```lean
theorem bridge_d06 (a b : Nat) : (a+b)^2 = a^2 + 2*a*b + b^2 := by ring
```

V7 development-source successes (1 recorded evaluations): `{"B_neutral": 0, "C_real": 0, "D_shuffled": 0, "E_token_matched": 0, "R_resample": 0, "initial_success": 0}`. The base-model development source is the archived V5 lineage; V8 development is separately recorded. No development success is counted as held-out.

V8 development-source successes (1 recorded evaluations): `{"B_neutral": 0, "C_real": 0, "D_shuffled": 0, "E_token_matched": 0, "R_resample": 0, "initial_success": 0}`. The base-model development source is the archived V5 lineage; V8 development is separately recorded. No development success is counted as held-out.

`bridge_t11`; family `bridge_nat_polynomial`.

Exact statement:
```lean
theorem bridge_t11 (x y : Nat) : (x+y)*(x+y)=x*x+2*x*y+y*y
```
Available reference proof:
```lean
theorem bridge_t11 (x y : Nat) : (x+y)*(x+y)=x*x+2*x*y+y*y := by ring
```

V7 test successes across 3 seeds: `{"B_neutral": 0, "C_real": 0, "D_shuffled": 0, "E_token_matched": 0, "R_resample": 0, "initial_success": 0}`.

V8 test successes across 3 seeds: `{"B_neutral": 0, "C_real": 0, "D_shuffled": 0, "E_token_matched": 0, "R_resample": 0, "initial_success": 0}`.

Recorded reference-screen source: `research/study2-raw-v8-v9/evidence-part-001.zip::study2_outputs/bridge_items_1_4_6_v8_20261103/coder_exploratory/reference_screen/bridge_d06.json`; recorded strict reference flag `True`. This is an archived check, not independent adjudication.

Recorded reference-screen source: `research/study2-raw-v8-v9/evidence-part-001.zip::study2_outputs/bridge_items_1_4_6_v8_20261103/coder_exploratory/reference_screen/bridge_t11.json`; recorded strict reference flag `True`. This is an archived check, not independent adjudication.

Recorded reference-screen source: `research/study2-raw-v8-v9/evidence-part-001.zip::study2_outputs/bridge_items_1_4_6_v8_20261103/reference_screen/reference_screen/bridge_t11.json`; recorded strict reference flag `True`. This is an archived check, not independent adjudication.

Existing proposals: [{"source": "ADDITIONAL_BENCHMARK_OVERLAPS.csv", "decision": null, "recommendation": "NEAR_DUPLICATE", "mathematical_justification": "Identical Nat binomial-square identity after converting (x+y)*(x+y) to (x+y)^2 and renaming variables.", "justification": null}].

Reviewer questions: Are the propositions identical under binder renaming, definitional equality, a proved rewrite, or only related by a specialization? Does development exposure supply the same proof template? Should inference cluster these items together? Are reference proofs valid in the pinned environment, and does the English accurately express the statement? Do not approve independence solely because each reference compiles.

Reviewer name/affiliation: ____; independence/conflicts: ____; signed date: ____; exact reasoning and disposition: ____.

## bridge_d06 / bridge_t12

Relationship to examine: Nat binomial square after binder renaming.

Potential development/test leakage: cross-split pair.

`bridge_d06`; family `bridge_nat_ring_squares`.

Exact statement:
```lean
theorem bridge_d06 (a b : Nat) : (a+b)^2 = a^2 + 2*a*b + b^2
```
Available reference proof:
```lean
theorem bridge_d06 (a b : Nat) : (a+b)^2 = a^2 + 2*a*b + b^2 := by ring
```

V7 development-source successes (1 recorded evaluations): `{"B_neutral": 0, "C_real": 0, "D_shuffled": 0, "E_token_matched": 0, "R_resample": 0, "initial_success": 0}`. The base-model development source is the archived V5 lineage; V8 development is separately recorded. No development success is counted as held-out.

V8 development-source successes (1 recorded evaluations): `{"B_neutral": 0, "C_real": 0, "D_shuffled": 0, "E_token_matched": 0, "R_resample": 0, "initial_success": 0}`. The base-model development source is the archived V5 lineage; V8 development is separately recorded. No development success is counted as held-out.

`bridge_t12`; family `bridge_nat_polynomial`.

Exact statement:
```lean
theorem bridge_t12 (x y : Nat) : (x+y)^2=x^2+2*x*y+y^2
```
Available reference proof:
```lean
theorem bridge_t12 (x y : Nat) : (x+y)^2=x^2+2*x*y+y^2 := by ring
```

V7 test successes across 3 seeds: `{"B_neutral": 0, "C_real": 0, "D_shuffled": 0, "E_token_matched": 0, "R_resample": 0, "initial_success": 0}`.

V8 test successes across 3 seeds: `{"B_neutral": 0, "C_real": 0, "D_shuffled": 0, "E_token_matched": 0, "R_resample": 0, "initial_success": 0}`.

Recorded reference-screen source: `research/study2-raw-v8-v9/evidence-part-001.zip::study2_outputs/bridge_items_1_4_6_v8_20261103/coder_exploratory/reference_screen/bridge_d06.json`; recorded strict reference flag `True`. This is an archived check, not independent adjudication.

Recorded reference-screen source: `research/study2-raw-v8-v9/evidence-part-001.zip::study2_outputs/bridge_items_1_4_6_v8_20261103/coder_exploratory/reference_screen/bridge_t12.json`; recorded strict reference flag `True`. This is an archived check, not independent adjudication.

Recorded reference-screen source: `research/study2-raw-v8-v9/evidence-part-001.zip::study2_outputs/bridge_items_1_4_6_v8_20261103/reference_screen/reference_screen/bridge_t12.json`; recorded strict reference flag `True`. This is an archived check, not independent adjudication.

Existing proposals: [{"source": "ADDITIONAL_BENCHMARK_OVERLAPS.csv", "decision": null, "recommendation": "NEAR_DUPLICATE", "mathematical_justification": "Exact Nat binomial-square identity after renaming a,b to x,y; development (a+b)^2=a^2+2ab+b^2 and test (x+y)^2=x^2+2xy+y^2. Critical cross-split equivalence missed by similarity rule.", "justification": null}].

Reviewer questions: Are the propositions identical under binder renaming, definitional equality, a proved rewrite, or only related by a specialization? Does development exposure supply the same proof template? Should inference cluster these items together? Are reference proofs valid in the pinned environment, and does the English accurately express the statement? Do not approve independence solely because each reference compiles.

Reviewer name/affiliation: ____; independence/conflicts: ____; signed date: ____; exact reasoning and disposition: ____.

## bridge_t11 / bridge_t12

Relationship to examine: Square versus repeated multiplication syntax.

Potential development/test leakage: within-test dependence.

`bridge_t11`; family `bridge_nat_polynomial`.

Exact statement:
```lean
theorem bridge_t11 (x y : Nat) : (x+y)*(x+y)=x*x+2*x*y+y*y
```
Available reference proof:
```lean
theorem bridge_t11 (x y : Nat) : (x+y)*(x+y)=x*x+2*x*y+y*y := by ring
```

V7 test successes across 3 seeds: `{"B_neutral": 0, "C_real": 0, "D_shuffled": 0, "E_token_matched": 0, "R_resample": 0, "initial_success": 0}`.

V8 test successes across 3 seeds: `{"B_neutral": 0, "C_real": 0, "D_shuffled": 0, "E_token_matched": 0, "R_resample": 0, "initial_success": 0}`.

`bridge_t12`; family `bridge_nat_polynomial`.

Exact statement:
```lean
theorem bridge_t12 (x y : Nat) : (x+y)^2=x^2+2*x*y+y^2
```
Available reference proof:
```lean
theorem bridge_t12 (x y : Nat) : (x+y)^2=x^2+2*x*y+y^2 := by ring
```

V7 test successes across 3 seeds: `{"B_neutral": 0, "C_real": 0, "D_shuffled": 0, "E_token_matched": 0, "R_resample": 0, "initial_success": 0}`.

V8 test successes across 3 seeds: `{"B_neutral": 0, "C_real": 0, "D_shuffled": 0, "E_token_matched": 0, "R_resample": 0, "initial_success": 0}`.

Recorded reference-screen source: `research/study2-raw-v8-v9/evidence-part-001.zip::study2_outputs/bridge_items_1_4_6_v8_20261103/coder_exploratory/reference_screen/bridge_t11.json`; recorded strict reference flag `True`. This is an archived check, not independent adjudication.

Recorded reference-screen source: `research/study2-raw-v8-v9/evidence-part-001.zip::study2_outputs/bridge_items_1_4_6_v8_20261103/reference_screen/reference_screen/bridge_t11.json`; recorded strict reference flag `True`. This is an archived check, not independent adjudication.

Recorded reference-screen source: `research/study2-raw-v8-v9/evidence-part-001.zip::study2_outputs/bridge_items_1_4_6_v8_20261103/coder_exploratory/reference_screen/bridge_t12.json`; recorded strict reference flag `True`. This is an archived check, not independent adjudication.

Recorded reference-screen source: `research/study2-raw-v8-v9/evidence-part-001.zip::study2_outputs/bridge_items_1_4_6_v8_20261103/reference_screen/reference_screen/bridge_t12.json`; recorded strict reference flag `True`. This is an archived check, not independent adjudication.

Existing proposals: [{"source": "ADDITIONAL_BENCHMARK_OVERLAPS.csv", "decision": null, "recommendation": "NEAR_DUPLICATE", "mathematical_justification": "Same Nat binomial-square proposition, differing only in squared-expression notation (* versus ^2).", "justification": null}].

Reviewer questions: Are the propositions identical under binder renaming, definitional equality, a proved rewrite, or only related by a specialization? Does development exposure supply the same proof template? Should inference cluster these items together? Are reference proofs valid in the pinned environment, and does the English accurately express the statement? Do not approve independence solely because each reference compiles.

Reviewer name/affiliation: ____; independence/conflicts: ____; signed date: ____; exact reasoning and disposition: ____.

## bridge_d07 / bridge_t13

Relationship to examine: Possible z=1 distributivity specialization.

Potential development/test leakage: cross-split pair.

`bridge_d07`; family `bridge_nat_ring_squares`.

Exact statement:
```lean
theorem bridge_d07 (a b : Nat) : a*(b+1)=a*b+a
```
Available reference proof:
```lean
theorem bridge_d07 (a b : Nat) : a*(b+1)=a*b+a := by ring
```

V7 development-source successes (1 recorded evaluations): `{"B_neutral": 0, "C_real": 1, "D_shuffled": 1, "E_token_matched": 0, "R_resample": 0, "initial_success": 0}`. The base-model development source is the archived V5 lineage; V8 development is separately recorded. No development success is counted as held-out.

V8 development-source successes (1 recorded evaluations): `{"B_neutral": 0, "C_real": 0, "D_shuffled": 0, "E_token_matched": 0, "R_resample": 0, "initial_success": 0}`. The base-model development source is the archived V5 lineage; V8 development is separately recorded. No development success is counted as held-out.

`bridge_t13`; family `bridge_nat_polynomial`.

Exact statement:
```lean
theorem bridge_t13 (x y z : Nat) : x*(y+z)=x*y+x*z
```
Available reference proof:
```lean
theorem bridge_t13 (x y z : Nat) : x*(y+z)=x*y+x*z := by ring
```

V7 test successes across 3 seeds: `{"B_neutral": 0, "C_real": 0, "D_shuffled": 0, "E_token_matched": 0, "R_resample": 0, "initial_success": 0}`.

V8 test successes across 3 seeds: `{"B_neutral": 0, "C_real": 0, "D_shuffled": 0, "E_token_matched": 0, "R_resample": 0, "initial_success": 0}`.

Recorded reference-screen source: `research/study2-raw-v8-v9/evidence-part-001.zip::study2_outputs/bridge_items_1_4_6_v8_20261103/coder_exploratory/reference_screen/bridge_d07.json`; recorded strict reference flag `True`. This is an archived check, not independent adjudication.

Recorded reference-screen source: `research/study2-raw-v8-v9/evidence-part-001.zip::study2_outputs/bridge_items_1_4_6_v8_20261103/coder_exploratory/reference_screen/bridge_t13.json`; recorded strict reference flag `True`. This is an archived check, not independent adjudication.

Recorded reference-screen source: `research/study2-raw-v8-v9/evidence-part-001.zip::study2_outputs/bridge_items_1_4_6_v8_20261103/reference_screen/reference_screen/bridge_t13.json`; recorded strict reference flag `True`. This is an archived check, not independent adjudication.

Existing proposals: [{"source": "ADDITIONAL_BENCHMARK_OVERLAPS.csv", "decision": null, "recommendation": "NEAR_DUPLICATE", "mathematical_justification": "Development a*(b+1)=a*b+a is specialization of test distributivity x*(y+z)=x*y+x*z with z=1.", "justification": null}].

Reviewer questions: Are the propositions identical under binder renaming, definitional equality, a proved rewrite, or only related by a specialization? Does development exposure supply the same proof template? Should inference cluster these items together? Are reference proofs valid in the pinned environment, and does the English accurately express the statement? Do not approve independence solely because each reference compiles.

Reviewer name/affiliation: ____; independence/conflicts: ____; signed date: ____; exact reasoning and disposition: ____.

## bridge_t07 / bridge_t08

Relationship to examine: Successor/addition identities related through commutativity, not assumed definitionally equal.

Potential development/test leakage: within-test dependence.

`bridge_t07`; family `bridge_nat_successor`.

Exact statement:
```lean
theorem bridge_t07 (a b : Nat) : Nat.succ (a+b) = Nat.succ a+b
```
Available reference proof:
```lean
theorem bridge_t07 (a b : Nat) : Nat.succ (a+b) = Nat.succ a+b := by omega
```

V7 test successes across 3 seeds: `{"B_neutral": 0, "C_real": 0, "D_shuffled": 0, "E_token_matched": 0, "R_resample": 0, "initial_success": 0}`.

V8 test successes across 3 seeds: `{"B_neutral": 3, "C_real": 3, "D_shuffled": 3, "E_token_matched": 3, "R_resample": 3, "initial_success": 3}`.

`bridge_t08`; family `bridge_nat_successor`.

Exact statement:
```lean
theorem bridge_t08 (a b : Nat) : a + Nat.succ b = Nat.succ (a + b)
```
Available reference proof:
```lean
theorem bridge_t08 (a b : Nat) : a + Nat.succ b = Nat.succ (a + b) := by rfl
```

V7 test successes across 3 seeds: `{"B_neutral": 0, "C_real": 0, "D_shuffled": 0, "E_token_matched": 0, "R_resample": 0, "initial_success": 0}`.

V8 test successes across 3 seeds: `{"B_neutral": 3, "C_real": 3, "D_shuffled": 3, "E_token_matched": 3, "R_resample": 3, "initial_success": 3}`.

Recorded reference-screen source: `research/study2-raw-v8-v9/evidence-part-001.zip::study2_outputs/bridge_items_1_4_6_v8_20261103/coder_exploratory/reference_screen/bridge_t07.json`; recorded strict reference flag `True`. This is an archived check, not independent adjudication.

Recorded reference-screen source: `research/study2-raw-v8-v9/evidence-part-001.zip::study2_outputs/bridge_items_1_4_6_v8_20261103/reference_screen/reference_screen/bridge_t07.json`; recorded strict reference flag `True`. This is an archived check, not independent adjudication.

Recorded reference-screen source: `research/study2-raw-v8-v9/evidence-part-001.zip::study2_outputs/bridge_items_1_4_6_v8_20261103/coder_exploratory/reference_screen/bridge_t08.json`; recorded strict reference flag `True`. This is an archived check, not independent adjudication.

Recorded reference-screen source: `research/study2-raw-v8-v9/evidence-part-001.zip::study2_outputs/bridge_items_1_4_6_v8_20261103/reference_screen/reference_screen/bridge_t08.json`; recorded strict reference flag `True`. This is an archived check, not independent adjudication.

Existing proposals: [{"source": "ADDITIONAL_BENCHMARK_OVERLAPS.csv", "decision": null, "recommendation": "NEAR_DUPLICATE", "mathematical_justification": "Both prove addition/successor compatibility for Nat, with successor applied to first vs second addend; related by commutativity.", "justification": null}].

Reviewer questions: Are the propositions identical under binder renaming, definitional equality, a proved rewrite, or only related by a specialization? Does development exposure supply the same proof template? Should inference cluster these items together? Are reference proofs valid in the pinned environment, and does the English accurately express the statement? Do not approve independence solely because each reference compiles.

Reviewer name/affiliation: ____; independence/conflicts: ____; signed date: ____; exact reasoning and disposition: ____.

Reference-screen attestations and their source hashes are indexed in PR20 `results/reference_evidence.json` and this supplement SOURCE_HASHES.json. No new Lean equivalence checks were executed, and no frozen entries were deleted, regrouped or relabeled.
