open scoped BigOperators

theorem study_i_fibonacci (n : ℕ) : Nat.fib (n + 2) = Nat.fib n + Nat.fib (n + 1) :=
by
  induction n with
  | zero =>
    calc
      Nat.fib (0 + 2) = Nat.fib 2   := by refl
      _               = 1 + 1       := by refl
      _               = Nat.fib 0 + Nat.fib 1 := by refl
  | succ n =>
    calc
      Nat.fib (succ n + 2) = Nat.fib (n + 3)   := by refl
      _                    = Nat.fib (n + 2) + Nat.fib (n + 3 - 1) := by rw [Nat.fib_add]
      _                    = Nat.fib (n + 2) + Nat.fib (n + 2)       := by refl
      _                    = Nat.fib n + Nat.fib (n + 1) + Nat.fib (n + 2) := by rw [Nat.fib_add]
      _                    = Nat.fib n + (Nat.fib (n + 1) + Nat.fib (n + 2)) := by refl
      _                    = Nat.fib n + Nat.fib (n + 1) := by refl