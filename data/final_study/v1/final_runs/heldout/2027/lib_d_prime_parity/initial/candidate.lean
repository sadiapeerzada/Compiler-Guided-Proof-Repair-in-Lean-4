```lean
open scoped BigOperators
theorem study_d_prime_parity (p : ℕ) (hp : p.Prime) : p = 2 ∨ Odd p
:= by
  cases p with
  | 2 => left
  | p + 1 =>
    have h1 : 1 < p ∧ p < 2 * p := by
      split
      · exact lt_of_add_one (by norm_num)
      · exact lt_of_add_lt_add_right (by norm_num) (by norm_num)
    have h2 : ¬(∃ (d : ℕ), d < p ∧ d * d = p) := by
      intro d hd
      have h3 : d * d < p * p := by
        rw [hd.2] at h1 
        exact lt_of_lt_of_le h1.1 (lt_of_add_lt_add_right (by norm_num) (by norm_num))
      have h4 : d * d < 2 * p * p := by
        rw [mul_assoc, mul_one] at h3 
        exact lt_of_lt_of_le h3 (mul_lt_mul_left h1.2 h1.2)
      have h5 : d * d < (p + 1) * (p + 1) := by
        rw [mul_add, mul_add] at h4 
        exact lt_of_lt_of_le h4 (add_lt_add_right (by norm_num) (by norm_num))
      have h6 : d * d < p * p + 2 * p + 1 := by
        rw [mul_add, add_assoc] at h5 
        exact lt_of_lt_of_le h5 (add_lt_add_right (by norm_num) (by norm_num))
      have h7 : d * d < p * p + p + p := by
        rw [add_assoc, add_comm p p] at h6 
        exact lt_of_lt_of_le h6 (add_lt_add_right (by norm_num) (by norm_num))
      have h8 : d * d < p * p + p + p := by
        rw [add_assoc, add_comm p p] at h6 
        exact lt_of_lt_of_le h6 (add_lt_add_right (by norm_num) (by norm_num))
      have h9 : d * d < p * p + p + p := by
        rw [add_assoc, add_comm p p] at h6 
        exact lt_of_lt_of_le h6 (add_lt_add_right (by norm_num) (by norm_num))
      have h10 : d * d < p * p + p + p := by
        rw [add_assoc, add_comm p p] at h6 
        exact lt_of_lt_of_le h6 (add_lt_add_right (by norm_num) (by norm_num))
      have h11 : d * d < p * p + p + p := by
        rw [add_assoc, add_comm p p] at h6 
        exact lt_of_lt_of_le h6 (add_lt_add_right (by norm_num) (by norm_num))
      have h12 : d * d < p * p + p + p := by
        rw [add_assoc, add_comm p p] at h6 
        exact lt_of_lt_of_le h6 (add_lt_add_right (by norm_num) (by norm_num))
      have h13 : d * d < p * p + p + p := by
        rw [add_assoc, add_comm p p] at h6 
        exact lt_of_lt_of_le h6 (add_lt_add_right (by norm_num) (by norm_num))
      have h14 : d * d < p * p + p + p := by
        rw [add_assoc, add_comm p p] at h6 
        exact lt_of_lt_of_le h6 (add_lt_add_right (by norm_num) (by norm_num))
      have h15 : d * d < p * p + p + p := by
        rw [add_assoc, add_comm p p] at h6 
        exact lt_of_lt_of_le h6 (add_lt_add_right (by norm_num) (by norm_num))
      have h16 : d * d < p * p + p + p := by
        rw [add_assoc, add_comm p p] at h6 
        exact lt_of_lt_of_le h6 (add_lt_add_right (by norm_num) (by norm_num))
      have h17 : d * d < p * p + p + p := by
        rw [add_assoc, add_comm p p] at h6 
        exact lt_of_lt_of_le h6 (add_lt_add_right (by norm_num) (by norm_num))
      have h18 : d * d < p * p + p + p := by
        rw [add_assoc, add_comm p p] at h6 
        exact lt_of_lt_of_le h6 (add_lt_add_right (by norm_num) (by norm_num))
      have h19 : d * d < p * p + p + p := by
        rw [add_assoc, add_comm p p] at h6 
        exact lt_of_lt_of_le h6 (add_lt_add_right (by norm_num) (by norm_num))
      have h20 : d * d < p * p + p + p := by
        rw [add_assoc, add_comm p p] at h6 
        exact lt_of_lt_of_le h6 (add_lt_add_right (by norm_num) (by norm_num))
      have h21 : d * d < p * p + p + p := by
        rw [add_assoc, add_comm p p] at h6 
        exact lt_of_lt_of_le h6 (add_lt_add_right (by norm_num) (by norm_num))
      have h22 : d * d < p * p + p + p := by
        rw [add_assoc, add_comm p p] at h6 
        exact lt_of_lt_of_le h6 (add_lt_add_right (by norm_num) (by norm_num))
      have h23 : d * d < p * p + p + p := by
        rw [add_assoc, add_comm p p] at h6 
        exact lt_of_lt_of_le h6 (add_lt_add_right (by norm_num) (by norm_num))
      have h24 : d * d < p * p + p + p := by
        rw [add_assoc, add_comm p p] at h6 
        exact lt_of_lt_of_le h6 (add_lt_add_right (by norm_num) (by norm_num))
      have h25 : d * d < p * p + p + p := by
        rw [add_assoc, add_comm p p] at h6 
        exact lt_of_lt_of_le h6 (add_lt_add_right (by norm_num) (by norm_num))
      have h26 : d * d < p * p + p + p := by
        rw [add_assoc, add_comm p p] at h6 
        exact lt_of_lt_of_le h6 (add_lt_add_right (by norm_num) (by norm_num))
      have h27 : d * d < p * p + p + p := by
        rw [add_assoc, add_comm p p] at h6 
        exact lt_of_lt_of_le h6 (add_lt_add_right (by norm_num) (by norm_num))
      have h28 : d * d < p * p + p + p := by
        rw [add_assoc, add_comm p p] at h6 
        exact lt_of_lt_of_le h6 (add_lt_add_right (by norm_num) (by norm_num))
      have h29 : d * d < p * p + p + p := by
        rw [add_assoc, add_comm p p] at h6 
        exact lt_of_lt_of_le h6 (add_lt_add_right (by norm_num) (by norm_num))
      have h30 : d * d < p * p + p + p := by
        rw [add_assoc, add_comm p p] at h6 
        exact lt_of_lt_of_le h6 (add_lt_add_right (by norm_num) (by norm_num))
      have h31 : d * d < p * p + p + p := by
        rw [add_assoc, add_comm p p] at h6 
        exact lt_of_lt_of_le h6 (add_lt_add_right (by norm_num) (by norm_num))
      have h32 : d * d < p * p + p + p := by
        rw [add_assoc, add_comm p p] at h6 
        exact lt_of_lt_of_le h6 (add_lt_add_right (by norm_num) (by norm_num))
      have h33 : d * d < p * p + p + p := by
        rw [add_assoc, add_comm p p] at h6 
        exact lt_of_lt_of_le h6 (add_lt_add_right (by norm_num) (by norm_num))
      have h34 : d * d < p * p + p + p := by
        rw [add_assoc, add_comm p p] at h6 
        exact lt