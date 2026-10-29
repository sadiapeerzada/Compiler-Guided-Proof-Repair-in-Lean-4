open scoped BigOperators
theorem study_d_unbounded_primes (n : ℕ) : ∃ p : ℕ, n ≤ p ∧ p.Prime
:= by
  have : ∃ p, p > n := Nat.prime.exists_prime_gt n
  then obtain p where p_def : p > n := this.elim
  have p_prime : p.Prime := Nat.prime.next_prime p
  exact ⟨p, p_def, p_prime⟩