theorem even_cube_sub_self (n : ℤ) : Even (n ^ 3 - n) :=
by
  have h = n ^ 3 - n = n * (n ^ 2 - 1)
  rw [h]
  have h1 = n ^ 2 - 1 = (n - 1) * (n + 1)
  rw [h1]
  have h2 = n * (n - 1) * (n + 1)
  rw [h2]
  have h3 = n * (n - 1) * (n + 1) % 2 = 0
  rw [Even_def]
  have h4 = (n % 2) * ((n - 1) % 2) * ((n + 1) % 2) % 2 = 0
  rw [mod_mul_mod]
  have h5 = (n % 2) * (n % 2) * (n % 2) % 2 = 0
  rw [mod_pow]
  exact h5