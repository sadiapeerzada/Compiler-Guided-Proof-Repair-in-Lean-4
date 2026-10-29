open scoped BigOperators
theorem study_q_reciprocal (x y : ℝ) (hx : 0 < x) (hxy : x ≤ y) : 1 / y ≤ 1 / x
:= by
  have hxy_pos : 0 < y := by
    exact div_pos hxy hx
  have hxy_inv : 0 < 1 / y := by
    exact div_pos (by rw [hxy_pos]; exact hx) (by rw [hxy_pos])
  have hxy_inv_le_inv_x : (1 / y) * (1 / x) ≤ 1 := by
    rw [mul_div_cancel' hx]
    exact hxy
  have h_inv_x_le_inv_y : 1 / x ≤ 1 / y := by
    rw [div_le_div_iff (by rw [hxy_inv])]
    exact hxy_inv_le_inv_x
  exact h_inv_x_le_inv_y