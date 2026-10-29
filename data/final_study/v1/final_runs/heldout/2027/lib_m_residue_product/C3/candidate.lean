open scoped BigOperators
theorem study_m_residue_product (a b m : ℕ) : (a * b) % m = ((a % m) * (b % m)) % m
:= by
  have h1 : (a * b) % m = (a * b) := by
    rw [mod_eq_of_lt (by apply le_of_lt; apply le_mod)]
  have h2 : (a % m) * (b % m) % m = (a % m) * (b % m) := by
    rw [mod_eq_of_lt (by apply le_of_lt; apply mod_lt)]
  have h3 : (a * b) % m = (a % m) * (b % m) % m := by
    rw [h1, h2]
  exact h3