open scoped BigOperators

theorem study_d_prime_factor_exists (n : ℕ) (hn : 2 ≤ n) : ∃ p : ℕ, p.Prime ∧ p ∣ n
:= by
  have h1 : ∃ p : ℕ, p ≤ n ∧ p > 1 := by
    apply exists.intro n
    split
    · exact hn
    · exact ⟨n, by rw [one_mul]; exact nat.prime.nat_of_prime n⟩
  obtain ⟨p, hp1, hp2⟩ := h1
  have hp3 : p.Prime := by
    rw [hp2]
    exact nat.prime_of_dvd_of_pos hp1
  have hp4 : p ∣ n := by
    use p
    exact hp1
  exact ⟨p, hp3, hp4⟩