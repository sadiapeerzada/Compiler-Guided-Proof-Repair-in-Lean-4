open scoped BigOperators

theorem study_d_prime_factor_exists (n : ℕ) (hn : 2 ≤ n) : ∃ p : ℕ, p.Prime ∧ p ∣ n
:= by
  have h1 : ∃ p : ℕ, p ≤ n ∧ p > 1 := by
    apply exists.intro
    exact n
    split
    · exact hn
    · exact ⟨2, by rw [two_mul]; exact nat.prime.two_is_prime⟩
  obtain ⟨p, hp1, hp2⟩ := h1
  have hp4 : p.Prime := by
    exact hp2
  have hp5 : p ∣ n := by
    apply nat.dvd_of_le
    exact hp1
  exact ⟨p, hp4, hp5⟩