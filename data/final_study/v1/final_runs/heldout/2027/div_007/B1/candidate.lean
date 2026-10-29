theorem even_add_of_even (a b : ℤ) (ha : Even a) (hb : Even b) : Even (a + b) :=
by
  obtain ⟨a', ha'⟩ := ha
  obtain ⟨b', hb'⟩ := hb
  exact even_add ha' hb'