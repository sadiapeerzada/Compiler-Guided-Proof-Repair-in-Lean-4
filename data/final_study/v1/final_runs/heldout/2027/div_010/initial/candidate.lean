theorem dvd_mul_right_int (a b c : ℤ) (hab : a ∣ b) : a ∣ b * c
:= by
  obtain ⟨k, hk⟩ := hab
  exact int.mul_right_dvd hk