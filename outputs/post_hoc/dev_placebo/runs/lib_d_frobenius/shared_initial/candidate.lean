open scoped BigOperators
theorem study_d_frobenius (m n a b : ℕ) (h : Nat.Coprime m n) (ha : a ≠ 0) (hb : b ≠ 0) : m * a + n * b ≠ m * n
:= by
  intro contra
  have h1 : m * a + n * b = m * n := contra
  have h2 : m * a = m * n - n * b := by
    rw [h1]
  have h3 : m * (a - n) = m * n * (1 - 1) := by
    rw [h2, sub_self]
  have h4 : m * (a - n) = 0 := by
    rw [h3]
  have h5 : a - n = 0 := by
    rw [h4] at h3
    exact Nat.mul_left_inj.mpr ha
  have h6 : a = n := by
    rw [h5]
  have h7 : Nat.Coprime m n → ¬ Nat.Coprime m n := by
    intro
    exact h5
  have h8 : m * 0 + n * 0 = m * n := by
    rw [mul_zero, add_zero, mul_zero]
  have h9 : ¬ (m * 0 + n * 0 = m * n) := by
    exact h8
  have h10 : b ≠ 0 := by
    exact hb
  have h11 : m * a + n * b = m * n → m * 0 + n * 0 = m * n := by
    intro
    exact h9
  have h12 : m * a + n * b = m * n → a = n ∧ b = 0 := by
    intro
    exact h7
  have h13 : m * a + n * b = m * n → ¬ (a ≠ 0 ∧ b ≠ 0) := by
    intro
    exact h12
  have h14 : ¬ (a ≠ 0 ∧ b ≠ 0) := by
    exact h13 contra
  exact h14