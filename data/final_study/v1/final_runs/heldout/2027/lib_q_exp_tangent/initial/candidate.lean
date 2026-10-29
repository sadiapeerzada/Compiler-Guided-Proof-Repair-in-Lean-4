open scoped BigOperators
theorem study_q_exp_tangent (x : ℝ) : x + 1 ≤ Real.exp x
:= by
  have h : 0 ≤ x + 1 := by
    apply le_add_right
    exact zero_le_one
  have h_exp : 0 ≤ Real.exp x := by
    apply Real.exp_nonneg
  have h_sum : (0 : ℝ) ≤ ∑ i in finset.range (x + 2), 1 := by
    apply le_sum
    intro i
    apply le_one
  have h_exp_sum : Real.exp x ≤ Real.exp (x + 1) := by
    apply Real.exp_le_exp_of_le
    exact h
  have h_add : x + 1 ≤ x + 1 + (0 : ℝ) := by
    apply le_add_right
    exact zero_le_one
  have h_exp_add : Real.exp (x + 1) ≤ Real.exp (x + 1) := by
    apply Real.exp_le_exp_of_le
    exact h_add
  exact h_exp_sum ▸ h_exp_add