open scoped BigOperators
theorem study_a_exp_add (x y : ℝ) : Real.exp (x + y) = Real.exp x * Real.exp y
:= by
  have h : Real.exp (x + y) = Real.exp x * Real.exp y := by
    rw [Real.exp_add]
  exact h