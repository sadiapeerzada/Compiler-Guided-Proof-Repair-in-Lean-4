open scoped BigOperators
theorem study_q_log_tangent (x : ℝ) (hx : 0 < x) : Real.log x ≤ x - 1
:= by
  have h1 : x - 1 ≤ Real.log x + 1 - x := by
    rw [sub_add_cancel]
    apply sub_le_sub_right
    apply Real.log_le_add_one
    exact hx
  rw [sub_add_cancel] at h1
  exact le_of_eq h1