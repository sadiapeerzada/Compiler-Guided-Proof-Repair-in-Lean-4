theorem add_three_lt_add_seven (n : ℕ) : n + 3 < n + 7 := by
  have h : 3 < 7 := by
    exact lt_of_add_lt_add_right (by
      rw [add_assoc] at this
      exact this
    )
  exact add_lt_add_right h n