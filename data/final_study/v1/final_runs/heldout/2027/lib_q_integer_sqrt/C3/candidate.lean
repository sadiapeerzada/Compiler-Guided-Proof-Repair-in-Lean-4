open scoped BigOperators
theorem study_q_integer_sqrt (n : ℕ) : Nat.sqrt n ^ 2 < n + 1
:= by
  induction' n with n IH
  · exact zero_lt_one
  · have h1 := Nat.sqrt_le_of_sq_le (by exact IH)
  have h2 := by linarith [h1]
  exact h2