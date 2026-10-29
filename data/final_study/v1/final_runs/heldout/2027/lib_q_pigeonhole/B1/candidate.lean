open scoped BigOperators
theorem study_q_pigeonhole (s t : Finset ℕ) (f : ℕ → ℕ) (h : t.card < s.card) (hm : ∀ x ∈ s, f x ∈ t) : ∃ x ∈ s, ∃ y ∈ s, x ≠ y ∧ f x = f y
:= by
  have h1 : ∀ x ∈ s, f x ∈ t := hm
  have h2 : t.card < s.card := h
  have h3 : ∃ x, x ∈ s ∧ f x ∈ t := by
    use [choose (λ x hx, h1 x hx)]; split; assumption
  obtain x with hx : x ∈ s ∧ f x ∈ t := h3
  have h4 : f x ∈ t := hx.2
  have h5 : ∃ y ∈ s, y ≠ x ∧ f y = f x := by
    have h6 : s.card > 1 := by
      rw [h2]; exact Nat.lt_of_le_of_lt (Finset.card_pos_of_mem hx.1) (Nat.lt_of_sub_pos (Nat.sub_self 1))
    obtain y with hy : y ∈ s ∧ f y ∈ t := by
      use [choose (λ y hy, h1 y hy)]; split; assumption
    obtain rfl | h7 : y = x := by
      rwa [hx.1, Finset.mem_insert]
    · contradiction
    · exact ⟨y, hy.1, h7, h4, h1 y hy.1⟩
  obtain y with hy : y ∈ s ∧ y ≠ x ∧ f y = f x := h5
  exact ⟨x, y, hy.2, hy.3⟩