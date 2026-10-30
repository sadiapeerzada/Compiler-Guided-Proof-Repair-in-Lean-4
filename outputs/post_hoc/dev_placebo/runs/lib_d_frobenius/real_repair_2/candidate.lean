open scoped BigOperators

theorem study_d_frobenius (m n a b : ℕ) (h : Nat.Coprime m n) (ha : a ≠ 0) (hb : b ≠ 0) : m * a + n * b ≠ m * n
:= by
  intro contra
  have h1 : m * a + n * b = m * n := contra
  have h2 : m * a = m * n - n * b := by
    rw [h1]
  have h3 : m * (a - n) = 0 := by
    rw [h2, sub_add_cancel]
  have h4 : a - n = 0 := by
    rw [h3] at h3
    exact Nat.mul_left_inj.1 h (by rw [h4])
  have h5 : a = n := by
    rw [h4]
  have h6 : b = 0 := by
    rw [h5, h1] at h1
    exact Nat.mul_right_inj.1 h (by rw [h1])
  exact h6