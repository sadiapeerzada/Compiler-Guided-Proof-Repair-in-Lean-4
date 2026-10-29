open scoped BigOperators

theorem study_d_prime_factor_exists (n : ℕ) (hn : 2 ≤ n) : ∃ p : ℕ, p.Prime ∧ p ∣ n
:= by
  have h1 : ∃ p : ℕ, p ≤ n ∧ p > 1 ∧ ∃ d : ℕ, p = d * d ∨ (∃ d : ℕ, d < p ∧ p = d * d) := by
    apply exists.intro
    exact n
    split
    · exact hn
    · exact ⟨n, by rw [one_mul]; exact nat.prime.nat_of_prime n⟩
  obtain ⟨p, hp1, hp2, hp3⟩ := h1
  have hp4 : p.Prime := by
    rw [hp2]
    exact nat.prime_of_dvd_of_pos hp3
  obtain ⟨d, hd⟩ := hp3
  have hp5 : p ∣ n := by
    by_cases h : p = d
    · rw [h]
      exact dvd_refl n
    · obtain ⟨d', hd'⟩ := hd
      have hd'p : d' < p := by
        exact lt_of_mul_lt_mul_of_pos hd' (lt_of_le_of_ne (by rw [h]; exact ne_of_gt hp1.2))
      have hp5' : p ∣ d' * d' := by
        exact dvd_mul_of_dvd_left hd'
      exact hp5' ▸ hd
  exact ⟨p, hp4, hp5⟩