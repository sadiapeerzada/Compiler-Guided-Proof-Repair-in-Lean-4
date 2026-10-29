theorem positive_nat_sum_distinct_powers_two (n : ℕ) (hn : 1 ≤ n) : ∃ s : Finset ℕ, n = ∑ k ∈ s, 2 ^ k
:= by
  have h1 : 0 < n := by exact lt_of_le_of_ne hn (ne_of_eq_of_gt zero_ne_one)
  have h2 : ∃ s : Finset ℕ, n = ∑ k ∈ s, 2 ^ k := by
    classical
    induction n with n ih
    · have h3 : 1 = ∑ k ∈ Finset.empty, 2 ^ k := by simp
      exact ⟨Finset.empty, h3⟩
    · have h4 : 2 * n = ∑ k ∈ Finset.of_list [0], 2 ^ k + ∑ k ∈ ih.1, 2 ^ k := by
        simp [Finset.sum_insert, ih]
      have h5 : 2 * n = ∑ k ∈ Finset.of_list [0] ∪ ih.1, 2 ^ k := by
        simp [Finset.sum_union_of_disjoint (Finset.disjoint_of_ne (Finset.mem_singleton 0))]
      have h6 : n = ∑ k ∈ ih.1, 2 ^ k := by
        rw [ih.2, h5]
      have h7 : ∃ s : Finset ℕ, n = ∑ k ∈ s, 2 ^ k := by
        exact ⟨Finset.of_list ih.1, h6⟩
      exact h7
  exact h2