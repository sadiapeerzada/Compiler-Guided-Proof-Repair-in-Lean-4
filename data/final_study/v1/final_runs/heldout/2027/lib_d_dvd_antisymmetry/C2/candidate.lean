open scoped BigOperators
theorem study_d_dvd_antisymmetry (a b : ℕ) (hab : a ∣ b) (hba : b ∣ a) : a = b
:= by
  have h1 : ∃ k : ℕ, b = a * k := hab
  have h2 : ∃ k : ℕ, a = b * k := hba
  obtain ⟨k1, hk1⟩ := h1
  obtain ⟨k2, hk2⟩ := h2
  have h3 : a * k1 = b := by rw [hk1]
  have h4 : b * k2 = a := by rw [hk2]
  have h5 : a * k1 * k2 = a := by rw [h4, h3]
  have h6 : k1 * k2 = 1 := by
    rw [h5]
    exact nat.mul_right_cancel' a
  have h7 : k1 = 1 := by
    rw [h6]
    exact nat.one_mul k2
  have h8 : k2 = 1 := by
    rw [h6]
    exact nat.mul_left_cancel' b
  rw [h7, h8]
  exact h1.1