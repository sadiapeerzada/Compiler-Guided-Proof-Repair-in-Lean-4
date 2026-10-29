open scoped BigOperators
theorem study_q_triangle (x y : ℝ) : |x + y| ≤ |x| + |y| :=
by
  have h1 : |x + y| ≤ |x + y| := by
    apply le_refl
  have h2 : |x + y| ≤ |x| + |y| := by
    apply le_trans h1
    apply abs_add_le_add
  exact h2