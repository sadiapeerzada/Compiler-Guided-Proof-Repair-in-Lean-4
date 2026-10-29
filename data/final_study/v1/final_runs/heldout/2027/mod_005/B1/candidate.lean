theorem pow_seven_sub_one_dvd_six (n : ℕ) : 6 ∣ 7 ^ n - 1 := by
  induction n with n ih
  · simp [pow_zero, sub_one]
  · have : 7 * (7 ^ n) - 1 = 6 * (7 ^ n) + (7 ^ n - 1) := by
      rw [mul_add, one_mul, add_comm]
    rw [this]
    exact dvd_add (by rw [mul_assoc, ih, pow_add, zero_mul]) (by rw [sub_one])