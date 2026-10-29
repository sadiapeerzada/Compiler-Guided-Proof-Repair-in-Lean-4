open scoped BigOperators
theorem study_q_integer_sqrt (n : ℕ) : Nat.sqrt n ^ 2 < n + 1
:= by
  induction' n with n IH
  · exact 0 < 0 + 1
  · have sqrt_n_plus_1 = Nat.sqrt (n + 1) : Nat.sqrt (n + 1) = Nat.sqrt (n + 1)
  have h1 : Nat.sqrt (n + 1) ^ 2 ≤ n + 1 := Nat.sqrt_le_of_sq_le this
  have h2 : Nat.sqrt (n + 1) ^ 2 < n + 2 := by
    rw [h1]
    exact lt_of_le_of_lt this (by linarith)
  have h3 : Nat.sqrt n ^ 2 < n + 1 := by
    rw [Nat.sqrt_eq_of_sq_eq this]
    exact IH
  have h4 : Nat.sqrt n ^ 2 < n + 2 := by
    rw [Nat.sqrt_eq_of_sq_eq h2]
    exact h3
  exact h4