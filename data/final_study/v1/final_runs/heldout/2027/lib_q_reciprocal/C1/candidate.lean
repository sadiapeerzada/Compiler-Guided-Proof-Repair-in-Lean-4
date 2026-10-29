open scoped BigOperators
theorem study_q_reciprocal (x y : ℝ) (hx : 0 < x) (hxy : x ≤ y) : 1 / y ≤ 1 / x
:= by
  have hxy_pos : 0 < y := by
    exact div_pos hxy hx
  have h_inv_x_le_inv_y : 1 / x ≤ 1 / y := by
    rw [div_le_div_iff (by linarith [hx, hxy])]
    exact hxy_pos
  exact h_inv_x_le_inv_y