open scoped BigOperators
theorem study_d_bezout (a b : ℤ) : ∃ x y : ℤ, (Int.gcd a b : ℤ) = a * x + b * y
:= by
  have h : ∃ x y, (Int.gcd a b : ℤ) = a * x + b * y := Int.bezout a b
  obtain x y := h
  exact x
  exact y
  refl