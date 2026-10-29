open scoped BigOperators
theorem study_m_canonical (m a b : ℕ) (ha : a < m) (hb : b < m) (h : Nat.ModEq m a b) : a = b
:= by
  have h1 : a % m = b % m := h
  have h2 : a - a % m = b - b % m := by
    rw [Nat.sub_mod_eq_sub_of_lt_m ha, Nat.sub_mod_eq_sub_of_lt_m hb]
  have h3 : a - b = (a % m) - (b % m) := by
    rw [h2, h1]
  have h4 : a - b = 0 := by
    rw [Nat.sub_self, h3]
  exact h4