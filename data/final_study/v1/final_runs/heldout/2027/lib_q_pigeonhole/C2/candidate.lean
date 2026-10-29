open scoped BigOperators
theorem study_q_pigeonhole (s t : Finset ℕ) (f : ℕ → ℕ) (h : t.card < s.card) (hm : ∀ x ∈ s, f x ∈ t) : ∃ x ∈ s, ∃ y ∈ s, x ≠ y ∧ f x = f y
:= by
  have h1 : ∀ x ∈ s, f x ∈ t := hm
  have h2 : t.card < s.card := h
  obtain x := classical.choose (λ x hx, h1 x hx)
  have h3 : x ∈ s := classical.choose_spec (λ x hx, h1 x hx)
  have h4 : f x ∈ t := h1 x h3
  obtain y := classical.choose (λ y hy, h1 y hy)
  have h5 : y ∈ s := classical.choose_spec (λ y hy, h1 y hy)
  have h6 : f y ∈ t := h1 y h5
  have h7 : f x = f y := by
    have h8 : x ∈ s := h3
    have h9 : f x ∈ t := h4
    have h10 : y ∈ s := h5
    have h11 : f y ∈ t := h6
    exact classical.by_contradiction (assume h12 : f x ≠ f y, by
      have h13 : x = y := by
        have h14 : f x ∈ t := h9
        have h15 : f y ∈ t := h11
        have h16 : x ∈ s := h8
        have h17 : y ∈ s := h10
        exact classical.by_contradiction (assume h18 : x ≠ y, by
          have h19 : f x = f y := by
            have h20 : f x ∈ t := h14
            have h21 : f y ∈ t := h15
            have h22 : x ∈ s := h16
            have h23 : y ∈ s := h17
            exact h12 h19 h20 h21 h22 h23
          exact h18 h13 h19
        )
      exact h12 h13
    )
  exact ⟨x, y, h3, h5, h7⟩