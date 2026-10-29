open scoped BigOperators

theorem study_q_triangle (x y : ℝ) : |x + y| ≤ |x| + |y :=
by
  have h1 : |x + y| = x + y ∨ |x + y| = -(x + y) := by
    apply Or.inl_or_Or_inr
    rw [abs_eq_add_of_nonneg (by simp)]
    apply Or.inl
    apply abs_add_le_add
  have h2 : |x| = x ∨ |x| = -x := by
    apply Or.inl_or_Or_inr
    rw [abs_eq_add_of_nonneg (by simp)]
    apply Or.inl
    apply abs_le_self
  have h3 : |y| = y ∨ |y| = -y := by
    apply Or.inl_or_Or_inr
    rw [abs_eq_add_of_nonneg (by simp)]
    apply Or.inl
    apply abs_le_self
  have h4 : x + y ≥ 0 ∨ x + y ≤ 0 := by
    apply Or.inl_or_Or_inr
    rw [abs_eq_add_of_nonneg (by simp)]
    apply Or.inl
    apply abs_add_le_add
  have h5 : |x| + |y| ≥ 0 := by
    apply le_trans
    apply add_nonneg
    apply le_of_lt
    apply abs_le_self
    apply le_of_lt
    apply abs_le_self
  have h6 : |x + y| + |x| + |y| ≥ 0 := by
    apply le_trans
    apply add_nonneg
    apply le_of_lt
    apply abs_add_le_add
    apply le_of_lt
    apply abs_le_self
  have h7 : |x + y| + |x| + |y| ≥ |x + y| := by
    apply le_trans
    apply add_nonneg
    apply le_of_lt
    apply abs_add_le_add
    apply le_of_lt
    apply abs_le_self
  have h8 : |x + y| ≤ |x| + |y| := by
    apply le_of_lt
    apply add_nonneg
    apply le_of_lt
    apply abs_add_le_add
    apply le_of_lt
    apply abs_le_self
  exact h8