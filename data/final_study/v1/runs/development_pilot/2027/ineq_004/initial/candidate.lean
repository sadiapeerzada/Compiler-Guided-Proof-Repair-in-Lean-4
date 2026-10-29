theorem add_three_lt_add_seven (n : ℕ) : n + 3 < n + 7 :=
begin
  have h : n + 3 < n + 4,
  { rw add_assoc, exact nat.lt_add_one_right n },
  have h' : n + 4 < n + 7,
  { rw add_assoc, exact nat.lt_add_one_right (n + 1) },
  exact h.lt_of_lt_of_eq h'
end