# Exploratory post-hoc summary

Reconciliation: 38 checks, zero mismatches. All measurements use original private raw records, never redacted publication substitutes. No held-out model call was run.

Repetition: B repeated its predecessor in 90/178 repairs (50.56%); C did so in 70/172 (40.70%). The exploratory repair-weighted C-minus-B difference is -9.86 percentage points, with a whole-family bootstrap interval [-19.77, -0.50]. This post-hoc contrast does not establish diagnostic-content use or a proof-success benefit.

Character edit distance: completed-repair means are B 0.1109 (n=178) and C 0.1176 (n=172); the cluster difference interval is [-0.0207, +0.0327]. Conditioning on nonidentical repairs changes the denominators and is reported separately; no mathematical-progress inference is implied.

Frozen-tokenizer edit distance: completed-repair means are B 0.1172 (n=178) and C 0.1245 (n=172); the cluster difference interval is [-0.0236, +0.0360]. Conditioning on nonidentical repairs changes the denominators and is reported separately; no mathematical-progress inference is implied.

Targeted-name removal: at least one preceding unknown identifier disappears in B 12/76 eligible repairs and C 14/70. B's diagnostics are used by the analyst only, as a chance baseline. Syntactic disappearance and newly introduced unknown symbols are not verified mathematical fixes.

Error transitions and diagnostic counts: all rows are actual completed consecutive-candidate pairs; stage advancement follows the declared parser/name/type/tactic order. Other and guard states are not forced into an ordered scale, and fewer error messages need not mean a stronger or correct proof.

Prompt length: C and B input-token distributions and C diagnostic-length repetition bins are descriptive. The same theorem, category, previous output length, and branch stopping affect these quantities; no causal length effect or independent-repair test is claimed.

Calibrated null: on 58 complete B/C pairs there are zero discordant outcomes; conventional exact two-sided McNemar p=1.0. The family bootstrap interval is [0,0] because all observed paired differences are zero, while the independent-pair Newcombe method-10 sensitivity interval is [-6.83, +6.83] percentage points. Neither interval establishes equivalence; family dependence and two unavailable C outcomes remain limitations.

Under the score approximation, effects larger than 6.83 pp are not supported by this data at this n; values up to that boundary remain inside the model-dependent interval. This statement is conditional on independent-pair score assumptions, not a general exclusion of effects under family dependence. Full-cohort C-minus-B identification bounds remain 0 to +3.33 pp, separately from confidence intervals.

Power: the MDE sensitivity table varies an assumed discordance probability; it does not use the observed zero to claim perfect precision. The normal formula is (z_.975+z_.8)*sqrt(q/58); exact discrete McNemar power additionally respects |difference|<=q, and sparse discordance can make 80% power unattainable. Family dependence can further reduce power.

Tasks 1–2 completed; development placebo execution follows only after its protocol, filename-only normalizer and code are committed and validation passes. Study 2 execution is deferred.

Caveats: post hoc, multiple descriptive comparisons, one seed, 54 original/52 complete-pair families, B-before-C execution order, longer C prompts, two unavailable C outcomes, and correlated repair attempts. No existing missing outcome is imputed, replayed or replaced.

## Completed exploratory development control

- A: 0/15 observed verified outcomes; 0 unavailable; 0 completed repairs.
- B: 0/15 observed verified outcomes; 0 unavailable; 45 completed repairs.
- C: 0/15 observed verified outcomes; 0 unavailable; 45 completed repairs.
- C_placebo: 0/15 observed verified outcomes; 0 unavailable; 45 completed repairs.

The observed higher own-name removal and lower repetition under real diagnostics are consistent with diagnostic-content sensitivity. This exploratory one-seed pattern does not prove that the model uses diagnostic content.

These results are exploratory and development-only. Fifteen problems in five families and one seed do not support a general claim of diagnostic-content use or nonuse. Study 2 model execution remains deferred.

## Final completion checks

Tasks 0–3 are complete. Reconciliation found zero mismatches. Existing-data reconciliation, process and calibrated-null JSON outputs reproduced byte-for-byte. The complete Python suite passed 316 tests and 28 subtests; the Lean build passed. The new anonymous manuscript has 15 pages and uses the requested title.

The dev worker interruption and no-replay recovery are recorded separately from the original execution log. All genuine model responses, streams and normalized compiler records are retained. Original held-out records and the two unavailable C outcomes are unchanged. Study 2 model execution remains deferred.

Development process counts (descriptive completed repairs, with separate name-eligible denominators):

- B: identical 22/45; own-name removal 1/18.
- C: identical 23/45; own-name removal 3/19.
- C_placebo: identical 32/45; own-name removal 2/17.

The observed higher own-name removal and lower repetition under real diagnostics are consistent with diagnostic-content sensitivity. This exploratory one-seed pattern does not prove that the model uses diagnostic content. No new verified success was observed in any arm.

Not computable: the unavailable original C outcomes and response-level metrics for those absent responses; broader equivalence or proof of diagnostic use/nonuse. No number is imputed for these. Public exact-byte reproduction of original held-out prompt/token metrics requires the preserved private originals.
