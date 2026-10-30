theorem postage_representable_large (n : ℕ) (hn : 28 ≤ n) : ∃ five eight : ℕ, 5 * five + 8 * eight = n
proof
  have h1 : ∃ k : ℕ, n - 28 = 5 * k, by
    have h2 : 0 ≤ n - 28, by linarith [hn]; 
    exact nat.exists_of_nonneg h2 (nat.exists_of_nonpos (nat.sub_nonpos_of_le h2) (nat.zero_le _));
  obtain k, hnk : n - 28 = 5 * k, from h1;
  have h4 : 5 * (k + 5) + 8 * 1 = n, by linarith [hnk];
  exact ⟨k + 5, 1, h4⟩
end