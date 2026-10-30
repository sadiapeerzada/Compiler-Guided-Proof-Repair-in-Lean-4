open scoped BigOperators

theorem study_a_choose_symmetry (n k : ℕ) (h : k ≤ n) : n.choose k = n.choose (n - k) :=
by
  have h1 : k ≤ n → n - (n - k) = k := by
    intro h2
    rw [sub_eq_add_neg, add_assoc, neg_add_cancel_right]
  have h2 : k ≤ n - k := by
    rw [h1 h]
  have h3 : n.choose k = ∑ i in range (k + 1), (n.choose i) * (n - i).choose (k - i) := by
    rw [choose_eq_multiset_perm]
  have h4 : n.choose (n - k) = ∑ i in range ((n - k) + 1), (n.choose i) * (n - i).choose ((n - k) - i) := by
    rw [choose_eq_multiset_perm]
  have h5 : ∑ i in range (k + 1), (n.choose i) * (n - i).choose (k - i) = ∑ i in range ((n - k) + 1), (n.choose (n - k - i)) * (n - (n - k - i)).choose (n - k - i) := by
    simp only [h1 h, sub_eq_add_neg, add_assoc, neg_add_cancel_right]
    congr
    apply sum_congr
    intro i
    rw [choose_symmetry]
  exact h3.trans h5.trans h4