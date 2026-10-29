open scoped BigOperators
theorem study_q_amgm (x y : ℝ) : 2 * x * y ≤ x ^ 2 + y ^ 2 := by
  have h : x ^ 2 + y ^ 2 - 2 * x * y ≥ 0 := by
    calc
      x ^ 2 + y ^ 2 - 2 * x * y = (x - y) ^ 2 : by ring
    _ ≥ 0 : by simp [sq_nonneg]
  exact h