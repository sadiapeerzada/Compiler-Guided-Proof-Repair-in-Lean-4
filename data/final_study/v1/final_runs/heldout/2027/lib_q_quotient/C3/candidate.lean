open scoped BigOperators
theorem study_q_quotient (m n : ℕ) : m / n ≤ m := by
  match n with
  | 0 => exact le_refl m
  | n + 1 => 
    have h1 : m / (n + 1) ≤ m := by
      apply le_of_add_le_add_right
      exact le_of_lt (lt_of_le_of_ne (le_of_ge (by linarith)) (ne_of_gt zero_pos))
    exact h1