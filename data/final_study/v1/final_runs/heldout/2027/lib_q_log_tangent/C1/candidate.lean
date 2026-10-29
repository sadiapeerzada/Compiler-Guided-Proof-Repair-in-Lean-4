open scoped BigOperators
theorem study_q_log_tangent (x : ℝ) (hx : 0 < x) : Real.log x ≤ x - 1
:= by
  have h1 : x - 1 - x + 1 ≤ Real.log x - (x - 1) := by
    rw [sub_add_cancel]
    apply sub_le_sub_right
    apply Real.log_le_log_add_one
    exact hx
  rw [sub_self, zero_sub] at h1
  exact h1