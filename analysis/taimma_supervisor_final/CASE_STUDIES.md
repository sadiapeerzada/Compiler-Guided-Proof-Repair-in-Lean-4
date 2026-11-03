# Three authentic proof-repair case studies

Selected post-hoc for contrasting behavior, not representative sampling. All text below is extracted from recorded candidates and diagnostics, never fabricated. Source-file hashes are in SOURCE_HASHES.json. Candidate SHA-256 refers to original UTF-8 candidate bytes; display-only personal home paths are redacted. The extracted Lean candidate may omit response code fences; no proof is reconstructed. Strict outcomes are historical verifier records, not a new Lean replay.

## lib_a_exp_add

Family: `exponential_addition_law`. Study 1 frozen heldout pilot; protocol a032110d7afbc367c2daa820bd17511c6ff5dba2d1164e0130ea5d1c4b693317; model `mlx-community/Qwen2.5-7B-Instruct-4bit`; revision `c26a38f6a37d0a51b4e9a1eb3026530fa35d9fed`; seed 2027.

Source: `publication/evidence/redacted_runs/heldout/2027/lib_a_exp_add/manifest.json`.

Publication-redacted views: recorded original hashes and current view-file hashes differ by design. Full generated candidates are shown, not reconstructed responses. Shuffled arm was not part of Study 1.

Both blind B and correct-diagnostic C retrieve the direct Real.exp_add rewrite and verify. This authentic repair does not establish diagnostic specificity.

### Initial

Candidate SHA-256: `774dabac6d8563cffce47790c6ac43d2b85a3e513b6c67a4097243e7bd15ce24`. Verified: **False**; exit 1; failure kind `compiler_error`; recorded axioms `None`.

```lean
open scoped BigOperators
theorem study_a_exp_add (x y : ℝ) : Real.exp (x + y) = Real.exp x * Real.exp y
:= by
  have h : Real.exp (x + y) = Real.ofReal (Real.exp x * Real.exp y) := by
    rw [Real.exp_add]
  have h' : Real.ofReal (Real.exp x * Real.exp y) = Real.exp x * Real.exp y := by
    rw [Real.ofReal_exp]
  exact h.symm.trans h'
```

Actual diagnostic:

```text
line 13: Unknown constant `Real.ofReal`
line 13: unsolved goals
x y : ℝ
⊢ Real.exp x * Real.exp y = sorry
line 15: Unknown constant `Real.ofReal`
line 16: Unknown constant `Real.ofReal_exp`
```

### B1

Candidate SHA-256: `87a0083ad1ea711b93ee41d187315e1e380270bc910b4b7d3493ee09b88f136c`. Verified: **True**; exit 0; failure kind `None`; recorded axioms `['propext', 'Classical.choice', 'Quot.sound']`.

```lean
open scoped BigOperators
theorem study_a_exp_add (x y : ℝ) : Real.exp (x + y) = Real.exp x * Real.exp y
:= by
  rw [Real.exp_add]
```

Actual diagnostic:

```text
[No error diagnostic recorded for this verified step]
```

Completion/trajectory source: `publication/evidence/redacted_runs/heldout/2027/lib_a_exp_add/B1/completion.json`; verification: `publication/evidence/redacted_runs/heldout/2027/lib_a_exp_add/B1/verification.json`.

### C1

Candidate SHA-256: `ac08a664fe0ffbb72889502923a199d6ceeb00e398e737949111ef5a389dab90`. Verified: **True**; exit 0; failure kind `None`; recorded axioms `['propext', 'Classical.choice', 'Quot.sound']`.

```lean
open scoped BigOperators
theorem study_a_exp_add (x y : ℝ) : Real.exp (x + y) = Real.exp x * Real.exp y
:= by
  have h : Real.exp (x + y) = Real.exp x * Real.exp y := by
    rw [Real.exp_add]
  exact h
```

Actual diagnostic:

```text
[No error diagnostic recorded for this verified step]
```

Completion/trajectory source: `publication/evidence/redacted_runs/heldout/2027/lib_a_exp_add/C1/completion.json`; verification: `publication/evidence/redacted_runs/heldout/2027/lib_a_exp_add/C1/verification.json`.

## div_008

Family: `integer_parity`. Study 1 frozen heldout pilot; protocol a032110d7afbc367c2daa820bd17511c6ff5dba2d1164e0130ea5d1c4b693317; model `mlx-community/Qwen2.5-7B-Instruct-4bit`; revision `c26a38f6a37d0a51b4e9a1eb3026530fa35d9fed`; seed 2027.

Source: `publication/evidence/redacted_runs/heldout/2027/div_008/manifest.json`.

Publication-redacted views: recorded original hashes and current view-file hashes differ by design. Full generated candidates are shown, not reconstructed responses. Shuffled arm was not part of Study 1.

Compiler feedback is followed by candidate edits, but the strict verifier still rejects the repairs. Edits and error changes are not theorem verification.

### Initial

Candidate SHA-256: `50b283f878373d81ef1de589315ca03173bc59ae5a9ca52b5d90915ac51546da`. Verified: **False**; exit 1; failure kind `compiler_error`; recorded axioms `None`.

```lean
theorem even_iff_even_three_mul (n : ℤ) : Even n ↔ Even (3 * n) :=
by
  split
  · intro h
    have := h
    cases h with k hk
    exact even_mul_of_even _ (by rw [hk]; exact even_of_add_one_even (by rw [mul_one]; exact even_of_add_one_even (by rw [mul_one])))

  · intro h
    have := h
    cases h with k hk
    have := even_of_add_one_even (by rw [mul_one]; exact even_of_add_one_even (by rw [mul_one]))
    rw [hk] at this
    exact even_of_add_one_even (by rw [this])
```

Actual diagnostic:

```text
line 14: unknown tactic
```

### B1

Candidate SHA-256: `2ad75dc9d1910668562da7790191a12edd22c353bf977f811c0fd8994c2ad207`. Verified: **False**; exit 1; failure kind `compiler_error`; recorded axioms `None`.

```lean
theorem even_iff_even_three_mul (n : ℤ) : Even n ↔ Even (3 * n) :=
by
  split
  · intro h
    have := h
    cases h with k hk
    exact even_mul_of_even _ (by rw [hk]; exact even_of_add_one_even (by rw [mul_one]))

  · intro h
    have := h
    cases h with k hk
    have := even_of_add_one_even (by rw [mul_one])
    rw [hk] at this
    exact even_of_add_one_even (by rw [this])
```

Actual diagnostic:

```text
line 14: unknown tactic
```

Completion/trajectory source: `publication/evidence/redacted_runs/heldout/2027/div_008/B1/completion.json`; verification: `publication/evidence/redacted_runs/heldout/2027/div_008/B1/verification.json`.

### B2

Candidate SHA-256: `f7dad148bd671b3b50533c7663a97f0aa51fe5bc0b467098cd0eb5261d5e0ed8`. Verified: **False**; exit 1; failure kind `compiler_error`; recorded axioms `None`.

```lean
theorem even_iff_even_three_mul (n : ℤ) : Even n ↔ Even (3 * n) :=
by
  split
  · intro h
    have := h
    cases h with k hk
    exact even_mul_of_even _ (by rw [hk]; exact even_of_add_one_even (by rw [mul_one]))

  · intro h
    have := h
    cases h with k hk
    rw [hk]
    exact even_of_add_one_even (by rw [mul_one])
```

Actual diagnostic:

```text
line 14: unknown tactic
```

Completion/trajectory source: `publication/evidence/redacted_runs/heldout/2027/div_008/B2/completion.json`; verification: `publication/evidence/redacted_runs/heldout/2027/div_008/B2/verification.json`.

### B3

Candidate SHA-256: `f7dad148bd671b3b50533c7663a97f0aa51fe5bc0b467098cd0eb5261d5e0ed8`. Verified: **False**; exit 1; failure kind `compiler_error`; recorded axioms `None`.

```lean
theorem even_iff_even_three_mul (n : ℤ) : Even n ↔ Even (3 * n) :=
by
  split
  · intro h
    have := h
    cases h with k hk
    exact even_mul_of_even _ (by rw [hk]; exact even_of_add_one_even (by rw [mul_one]))

  · intro h
    have := h
    cases h with k hk
    rw [hk]
    exact even_of_add_one_even (by rw [mul_one])
```

Actual diagnostic:

```text
line 14: unknown tactic
```

Completion/trajectory source: `publication/evidence/redacted_runs/heldout/2027/div_008/B3/completion.json`; verification: `publication/evidence/redacted_runs/heldout/2027/div_008/B3/verification.json`.

### C1

Candidate SHA-256: `39c018c0c22c0af813c8ae793cb98d69e034af5cc1d373a1d7aea3c86ecca872`. Verified: **False**; exit 1; failure kind `compiler_error`; recorded axioms `None`.

```lean
theorem even_iff_even_three_mul (n : ℤ) : Even n ↔ Even (3 * n) :=
by
  split
  · intro h
    obtain ⟨k, hk⟩ := h
    exact even_of_add_one_even (by rw [mul_one, hk, mul_one])

  · intro h
    obtain ⟨k, hk⟩ := h
    have := even_of_add_one_even (by rw [mul_one, hk, mul_one])
    exact this
```

Actual diagnostic:

```text
line 11: Tactic `split` failed: Could not split an `if` or `match` expression in the goal

Hint: If you meant to destruct this structure, use the `cases` tactic instead

Hint: Use `set_option trace.split.failure true` to display additional diagnostic information

n : ℤ
⊢ Even n ↔ Even (3 * n)
```

Completion/trajectory source: `publication/evidence/redacted_runs/heldout/2027/div_008/C1/completion.json`; verification: `publication/evidence/redacted_runs/heldout/2027/div_008/C1/verification.json`.

### C2

Candidate SHA-256: `ebbb31cd3adb414046d864e957eb05a64954c7229cbc7cd410e2933c6150ba17`. Verified: **False**; exit 1; failure kind `compiler_error`; recorded axioms `None`.

```lean
theorem even_iff_even_three_mul (n : ℤ) : Even n ↔ Even (3 * n) :=
by
  split
  · intro h
    obtain ⟨k, hk⟩ := h
    exact even_of_add_one_even (by rw [mul_one, hk, mul_one])

  · intro h
    obtain ⟨k, hk⟩ := h
    rw [mul_one, hk, mul_one]
    exact even_of_add_one_even _
```

Actual diagnostic:

```text
line 11: Tactic `split` failed: Could not split an `if` or `match` expression in the goal

Hint: If you meant to destruct this structure, use the `cases` tactic instead

Hint: Use `set_option trace.split.failure true` to display additional diagnostic information

n : ℤ
⊢ Even n ↔ Even (3 * n)
```

Completion/trajectory source: `publication/evidence/redacted_runs/heldout/2027/div_008/C2/completion.json`; verification: `publication/evidence/redacted_runs/heldout/2027/div_008/C2/verification.json`.

### C3

Candidate SHA-256: `70a05c0aec1d161b0236eb52e8e0891bd43c6177a81e300a879745b53b556be3`. Verified: **False**; exit 1; failure kind `compiler_error`; recorded axioms `None`.

```lean
theorem even_iff_even_three_mul (n : ℤ) : Even n ↔ Even (3 * n) :=
by
  split
  · intro h
    obtain ⟨k, hk⟩ := h
    exact even_of_add_one_even (by rw [mul_one, hk, mul_one])

  · intro h
    obtain ⟨k, hk⟩ := h
    rw [mul_one, hk, mul_one]
    exact even_of_add_one_even (by rw [mul_one, hk, mul_one])
```

Actual diagnostic:

```text
line 11: Tactic `split` failed: Could not split an `if` or `match` expression in the goal

Hint: If you meant to destruct this structure, use the `cases` tactic instead

Hint: Use `set_option trace.split.failure true` to display additional diagnostic information

n : ℤ
⊢ Even n ↔ Even (3 * n)
```

Completion/trajectory source: `publication/evidence/redacted_runs/heldout/2027/div_008/C3/completion.json`; verification: `publication/evidence/redacted_runs/heldout/2027/div_008/C3/verification.json`.

## bridge_t16

Family: `bridge_int_polynomial`. Study 2 V7 test; 2026-11-03-study2-v7-t08-application-syntax; model `mlx-community/Qwen2.5-7B-Instruct-4bit`; revision `c26a38f6a37d0a51b4e9a1eb3026530fa35d9fed`; seed 2027.

Source: `study2_outputs/bridge_v7_base/trajectories/Qwen2_5-7B-Instruct-4bit/2027/test/bridge_t16.json`.

V7 raw trajectory is a local untracked snapshot, not in the public V8/V9 archive; its minimal sanitized view is committed in sources/v7_trajectory_views.json for portable reanalysis. Candidate hashes bind text internally; final arm outcomes are checked against frozen V7 outcomes.csv. Newly hashed excerpts do not retroactively authenticate raw history.

C fixes the Lean 3 begin/end shell to Lean 4 := by ring and verifies at step 1; blind B and shuffled D exhaust their budgets without verification. This selected discordance illustrates a possible mechanism, not an average causal benefit.

### Initial

Candidate SHA-256: `45a62122905f46beebfee21ec2ec2c53e765cfe48dd82d36cab5f55d1b1765f7`. Verified: **False**; exit 1; failure kind `compiler_error`; recorded axioms `None`.

```lean
theorem bridge_t16 (x y : Int) : (x+y)*(x-y) = x^2 - y^2 :=
begin
  ring,
end
```

Actual diagnostic:

```text
line 11: Unknown identifier `begin`
line 12: unexpected token ','; expected command
line 13: Missing name after `end`: Expected the current scope name `Nl2LeanCandidate`

Hint: To end the current scope `Nl2LeanCandidate`, specify its name:
  end ̲N̲l̲2̲L̲e̲a̲n̲C̲a̲n̲d̲i̲d̲a̲t̲e̲
```

### B_neutral_1

Candidate SHA-256: `8d2babd3ef08c39bbbed6f0b7b0ecfb808ec243b1e010f8f396d5cbf794be421`. Verified: **False**; exit 1; failure kind `compiler_error`; recorded axioms `None`.

```lean
theorem bridge_t16 (x y : Int) : (x+y)*(x-y)=x^2-y^2 :=
begin
  ring,
end
```

Actual diagnostic:

```text
line 11: Unknown identifier `begin`
line 12: unexpected token ','; expected command
line 13: Missing name after `end`: Expected the current scope name `Nl2LeanCandidate`

Hint: To end the current scope `Nl2LeanCandidate`, specify its name:
  end ̲N̲l̲2̲L̲e̲a̲n̲C̲a̲n̲d̲i̲d̲a̲t̲e̲
```

Completion/trajectory source: `study2_outputs/bridge_v7_base/trajectories/Qwen2_5-7B-Instruct-4bit/2027/test/bridge_t16.json`; verification: `study2_outputs/bridge_v7_base/trajectories/Qwen2_5-7B-Instruct-4bit/2027/test/bridge_t16.json`.

### B_neutral_2

Candidate SHA-256: `8d2babd3ef08c39bbbed6f0b7b0ecfb808ec243b1e010f8f396d5cbf794be421`. Verified: **False**; exit 1; failure kind `compiler_error`; recorded axioms `None`.

```lean
theorem bridge_t16 (x y : Int) : (x+y)*(x-y)=x^2-y^2 :=
begin
  ring,
end
```

Actual diagnostic:

```text
line 11: Unknown identifier `begin`
line 12: unexpected token ','; expected command
line 13: Missing name after `end`: Expected the current scope name `Nl2LeanCandidate`

Hint: To end the current scope `Nl2LeanCandidate`, specify its name:
  end ̲N̲l̲2̲L̲e̲a̲n̲C̲a̲n̲d̲i̲d̲a̲t̲e̲
```

Completion/trajectory source: `study2_outputs/bridge_v7_base/trajectories/Qwen2_5-7B-Instruct-4bit/2027/test/bridge_t16.json`; verification: `study2_outputs/bridge_v7_base/trajectories/Qwen2_5-7B-Instruct-4bit/2027/test/bridge_t16.json`.

### B_neutral_3

Candidate SHA-256: `45a62122905f46beebfee21ec2ec2c53e765cfe48dd82d36cab5f55d1b1765f7`. Verified: **False**; exit 1; failure kind `compiler_error`; recorded axioms `None`.

```lean
theorem bridge_t16 (x y : Int) : (x+y)*(x-y) = x^2 - y^2 :=
begin
  ring,
end
```

Actual diagnostic:

```text
line 11: Unknown identifier `begin`
line 12: unexpected token ','; expected command
line 13: Missing name after `end`: Expected the current scope name `Nl2LeanCandidate`

Hint: To end the current scope `Nl2LeanCandidate`, specify its name:
  end ̲N̲l̲2̲L̲e̲a̲n̲C̲a̲n̲d̲i̲d̲a̲t̲e̲
```

Completion/trajectory source: `study2_outputs/bridge_v7_base/trajectories/Qwen2_5-7B-Instruct-4bit/2027/test/bridge_t16.json`; verification: `study2_outputs/bridge_v7_base/trajectories/Qwen2_5-7B-Instruct-4bit/2027/test/bridge_t16.json`.

### C_real_1

Candidate SHA-256: `984af7ba243abe62195d0371ff7d795485e068ab6e1f895ba750ea4eeb7b44f6`. Verified: **True**; exit 0; failure kind `None`; recorded axioms `['propext', 'Quot.sound']`.

```lean
theorem bridge_t16 (x y : Int) : (x+y)*(x-y) = x^2 - y^2 := by ring
```

Actual diagnostic:

```text
[No error diagnostic recorded for this verified step]
```

Completion/trajectory source: `study2_outputs/bridge_v7_base/trajectories/Qwen2_5-7B-Instruct-4bit/2027/test/bridge_t16.json`; verification: `study2_outputs/bridge_v7_base/trajectories/Qwen2_5-7B-Instruct-4bit/2027/test/bridge_t16.json`.

### D_shuffled_1

Candidate SHA-256: `45a62122905f46beebfee21ec2ec2c53e765cfe48dd82d36cab5f55d1b1765f7`. Verified: **False**; exit 1; failure kind `compiler_error`; recorded axioms `None`.

```lean
theorem bridge_t16 (x y : Int) : (x+y)*(x-y) = x^2 - y^2 :=
begin
  ring,
end
```

Actual diagnostic:

```text
line 11: Unknown identifier `begin`
line 12: unexpected token ','; expected command
line 13: Missing name after `end`: Expected the current scope name `Nl2LeanCandidate`

Hint: To end the current scope `Nl2LeanCandidate`, specify its name:
  end ̲N̲l̲2̲L̲e̲a̲n̲C̲a̲n̲d̲i̲d̲a̲t̲e̲
```

Completion/trajectory source: `study2_outputs/bridge_v7_base/trajectories/Qwen2_5-7B-Instruct-4bit/2027/test/bridge_t16.json`; verification: `study2_outputs/bridge_v7_base/trajectories/Qwen2_5-7B-Instruct-4bit/2027/test/bridge_t16.json`.

### D_shuffled_2

Candidate SHA-256: `45a62122905f46beebfee21ec2ec2c53e765cfe48dd82d36cab5f55d1b1765f7`. Verified: **False**; exit 1; failure kind `compiler_error`; recorded axioms `None`.

```lean
theorem bridge_t16 (x y : Int) : (x+y)*(x-y) = x^2 - y^2 :=
begin
  ring,
end
```

Actual diagnostic:

```text
line 11: Unknown identifier `begin`
line 12: unexpected token ','; expected command
line 13: Missing name after `end`: Expected the current scope name `Nl2LeanCandidate`

Hint: To end the current scope `Nl2LeanCandidate`, specify its name:
  end ̲N̲l̲2̲L̲e̲a̲n̲C̲a̲n̲d̲i̲d̲a̲t̲e̲
```

Completion/trajectory source: `study2_outputs/bridge_v7_base/trajectories/Qwen2_5-7B-Instruct-4bit/2027/test/bridge_t16.json`; verification: `study2_outputs/bridge_v7_base/trajectories/Qwen2_5-7B-Instruct-4bit/2027/test/bridge_t16.json`.

### D_shuffled_3

Candidate SHA-256: `45a62122905f46beebfee21ec2ec2c53e765cfe48dd82d36cab5f55d1b1765f7`. Verified: **False**; exit 1; failure kind `compiler_error`; recorded axioms `None`.

```lean
theorem bridge_t16 (x y : Int) : (x+y)*(x-y) = x^2 - y^2 :=
begin
  ring,
end
```

Actual diagnostic:

```text
line 11: Unknown identifier `begin`
line 12: unexpected token ','; expected command
line 13: Missing name after `end`: Expected the current scope name `Nl2LeanCandidate`

Hint: To end the current scope `Nl2LeanCandidate`, specify its name:
  end ̲N̲l̲2̲L̲e̲a̲n̲C̲a̲n̲d̲i̲d̲a̲t̲e̲
```

Completion/trajectory source: `study2_outputs/bridge_v7_base/trajectories/Qwen2_5-7B-Instruct-4bit/2027/test/bridge_t16.json`; verification: `study2_outputs/bridge_v7_base/trajectories/Qwen2_5-7B-Instruct-4bit/2027/test/bridge_t16.json`.
