open scoped BigOperators
theorem study_a_log_product (x y : ℝ) (hx : x ≠ 0) (hy : y ≠ 0) : Real.log (x * y) = Real.log x + Real.log y
:= by
  cases! (lt_or_ge 0 x) with
  | inl hx_pos =>
    cases! (lt_or_ge 0 y) with
    | inl hy_pos =>
      have hxy_pos : 0 < x * y := by
        exact! mul_pos hx_pos hy_pos
      calc
        Real.log (x * y) = Real.log (abs (x * y)) : by rw [Real.log_abs]
        ... = Real.log (abs x * abs y) : by rw [abs_mul]
        ... = Real.log (abs x) + Real.log (abs y) : by rw [Real.log_mul]
        ... = Real.log x + Real.log y : by rw [hx_pos, hy_pos, abs_of_pos, abs_of_pos]
    | inr hy_neg =>
      have hxy_neg : 0 < -x * y := by
        exact! mul_pos (not_le.mp hx_pos) hy_neg
      calc
        Real.log (x * y) = Real.log (-x * y) : by rw [mul_neg_y]
        ... = Real.log (abs (-x * y)) : by rw [Real.log_neg, Real.log_abs]
        ... = Real.log (abs x * abs y) : by rw [abs_neg, abs_mul]
        ... = Real.log (abs x) + Real.log (abs y) : by rw [Real.log_mul]
        ... = Real.log x + Real.log y : by rw [hx_pos, hy_neg, abs_of_neg, abs_of_pos]
  | inr hx_neg =>
    cases! (lt_or_ge 0 y) with
    | inl hy_pos =>
      have hxy_neg : 0 < -x * y := by
        exact! mul_pos (not_le.mp hx_neg) hy_pos
      calc
        Real.log (x * y) = Real.log (-x * y) : by rw [mul_neg_y]
        ... = Real.log (abs (-x * y)) : by rw [Real.log_neg, Real.log_abs]
        ... = Real.log (abs x * abs y) : by rw [abs_neg, abs_mul]
        ... = Real.log (abs x) + Real.log (abs y) : by rw [Real.log_mul]
        ... = Real.log x + Real.log y : by rw [hx_neg, hy_pos, abs_of_neg, abs_of_pos]
    | inr hy_neg =>
      have hxy_pos : 0 < x * y := by
        exact! mul_pos hx_neg (not_le.mp hy_neg)
      calc
        Real.log (x * y) = Real.log (x * y) : by rw [hxy_pos]
        ... = Real.log (abs (x * y)) : by rw [Real.log_abs]
        ... = Real.log (abs x * abs y) : by rw [abs_mul]
        ... = Real.log (abs x) + Real.log (abs y) : by rw [Real.log_mul]
        ... = Real.log x + Real.log y : by rw [hx_neg, hy_neg, abs_of_neg, abs_of_neg]