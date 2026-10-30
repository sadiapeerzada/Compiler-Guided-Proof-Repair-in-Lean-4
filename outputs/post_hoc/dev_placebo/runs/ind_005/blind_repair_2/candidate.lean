theorem pascal_row_sum (n : ℕ) : ∑ k ∈ Finset.range (n + 1), Nat.choose n k = 2 ^ n
:= by
  induction n with
  | zero =>
    simp [Finset.range, Nat.choose, two_pow_zero]
  | succ n ih =>
    have : ∑ k ∈ Finset.range (succ n + 1), Nat.choose (succ n) k = 2 ^ (succ n) := ih
    have : ∑ k ∈ Finset.range (succ n + 1), Nat.choose (succ n) k = ∑ k ∈ Finset.range (succ n), Nat.choose (succ n) k + Nat.choose (succ n) (succ n) := by
      rw [Finset.sum_range_succ]
    rw [this, add_comm, two_pow_succ, add_assoc, ih, add_zero]
    simp [Finset.range, Nat.choose]