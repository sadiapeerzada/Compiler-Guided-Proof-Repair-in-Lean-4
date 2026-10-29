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
  have h6 : |x| * |y| = x * y ∨ |x| * |y| = -x * y := by
    by_contra
    have := h2
    linarith
  have h7 : |x * y| = x * y ∨ |x * y| = -x * y := by
    by_contra
    have := h1
    linarith
  have h8 : x * y = |x * y| ∨ x * y = -|x * y| := by
    by_contra
    have := h3
    linarith
  have h9 : x = |x| ∨ x = -|x| := by
    by_contra
    have := h4
    linarith
  have h10 : y = |y| ∨ y = -|y| := by
    by_contra
    have := h5
    linarith
  have h11 : |x| * |y| = |x * y| := by
    by_cases h12 : x * y = |x * y|
    · rw [h12]
      rw [h11]
    · rw [h12]
      rw [mul_neg_neg, h11]
  have h12 : |x * y| = |x| * |y| := by
    by_cases h13 : x * y = |x * y|
    · rw [h13]
      rw [h11]
    · rw [h13]
      rw [mul_neg_neg, h11]
  exact h12