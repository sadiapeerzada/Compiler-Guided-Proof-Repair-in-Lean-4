open scoped BigOperators
theorem study_i_alternating_binomial (n : ℕ) (hn : n ≠ 0) : (∑ k ∈ Finset.range (n + 1), ((-1 : ℤ) ^ k * (n.choose k : ℤ))) = 0
:= by
  have h : ∀ k : ℕ, k ≤ n → (-1 : ℤ) ^ k * (n.choose k : ℤ) = (-1 : ℤ) ^ (n - k) * (n.choose (n - k) : ℤ) := by
    intro k hk
    rw [Nat.choose_symm, Nat.choose_symm]
    simp [Nat.choose_symm]
  have h_sum : ∑ k ∈ Finset.range (n + 1), ((-1 : ℤ) ^ k * (n.choose k : ℤ)) = ∑ k ∈ Finset.range (n + 1), ((-1 : ℤ) ^ (n - k) * (n.choose (n - k) : ℤ)) := by
    rw [h]
    simp [Finset.range_comm]
  have h_even : ∀ k : ℕ, k ≤ n → k % 2 = 0 → (-1 : ℤ) ^ k = 1 := by
    intro k hk h
    rw [Nat.mod_eq_zero_of_even, Nat.pow_two_eq_one]
  have h_odd : ∀ k : ℕ, k ≤ n → k % 2 = 1 → (-1 : ℤ) ^ k = -1 := by
    intro k hk h
    rw [Nat.mod_eq_one_of_odd, Nat.pow_two_eq_neg_one]
  have h_pair : ∀ k : ℕ, k ≤ n → ∃ k1 k2 : ℕ, k = k1 + k2 ∧ k1 < k ∧ k2 < k := by
    intro k hk
    use k / 2, k % 2
    simp [Nat.div_add_mod_eq, Nat.mul_mod_eq_zero, Nat.mod_add_div_eq]
  have h_pair_sum : ∑ k ∈ Finset.range (n + 1), ((-1 : ℤ) ^ k * (n.choose k : ℤ)) = ∑ k1 k2 : ℕ, k1 + k2 < n + 1, ((-1 : ℤ) ^ (k1 + k2) * (n.choose (k1 + k2) : ℤ)) := by
    simp [Finset.range_add, h_sum, h, h_even, h_odd, h_pair]
  have h_pair_sum_even : ∑ k1 k2 : ℕ, k1 + k2 < n + 1, ((-1 : ℤ) ^ (k1 + k2) * (n.choose (k1 + k2) : ℤ)) = 0 := by
    simp [Finset.sum_eq_zero_of_even, h_even, h_odd]
  exact h_pair_sum_even