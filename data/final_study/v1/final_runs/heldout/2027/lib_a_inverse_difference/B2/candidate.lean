open scoped BigOperators
theorem study_a_inverse_difference (x y : ℝ) (hx : x ≠ 0) (hy : y ≠ 0) : 1 / x - 1 / y = (y - x) / (x * y) :=
by
  have h3 : (1 / x) - (1 / y) = (y - x) / (x * y) := by
    rw [div_sub_div_eq_sub_div, div_mul_div_comm]
    ring
  exact h3