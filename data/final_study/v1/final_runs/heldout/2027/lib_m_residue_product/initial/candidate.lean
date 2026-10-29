open scoped BigOperators
theorem study_m_residue_product (a b m : ℕ) : (a * b) % m = ((a % m) * (b % m)) % m
:= by
  have h1 : (a % m) * (b % m) < m * m := by
    calc
      (a % m) * (b % m) ≤ a * b : by apply le_of_lt; apply mod_lt; assumption
      _ < m * m : by apply mul_lt_mul; [apply zero_lt_one, apply zero_lt_one]
  have h2 : (a * b) % m ≤ m := by apply mod_lt; assumption
  have h3 : ((a % m) * (b % m)) % m ≤ m := by apply mod_lt; exact h1
  have h4 : (a * b) % m - ((a % m) * (b % m)) % m ≤ m := by
    calc
      (a * b) % m - ((a % m) * (b % m)) % m ≤ (a * b) % m : by apply le_of_sub_nonneg; apply le_mod
      _ ≤ m : h2
  have h5 : (a * b) % m - ((a % m) * (b % m)) % m ≥ 0 := by apply le_mod; assumption
  have h6 : (a * b) % m - ((a % m) * (b % m)) % m = 0 ∨ (a * b) % m - ((a % m) * (b % m)) % m = m := by
    apply mod_unique; [apply h4, apply h5]
  have h7 : (a * b) % m = ((a % m) * (b % m)) % m ∨ (a * b) % m = ((a % m) * (b % m)) % m + m := by
    apply or_of_le; exact h6
  have h8 : (a * b) % m = ((a % m) * (b % m)) % m := by
    by_cases h : (a * b) % m = ((a % m) * (b % m)) % m + m; [left, apply h, right, apply zero_add]
    have h9 : (a * b) % m - ((a % m) * (b % m)) % m = m := by apply eq_of_sub_eq_add; assumption
    have h10 : m = 0 := by apply mod_eq_zero; assumption
    contradiction
  exact h8