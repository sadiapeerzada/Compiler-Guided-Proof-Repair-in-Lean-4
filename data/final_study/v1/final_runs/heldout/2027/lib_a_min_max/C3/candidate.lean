open scoped BigOperators
theorem study_a_min_max (x y : ℝ) : min x y + max x y = x + y
:= by
  cases le_or_gt x y with
  | inl h => calc
    min x y + max x y = x + max x y : by simp [h]
    ... = x + y : by simp [h]
  | inr h => calc
    min x y + max x y = y + max y x : by simp [h]
    ... = y + x : by simp [h]