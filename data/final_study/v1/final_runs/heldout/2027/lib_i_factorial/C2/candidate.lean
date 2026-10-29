open scoped BigOperators
theorem study_i_factorial (n : ℕ) : (n + 1).factorial = (n + 1) * n.factorial := by
  simp [factorial_def]