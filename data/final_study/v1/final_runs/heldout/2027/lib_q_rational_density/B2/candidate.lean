open scoped BigOperators
theorem study_q_rational_density (x y : ℝ) (h : x < y) : ∃ q : ℚ, x < q ∧ (q : ℝ) < y
:= by
  obtain ⟨n, d, q⟩ := classical.rational_between (x : ℝ) (y : ℝ) h
  use q
  split
  - exact h
  - exact lt_of_le_of_lt (le_of_lt_of_eq (eq_of_le_of_lt h)) (lt_of_pos_of_ne_zero (by norm_num) (by norm_num))