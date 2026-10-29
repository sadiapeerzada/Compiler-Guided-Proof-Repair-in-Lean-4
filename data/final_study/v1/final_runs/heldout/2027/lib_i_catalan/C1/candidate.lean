open scoped BigOperators

theorem study_i_catalan (n : ℕ) : catalan (n + 1) = ∑ i : Fin (n + 1), catalan i * catalan (n - i) := by
  induction' n with n ih
  · simp [catalan, Fin.cases_on, catalan_zero, zero_add, zero_mul, add_zero]
  · have : ∑ i : Fin (n + 2), catalan i * catalan (n - i + 1) = ∑ i : Fin (n + 1), catalan i * catalan (n - i) + catalan (n + 1) * catalan 0 := by
      simp [catalan, Fin.cases_on, add_assoc, add_comm, add_zero, zero_add, zero_mul, zero_add, Fin.cases_on, catalan_succ]
    rw [ih, this]
    simp [catalan, Fin.cases_on, add_assoc, add_comm, add_zero, zero_add, zero_mul, zero_add, Fin.cases_on, catalan_succ]