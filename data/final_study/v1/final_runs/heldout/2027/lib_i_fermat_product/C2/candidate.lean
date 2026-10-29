open scoped BigOperators

theorem study_i_fermat_product (n : ℕ) : (∏ k ∈ Finset.range n, Nat.fermatNumber k) = Nat.fermatNumber n - 2
:= by
  induction n with n ih
  · simp [Nat.fermatNumber, Finset.range_zero, prod_empty]
  · simp [Nat.fermatNumber, Finset.range_succ]
    let k := n
    have h := ih k
    rw [h]
    simp