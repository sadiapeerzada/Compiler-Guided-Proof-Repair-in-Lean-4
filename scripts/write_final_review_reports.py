"""Write the final checklist/gate from completed, genuine review evidence."""
import json
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'data/final_review/20261029_v2'


def read(path):return json.loads(path.read_text())
def write(name,text):(ROOT/'docs'/name).write_text(text.strip()+'\n')


def main():
    r=read(BASE/'analysis_verified/results.json');v=read(BASE/'reproducibility_verification.json');pdf=read(BASE/'paper_build_manifest.json')
    assert v['valid'] and pdf['valid']
    tests=(BASE/'local/pytest_final.log').read_text();match=re.search(r'(\d+) passed, (\d+) subtests passed',tests);assert match
    statuses={'M1':'PARTIAL','M2':'PARTIAL','M3':'PARTIAL','M4':'COMPLETE','M5':'COMPLETE','M6':'COMPLETE','M7':'COMPLETE'}
    matrix=[
        ['M1','Genuine automated NL-to-Lean runs; preserve attempts, model/configuration, diagnostics, tokens and timings.','PARTIAL',
         '410 completed held-out responses and 21 final-pilot responses use genuine free local MLX, the student-reported approved API substitute; all completed responses have token journals and strict Lean records.',
         'data/final_study/v1/final_runs/; analysis_verified/results.json',
         'Fixed reviewed theorem supplied with English. Autonomous NL-to-statement and end-to-end accuracy were not measured; no manual proofs enter model scores.','YES for full end-to-end claim'],
        ['M2','At least 60 distinct test / 15–20 development; five categories; disjoint families; provenance; publish ordered IDs/hash before testing.','PARTIAL',
         '15 development / 60 test, five categories, curated family separation, item sources, difficulty and internal hash freeze before inference.',
         'data/final_study/v1/freeze.json; heldout_launch.json; dataset_validation.json',
         'No evidence of public publication of the final ordered IDs/hash before testing. Local committed freeze is not external preregistration. Library/pretraining exposure remains possible.','YES unless internal freeze/deviation accepted for reduced pilot'],
        ['M3','Same failed initial, theorem, primary model, prompt/context/output caps and at most three retries; blind baseline versus real diagnostics.','PARTIAL',
         'All 60 initial pairings and 410 completed calls pass prompt/stream/target/feedback checks. 58 full pairs remain. Both arms share caps but diagnostics increase actual C input cost.',
         'docs/PAIRED_COMPARISON_AUDIT.md; analysis_verified/results.json; missingness_recovery.json',
         'Two unavailable C outcomes cannot be recovered under no-replay rules. Do not claim 60 complete pairs or equal realized input-token cost.','YES for complete 60-pair study'],
        ['M4','Review reference faithfulness; fixed reviewed targets in all arms; separate semantic from compiler/end-to-end success.','COMPLETE',
         'Approved-method AI review/adjudication binds all 75 eligible references; original 96-item labels include faithful/unfaithful/uncertain, retained disagreements and corrections; target is identical across arms.',
         'data/final_study/v1/ai_eligibility_policy.json; adjudications.json; data/ai_semantic_audit/20261028/delivery/summary.json',
         'Student-reported supervisor substitution, not independently authenticated correspondence. Author-assisted AI reference screening is not human-gold or generated-translation accuracy.','NO under reported substitution; limits must remain'],
        ['M5','Correct first-attempt/budget/error success, paired improvement/test, attempts, tokens, time, denominators and uncertainty.','COMPLETE',
         'Observed A=0/60, B=1/60, C=1/58; complete paired B=C=1/58. Pre-specified C=1/60 sensitivity is separate. Matched effects/intervals/tests, bounds, resource distributions and error outcomes regenerated.',
         'docs/FINAL_EXPERIMENT_RESULTS.md; analysis_verified/results.json; paired_resources.json; diagnostic_subtypes.json',
         'No informative discordance or power to establish equivalence. Timing confounded by ordering/cache/shared host.','NO; negative/inconclusive result is valid'],
        ['M6','One stable pinned Lean/Mathlib/model environment; check all final proofs for shortcuts; preserve manifests/hashes.','COMPLETE',
         f'Lean 4.32.0 / pinned Mathlib; every snapshot file hashed; {match[1]} tests/{match[2]} subtests; Lean build; fresh reference batch and both model-success exact-target/axiom checks; deterministic metrics and unchanged original artifacts.',
         'environment_verification.json; verification_steps.json; reproducibility_verification.json; reference_axiom_validation.json',
         'COMPLETE for local original-byte logs/metrics/proofs. Redacted public C prompts cannot provide exact original-byte inference replay. Immutable raw whitespace is preserved and not treated as editable source.','NO locally; disclose public limits'],
        ['M7','Empirical feedback question, recent related work, baselines, failure analysis, limitations and complete reproducibility details.','COMPLETE',
         f'Actual {pdf["pages"]}-page Springer pilot manuscript, four required main tables, two figures, five authentic before/after cases, correct missingness, genuine taxonomy and verified citations.',
         'paper/main.tex; paper/compiled_final_review_v2.pdf; manuscript_claims.json; paper_build_manifest.json; citation_verification.json',
         'Manuscript rewrite complete for reduced fixed-theorem pilot. Final independent editorial review, author/contact/affiliation choice and submission category/approval remain separate submission steps.','NO for rewrite; final submission checks remain']]
    data={'controlling_checklist':'docs/NL2Lean_TAIMMA2027_Student_Revision_Report(10).md','provenance':'User supplied checklist text; supervisor substitutions are student-reported, not independently verified.',
          'statuses':statuses,'requirements':[dict(zip(['id','professor_requirement','status','implementation_and_evidence','files','remaining_limitation','blocks_submission'],row)) for row in matrix],
          'full_study_submission_recommendation':'NO-GO','pilot_internal_review_recommendation':'GO for supervisor/editorial review only; not submission authorization.'}
    (BASE/'compliance_matrix.json').write_text(json.dumps(data,indent=2)+'\n')
    lines=['# Final M1–M7 compliance report','',
           'Controlling requirements: the user-supplied [professor checklist](NL2Lean_TAIMMA2027_Student_Revision_Report(10).md). The earlier blanket completion labels are replaced by this exact-scope mapping. COMPLETE describes the stated requirement, not conference acceptance.','',
           '| Requirement | Professor’s requirement | Status | Actual implementation / experiment evidence | Files | Remaining limitation | Blocks submission? |',
           '|---|---|---|---|---|---|---|']
    lines += ['| '+' | '.join(row)+' |' for row in matrix]
    lines += ['', '**Final full-study submission gate: NO-GO.** M1, M2 and M3 remain partial. M4 is complete only under the student-reported approved AI-review substitution; no human review is invented. M6 local reproducibility and M7 empirical manuscript rewrite now satisfy their exact requirements. Final submission readiness is separate from that implementation/evidence completeness.',
              '', 'A reduced, explicitly limited fixed-theorem pilot is prepared for supervisor review. It cannot retroactively publish a pretest freeze, fill the unavailable C calls or create an unmeasured end-to-end result. No new inference, push, merge or submission occurred in this review.']
    write('FINAL_M1_M7_COMPLIANCE_REPORT.md','\n'.join(lines))
    m=r['conditions'];rows=[]
    for c in ['A','B','C']:
        x=m[c];ci=x['wilson_95_observed'];rows.append(f'| {c} | {x["successes"]}/{x["observed_denominator"]} | {100*x["observed_rate"]:.2f}% | [{100*ci[0]:.2f}, {100*ci[1]:.2f}]% | {x["known_failures"]} | {x["unavailable"]} |')
    comparisons=[]
    for c in r['comparisons']:
        ci=c['family_bootstrap_95_complete_case'];comparisons.append(f'- {c["comparison"]}: {c["complete_pairs"]} matched cases; difference {100*c["risk_difference_complete_case"]:+.2f} percentage points; family-cluster interval [{100*ci[0]:+.2f}, {100*ci[1]:+.2f}]; exact p={c["exact_mcnemar_p"]}; Holm p={c["holm_adjusted_p"]}.')
    write('FINAL_EXPERIMENT_RESULTS.md','''# Final corrected experimental results

The primary observed and complete-case rates are separated from the internally frozen missing-as-failure sensitivity. There is no autonomous Stage-A or end-to-end accuracy estimate.

| Condition | Success / observed | Rate | Wilson 95% | Known failures | Unavailable |
|---|---:|---:|---|---:|---:|
'''+ '\n'.join(rows)+'''

The primary B/C comparison uses **58 complete pairs**, with B=C=1/58 (1.72%) on the same target, `lib_a_exp_add`. C−B is 0.00 percentage points and there are zero discordant pairs. The frozen helper reports McNemar as `null` / non-informative; conventionally p=1. Neither is evidence of equivalence. Complete-pair problem/family bootstrap intervals [0,0] are conditional on observed pairs, not missingness uncertainty. The matched subset has 52 family clusters; all 60 statements occupy 54.

The frozen protocol explicitly defines full-denominator missing-as-failure **sensitivity**. Under that coding C=1/60 (1.67%), with Wilson interval [0.29,8.86]%; it is not 60 measured C outcomes. Both missing C cases failed in B, so possible full-cohort C−B effects span 0 to +3.33 percentage points. These are identification bounds, not confidence limits or an equivalence margin.

'''+ '\n'.join(comparisons)+'''

There are **410 completed held-out responses**: 60 initial, 178 B repairs and 172 C repairs. The **412 durable logical intents** include one preflight context rejection and one header-only interruption; they are not 412 confirmed completed inference calls. The final frozen pilot has three cases / 21 responses, excluded from test estimates. No new inference was run during this revision.

Known physical completed-response totals: 362,035 input tokens, 130,401 output tokens, 11,233.6 native generation seconds. Shared initials are counted once physically and once per counterfactual condition row. Completed repairs per eligible case: B mean 2.97, C mean 2.87; C consumed-intent mean 2.90; both medians are three. Full resource distributions, including medians, are machine-readable. The same 58 complete cases have 230 completed responses per condition (including initials); paired per-problem resource comparisons are in `paired_resources.json`. No cost or duration is imputed for the unavailable response; completed-only costs are not full-run cost estimates.

One seed (2027), low success, related families, author-assisted AI adjudication, library/pretraining exposure, B-before-C order, cached loads and observed shared-host activity limit inference. No supported superiority, equivalence or causal latency claim is made.

Canonical reconstruction: `data/final_review/20261029_v2/analysis_verified/results.json`. Deterministic repeat: `analysis_repeat/results.json`. Original `data/final_study/v1/analysis/` is unchanged historical evidence. Every revised table/figure uses the canonical reconstruction; qualified old all-60 estimates remain separately labeled rather than overwritten.
''')
    write('PAIRED_COMPARISON_AUDIT.md','''# Formal paired comparison audit

All **60** test identities and **410** completed response/verification pairs were reconstructed from the raw evidence. The machine-readable per-case audit is `data/final_review/20261029_v2/analysis_verified/results.json` (`pairing_audits`, 60 entries), with exact record IDs and artifact paths. `case_outcomes.json` contains all A/B/C outcomes. No integrity discrepancy was found; reporting corrections are separately listed in `reporting_corrections`.

Checks cover identical failed initial hashes, the exact frozen theorem and model, fixed environment/prompt-template hashes, reconstructed prompts, durable intent hashes, native chat text, offline tokenization, complete token journals matching raw responses, maximum three repairs, genuine predecessor C diagnostics and fixed B feedback. Each actual compiled source is rebuilt from the exact candidate and target; successful raw Lean JSON and axiom dependencies are checked. C’s preflight rejection obeys the context stop rule; it is not a completed within-budget generation.

**58 B/C pairs are complete; two are incomplete.** Initials are shared in all 60. The common budgets are 8,192 total context / 2,000 output tokens and at most three repair calls. C’s actual input is longer because it contains diagnostics; equal realized input-token expenditure is not claimed. No reference proof is present in any reconstructed prompt. Named-library-lemma/pretraining exposure remains possible and is not disproved by prompt isolation. Curated families and exact statements are disjoint across splits; this is not proof of all mathematical/pretraining independence.

M3 remains **PARTIAL**. The fixed pilot planned three cases, not all fifteen development items. No prompt tuning or new condition was added after test outcomes, and no unavailable trajectory was backfilled.
''')
    missing=read(BASE/'missingness_recovery.json');details=[]
    for x in missing['missing_outcomes']:
        details.append(f'- `{x["problem_id"]}` / {x["logical_step"]}: {x["failure_class"]}; input {x["input_tokens"]:,} + output reservation {x["output_cap"]:,}, context cap {x["context_cap"]:,}. Durable frames: {x["durable_stream_frames"]}; durable generated tokens: {x["durably_observed_generated_tokens"]}. {x["reason"]} Intent: `{x["source_paths"][0]}`.')
    write('MISSING_C_OUTCOME_INVESTIGATION.md','''# Missing C outcome investigation

The two exact prompts were reconstructed from the correct predecessor and retokenized offline; both match their original intent hashes. No model weights were loaded for generation, no inference occurred, and no historical output or checkpoint was modified.

'''+ '\n'.join(details)+'''

Neither logical context has a durable completed response anywhere in the final-run artifacts. The context failure is a generation preflight resource failure, not a Lean timeout. The interrupted case has only a header, not a partial proof or resumable KV/RNG state. Its interruption cause is unknown. Both are terminal under the frozen runner and consume their intent.

**Recovery status: unavailable, not safely recoverable under the frozen protocol.** Repeating a seed is still a replay; altering caps, prompts, diagnostics or terminal statuses would change the study. New experiments require a separately versioned follow-up and cannot replace these records. Machine-readable evidence: `data/final_review/20261029_v2/missingness_recovery.json`.
''')
    write('REPRODUCIBILITY_CHECKLIST.md',f'''# Reproducibility verification

**M6: COMPLETE for the exact local professor requirement.** Complete does not mean all private original prompt bytes are publicly disclosed.

- Stable Lean 4.32.0 and Mathlib `81a5d257c8e410db227a6665ed08f64fea08e997` match frozen and live environment checks.
- Every model, weight, tokenizer and native chat-template file matches the frozen inventory. Qwen2.5-7B-Instruct 4-bit revision `c26a38f6a37d0a51b4e9a1eb3026530fa35d9fed`; runtime MLX 0.32.4 / MLX-LM 0.32.2 / Transformers 5.21.0 / NumPy 2.5.4 validated.
- Dataset manifest `{r['dataset_manifest_sha256']}` and protocol `{r['frozen_protocol_sha256']}` recalculate exactly. All frozen pinned source/template/environment files validate.
- The operative AI-review/freeze validator passes for 15 development / 60 test examples. Legacy human-review gates remain intact; AI records are not imported as human reviews.
- All 410 raw response/stream/prompt/target/verification bindings and 60 pairings validate. All 96 reference proofs freshly compile in the pinned environment. Both claimed final model successes freshly compile against exact targets with only allowed axioms; no `sorry`, `admit`, `sorryAx` or added assumptions are accepted as successes.
- {match[1]} Python tests and {match[2]} subtests passed; Lean build passed (8,658 jobs). Actual output/exit statuses: `data/final_review/20261029_v2/verification_steps.json` and its log paths.
- Metric regeneration is byte-identical in a fresh output directory. All {v['original_artifacts_checked']} original final-study artifacts retain their hashes. No inference was performed during verification.
- Editable source-file whitespace is checked separately. Original generated `.lean` evidence and CSV exports retain historical trailing whitespace/CRLF. They are immutable data, not source to normalize; old raw diff-check findings remain preserved, not relabeled as passing source checks.

Public evidence is a labeled redacted view. All candidate proof texts preserve original hashes, and aggregate/pairing reanalysis is public, but 172 C prompt byte strings differ because home paths in diagnostics are redacted. Original hashes/seeds/token counts still describe original bytes. Exact prompt replay and complete private source-evidence validation require the preserved original checkout; model weights and backend can be restored from pinned public revisions, but private exact paths cannot be reconstructed from the redacted bundle alone. No bit-identical cross-hardware generation claim is made.

Core evidence: `environment_verification.json`, `reproducibility_verification.json`, `reference_axiom_validation.json`, `verification_steps.json`, `analysis_verified/results.json`, and `analysis_repeat/results.json`, under `data/final_review/20261029_v2/`.
''')
    write('FINAL_PAPER_READINESS.md',f'''# Final paper readiness

The revised **{pdf['pages']}-page** Springer manuscript is `paper/main.tex`; PDF: `{pdf['pdf']}`; SHA-256 `{pdf['pdf_sha256']}`. The original 12-page identifiable PDF and original experiment results remain preserved. The new manuscript is a reduced fixed-theorem empirical pilot, not a claim of complete autonomous NL-to-Lean evaluation.

M7’s empirical rewrite is COMPLETE: the paper asks whether compiler diagnostics improve repair over equally call/output-capped blind retries, reports the negative/inconclusive outcomes, and includes four numbered required tables, two genuine figures, five actual before/after cases, an authentic compiler-error taxonomy, AI faithful/unfaithful/uncertain reference labels, recent direct repair/faithfulness work, and full public/private reproducibility limits. All ten cited keys were checked against primary sources; LeanDojo’s bibliography link was corrected. Actual model outputs and diagnostics, including failed/unchanged attempts, are preserved.

Observed A=0/60, B=1/60 and C=1/58 are distinguished from matched B=C=1/58 and the separately planned C=1/60 sensitivity. Matched point estimates, intervals and tests use the same populations. Missingness identification bounds and the degeneracy/low-power limitations are explicit. The one seed and three-case final pilot are disclosed. No compiler-feedback superiority, equivalence, independent-human semantics, external preregistration or measured end-to-end accuracy is asserted.

The compiled PDF passes actual text checks for counts, missingness, anonymity and unresolved markers. No overfull-box or unresolved-reference warning is present; ordinary bibliography underfull boxes remain. The current [TAIMMA call](https://easychair.org/cfp/taimma2027), checked 29 October 2026, recommends 12–15 full-paper pages and at least six short-paper pages; the current PDF is within the full-paper recommendation. Page count is not acceptance or category approval.

Remaining final manuscript/publication steps: independent final editorial review, final author/contact/affiliation choice, venue submission category, supervisor acceptance of the reduced scope/deviations, and explicit approval of the newly enumerated public payload. Author/contact information remains withheld in this release candidate. No affiliation or expert approval is invented.

**Full-compliance submission: NO-GO** because M1/M2/M3 remain partial. **Reduced pilot: ready for supervisor review**, not automatic submission. No new push/merge/submission is authorized by the prior version’s approval.
''')
    write('FINAL_SUBMISSION_GATE.md','''# Final submission gate

**Recommendation: NO-GO for a full M1–M7-compliant conference submission now.**

| Professor’s gate | Status | Evidence / unresolved point |
|---|---|---|
| Genuine model results (approved local MLX substitute) | PARTIAL | Genuine fixed-type proof synthesis exists; autonomous NL-to-statement / full end-to-end evaluation does not |
| Frozen independently checked test set | PARTIAL | 60 internally frozen AI-policy examples; no evidence that final ordered IDs/hash were public before testing; review is author-assisted AI under the reported substitution |
| Valid no-feedback retry baseline | COMPLETE | Every B prompt reconstructs to fixed blind feedback; 58 complete B/C pairs |
| Comparable budgets and paired study | PARTIAL | Same caps and initial candidate; two C outcomes missing; actual diagnostic input costs differ |
| Semantic evaluation | COMPLETE | Approved-method AI reference labels and exact targets; no human-gold or generated-translation accuracy invented |
| Correct metrics and reproducible evidence | COMPLETE | Explicit observed/paired/sensitivity denominators, pinned environment, strict proofs, deterministic metrics and disclosed private-public replay boundary |
| Claims match manuscript results | COMPLETE | Verified negative/inconclusive 14-page empirical pilot with limits and authentic examples |

The professor’s fallback is appropriate: reduce claims and seek review of an empirical pilot rather than imply complete full-study compliance. The prepared pilot is technically ready for that internal review. Submission still requires acceptance of its scope/deviations, final independent editorial review, final author/category decisions and explicit publication approval. A negative result itself is not a reason to reject the paper; missing requirements and unapproved scope changes are the present gate issues.

The two missing C outcomes cannot be safely backfilled; a pretest public freeze cannot be created retroactively; unmeasured statement-generation accuracy cannot be manufactured. Additional studies must be separately versioned. The previously approved publication bundle was pushed and merged earlier in the conversation; this revision is new and has NOT been pushed or merged.
''')
    subtype=read(BASE/'diagnostic_subtypes.json');tr=[]
    for t in subtype['groups']:
        b=t['B_successes'];c=t['C_successes'];tr.append(f'| {t["tag"]} | {t["examples"]} | {b}/{t["B_observed"]} ({100*b/t["B_observed"]:.1f}%) | {c}/{t["C_observed"]} ({100*c/t["C_observed"]:.1f}%) | `{t["representative_id"]}` |')
    write('COMPILER_ERROR_TAXONOMY.md','''# Genuine compiler-error taxonomy

The main paper preserves the pre-specified, mutually exclusive initial-error classifier: 26 parser/syntax, 20 unknown-name, nine tactic/goals, four type/elaboration and one other case. C is unavailable once in parser and once in tactic/goals. The only solved target is in the unknown-name group (B=C=1/20); all other observed repairs fail. These groups support descriptive error outcomes, not subgroup significance claims.

The following **post-hoc overlapping message tags** refine the actual initial diagnostics. A case can belong to several rows, so counts must not be summed. Unknown identifier and theorem/lemma names are not distinguished without evidence from compiler text. Tactic and unsolved-goal tags may co-occur.

| Message tag | Examples | B solved/observed | C solved/observed | Authentic representative |
|---|---:|---:|---:|---|
'''+ '\n'.join(tr)+'''

Actual full representative messages and author-assessed potential actionability are in `data/final_review/20261029_v2/diagnostic_subtypes.json`. For example, an unavailable symbol localizes a name problem; failed instance synthesis localizes incompatible operand/application types; an unsolved goal states a remaining proof obligation. These are potentially useful diagnostics, not measured helpfulness ratings or a guarantee the model follows them. Groups below five examples remain small descriptive cases. No initial Lean timeout/resource-exhaustion case occurred; the context rejection happened before model generation, separately from Lean compilation. All 408 failed completed candidate verifications are compiler errors, and the original all-attempt primary event counts are preserved separately from problem counts.
''')
    print('Exact checklist, corrected metrics, pairing, missingness, taxonomy, reproducibility and submission-gate reports written.')


if __name__=='__main__':main()
