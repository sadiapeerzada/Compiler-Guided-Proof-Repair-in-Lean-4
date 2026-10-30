theorem modEq_add_two (a b c d n : ℤ) (_hn : 0 < n) (hab : a ≡ b [ZMOD n]) (hcd : c ≡ d [ZMOD n]) : a + c ≡ b + d [ZMOD n] :=
by
  have h1 : a - b ≡ 0 [ZMOD n] := hab
  have h2 : c - d ≡ 0 [ZMOD n] := hcd
  have h3 : (a - b) + (c - d) ≡ 0 [ZMOD n] := by rw [h1, h2]
  have h4 : a + c - (b + d) ≡ 0 [ZMOD n] := by rw [ZMOD.add_sub_add, h3]
  exact h4