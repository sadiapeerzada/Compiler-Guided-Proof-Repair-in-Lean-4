open scoped BigOperators
theorem study_a_truncated_sub (a b : ℕ) (h : b ≤ a) : a - b + b = a := by
  rw [add_assoc]
  rfl