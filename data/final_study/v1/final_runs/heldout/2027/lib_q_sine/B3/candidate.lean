open scoped BigOperators
theorem study_q_sine (x : ℝ) (hx : 0 ≤ x) : Real.sin x ≤ x
:= by
  have key_sin_le_x : Real.sin x ≤ x
  := by
    apply Real.sin_le_self
    exact hx
  exact key_sin_le_x