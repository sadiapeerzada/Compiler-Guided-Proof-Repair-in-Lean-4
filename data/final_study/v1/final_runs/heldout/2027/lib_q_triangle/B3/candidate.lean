open scoped BigOperators
theorem study_q_triangle (x y : ℝ) : |x + y| ≤ |x| + |y| :=
by
  apply le_trans (le_of_eq (abs_add_eq_add_of_nonneg (by linarith)))
  apply abs_add_le_add