open scoped BigOperators
theorem study_q_integer_sqrt (n : ℕ) : Nat.sqrt n ^ 2 < n + 1
:= by
  induction' n with n IH
  · exact zero_lt_one
  · have h1 : Nat.sqrt (n + 1) ^ 2 ≤ n + 1 := Nat.sqrt_le_of_sq_le (by exact IH)
  have h2 : Nat.sqrt (n + 1) ^ 2 < n + 2 := by
    rw [h1]
    exact lt_of_le_of_lt h1 (by linarith)
  exact h2