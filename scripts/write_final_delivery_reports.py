"""Deliver reports from actual completed runs, tests, build and PDF evidence."""
from pathlib import Path
import json
import re
import shutil
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from final_study import BASE,read,sha,validate_protocol,validate_freeze

def main():
    protocol=ROOT/'configs/repair_experiment_local_v0.4.2.json';p=validate_protocol(protocol);v=validate_freeze();r=read(BASE/'analysis/results.json');render=read(BASE/'analysis/rendered_evidence.json')
    build=read(BASE/'paper_build_manifest.json')
    if build['exit_code']!=0 or sha(ROOT/build['pdf'])!=build['pdf_sha256']:raise ValueError('Final PDF build is absent/changed')
    tests=(BASE/'pytest_final.log').read_text();testmatch=re.search(r'(\d+) passed, (\d+) subtests passed',tests)
    if not testmatch or 'failed' in tests.casefold():raise ValueError('Full final tests did not pass')
    if 'Build completed successfully' not in (BASE/'lake_build_final.log').read_text():raise ValueError('Final Lean build did not pass')
    history=BASE/'history';history.mkdir(exist_ok=True)
    names=['FINAL_M1_M7_COMPLIANCE_REPORT.md','FINAL_EXPERIMENT_RESULTS.md','FINAL_DATASET_COMPLETION.md','FINAL_PAPER_READINESS.md']
    for name in [*names,'LOCAL_MODEL_EXECUTION_REPORT.md']:
        original=ROOT/'docs'/name;copy=history/('preexecution_'+name)
        if original.exists() and not copy.exists():shutil.copyfile(original,copy)
    condition_lines=[]
    for name in ['A','B','C']:
        c=r['conditions'][name];ci=c['wilson_95'];attempts=render['condition_resources'][name]['actual_repair_generation_attempts']
        condition_lines.append(f'| {name} | {c["successes"]}/60 | {100*c["success_rate"]:.1f}% | [{100*ci[0]:.1f}, {100*ci[1]:.1f}] | {c["incomplete"]} | {attempts} |')
    table='| Condition | Verified | Rate | Wilson 95% (%) | Missing | Repair attempts |\n|---|---:|---:|---|---:|---:|\n'+'\n'.join(condition_lines)
    comparisons=[]
    for c in r['comparisons']:
        ci=c['family_cluster_bootstrap_95'];comparisons.append(f'- {c["comparison"]}: {100*c["difference_missing_as_failure"]:+.1f} pp; family-cluster 95% [{100*ci[0]:+.1f}, {100*ci[1]:+.1f}] pp; complete pairs {c["complete_pairs"]}; exact McNemar p={c["exact_mcnemar_p"]}; Holm p={c["holm_adjusted_p"]}.')
    approval=('The user directly reported supervisor approval of AI-assisted semantic review replacing independent human semantic review, and free local MLX replacing Groq. Report date: **28 October 2026**. Actual supervisor decision date is unknown. Evidence is the student\'s direct report, **not independently verified**; no supervisor document, identity, signature or original date has been invented. Exact implementation choices were made under the user\'s explicit execution authorization.')
    evidence='`data/final_study/v1/` contains the frozen datasets, policy, reported approval, corrections, pilot audit, launch record, actual runs, analysis and final verification. The final protocol is `configs/repair_experiment_local_v0.4.2.json`.'
    limits=('Limits: one primary seed (2027), one general instruction model and quantization; 60 test statements in 54 curated family clusters, rather than 60 independent topic families; five development clusters; author-assisted AI adjudication and unreliable independent-model judgments; named-lemma/pretraining exposure; fixed-theorem proof synthesis rather than unrestricted NL translation; B-before-C order and host/cache effects on timings. These limits remain explicit rather than being concealed as completed multi-seed or independent-human validation.')
    compliance=f'''# Final M1–M7 compliance report

The frozen single-seed study reached terminal records for all 60 cases, with 58 complete A/B/C comparisons and two unavailable C outcomes. Technical delivery does not imply full completion of every requested experiment. The student-reported substitutions and explicit execution instruction cover M1–M6; no further experiment approval is required. Negative or unverified model outputs are retained as outcomes, not repaired manually. No automatic merge or submission occurred.

{approval}

| Requirement | Status | Delivered evidence | Exact remaining work / limit; approval needed |
|---|---|---|---|
| M1 genuine generation | COMPLETE | 60 frozen held-out cases, actual MLX generations and Lean checks | One planned seed, not three-seed robustness |
| M2 dataset | COMPLETE | 15 development / 60 test, five categories, source evidence, ordered hashes, no cross-split curated family overlap | AI-policy eligibility; 54 test families, not 60 independent families |
| M3 A/B/C | PARTIAL | One shared initial, matched model/environment/output budgets, at most three B/C repairs, no B diagnostics, latest genuine C diagnostics | 58 complete pairs; two unavailable C outcomes retained without replay; final pilot covers 3 of 15 development items |
| M4 semantics | COMPLETE | 75 source-eligible AI-adjudicated references, corrected/reviewed original pairs preserved, zero invented human reviews | AI adjudication is not measured human semantic accuracy |
| M5 analysis | COMPLETE | Actual rates, intervals, exact McNemar/Holm, family sensitivity, calls/tokens/timing, error outcomes and authentic examples | No unsupported significance or equivalence claim |
| M6 verification | PARTIAL | {testmatch[1]} Python tests and {testmatch[2]} subtests; Lean build; dataset/result validators; source/evidence hashes | Full diff whitespace check flags preserved raw evidence; scientific validators, tests and Lean pass. Reproduction remains backend/hardware scoped |
| M7 paper | PARTIAL | Actual empirical methods/results, four required numbered tables, two figures, qualitative examples, compiled PDF | No institutional affiliation supplied; venue-specific final submission checks remain; separate submission authorization needed |

{table}

{evidence}

Final protocol SHA-256: `{sha(protocol)}`. Final PDF: `{build['pdf']}`, SHA-256 `{build['pdf_sha256']}`. Source implementation was committed before held-out generation at `{read(BASE/'heldout_launch.json')['source_git_commit']}`. Original Groq, pre-results artifacts and exploratory protocols/runs are preserved and excluded from empirical estimates.

{limits}
'''
    experiments=f'''# Final genuine experimental results

{approval}

All 60 frozen eligible held-out statements were processed under one seed, 2027, using the exact cached Qwen2.5-7B-Instruct 4-bit snapshot. The final development pilot and actual no-new-generation resume check passed control/provenance validation. Pilot model failures were not counted as held-out results.

{table}

Full-denominator rates and Wilson intervals count missing outcomes as failures for sensitivity; paired tests use complete matched outcomes. Incomplete trajectories: **{r['incomplete_trajectories']}**. Individual/problem-level inference assumes independence; family-cluster intervals address the recorded related-target grouping. `None` McNemar p-values mean no informative discordant-pair test, not equivalence.

'''+'\n'.join(comparisons)+f'''

Actual generation attempts: **{r['actual_unique_generation_attempts']}**; completed generations: **{r['actual_unique_generation_calls']}**. Known completed-call prompt tokens: **{r['actual_unique_prompt_tokens']:,}**; completion tokens: **{r['actual_unique_completion_tokens']:,}**. Physical totals count the shared initial once, while each condition's counterfactual resource row includes it. Complete native generation seconds: **{r['actual_unique_generation_seconds']:.1f}**; recorded trajectory wall seconds: **{r['actual_trajectory_wall_seconds']:.1f}**. Unknown interrupted-call endpoints are not invented.

Actual outputs: `analysis/results.json`, `condition_results.csv`, `initial_failure_outcomes.csv`, `rendered_evidence.json`, `selected_qualitative_examples.json`; all relative to `data/final_study/v1/`. Figures and four main tables are under `paper/generated/final_*`. The selected authentic examples are {', '.join(render['selected_examples'])}; their display-only snippets are truncated/transliterated, while original Unicode outputs remain unchanged.

{limits}

No paid inference, fabricated score, manual proof counted as model output, hidden retry or retrospective protocol change was used.
'''
    experiments+='\nRepair calls per eligible problem (60-case denominator, including zeros and consumed interrupted intents):\n\n'
    for name in ['A','B','C']:
        resource=render['condition_resources'][name]
        experiments+=f"- {name}: mean {resource['mean_repair_attempts_per_eligible_problem']:.2f}; median {resource['median_repair_attempts_per_eligible_problem']:.1f}.\n"
    experiments+='\nA read-only process sample identified another local MLX workload on the host during execution. Its duration and overhead were not measured; timing is observed shared-host performance, not an isolated-hardware benchmark. See `runtime_observations.json`.\n'
    experiments+=f"\nIncomplete generation streams additionally preserve **{render['observed_partial_generation_tokens']}** observed output tokens. These are retained partial tokens, not completed responses or an invented exact total beyond the durable stream; completed-call totals above exclude them.\n"
    experiments+='\nUnavailable condition outcomes and recorded causes:\n\n'
    for detail in render['incomplete_condition_outcomes']:
        experiments+=f"- `{detail['problem_id']}` / {detail['condition']}: {detail['category']}; {detail['status']}.\n"
    if not render['incomplete_condition_outcomes']:experiments+='- None.\n'
    experiments+='\nCheckpoint recovery preserved an interrupted generation without replay. Its trajectory elapsed wall time includes the inactive interval before recovery and must not be read as uninterrupted compute time. Exact recovery records and hashes are in `data/final_study/v1/resume_history/`.\n'
    dataset=f'''# Final dataset completion

Status: frozen and valid under the expressly authorized AI-assisted eligibility policy v1.0. Historical independent-human gates remain unchanged and are not misrepresented as passed; the new policy/validator is explicit and versioned.

| Measure | Actual count |
|---|---:|
| Original candidates inspected | 96 |
| Exact duplicate excluded | 1 |
| Other source-insufficient records excluded | 20 |
| Frozen AI-eligible development | 15 |
| Frozen AI-eligible held-out test | 60 |
| Mathematical categories | 5 |
| Development / test curated families | 5 / 54 |
| Cross-split family overlap | 0 |
| Textbook / formal-library-derived items | 16 / 59 |
| Independent human semantic reviews claimed | 0 |

The missing positive-modulus assumption and ambiguous summation endpoints were corrected, their affected proofs reverified and separate-model review repeated. The separate reviewer remained fallible; explicit AI adjudication resolves its incorrect literal/mathematical objections. Both corrected original items remain excluded for source-provenance gaps. Original records, corrections, raw reviews and mathematical checks are preserved.

Eligibility requires a faithful content-bound AI adjudication with no remaining semantic uncertainty, strict reference proof/type evidence, item-level source and published-license evidence with attribution, no exact duplicate, and curated whole-family split assignment. Invalid/placeholder reviewer outputs are never faithful votes. This is an AI-assisted source assessment, not fabricated legal permission or human review. The historical curation fields are preserved; `study_eligibility` and the new policy are authoritative for this approved-method study.

Ordered IDs, exact bytes and hashes: `data/final_study/v1/freeze.json`; full criteria: `ai_eligibility_policy.json`; actual decisions: `adjudications.json`; excluded IDs: `excluded.json`; attribution: `ATTRIBUTION.md`. All selection and final protocol freezing precede held-out proof generation. No theorem/dataset/prompt/model/budget was changed in response to held-out outcomes.

{approval}
'''
    paper=f'''# Final paper readiness

The empirical manuscript is `paper/main.tex`; the actual compiled PDF is `{build['pdf']}`. It reports genuine recorded outcomes, including failures and missingness, under the exact frozen local protocol. PDF SHA-256: `{build['pdf_sha256']}`. The build manifest records the exact TeX/bibliography/generated-table/figure hashes and actual compiler exit status.

It includes the research question, related work, fixed-type architecture, dataset/source/AI review, matched A/B/C design, exact model configuration, actual results and planned statistics, family-cluster sensitivity, error taxonomy, authentic qualitative examples, limitations and reproducibility. Main numbered Tables 1–4 are dataset composition, A/B/C results, error outcomes and semantic-review evidence; Figures 1–2 show success by budget and initial-error repair outcomes. Paired-test and resource matrices are unnumbered supplements in the results section.

Author name and correspondence are the user's supplied **Sadia Peerzada**, **sadiapeerzada2006@gmail.com**. No institutional affiliation was supplied or invented; the author block contains contact only. Conference-specific page limits, affiliation requirements and submission details still require final confirmation. No automatic submission is claimed.

Quantitative manuscript substitutions are generated from actual analysis, with a claims manifest and consistency checks against raw verifier successes. Original pre-results PDFs, authoring attempts, manual illustrations and old protocols remain historical artifacts; they are not empirical model evidence.

{approval}

{limits}
'''
    for name,text in zip(names,[compliance,experiments,dataset,paper]):(ROOT/'docs'/name).write_text(text)
    local=f'''# Final local model execution report

The genuine development pilot and full 60-case held-out study ran with free local MLX inference. {approval}

Exact protocol: `configs/repair_experiment_local_v0.4.2.json`; Qwen2.5-7B-Instruct 4-bit snapshot `c26a38f6a37d0a51b4e9a1eb3026530fa35d9fed`. Every model/tokenizer/template file is bound by `data/local_model/20261027/model_inventory.json`. Runtime: MLX 0.32.4, MLX-LM 0.32.2, Transformers 5.21.0; Apple M4, 16 GiB. The frozen configuration uses one seed 2027, temperature 0.2, top-p 1, 2000 output tokens, 8192 context tokens and at most three repairs per branch. Exact environment/source checks occur before execution.

{table}

Actual held-out generation attempts: {r['actual_unique_generation_attempts']}; completed generations: {r['actual_unique_generation_calls']}; incomplete trajectories: {r['incomplete_trajectories']}. Native model responses, streams, prompts, per-call seeds, timing, strict compiler diagnostics and manifests are preserved in `data/final_study/v1/final_runs/heldout/2027/`. Pilot and interrupted developmental prototypes are retained separately and excluded from study estimates. The actual final pilot resume generated no additional calls.

Model weights are released before Lean and reloaded from identical verified bytes for each independent generation. The actual common initial is counted once physically. A separate MLX workload was observed on the host during execution; its contribution to latency was not measured. Wall times describe this host, not isolated hardware or a causal speed comparison.

No paid API, fallback provider, manually supplied proof counted as model output, hidden replay, or retrospective protocol amendment was used. The earlier Groq and disabled local proposal remain historical artifacts; the final study uses the explicit new AI-policy validator and does not relabel human-review fields.

See `docs/FINAL_EXPERIMENT_RESULTS.md`, `docs/FINAL_EXECUTION_REPRODUCIBILITY.md`, and the raw artifact directory for exact statistics, source hashes and reproduction.
'''
    (ROOT/'docs/LOCAL_MODEL_EXECUTION_REPORT.md').write_text(local)
    summary={'status':'completed_frozen_single_seed_study','eligible':v['eligible_counts'],'test_families':r['test_families'],'conditions':r['conditions'],
        'comparisons':r['comparisons'],'tests_passed':int(testmatch[1]),'subtests_passed':int(testmatch[2]),'pdf':build['pdf'],'pdf_sha256':build['pdf_sha256'],
        'protocol_sha256':sha(protocol),'independent_human_reviews':0,'supervisor_approval_evidence_status':'student_reported_not_independently_verified','automatic_merge':False}
    (BASE/'final_delivery_summary.json').write_text(json.dumps(summary,indent=2)+'\n');print('All four required final reports written from completed real artifacts.')

if __name__=='__main__':main()
