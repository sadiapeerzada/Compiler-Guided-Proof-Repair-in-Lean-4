open scoped BigOperators
theorem study_d_bezout (a b : ℤ) : ∃ x y : ℤ, (Int.gcd a b : ℤ) = a * x + b * y
:= by
  have h : ∃ x y : ℤ, (Int.gcd a b : ℤ) = a * x + b * y := Int.bezout a b
  existsi h.1
  existsi h.2
  refl