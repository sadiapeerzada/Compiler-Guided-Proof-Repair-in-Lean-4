open scoped BigOperators

theorem study_a_abs_product (x y : ℝ) : |x * y| = |x| * |y|
proof
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
  have h6 : |x| * |y| = |x * y| := by
    by_cases h12 : x * y = |x * y|
    · rw [h12]
      rw [abs_mul]
    · rw [h12]
      rw [mul_neg_neg, abs_mul]
  have h7 : |x * y| = |x| * |y| := by
    by_cases h13 : x * y = |x * y|
    · rw [h13]
      rw [abs_mul]
    · rw [h13]
      rw [mul_neg_neg, abs_mul]
  exact h7
end