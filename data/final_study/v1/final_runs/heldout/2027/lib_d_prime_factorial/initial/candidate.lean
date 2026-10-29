open scoped BigOperators

theorem study_d_prime_factorial (p n : ℕ) (hp : p.Prime) : p ∣ n.factorial ↔ p ≤ n
:= by
  split
  · intro h
    have h1 : ∃ k ≤ n, n.factorial = p * k := h
    obtain ⟨k, hk, hk'⟩ := h1
    exact le_of_exists (λ i, by
      cases i with
      | zero =>
        have : n.factorial = 0 := by
          rw [factorial_zero]
          exact hk'
        contradiction
      | succ i =>
        have : p ∣ (i + 1) := by
          rw [factorial_succ]
          exact h
        obtain ⟨j, hj, hj'⟩ := this
        exact le_of_exists (λ i, by
          have : (i + 1) * (i + 1) = (i + 1) * (i + 1) := by
            rw [mul_comm, mul_one]
          have : (i + 1) * (i + 1) = (i + 1) * (i + 1) := by
            rw [hj']
          exact hj'
        )
    )
  · intro h
    have : p ≤ n := h
    exact le_of_exists (λ i, by
      cases i with
      | zero =>
        have : n.factorial = 0 := by
          rw [factorial_zero]
          exact h
        contradiction
      | succ i =>
        have : p ∣ (i + 1) := by
          rw [factorial_succ]
          exact h
        obtain ⟨j, hj, hj'⟩ := this
        exact le_of_exists (λ i, by
          have : (i + 1) * (i + 1) = (i + 1) * (i + 1) := by
            rw [mul_comm, mul_one]
          have : (i + 1) * (i + 1) = (i + 1) * (i + 1) := by
            rw [hj']
          exact hj'
        )
    )