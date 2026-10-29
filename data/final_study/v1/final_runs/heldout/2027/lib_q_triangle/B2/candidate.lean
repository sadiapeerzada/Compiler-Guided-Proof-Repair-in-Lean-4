open scoped BigOperators
theorem study_q_triangle (x y : ℝ) : |x + y| ≤ |x| + |y| :=
by
  apply le_trans (le_refl (abs (x + y)))
  apply abs_add_le_add