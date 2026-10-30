open scoped BigOperators
theorem study_d_frobenius (m n a b : ℕ) (h : Nat.Coprime m n) (ha : a ≠ 0) (hb : b ≠ 0) : m * a + n * b ≠ m * n
:= by
  intro contra
  have h1 : m * a + n * b = m * n := contra
  have h2 : m * a = m * n - n * b := by
    rw [h1]
  have h3 : m * (a - n) = 0 := by
    rw [h2, sub_self, h1]
  have h4 : a - n = 0 := by
    rw [h3]
  have h5 : a = n := by
    rw [h4]
  have h6 : ¬ Nat.Coprime m n := by
    intro
    exact h5
  exact h6 h