open scoped BigOperators
theorem study_a_inverse_difference (x y : ℝ) (hx : x ≠ 0) (hy : y ≠ 0) : 1 / x - 1 / y = (y - x) / (x * y) :=
by
  have h1 : 1 / x = x⁻¹ := by
    rw [inv_inv]
    assumption
  have h2 : 1 / y = y⁻¹ := by
    rw [inv_inv]
    assumption
  have h3 : x⁻¹ - y⁻¹ = (y - x) / (x * y) := by
    rw [h1, h2]
    ring
  exact h3