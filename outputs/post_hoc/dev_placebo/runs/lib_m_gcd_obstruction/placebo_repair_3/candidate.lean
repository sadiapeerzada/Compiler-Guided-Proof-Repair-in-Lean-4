open scoped BigOperators
theorem study_m_gcd_obstruction (a b m : ℤ) (h : ¬ (Int.gcd a m : ℤ) ∣ b) : ¬ ∃ x : ℤ, Int.ModEq m (a * x) b
:= by
  intro ex
  obtain ⟨x, eq⟩ := ex
  have h1 : (Int.gcd a m : ℤ) ∣ (a * x) := by
    rw [eq]
    exact Int.mul_div_self_right a x
  have h2 : (Int.gcd a m : ℤ) ∣ b := by
    rw [Int.ModEq_def] at eq
    exact Int.divides_trans h1 h
  contradiction