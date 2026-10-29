open scoped BigOperators
theorem study_m_wilson (p : ℕ) [Fact p.Prime] : ((p - 1).factorial : ZMod p) = -1
:= by
  have h : (p - 1).factorial = ∏ k in Finset.range (p - 1), k := by
    apply Finset.prod_eq_big_prod
    simp
  have h2 : ∏ k in Finset.range (p - 1), k = -1 := by
    rw [h]
    apply ZMod.prod_inv_eq_neg_one
    exact p.prime
  exact h2