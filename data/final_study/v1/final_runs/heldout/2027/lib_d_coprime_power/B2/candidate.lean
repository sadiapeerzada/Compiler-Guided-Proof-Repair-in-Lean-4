open scoped BigOperators
theorem study_d_coprime_power (a b n : ℕ) (hn : 0 < n) : Nat.Coprime (a ^ n) b ↔ Nat.Coprime a b
:= by
  split
  intro h
  induction' a with a ha generalizing b
  · exact Nat.coprime_zero _
  · have h1 : a ^ n = a * (a ^ (n - 1)) := by rw [Nat.mul_one, Nat.pow_add_one]
    have h2 : Nat.Coprime (a * (a ^ (n - 1))) b ↔ Nat.Coprime a b := by
      rw [Nat.coprime_mul_left ha, Nat.coprime_one]
    have h3 : Nat.Coprime (a ^ (n - 1)) b := by
      have h4 : 0 < n - 1 := by linarith [hn]
      exact h.trans (Nat.coprime_pow h3 h4)
    exact h2.mp h3
  intro h
  induction' a with a ha generalizing b
  · exact Nat.coprime_zero _
  · have h1 : a ^ n = a * (a ^ (n - 1)) := by rw [Nat.mul_one, Nat.pow_add_one]
    have h2 : Nat.Coprime (a * (a ^ (n - 1))) b ↔ Nat.Coprime a b := by
      rw [Nat.coprime_mul_left ha, Nat.coprime_one]
    have h3 : Nat.Coprime (a ^ (n - 1)) b := by
      have h4 : 0 < n - 1 := by linarith [hn]
      exact h.trans (Nat.coprime_pow h3 h4)
    exact h2.mpr h3