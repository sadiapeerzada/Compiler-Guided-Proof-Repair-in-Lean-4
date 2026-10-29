open scoped BigOperators
theorem study_a_inverse_difference (x y : ℝ) (hx : x ≠ 0) (hy : y ≠ 0) : 1 / x - 1 / y = (y - x) / (x * y) :=
by
  have h1 : 1 / x - 1 / y = (y - x) / (x * y) := by
    rw [sub_eq_add_neg, div_add_div]
    ring
  exact h1