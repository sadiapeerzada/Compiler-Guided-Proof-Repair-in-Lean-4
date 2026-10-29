open scoped BigOperators
theorem study_i_stirling (n k : ℕ) : Nat.stirlingSecond (n + 1) (k + 1) = (k + 1) * Nat.stirlingSecond n (k + 1) + Nat.stirlingSecond n k
:= by
  induction n with i ih
  · simp [Nat.stirlingSecond]
  · simp [ih, Nat.stirlingSecond]