open scoped BigOperators
theorem study_a_sqrt_square (x : ℝ) (h : 0 ≤ x) : (Real.sqrt x) ^ 2 = x := by
  rw [Real.sqrt_def]
  have h' : (Real.sqrt x) * (Real.sqrt x) = x := by
    rw [Real.sqrt_def]
    exact h
  exact h'