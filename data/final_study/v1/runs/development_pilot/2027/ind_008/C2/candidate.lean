theorem positive_nat_sum_distinct_powers_two (n : ℕ) (hn : 1 ≤ n) : ∃ s : Finset ℕ, n = ∑ k in s, 2 ^ k :=
begin
  have h1 : n > 0 := le_of_lt hn,
  have h2 : ∃ s : Finset ℕ, n = ∑ k in s, 2 ^ k, by
  { 
    induction n with m hm,
    { 
      have : 1 = ∑ k in Finset.empty, 2 ^ k := by simp,
      use Finset.empty,
      exact this 
    },
    { 
      have : m + 1 > 0 := by { rw add_one, exact h1 },
      have : ∃ s : Finset ℕ, m = ∑ k in s, 2 ^ k := by { exact hm },
      then obtain ⟨s, hs⟩ := this,
      have : m + 1 = ∑ k in s, 2 ^ k + 1 := by { rw add_comm, rw add_one, exact hs },
      have : ∃ s : Finset ℕ, m + 1 = ∑ k in s, 2 ^ k := by
      { 
        use s.insert (1 : ℕ),
        rw [Finset.sum_insert_of_not_mem hs.1, add_comm, add_one, hs.2]
      },
      then obtain ⟨t, ht⟩ := this,
      use t,
      exact ht 
    }
  },
  exact h2
end