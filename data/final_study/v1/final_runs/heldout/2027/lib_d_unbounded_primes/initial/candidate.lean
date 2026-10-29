open scoped BigOperators
theorem study_d_unbounded_primes (n : ℕ) : ∃ p : ℕ, n ≤ p ∧ p.Prime
:= by
  have : ∃ p : ℕ, p > n := by
    apply exists.elim (Nat.prime.exists_prime_gt)
    exact (Nat.prime.next_prime n).exists
  then obtain p where p_def : p > n := this.elim
  have p_prime : p.Prime := by
    apply Nat.prime.next_prime.prime
    exact p_def
  exact ⟨p, p_def, p_prime⟩