open scoped BigOperators
theorem study_d_bezout (a b : ℤ) : ∃ x y : ℤ, (Int.gcd a b : ℤ) = a * x + b * y
:= by
  have h : ∃ x y : ℤ, (Int.gcd a b : ℤ) = a * x + b * y := Int.bezout a b
  obtain x y := h
  existsi x
  existsi y
  refl