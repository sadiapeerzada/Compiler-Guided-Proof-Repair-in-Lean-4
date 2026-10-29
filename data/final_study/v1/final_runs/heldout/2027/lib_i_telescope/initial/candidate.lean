open scoped BigOperators
theorem study_i_telescope (f : ℕ → ℤ) (n : ℕ) : (∑ i ∈ Finset.range n, (f (i + 1) - f i)) = f n - f 0
:= by
  induction n with n IH
  · simp [Finset.range_zero]
  · simp [Finset.range_succ, IH, add_sub_add_right]