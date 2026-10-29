open scoped BigOperators
theorem study_a_gcd_lcm (a b : ℕ) : Nat.gcd a b * Nat.lcm a b = a * b
:= by
  have h1 : a = a * Nat.gcd a b + b * (a / Nat.gcd a b) := by
    rw [Nat.gcd_eq_gcd_symm]
  have h2 : b = a * (b / Nat.gcd a b) + b * (b / Nat.gcd a b) := by
    rw [Nat.gcd_eq_gcd_symm]
  have h3 : Nat.lcm a b = a * b / Nat.gcd a b := by
    rw [Nat.lcm_eq_mul_div_gcd]
  rw [h3]
  ring