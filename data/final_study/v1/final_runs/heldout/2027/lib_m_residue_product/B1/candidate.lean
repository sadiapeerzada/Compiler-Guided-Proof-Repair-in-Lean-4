open scoped BigOperators
theorem study_m_residue_product (a b m : ℕ) : (a * b) % m = ((a % m) * (b % m)) % m
:= by
  have h1 : (a % m) * (b % m) % m ≤ (a * b) % m := by
    apply mod_le; assumption
  have h2 : (a * b) % m ≤ (a % m) * (b % m) % m := by
    apply mod_le; apply mul_mod; [apply mod_le, apply mod_le]
  exact le_antisymm h1 h2