theorem diophantine_six_ten (x y : ℤ) :
    6 * x + 10 * y = 32 ↔ ∃ k : ℤ, x = 2 - 5 * k ∧ y = 2 + 3 * k
:= by
  split
  intro h
  obtain ⟨k, h1, h2⟩ := h
  have h3 : 6 * (2 - 5 * k) + 10 * (2 + 3 * k) = 32 := by
    rw [mul_add, add_mul, h1, h2]
    ring
  exact h3
  intro ⟨k, h1, h2⟩
  have h4 : 6 * x + 10 * y = 6 * (2 - 5 * k) + 10 * (2 + 3 * k) := by
    rw [h1, h2]
    ring
  exact h4