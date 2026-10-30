theorem choose_zero_and_self (n : ℕ) : Nat.choose n 0 = 1 ∧ Nat.choose n n = 1
:= by
  split
  · rw [Nat.choose_zero]
  · rw [Nat.choose_self]