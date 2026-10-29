theorem even_iff_even_three_mul (n : ℤ) : Even n ↔ Even (3 * n) :=
by
  split
  · intro h
    have := h
    cases h with k hk
    exact even_mul_of_even _ (by rw [hk]; exact even_of_add_one_even (by rw [mul_one]))

  · intro h
    have := h
    cases h with k hk
    have := even_of_add_one_even (by rw [mul_one])
    rw [hk] at this
    exact even_of_add_one_even (by rw [this])