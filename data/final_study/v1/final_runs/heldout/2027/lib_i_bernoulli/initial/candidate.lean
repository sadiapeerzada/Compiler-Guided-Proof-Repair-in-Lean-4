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
    have h2 : (n + 1 : ℝ) * x ≤ (1 + x) ^ n * x := by
      rw [mul_add, add_comm, add_assoc, add_right_comm, add_right_cancel]
      apply le_mul_of_pos_add_right
      · exact h
      · exact ih
    have h3 : 1 + (n + 1 : ℝ) * x ≤ (1 + x) ^ n * (1 + x) := by
      rw [mul_add, add_comm, add_assoc, add_right_comm, add_right_cancel]
      apply le_add_of_le_add_right
      · exact h1
      · exact h2
    rw [pow_succ, add_comm, add_assoc, add_right_comm, add_right_cancel] at h3
    exact h3