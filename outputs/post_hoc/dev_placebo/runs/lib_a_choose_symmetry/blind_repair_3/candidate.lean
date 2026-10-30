open scoped BigOperators

theorem study_a_choose_symmetry (n k : ℕ) (h : k ≤ n) : n.choose k = n.choose (n - k) :=
by
  have h1 : k ≤ n → n - (n - k) = k := by
    intro h2
    rw [sub_eq_add_neg, add_assoc, neg_add_cancel_right]
  have h2 : k ≤ n - k := by
    rw [h1 h]
  have h3 : n.choose k = n.choose (n - k) := by
    rw [choose_symmetry]
  exact h3