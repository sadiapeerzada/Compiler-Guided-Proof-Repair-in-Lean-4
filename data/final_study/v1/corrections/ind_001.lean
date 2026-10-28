import Mathlib
theorem gauss_sum (n : ℕ) : 2 * (Finset.range (n + 1)).sum id = n * (n + 1) := by
  simpa [Nat.mul_comm] using Finset.sum_range_id_mul_two (n + 1)
