# Final scientific integrity audit

Audit base: latest fetched main `af5534217c25d966bf15c44280942113891e2523`, merging PR20 on top of PR19. The supplement branch does not edit their outputs or manuscript. All new summaries are exploratory post-hoc. No inference, held-out rerun, tokenizer execution or Lean replay was run.

- base_main: `af5534217c25d966bf15c44280942113891e2523`
- v7_sha256: `e766a98ae53830e748da273aaace3ff958e15d53dd72cd92387f25928a3cc72a`
- archive_members_verified: `4736`
- lock_entries_verified: `40`
- study1_missing_C: `2`
- v8_new_repairs_B_C_D_E: `0`
- case_count: `3`
- raw_trajectory_counts: `{'V7': 72, 'V8': 72}`
- repair_observation_count: `1916`
- privacy_manual_review_required: `True`

PR20 results are reused, not regenerated. Verification assertions compare frozen outcome discordances and call-token totals with its tables. The 24 theorem types reuse three dependent seeds, with eight recorded families; nominal theorem independence remains questionable because of known overlap. No 72-independent-problem inference is justified. All V8 B/C/D/E verified outcomes are already initial successes. Study 1 keeps two missing C trajectories unknown, with 58 observed C endpoints and 58 complete B/C pairs. Its shared B/C success is not new diagnostic benefit.

## Numerical and documentation discrepancies

The old handoff reports pooled family C−B interval [−1.67,+15.39] and C−D [−2.78,+6.41] percentage points, while PR20's pooled family bootstrap gives [−1.52,+15.38] and [−3.03,+6.67]. A pooled recipe/source draw stream for the handoff numbers is not recorded in the handoff. Sampling variation is a possible explanation, NOT an established attribution. PR20 explicitly uses all seeds, family clusters, row-weighted ratio, 10,000 draws and seed 20261104; its theorem-cluster C−B interval is [−1.39,+18.06]. Historical per-seed family intervals instead use seed 20271102 and each seed's 24 rows. Different units/cohorts/streams must not be silently substituted. Original intervals remain untouched; all cross zero and none establishes equivalence.

The handoff's earlier statement that V8 raw trajectories were not public is stale relative to PR19's indexed ZIP release; provenance is now inspectable, without implying independent experiment replication. Its base-C 10/72 versus Coder-C 11/72 comparison must not be called improved repair: the Coder numerator is entirely initial success. V7 blind/C/shuffled solve 3/4/7 theorem types, so ordering by successful evaluations differs from theorem coverage. Existing overlap exclusions retain all successes while removing failed cases; improved percentages are denominator changes only.

APRIL's v1 and v2 primary HTML list Yiran Wang, whereas the official arXiv abstract metadata labels the first author Evan Wang; the exact version/metadata discrepancy is linked in RELATED_WORK_COMPARISON.md and requires author reconciliation before submission. No bibliography file was edited. The paper's empirical task is fixed-statement proof repair; placeholder English in Study 2 does not establish NL-to-Lean semantic correctness.

## Provenance and privacy

ZIP and every indexed member hash are verified, as are the 40 prior frozen-lock entries. V9 is development-only; archival consistency is not a fresh held-out test. Model weights, caches, hardware and original toolchain are not independently recreated. Source hashes authenticate consistency with committed manifests, not the truth of an experiment or independent human review.

V7 raw trajectory snapshots are local and untracked, with hashes recorded on this audit; PR20 only supplies processed V7 records. Cases and raw length observations can be inspected from the committed sanitized excerpt/CSV views, and a fresh checkout can reproduce the analyses from committed sanitized trajectory views, which retain candidate text and recorded verification fields. Their original-file digests are recorded separately; these new views are derivatives, not newly recovered historical archives. No response is filled from aggregate counts. V8 raw inputs are indexed archival members. Study 1 publication views are redacted derivatives, whose current file hashes need not equal original hashes embedded in manifests. Candidate text is checked against recorded candidate SHA and public candidate views. SOURCE_HASHES.json records exact bytes of every source used by this script.

PR19 privacy warnings explicitly require manual review and contain local-path warnings. No credential-regex matches is not general privacy approval. New display excerpts redact personal home-directory prefixes while retaining original source hashes; originals and archives are untouched. This supplement's scan does not certify the existing archive for privacy, licensing or human consent.

## What remains unresolved

Independent mathematical/split/NL-semantic adjudication, training-contamination uncertainty, adequate precision, and a fresh diagnostic-content experiment remain open. Later repair histories diverge, and error/candidate changes are not proof verification. No new inferential p-values or independent-row significance claims are introduced. Manuscript integration and venue checks remain with the author. See SUPERVISOR_29_POINT_STATUS.md, RELATED_WORK_COMPARISON.md and the signed-review blanks in the benchmark packet.
