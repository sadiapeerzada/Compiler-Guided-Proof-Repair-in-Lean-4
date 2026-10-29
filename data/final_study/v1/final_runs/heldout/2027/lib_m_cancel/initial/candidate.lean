open scoped BigOperators
theorem study_m_cancel (m c a b : ℕ) (hm : 0 < m) (h : Nat.ModEq m (c * a) (c * b)) : Nat.ModEq (m / Nat.gcd m c) a b
:= by
  let g := Nat.gcd m c
  have h1 : m = (m / g) * g := by rw [Nat.gcd_eq_gcd_mul]
  have h2 : c * a % m = c * b % m := by rw [h]
  have h3 : c * a % (m / g) = c * b % (m / g) := by
    rw [h1, Nat.mod_div_eq_mod]
  have h4 : c * (a % (m / g)) = c * (b % (m / g)) := by
    rw [Nat.mod_eq_mod_add_mul_of_div_eq, h3]
  have h5 : a % (m / g) = b % (m / g) := by
    rw [Nat.mul_right_cancel h4, Nat.gcd_pos_of_pos hm, Nat.gcd_eq_gcd_mul]
  exact Nat.mod_eq_mod_of_div_eq h5