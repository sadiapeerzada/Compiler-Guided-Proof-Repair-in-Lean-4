theorem modEq_add_two (a b c d n : ℤ) (_hn : 0 < n) (hab : a ≡ b [ZMOD n]) (hcd : c ≡ d [ZMOD n]) : a + c ≡ b + d [ZMOD n] :=
by
  have h1 : a ≡ b [ZMOD n] := hab
  have h2 : c ≡ d [ZMOD n] := hcd
  have h3 : a - b ≡ 0 [ZMOD n] := by rw [h1]
  have h4 : c - d ≡ 0 [ZMOD n] := by rw [h2]
  have h5 : (a - b) + (c - d) ≡ 0 + 0 [ZMOD n] := by rw [h3, h4]
  have h6 : a + c - (b + d) ≡ 0 [ZMOD n] := by rw [h5]
  have h7 : a + c ≡ b + d [ZMOD n] := by rw [h6]
  exact h7