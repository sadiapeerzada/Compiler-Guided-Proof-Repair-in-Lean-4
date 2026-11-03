# V9 Study 2 benchmark review — provisional adjudication

The 31-row `PROPOSED_VALIDATION_DECISIONS.csv` contains reasoned **proposals**, not independent sign-off. Its `ACCEPT_FORMAL_ONLY` decisions mean reference theorem coherency and Lean proof validity only, *not* that the task is unique, independent, natural-language faithful, or free of training contamination. `NEAR_DUPLICATE` is a conservative template-level label, not always logical identity.

**Critical extra findings not present in the 31-row checker:**

- `bridge_d06` and `bridge_t12` are mathematically identical Nat binomial-square identities (renamed variables).
- `bridge_d06` and `bridge_t11` are the same Nat identity, with squared multiplication written as `*`.
- `bridge_t11` and `bridge_t12` are identical propositions despite different syntax.
- `bridge_d07` specializes test `bridge_t13` via `z=1`.
- `bridge_t07` and `bridge_t08` share Nat successor-addition identities.

These must be recorded **separately** in `ADDITIONAL_BENCHMARK_OVERLAPS.csv`: adding rows to the original 31-row V9 CSV will fail the script's fixed-key check. Human reviewer should reconsider all proposed pair labels and give signed/dated justification.

## Practical next steps

1. Review the 31 proposed rows and the five additional overlap findings against Lean statements. If approved, save the 31-row file to the Mac V9 `VALIDATION_DECISIONS.csv` **after backing up** the existing original. Do not alter theorem data or observed outcomes.
2. Run the V9 `finalize` command to record the in-script disposition. Caution: V9 will count `NEAR_DUPLICATE` as a serious flag; getting zero unresolved does not mean the full benchmark passes.
3. As a separate **post-hoc exploratory sensitivity analysis**, group or exclude genuine duplicate theorem families using explicit criteria and report counts for all groups; do not replace original 72/72 denominators or call the adjusted sample an untouched test.
4. For a genuinely validated NL→Lean benchmark, construct independent human-written NL theorem texts with separately reviewed equivalence to the exact Lean statements; current synthetic placeholder descriptions cannot support NL-semantic accuracy.