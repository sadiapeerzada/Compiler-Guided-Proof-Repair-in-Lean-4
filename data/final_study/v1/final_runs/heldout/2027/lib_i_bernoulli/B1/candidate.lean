open scoped BigOperators
theorem study_i_bernoulli (x : ℝ) (n : ℕ) (h : -1 ≤ x) : 1 + (n : ℝ) * x ≤ (1 + x) ^ n
:= by
  induction' n with n ih
  · rw [pow_zero, add_zero]
  · have h1 : 1 + (n + 1 : ℝ) * x ≤ (1 + x) * (1 + x) ^ n := by
      rw [mul_add, add_comm, add_assoc, add_right_comm, add_right_cancel]
      apply le_mul_of_pos_add_right
      · exact h
      · exact ih
    rw [pow_succ, add_comm, add_assoc, add_right_comm, add_right_cancel] at h1
    exact h1