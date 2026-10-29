theorem dvd_add_sub_int (a b c : ℤ) (hab : a ∣ b) (hac : a ∣ c) : a ∣ b + c ∧ a ∣ b - c
:= by
  obtain ⟨k, hk₁⟩ := hab
  obtain ⟨l, hl₁⟩ := hac
  exact ⟨k + l, k - l, by rw [mul_add, mul_sub, hk₁, hl₁]⟩