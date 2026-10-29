open scoped BigOperators
theorem study_q_log_tangent (x : ℝ) (hx : 0 < x) : Real.log x ≤ x - 1
:= by
  have h1 : 0 < x → x - 1 - x + 1 ≤ Real.log x - (x - 1) := by
    intro hx
    rw [sub_add_cancel]
    apply sub_le_sub_right
    apply Real.log_le_log_add_one
    exact hx
  exact h1 hx