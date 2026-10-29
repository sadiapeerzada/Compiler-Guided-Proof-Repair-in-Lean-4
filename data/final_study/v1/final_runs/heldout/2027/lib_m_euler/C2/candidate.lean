open scoped BigOperators
theorem study_m_euler (a m : ℕ) (h : Nat.Coprime a m) : Nat.ModEq m (a ^ Nat.totient m) 1
:= by
  have h1 : a ^ Nat.totient m % m = 1 := by
    classical
    have h2 : a ^ Nat.totient m = a ^ (m - (m / (gcd a m))) := by
      rw [Nat.totient, Nat.gcd_eq_one_of_coprime h, Nat.mul_comm, Nat.mul_one]
    have h3 : a ^ (m - (m / (gcd a m))) % m = 1 := by
      rw [h2]
      have h4 : a ^ (m / (gcd a m)) % m = 1 := by
        have h5 : gcd a m = 1 := by
          rw [h]
        exact Nat.coprime_pow h5 (m / (gcd a m))
      exact Nat.mul_mod_eq_mul_mod h4 (Nat.one_dvd m)
    exact h3
  exact h1