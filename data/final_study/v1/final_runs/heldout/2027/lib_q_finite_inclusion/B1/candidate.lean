open scoped BigOperators
theorem study_q_finite_inclusion (s t : Finset ℕ) (h : s ⊆ t) : s.card ≤ t.card
:= by
  have h_card : ∀ x : ℕ, x ∈ s → x ∈ t := fun x hx => h hx
  exact s.card_le_of_subset h_card