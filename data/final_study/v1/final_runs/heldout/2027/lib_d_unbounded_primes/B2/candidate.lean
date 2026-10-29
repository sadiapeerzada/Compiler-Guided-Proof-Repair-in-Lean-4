open scoped BigOperators
theorem study_d_unbounded_primes (n : ℕ) : ∃ p : ℕ, n ≤ p ∧ p.Prime
:= by
  have : ∃ p : ℕ, p > n := Nat.prime.exists_prime_gt n
  then obtain p where h : p > n := this.elim
  have h_prime : p.Prime := Nat.prime.next_prime.prime h
  exact ⟨p, h, h_prime⟩