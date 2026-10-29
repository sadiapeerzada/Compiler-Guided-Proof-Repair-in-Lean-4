open scoped BigOperators

theorem study_a_abs_product (x y : ℝ) : |x * y| = |x| * |y| :=
by
  have h1 : |x * y| = x * y ∨ |x * y| = -x * y := by
    apply abs_eq
  have h2 : |x| * |y| = x * y ∨ |x| * |y| = -x * y := by
    apply abs_mul
  have h3 : x * y = |x * y| ∨ x * y = -|x * y| := by
    apply mul_eq_abs
  have h4 : x = |x| ∨ x = -|x| := by
    apply eq_abs
  have h5 : y = |y| ∨ y = -|y| := by
    apply eq_abs
  have h6 : |x * y| = |x| * |y| := by
    by_cases h12 : x * y = |x * y|
    · rw [h12, h1]
    · rw [h12, h2]
  exact h6