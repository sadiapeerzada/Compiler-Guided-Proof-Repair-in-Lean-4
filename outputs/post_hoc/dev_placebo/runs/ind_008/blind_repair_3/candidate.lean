theorem positive_nat_sum_distinct_powers_two (n : ℕ) (hn : 1 ≤ n) : ∃ s : Finset ℕ, n = ∑ k ∈ s, 2 ^ k
:= by
  have h1 : 0 < n := by { from lt_of_le_of_ne hn (ne_of_gt hn) }
  have h2 : ∃ s : Finset ℕ, n = ∑ k in s, 2 ^ k := by
    classical
    induction n with n ih
    · exact ⟨∅, by simp⟩
    · obtain ⟨s, hs⟩ := ih (n - 1) (by { from le_of_lt (lt_of_le_of_ne (le_of_lt h1) (ne_of_gt h1)) })
      let s' := s.insert n
      have hss : s'.card = s.card + 1 := by { unfold Finset.card; simp [Finset.insert] }
      have hsum : ∑ k in s', 2 ^ k = 2 ^ n + ∑ k in s, 2 ^ k := by { unfold Finset.sum; simp [Finset.insert] }
      have hsum' : 2 ^ n + ∑ k in s, 2 ^ k = n + ∑ k in s, 2 ^ k := by { rw [add_assoc, hs, add_zero] }
      exact ⟨s', by { rw [hsum, hsum'], simp [hss] }⟩
  exact h2