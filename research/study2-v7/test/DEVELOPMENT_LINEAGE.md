# Study 2 development evidence lineage

Development calibration belongs to **V5**, not V7. Test inference belongs to **V7**. The bridge_t08 test theorem spelling was corrected after reference-screen failure but before any test-model inference. No development inferences were copied, replayed, or relabeled.

{
  "V7_test_only_syntax_fix": "bridge_t08 source `Nat.succ(a+b)` -> `Nat.succ (a + b)` to correct function application; reference proof omega -> rfl; the corrected theorem goes to model prompts but the reference proof does not; only test item t08 changes",
  "caveat": "Development results are V5; test results V7. Test-only theorem spelling corrected after reference-screen failure and before model inference. Do not merge them into one identically scripted run.",
  "completed_dev_cases": 12,
  "source_development_outcomes_sha256": "db0b57e1938710992d08c36e2c7cb6c6b373484552c7d3a448a84d4863dcfe3f",
  "source_development_report_sha256": "e9b4e1e7c348b91d43beec88b9ac27d22565084665d6247f47c0cc9c8b9e7f5e",
  "source_development_summary_sha256": "176179dc5db6e7f57810e43d48a7eccf56bc0be78ac30992f854bb0ba7eacb25",
  "source_plan_sha256": "0e4ba2a9aad46a189d85ff73fbd199961d7ef1223a1c94aa60d0daedea27a98f",
  "source_relative": "study2_outputs/bridge_v5_base",
  "source_v5_script_sha256": "44e1215de441526de44e3177e3b890273c3e1e4c4ff7ab66cf334a6676f3ac15",
  "source_version": "2026-11-02-study2-v5-bridge-reference-fix",
  "type": "separately archived V5 development evidence; NOT V7 recalculated calibration"
}
