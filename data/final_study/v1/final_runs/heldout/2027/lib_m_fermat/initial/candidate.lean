open scoped BigOperators
theorem study_m_fermat (p : ℕ) (hp : p.Prime) (a : ℤ) : Int.ModEq (p : ℤ) (a ^ p) a
:= by
  have h1 : a ^ p = (if a = 0 then 0 else a * (a ^ (p - 1))) := by
    by_cases h : a = 0
    · simp [h]
    · rw [pow_add_one, one_mul]
  have h2 : Int.ModEq (p : ℤ) (a * (a ^ (p - 1))) (a * 1) := by
    rw [h1]
    apply Int.ModEq_mul
    · exact hp.ne_zero
    · exact Int.ModEq.refl (a * 1)
  have h3 : Int.ModEq (p : ℤ) (a * 1) a := by
    rw [Int.ModEq.refl (a * 1)]
  exact h2.trans h3