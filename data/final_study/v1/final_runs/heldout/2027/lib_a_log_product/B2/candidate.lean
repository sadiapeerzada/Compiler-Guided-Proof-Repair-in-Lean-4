open scoped BigOperators
theorem study_a_log_product (x y : ℝ) (hx : x ≠ 0) (hy : y ≠ 0) : Real.log (x * y) = Real.log x + Real.log y
:= by
  have hxy_pos : 0 < x * y := by
    exact! mul_pos hx hy
  calc
    Real.log (x * y) = Real.log (abs (x * y)) : by rw [Real.log_abs]
    ... = Real.log (abs x * abs y) : by rw [abs_mul]
    ... = Real.log (abs x) + Real.log (abs y) : by rw [Real.log_mul]
    ... = Real.log x + Real.log y : by rw [hx, hy, abs_of_pos, abs_of_pos]