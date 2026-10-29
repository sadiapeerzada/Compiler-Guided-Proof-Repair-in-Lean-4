open scoped BigOperators
theorem study_q_rearrangement (a b c d : ℝ) (hab : a ≤ b) (hcd : c ≤ d) : a * d + b * c ≤ a * c + b * d
:= by
  have h1 : a * d - a * c ≤ b * d - b * c := by
    rw [sub_eq_add_neg, sub_eq_add_neg] at hab hcd 
    exact le_add_of_pos_left (le_sub_of_le_of_le hab hcd)
  have h2 : a * d - a * c = a * (d - c) := by ring
  have h3 : b * d - b * c = b * (d - c) := by ring
  rw [h2, h3] at h1 
  have h4 : a * (d - c) ≤ b * (d - c) := by
    rw [h1]
    exact le_of_add_le_add_left hcd
  have h5 : a * c + b * d ≤ a * c + b * c + b * (d - c) := by
    rw [add_assoc, h4, add_comm b (b * (d - c))]
  exact le_add_of_pos_left (le_sub_of_le_of_le h5 hcd)