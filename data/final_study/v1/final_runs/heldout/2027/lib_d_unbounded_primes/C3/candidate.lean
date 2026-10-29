open scoped BigOperators
theorem study_d_unbounded_primes (n : ℕ) : ∃ p : ℕ, n ≤ p ∧ p.Prime
:= by
  have : ∃ p, p > n := Nat.prime.exists_prime_gt n
  then obtain p where h : p > n := this.elim
  have : p.Prime := Nat.prime.exists_prime_gt.1 (Nat.prime.exists_prime_gt n)
  exact ⟨p, h, this⟩