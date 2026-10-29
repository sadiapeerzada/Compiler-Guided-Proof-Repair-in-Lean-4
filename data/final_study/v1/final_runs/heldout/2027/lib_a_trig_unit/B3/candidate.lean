open scoped BigOperators
theorem study_a_trig_unit (x : ℝ) : (Real.sin x) ^ 2 + (Real.cos x) ^ 2 = 1
:= by
  have h1 : (Real.sin x) ^ 2 + (Real.cos x) ^ 2 = (Real.sin x) * (Real.sin x) + (Real.cos x) * (Real.cos x) := by
    simp
  have h2 : (Real.sin x) * (Real.sin x) + (Real.cos x) * (Real.cos x) = (Real.sin x) * (Real.sin x) + (Real.cos x) * (Real.cos x) + (Real.sin x) * (Real.cos x) - (Real.sin x) * (Real.cos x) := by
    simp
  have h3 : (Real.sin x) * (Real.sin x) + (Real.cos x) * (Real.cos x) + (Real.sin x) * (Real.cos x) - (Real.sin x) * (Real.cos x) = (Real.sin x) * (Real.sin x) + (Real.cos x) * (Real.cos x) + (Real.sin x) * (Real.cos x) - (Real.sin x) * (Real.cos x) := by
    simp
  have h4 : (Real.sin x) * (Real.sin x) + (Real.cos x) * (Real.cos x) + (Real.sin x) * (Real.cos x) - (Real.sin x) * (Real.cos x) = (Real.sin x) * (Real.sin x) + (Real.cos x) * (Real.cos x) + (Real.sin x) * (Real.cos x) - (Real.sin x) * (Real.cos x) := by
    simp
  have h5 : (Real.sin x) * (Real.sin x) + (Real.cos x) * (Real.cos x) + (Real.sin x) * (Real.cos x) - (Real.sin x) * (Real.cos x) = (Real.cos x) * (Real.cos x) + (Real.sin x) * (Real.sin x) := by
    simp
  have h6 : (Real.cos x) * (Real.cos x) + (Real.sin x) * (Real.sin x) = 1 := by
    simp
  exact h6