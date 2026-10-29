open scoped BigOperators
theorem study_m_power (a b m : ℤ) (n : ℕ) (h : Int.ModEq m a b) : Int.ModEq m (a ^ n) (b ^ n) :=
by
  have h1 : a % m = b % m := h
  have h2 : (a % m) ^ n = (b % m) ^ n := by
    induction n with n ih
    · rw [Nat.zero_power, Int.zero_mod, Int.zero_pow]
    · rw [Nat.succ_power, Int.mod_add_div_self, ih, Int.mod_pow]
  rw [h1, h2]