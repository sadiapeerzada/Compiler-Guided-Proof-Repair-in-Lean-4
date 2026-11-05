"""Broad prospective grouping for conservative donor/partition constraints.

The definitions are grouping hypotheses, not certificates of semantic novelty.
"""
FAMILIES=(
 ('norm_composition','composition identities for sums of two squares over reals'),
 ('power_difference_factorization','integer factorization of differences of cubes or higher powers'),
 ('symmetric_polynomial','symmetric polynomial identities over integers'),
 ('natural_linear_bounds','natural-number linear constraints with several nonredundant premises'),
 ('integer_absolute_bounds','integer absolute value bounds'),
 ('divisibility_linear_combinations','natural-number divisibility of linear combinations; not transitivity'),
 ('arithmetic_progression_sum','finite sums of arithmetic progressions'),
 ('geometric_sum','finite geometric sums'),
 ('list_reverse_concat','relations between list reversal and concatenation'),
 ('list_map_length','length preservation under list maps and concatenation'),
 ('list_filter_length','bounds on lengths after filtering lists'),
 ('finset_difference_card','finite-set difference and cardinality relations'),
 ('finset_image','membership in images and inverse images of finite sets'),
 ('iteration_composition','elementary function iteration/composition identities'),
 ('natural_power_bounds','natural-number power inequalities proved by induction'),
 ('parity_square','elementary parity and square divisibility'),
 ('gcd_linear_combination','integer gcd and linear combination relations'),
 ('quadratic_discriminant','positive real quadratic polynomials with negative discriminant'),
 ('quadratic_inequality','real quadratic polynomial inequalities, excluding binomial-square identities'),
 ('logical_distribution','nontrivial quantified logical distribution equivalences'),
 ('finite_product','finite product relations under reindexing'),
 ('list_recursive_sum','recursive list-sum relations'),
 ('natural_quotient_remainder','natural-number quotient and remainder bounds'),
 ('integer_order_constraints','integer linear-order implications with multiple nonredundant premises'))
V3_GROUPS={'v3_gen_001':'norm_composition','v3_gen_002':'integer_order_constraints'}
