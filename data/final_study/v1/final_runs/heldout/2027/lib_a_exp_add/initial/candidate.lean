open scoped BigOperators
theorem study_a_exp_add (x y : ℝ) : Real.exp (x + y) = Real.exp x * Real.exp y
:= by
  have h : Real.exp (x + y) = Real.ofReal (Real.exp x * Real.exp y) := by
    rw [Real.exp_add]
  have h' : Real.ofReal (Real.exp x * Real.exp y) = Real.exp x * Real.exp y := by
    rw [Real.ofReal_exp]
  exact h.symm.trans h'