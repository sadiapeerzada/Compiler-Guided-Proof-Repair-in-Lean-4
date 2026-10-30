open scoped BigOperators

theorem study_i_vandermonde (m n k : ℕ) : (m + n).choose k = ∑ i ∈ Finset.range (k + 1), m.choose i * n.choose (k - i) :=
by
  induction k generalizing m n with
  | zero =>
    have : (m + n).choose 0 = 1 ∧ ∑ i ∈ Finset.range 1, m.choose i * n.choose (0 - i) = 1 := by
      split
      · exact choose_zero_right
      · simp [Finset.range_one, zero_sub]
    exact this
  | succ k ih =>
    have : (m + n).choose (succ k) = ∑ i ∈ Finset.range (succ k + 1), m.choose i * n.choose (succ k - i) := by
      simp [choose_add_left, Finset.range_add_one, ih]
    exact this