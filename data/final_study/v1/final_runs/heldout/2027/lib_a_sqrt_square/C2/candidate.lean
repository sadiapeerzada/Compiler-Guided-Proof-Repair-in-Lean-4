open scoped BigOperators
theorem study_a_sqrt_square (x : ℝ) (h : 0 ≤ x) : (Real.sqrt x) ^ 2 = x := by
  rw [Real.sqrt_sq_of_nonneg h]