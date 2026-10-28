import Mathlib
theorem cong_add_one (a b m : ℤ) (_hm : 0 < m) (h : a ≡ b [ZMOD m]) : a + 1 ≡ b + 1 [ZMOD m] := by
  exact h.add (Int.ModEq.refl 1)
