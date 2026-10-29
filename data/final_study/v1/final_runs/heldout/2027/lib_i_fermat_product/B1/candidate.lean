open scoped BigOperators
theorem study_i_fermat_product (n : ℕ) : (∏ k ∈ Finset.range n, Nat.fermatNumber k) = Nat.fermatNumber n - 2
:= by
  induction n with n ih
  · simp [Nat.fermatNumber, Finset.range_zero, prod_empty]
  · have h := ih n
    simp [Nat.fermatNumber, Finset.range_succ, prod_insert] at h
    have := by rw [h, Nat.fermatNumber, pow_add, pow_one, two_pow_add, two_pow_one, sub_add_cancel]
    simp [this]