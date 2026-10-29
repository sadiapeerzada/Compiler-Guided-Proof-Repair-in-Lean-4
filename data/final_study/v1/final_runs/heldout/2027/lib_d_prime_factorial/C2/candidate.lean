open scoped BigOperators

theorem study_d_prime_factorial (p n : ℕ) (hp : p.Prime) : p ∣ n.factorial ↔ p ≤ n
:= by
  split
  · intro h
    obtain ⟨k, hk, hk'⟩ := h
    have : p ≤ n := by
      have : k ≤ n := by
        rw [hk]
        exact le_of_not_gt (λ hkn, by
          have : n.factorial = 0 := by
            rw [factorial_of_not_le hp hkn]
            exact hk'
          contradiction
        )
    exact this
  · intro h
    have : p ≤ n := h
    exact le_of_not_gt (λ hnp, by
      have : p ∣ n.factorial := by
        rw [factorial_of_le hnp]
        exact h
      obtain ⟨k, hk, hk'⟩ := this
      have : n ≤ k := by
        rw [hk]
        exact le_of_not_gt (λ hkn, by
          have : n.factorial = 0 := by
            rw [factorial_of_not_le hp hkn]
            exact hk'
          contradiction
        )
      contradiction
    )