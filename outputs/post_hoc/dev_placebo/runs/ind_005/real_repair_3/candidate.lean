theorem pascal_row_sum (n : ℕ) : ∑ k ∈ Finset.range (n + 1), Nat.choose n k = 2 ^ n
:= by
  induction n with
  | zero =>
    simp [Finset.range, Nat.choose]
  | succ n ih =>
    have : ∑ k ∈ Finset.range (n + 2), Nat.choose (n + 1) k = 2 ^ (n + 1) := by
      rw [Finset.sum_range_succ]
      exact ih
    rw [this, add_comm, two_pow_succ, add_assoc, ih, add_zero]
    simp [Finset.range, Nat.choose]