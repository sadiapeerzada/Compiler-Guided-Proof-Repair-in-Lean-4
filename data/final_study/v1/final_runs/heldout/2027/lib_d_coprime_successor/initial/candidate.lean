open scoped BigOperators
theorem study_d_coprime_successor (n : ℕ) : Nat.Coprime n (n + 1) := by
  have h1 : n * 0 = 0 := by
    rw [Nat.zero_mul]
  have h2 : (n + 1) * 0 = 0 := by
    rw [Nat.zero_mul]
  have h3 : Nat.gcd n (n + 1) = 1 := by
    rw [Nat.gcd_eq_gcd_add_one]
    exact h1
  exact h3