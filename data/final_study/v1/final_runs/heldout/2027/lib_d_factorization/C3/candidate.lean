open scoped BigOperators
theorem study_d_factorization (a b : ℕ) (ha : a ≠ 0) (hb : b ≠ 0) : (a * b).factorization = a.factorization + b.factorization := by
  have h1 : (a * b).factorization = (a * b).primeExponentFactorization := by
    rw [factorization]
  have h2 : a.factorization + b.factorization = (a.factorization ++ b.factorization).primeExponentFactorization := by
    rw [primeExponentFactorization_add]
    simp
  have h3 : (a * b).primeExponentFactorization = (a.factorization ++ b.factorization).primeExponentFactorization := by
    rw [h1, h2]
  have h4 : (a * b).factorization = (a.factorization ++ b.factorization).factorization := by
    rw [factorization, h3]
  rw [h4]