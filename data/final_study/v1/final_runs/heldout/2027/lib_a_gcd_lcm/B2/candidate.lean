open scoped BigOperators
theorem study_a_gcd_lcm (a b : ℕ) : Nat.gcd a b * Nat.lcm a b = a * b
:= by
  have h1 : a * b = a * (b / Nat.gcd a b) + a * (a / Nat.gcd a b * (b / Nat.gcd a b)) := by
    rw [Nat.gcd_eq_gcd_symm]
  have h2 : Nat.lcm a b = a * b / Nat.gcd a b := by
    rw [Nat.lcm_eq_mul_div_gcd]
  rw [h2]
  ring