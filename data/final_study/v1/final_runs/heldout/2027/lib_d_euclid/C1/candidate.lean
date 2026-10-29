open scoped BigOperators
theorem study_d_euclid (p a b : ℕ) (hp : p.Prime) : p ∣ a * b ↔ p ∣ a ∨ p ∣ b
:= by
  split
  · intro h
    cases h with ha hb
    · exact or.inl ha
    · exact or.inr hb
  · intro h
    cases h with ha hb
    · exact or.inl (by linarith [hp, ha])
    · exact or.inr (by linarith [hp, hb])