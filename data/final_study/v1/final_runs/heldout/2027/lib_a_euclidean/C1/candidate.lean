open scoped BigOperators
theorem study_a_euclidean (a b : ℤ) : a % b + b * (a / b) = a
:= by
  cases b with
  | zero =>
    have h: a % 0 + 0 * (a / 0) = a := by
      rw [mod_zero, zero_mul]
      exact eq_self a
    exact h
  | nonZero b' =>
    have h: a % b' + b' * (a / b') = a := by
      rw [mod_add_div_self]
      exact eq_self a
    exact h