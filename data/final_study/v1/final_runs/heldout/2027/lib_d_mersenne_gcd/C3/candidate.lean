open scoped BigOperators
theorem study_d_mersenne_gcd (a b c : ℕ) : Nat.gcd (a ^ b - 1) (a ^ c - 1) = a ^ Nat.gcd b c - 1
:= by
  induction' (Nat.gcd b c) with d hd hd' generalizing a b c
  · simp [hd]
  · have h1 : a ^ b - 1 = (a ^ d - 1) * (a ^ (b % d) ^ (b / d) - 1) + (a ^ (b % d) - 1) := by
      rw [Nat.gcd_eq_bezout, Nat.gcd_pos, Nat.gcd_eq_0, Nat.gcd_eq_1]
    have h2 : a ^ c - 1 = (a ^ d - 1) * (a ^ (c % d) ^ (c / d) - 1) + (a ^ (c % d) - 1) := by
      rw [Nat.gcd_eq_bezout, Nat.gcd_pos, Nat.gcd_eq_0, Nat.gcd_eq_1]
    have h3 : a ^ (b % d) - 1 = (a ^ (gcd b d) - 1) * (a ^ (b % (gcd b d)) - 1) := by
      rw [Nat.gcd_eq_bezout, Nat.gcd_pos, Nat.gcd_eq_0, Nat.gcd_eq_1]
    have h4 : a ^ (c % d) - 1 = (a ^ (gcd c d) - 1) * (a ^ (c % (gcd c d)) - 1) := by
      rw [Nat.gcd_eq_bezout, Nat.gcd_pos, Nat.gcd_eq_0, Nat.gcd_eq_1]
    have h5 : a ^ (gcd b d) - 1 = (a ^ (gcd b c) - 1) := by
      rw [Nat.gcd_eq_bezout, Nat.gcd_pos, Nat.gcd_eq_0, Nat.gcd_eq_1]
    have h6 : a ^ (gcd c d) - 1 = (a ^ (gcd b c) - 1) := by
      rw [Nat.gcd_eq_bezout, Nat.gcd_pos, Nat.gcd_eq_0, Nat.gcd_eq_1]
    have h7 : a ^ (gcd b c) - 1 = (a ^ (gcd b c) - 1) := by
      rw [Nat.gcd_eq_bezout, Nat.gcd_pos, Nat.gcd_eq_0, Nat.gcd_eq_1]
    rw [h1, h2, h3, h4, h5, h6, h7]
    refl