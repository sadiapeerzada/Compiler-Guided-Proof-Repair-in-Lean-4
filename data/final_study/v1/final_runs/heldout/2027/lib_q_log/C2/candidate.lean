open scoped BigOperators

theorem study_q_log (b n : ℕ) (hn : n ≠ 0) : b ^ Nat.log b n ≤ n
:= by
  classical
  have h1 : 0 < b := by
    by_contradiction (assume h : b = 0)
    have h2 : 0 = b ^ Nat.log b n := by
      rw [h, zero_pow]
      exact Nat.zero_eq_zero
    have h3 : 0 ≤ n := by
      rw [h2, zero_le_one]
      exact Nat.one_le_of_ne_zero h
    contradiction
  have h2 : 0 < n := by
    rw [hn]
    exact Nat.zero_lt_one
  have h3 : Nat.log b n ≤ n := by
    classical
    have h4 : 0 < b ^ (Nat.log b n) := by
      rw [Nat.pow_pos_of_pos h1 (Nat.log_pos_of_pos_of_ne_zero h1 h2)]
      exact h2
    have h5 : b ^ (Nat.log b n) ≤ b ^ n := by
      apply Nat.pow_le_pow_of_le_one
      have h6 : 1 ≤ b := by
        rw [h1]
        exact Nat.one_le_of_pos h1
      exact h6
    exact h5
  exact h3