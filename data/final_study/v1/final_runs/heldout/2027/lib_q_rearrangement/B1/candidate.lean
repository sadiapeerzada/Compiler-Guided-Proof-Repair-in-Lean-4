open scoped BigOperators
theorem study_q_rearrangement (a b c d : ℝ) (hab : a ≤ b) (hcd : c ≤ d) : a * d + b * c ≤ a * c + b * d
:= by
  have h1 : a * d - a * c ≤ b * d - b * c := by
    rw [sub_mul, sub_mul] at hab hcd 
    exact le_add_of_pos_left (le_sub_of_le_of_le hab hcd)
  have h2 : a * d - a * c = a * (d - c) := by ring
  have h3 : b * d - b * c = b * (d - c) := by ring
  rw [h2, h3] at h1 
  exact le_add_of_pos_left h1