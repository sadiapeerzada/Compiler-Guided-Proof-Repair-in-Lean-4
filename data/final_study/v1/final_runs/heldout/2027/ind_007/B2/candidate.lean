theorem sum_squares_closed_form (n : ℕ) : (∑ k ∈ Finset.range (n + 1), k ^ 2) = n * (n + 1) * (2 * n + 1) / 6
:= by
  induction n with i hi
  · simp [Finset.sum_range_zero]
  · have := hi i
    have := congr_arg (λ x, x * (i + 1) * (i + 2) * (2 * i + 3) / 6) (Finset.sum_range_succ i)
    rw [Finset.sum_range_succ, add_assoc, mul_assoc, mul_comm i (i + 1), add_comm (i + 1), add_assoc, add_left_comm, add_right_comm, hi, this]
    ring