open scoped BigOperators

theorem study_d_totient_sum (n : ℕ) : (∑ d ∈ n.divisors, Nat.totient d) = n
:= by
  induction' n with a ha
  · simp [Nat.divisors_zero, Nat.totient_zero]
  · have h := study_d_totient_sum a
    rw h
    simp [Nat.divisors_pos, Nat.divisors_eq_divisors_of_pos ha, Nat.totient_add]