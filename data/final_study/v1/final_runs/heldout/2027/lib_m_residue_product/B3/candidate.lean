open scoped BigOperators
theorem study_m_residue_product (a b m : ℕ) : (a * b) % m = ((a % m) * (b % m)) % m
:= by
  have h1 : (a * b) % m = (a % m * b % m) % m := by
    rw [mod_mul]
  exact h1