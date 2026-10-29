theorem sum_squares_closed_form (n : ℕ) : (∑ k ∈ Finset.range (n + 1), k ^ 2) = n * (n + 1) * (2 * n + 1) / 6
:= by
  induction n with i ih
  · simp [Finset.sum_range_zero]
  · have h := ih i
    rw [Finset.sum_range_succ, add_assoc, mul_assoc, mul_comm i (i + 1), add_comm (i + 1), add_assoc, add_left_comm, add_right_comm]
    ring