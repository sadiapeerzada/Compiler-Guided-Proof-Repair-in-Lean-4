open scoped BigOperators
theorem study_a_choose_symmetry (n k : ℕ) (h : k ≤ n) : n.choose k = n.choose (n - k) :=
by
  have h1 : k ≤ n → n - (n - k) = k := by
    intro h2
    rw [sub_eq_add_neg, add_assoc, neg_add_cancel_right]
  have h2 : n - k ≤ n := by
    rw [sub_le_sub_right] <;> assumption
  have h3 : k ≤ n - k := by
    rw [sub_le_sub_right] <;> assumption
  have h4 : n.choose k = ∑ i in range (k + 1), (n.choose i) / ((i + 1) * (n - i).choose (k - i)) := by
    rw [choose_eq_multiset_perm]
  have h5 : n.choose (n - k) = ∑ i in range ((n - k) + 1), (n.choose i) / ((i + 1) * (n - i).choose ((n - k) - i)) := by
    rw [choose_eq_multiset_perm]
  have h6 : ∑ i in range (k + 1), (n.choose i) / ((i + 1) * (n - i).choose (k - i)) = ∑ i in range ((n - k) + 1), (n.choose (n - k - i)) / ((n - k - i + 1) * (n - (n - k - i)).choose (n - k - i - (n - k - i))) := by
    rw [h1, h2, h3]
    simp only [sub_eq_add_neg, add_assoc, neg_add_cancel_right]
    congr
    apply sum_congr
    intro i
    rw [choose_symmetry]
  exact h4.trans h6.trans h5