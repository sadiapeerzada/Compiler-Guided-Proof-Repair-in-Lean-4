theorem hockey_stick_binomial_identity (n : ℕ) : (∑ k ∈ Finset.range (n + 1), Nat.choose (4 + k) k) = Nat.choose (5 + n) n
:= by
  induction n with n IH
  · simp [Finset.range_zero, Nat.choose]
  · simp [Finset.range_succ, Nat.choose_add_right, Nat.choose_add_left]
    have := IH n
    rw [Finset.sum_range_add_one, Nat.choose_add_right, Nat.choose_add_left]
    refl