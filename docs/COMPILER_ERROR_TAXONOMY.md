# Genuine compiler-error taxonomy

The main paper preserves the pre-specified, mutually exclusive initial-error classifier: 26 parser/syntax, 20 unknown-name, nine tactic/goals, four type/elaboration and one other case. C is unavailable once in parser and once in tactic/goals. The only solved target is in the unknown-name group (B=C=1/20); all other observed repairs fail. These groups support descriptive error outcomes, not subgroup significance claims.

The following **post-hoc overlapping message tags** refine the actual initial diagnostics. A case can belong to several rows, so counts must not be summed. Unknown identifier and theorem/lemma names are not distinguished without evidence from compiler text. Tactic and unsolved-goal tags may co-occur.

| Message tag | Examples | B solved/observed | C solved/observed | Authentic representative |
|---|---:|---:|---:|---|
| Unknown identifier/theorem name | 25 | 1/25 (4.0%) | 1/25 (4.0%) | `div_007` |
| Tactic failure | 31 | 0/31 (0.0%) | 0/30 (0.0%) | `div_008` |
| Unsolved goals | 23 | 1/23 (4.3%) | 1/22 (4.5%) | `div_009` |
| Syntax/parser | 26 | 0/26 (0.0%) | 0/25 (0.0%) | `div_009` |
| Type mismatch/elaboration | 13 | 0/13 (0.0%) | 0/13 (0.0%) | `div_011` |
| Missing instance | 3 | 0/3 (0.0%) | 0/2 (0.0%) | `lib_a_trig_unit` |

Actual full representative messages and author-assessed potential actionability are in `data/final_review/20261029_v2/diagnostic_subtypes.json`. For example, an unavailable symbol localizes a name problem; failed instance synthesis localizes incompatible operand/application types; an unsolved goal states a remaining proof obligation. These are potentially useful diagnostics, not measured helpfulness ratings or a guarantee the model follows them. Groups below five examples remain small descriptive cases. No initial Lean timeout/resource-exhaustion case occurred; the context rejection happened before model generation, separately from Lean compilation. All 408 failed completed candidate verifications are compiler errors, and the original all-attempt primary event counts are preserved separately from problem counts.
