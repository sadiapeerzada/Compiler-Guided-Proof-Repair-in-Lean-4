theorem add_three_lt_add_seven (n : ℕ) : n + 3 < n + 7 :=
by
  have h : 3 < 7 := lt_of_add_pos (by simp)
  exact add_lt_add_right h n