open scoped BigOperators
theorem study_a_power_add (a m n : ℕ) : a ^ (m + n) = a ^ m * a ^ n
:= by
  induction m with m IH
  · rw [add_zero, pow_zero, mul_one]
  · rw [add_succ, pow_add, IH, pow_mul]