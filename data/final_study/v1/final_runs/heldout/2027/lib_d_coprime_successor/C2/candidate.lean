open scoped BigOperators
theorem study_d_coprime_successor (n : ℕ) : Nat.Coprime n (n + 1) := by
  have h1 : Nat.gcd n (n + 1) = 1 := by
    rw [Nat.gcd_add_one]
  exact h1