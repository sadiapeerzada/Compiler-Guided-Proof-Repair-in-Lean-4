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
        rw [mul_add, add_assoc] at h4 
        exact lt_of_lt_of_le h4 (add_lt_add_right (by norm_num) (by norm_num))
      exact absurd h5 (lt_irrefl p (by norm_num))