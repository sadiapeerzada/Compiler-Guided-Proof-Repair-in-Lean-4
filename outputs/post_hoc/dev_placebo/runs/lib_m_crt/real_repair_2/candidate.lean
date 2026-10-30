open scoped BigOperators
theorem study_m_crt (a b n m : ℕ) (h : Nat.ModEq (Nat.gcd n m) a b) : ∃ k : ℕ, Nat.ModEq n k a ∧ Nat.ModEq m k b
:= by
  let ⟨c, h1⟩ := h
  have h2 : ∃ k : ℤ, a = k * n + c := by
    use [c / n, by rw [Nat.div_mod_eq, h1, Nat.mul_add]]; norm_num
  have h3 : ∃ k : ℤ, b = k * m + c := by
    use [c / m, by rw [Nat.div_mod_eq, h1, Nat.mul_add]]; norm_num
  obtain ⟨k1, h4⟩ := h2
  obtain ⟨k2, h5⟩ := h3
  have h6 : k1 * n + c = k2 * m + c := by
    rw [h4, h5]
  have h7 : k1 * n = k2 * m := by
    rw [h6, Nat.add_left_cancel h5]
  have h8 : ∃ k : ℤ, k1 = k * (m / (Nat.gcd n m)) := by
    use [k1 / (m / (Nat.gcd n m)), by rw [Nat.div_mul_eq_div_gcd, h7, Nat.gcd_eq_gcd]]
  obtain ⟨k3, h9⟩ := h8
  have h10 : k3 * (m / (Nat.gcd n m)) * n = k1 * n := by
    rw [h9, Nat.mul_assoc, h7]
  have h11 : k3 * (m / (Nat.gcd n m)) = k1 := by
    rw [h10, Nat.mul_left_cancel h1]
  have h12 : ∃ k : ℕ, k3 * (m / (Nat.gcd n m)) = k1 := by
    use [k3]; rw [h11]
  obtain ⟨k, h13⟩ := h12
  exact ⟨k, by rw [h4, h5, h10, h11, h13]⟩