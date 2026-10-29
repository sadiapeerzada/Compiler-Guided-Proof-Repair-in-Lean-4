theorem even_iff_even_three_mul (n : ℤ) : Even n ↔ Even (3 * n) :=
by
  split
  · intro h
    obtain ⟨k, hk⟩ := h
    exact even_of_add_one_even (by rw [mul_one, hk, mul_one])

  · intro h
    obtain ⟨k, hk⟩ := h
    rw [mul_one, hk, mul_one]
    exact even_of_add_one_even (by rw [mul_one, hk, mul_one])