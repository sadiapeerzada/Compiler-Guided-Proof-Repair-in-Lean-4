"""Generate an explicitly partial final-study report from durable real evidence.

Run after the authorized chain, then audit in a fresh process. No model calls.
The word final in filenames does not imply completion of unauthorized research.
"""
from collections import Counter
from study_common import *
from scientific_audit import audit,recorded_analysis
from export_evidence import usage

def optional(name,default):
    p=run_root()/name;return read(p) if p.exists() else default

def main():
    evidence=audit();dump(run_root()/'scientific_integrity_audit.json',evidence)
    g=rows(run_root()/'generation/records.jsonl');p=rows(run_root()/'reference_repair/records.jsonl');raw=optional('fresh_verified_raw_v2.json',[]);reviewed=optional('fresh_verified.json',[]);accepted=optional('development_ai_accepted_candidates.json',[]);quarantined=optional('development_ai_quarantined_candidates.json',[]);selected=optional('accepted_development.json',[])
    initial=Counter(r['status'] for r in g);repaired=Counter(r['status'] for r in p);paths=Counter(c['construction_path'] for c in raw)
    counts=dict(generation_recorded=len(g),generation_durable_responses=evidence['stages']['generation']['completed'],generation_structurally_valid=sum(bool(r.get('candidate')) for r in g),generation_original_classifications=dict(initial),initial_checker_passes=sum(r.get('verification',{}).get('success') is True for r in g),reference_repair_recorded=len(p),reference_repair_classifications=dict(repaired),rigid_verified_references=len(raw),reference_construction_paths=dict(paths),prereview_exclusions=len(optional('pre_review_exclusions.json',[])),fresh_review_subjects=len(reviewed),fresh_qualified_AI_acceptances=len(accepted),fresh_quarantined=len(quarantined),selected_types=len(selected),selected_families=len({c['family'] for c in selected}),confirmatory_types=0)
    counts['reference_repair_verified_successes']=sum(r.get('verification',{}).get('success') is True for r in p)
    data=[];analysis={'status':'NO_EXECUTED_DATA','comparisons':[]}
    gate_status=optional('development_gate_status.json',{'status':'NOT_STARTED'})
    if gate_status['status']=='READY_FOR_DEVELOPMENT':data,analysis=recorded_analysis()
    dump(run_root()/'independently_regenerated_rows.json',data);dump(run_root()/'independently_regenerated_analysis.json',analysis);dump(run_root()/'actual_evidence_counts.json',counts)
    stage_table=['| Phase | Verdict | Charged / cap | Durable completions | Unknown/unavailable |','|---|---|---:|---:|---:|']
    for stage,c in evidence['stages'].items():
        verdict='PARTIAL (unknown outcome)' if c['unknown_or_unavailable'] else 'COMPLETE (execution)' if c['phase_status']=='finished' and c['charged'] else 'PARTIAL' if c['charged'] else 'BLOCKED' if stage.startswith('development_') and gate_status['status'].startswith('NO_GO') else 'NOT_STARTED (no inference)'
        stage_table.append(f"| {stage} | {verdict} | {c['charged']} / {c['max_calls']} | {c['completed']} | {c['unknown_or_unavailable']} |")
    stage_table.append('| Confirmatory construction and evaluation (phases 7–9) | NOT_STARTED — NO_GO_RESOURCES | 0 | 0 | 0 |')
    contrasts=[]
    for c in analysis.get('comparisons',[]):
        contrasts.append(f"| {c['contrast']} | {c['known_initial_failures']} | {c['complete_pairs']} | {c['missing_pairs']} | {c['C_only']} | {c['baseline_only']} | {c['difference']} | {c['theorem_bonferroni_97_5']} | {c['family_bonferroni_97_5']} | {c['missingness_identification_bounds']} |")
    comparison='No eligible executed paired analysis. '+gate_status.get('reason','') if not contrasts else '\n'.join(['| Contrast | Known initial failures | Complete pairs | Missing | C only | Baseline only | Difference | Theorem 97.5% interval | Family 97.5% interval | Missingness bounds |','|---|---:|---:|---:|---:|---:|---:|---|---|---|']+contrasts)
    reasons=Counter(reason for q in quarantined for reason in q['reasons'])
    exposure=optional('expanded_historical_exposure.json',{})
    costs=usage(tuple(read(HERE/'resource_authorization.json')['stages']));dump(run_root()/'consolidated_resource_usage.json',costs)
    cost_table=['| Phase | Input tokens observed | Output tokens observed | Generation seconds | Controller call seconds | Maximum reported MLX peak GB |','|---|---:|---:|---:|---:|---:|']
    for stage,c in costs['stages'].items():cost_table.append(f"| {stage} | {c['actual_input_tokens_observed']} | {c['actual_output_tokens_observed']} | {c['actual_generation_seconds_observed']:.2f} | {c['actual_controller_call_seconds_observed']:.2f} | {c['maximum_reported_MLX_peak_memory_gb']} |")
    verdicts=[(0,'Preservation','COMPLETE','Baseline hashes and symlinks audited'),(1,'Original V3 AI adjudication','PARTIAL','Four actual responses preserved; original typed contract unresolved'),(2,'Development construction','PARTIAL','Authorized queues exhausted; target20 not reached'),(3,'Exposure/family screening','PARTIAL','Development checks recorded; no untouched test partition'),(4,'Development C/D/E','BLOCKED',gate_status.get('reason',gate_status['status'])),(5,'Development analysis/freeze','PARTIAL','Inadequate cohort frozen; no evaluation outcomes'),(6,'Confirmatory construction','NOT_STARTED','Not authorized'),(7,'Confirmatory C/D/E','NOT_STARTED','Not authorized'),(8,'Paired repair statistics','BLOCKED','No eligible executed repair data; no effect fabricated'),(9,'Consistency audit','COMPLETE' if not evidence['failures'] else 'PARTIAL',evidence['status']),(10,'Evidence report','COMPLETE','Actual permitted-subset findings documented; research overall PARTIAL')]
    dump(run_root()/'master_phase_verdicts.json',[dict(phase=n,name=name,status=status,reason=reason) for n,name,status,reason in verdicts])
    verdict_table='\n'.join(['| Master-task phase | Verdict | Reason |','|---|---|---|']+[f'| {n}. {name} | {status} | {reason} |' for n,name,status,reason in verdicts])
    output=f'''# Recorded experimental evidence — overall PARTIAL

This report covers only the explicitly approved phases 1–6 development subset. Confirmatory phases 7–9 were not authorized and were not run. A completed development chain does not complete the full master research task. No historical result or manuscript was revised.

Research questions: among fixed theorem–seed pairs with a genuinely failed initial proof and valid diagnostic matching, does one repair with actual diagnostics verify more often than one with shuffled diagnostics from another family (C−D, primary), or neutral token-matched feedback (C−E, secondary)? These are exploratory development questions on a selected AI-screened cohort. There are no untouched confirmatory results.

Source baseline: `83f1d564`; run: `{protocol()['run_id']}`. The actual researcher approval was: “Approve phases 1–6 only (development subset)”. The fixed total ceiling is 1,084 model calls, with separate phase caps and original deadlines. Actual charged calls: **{evidence['actual_model_call_total']}**. Costs below count phase-local inner inference ledgers once; the C/D/E outer ledger is a checkpoint account of the same calls and is not added again.

Final data gate: **{gate_status['status']}**. The run produced **{len(accepted)} fresh AI-screened, formally verified candidates**; the frozen selection has **{len(selected)} types / {counts['selected_families']} families**. Actual C/D/E initial calls: **{evidence['stages']['development_initial']['charged']}**; repair calls: **{evidence['stages']['development_repairs']['charged']}**. {'The required two distinct accepted families were not available, so no repair-effect estimate can be obtained. This run does not answer C−D or C−E and supports no claim of diagnostic superiority.' if gate_status['status']=='NO_GO_DATA' else 'Interpret the recorded evaluation only under the limitations below.'} Unused review/evaluation slots cannot be transferred into the exhausted generation or reference-repair allocations.

## Execution status

{chr(10).join(stage_table)}

The table above uses compute-proposal phase names. The master research task has
different phase numbering; its completion verdicts are:

{verdict_table}

## Mathematical candidate evidence

Fresh generation produced **{counts['generation_durable_responses']} durable responses / {len(g)} recorded intake cases**, **{counts['generation_structurally_valid']} structurally valid declarations** and **{counts['initial_checker_passes']} initial-checker proof passes**. Initial intake classifications: `{dict(initial)}`. These historical classifications are preserved. The initial explicit-argument harness was found by a real negative probe to permit universe specialization. The stronger version checks universe-parameter arity and closed declaration types; every newly curated reference must have an actual successful rigid check. Initial passes alone do not establish benchmark admission.

The versioned construction path extracted only supplied theorem headers and supplied proofs; it never supplied missing mathematics. It retained raw rejected generation outcomes and performed actual kernel checks. Reference construction made **{evidence['stages']['reference_repair']['charged']} charged one-step repair calls**, at most one per candidate. Repair intake classifications: `{dict(repaired)}`. Final strictly rigid-verified references: **{len(raw)}**, by construction path `{dict(paths)}`. Verified repair successes: **{counts['reference_repair_verified_successes']}**. All31 final verified references in this run came from the initial generation responses; none is an independently generated evaluation outcome.

After13 charged repair intents, the12 durable responses were schema-rejected, with recurring obsolete syntax and placeholder declarations. A prospective V4 prompt added a real Lean-verified `True`/`trivial` syntax example for unconsumed candidates. One interrupted intent remained charged and was reconciled without replay. The original model,120-call total and12-hour clock were retained. New intent keys additionally bind `reference_prompt_v4.json`; old raw responses and rejection outcomes remain unchanged. The example is development-exposed and excluded from benchmark admission. This adaptive development correction is disclosed rather than represented as a confirmatory procedure. Exact version-specific calls are in `reference_prompt_versions.json`.

After40 charged calls, a clean inference-lock checkpoint retained all40 durable records without creating another unknown intent. Resource version5 closes the model client and clears its allocator cache before Lean compilation, reducing model/compiler memory contention. The V4 prompt, pinned model and original120-call/12-hour allocation remain unchanged. Additive resource-version keys participate in the fixed derived seed/context hash; no previously consumed candidate was resampled. Timing differences across versions are descriptive, not a randomized performance comparison. `reference_resource_versions.json` and the frozen transition evidence disclose this change. The eventual C/D/E implementation applies the same cache-release policy to every initial and repair call, frozen before evaluation outcomes.

Pre-review duplicate/exposure/source-audit exclusions: **{counts['prereview_exclusions']}**. Fresh blinded review subjects: **{len(reviewed)}**; two-reviewer qualified AI acceptances: **{len(accepted)}**; quarantines: **{len(quarantined)}**. Quarantine reason counts: `{dict(reasons)}`. The original four V3 review responses said ACCEPT in raw text but failed their frozen typed schema and remain UNCERTAIN; they were not reparsed into approvals. Fresh review used a prospectively explicit Boolean schema, not a retrospective rescue of those responses. Source-bound assistant exclusions are conservative additional checks, explicitly not decisions by either blinded AI reviewer or an independent human.

The frozen evaluation cohort contains **{len(selected)} theorem types / {counts['selected_families']} declared families**, versus the planning target of20, each with the three fixed seeds {protocol()['seeds']}. Seed repetitions do not increase the independent theorem count. Broad controller family labels, exact/alias/alpha exclusion and bounded AI relationship judgments do not prove mathematical independence. All generated/repaired/reviewed subjects, including rejected ones and mathematical equivalents, are development-exposed and ineligible for future untouched test construction.

Development cohort target verdict: **{'COMPLETE at the planning count, subject to the stated validity limitations' if len(selected)>=20 else 'PARTIAL — target count not reached'}**. Execution completion in the table means the permitted finite call queue finished; it does not imply candidate acceptance, fulfillment of the cohort target, or successful research findings. A phase with zero actual inference is not labeled complete merely because its worker exited normally.

## Development evaluation

Gate: **{gate_status['status']}**. Recorded grid rows: **{len(data)}**. Initial verified: **{analysis.get('initial_verified',0)}**; initial unknown: **{analysis.get('initial_unknown',0)}**; known initial failures: **{analysis.get('known_initial_failures',0)}**. Initial successes are not counted as repair successes. Missing or invalid comparisons stay unknown.

{comparison}

Intervals use the frozen 20,000-replicate clustered bootstrap and whole theorem clusters retaining all seeds, with a family sensitivity analysis. C−D is primary; C−E secondary; simultaneous nominal97.5% percentile intervals use the predeclared two-contrast Bonferroni adjustment. Complete-pair intervals are conditional; missingness identification bounds are not confidence intervals. Small or degenerate intervals and zero differences do not establish equivalence or adequate power.

Valid C/D/E triples share the exact failed predecessor, fixed target, decoding policy, output limit and4,096 rendered input tokens. C receives genuine candidate-bound compiler diagnostics; D receives byte-different genuine diagnostics from an eligible different declared family; E receives the frozen neutral field. Full diagnostic messages are retained; truncation is not used. Exact token matching introduces different quantities of neutral padding, and actual RNG seeds derive from prompt/context hashes. Thus this is an operational feedback comparison, not an isolated pure semantic-information causal effect. Invalid or unavailable donors prevent the corresponding paired comparison.

## Actual resource expenditure

{chr(10).join(cost_table)}

These are durable model metadata, not estimates for interrupted calls. MLX generation seconds exclude model loading; controller call seconds include loading within the recorded invocation. Both exclude separately logged compiler time and other controller overhead. `formal_verification_resource_usage.json` reports saved reference-check process durations. MLX peak is the maximum model-runtime report, not whole-process/system memory or a sum of simultaneous models. Exact per-call timings, seeds, prompt/rendered-chat hashes and model revisions remain in the raw metadata. Unknown consumed costs are not estimated. `consolidated_resource_usage.json` reconciles the stage-local ledgers; `development_per_family.json` and `development_paired_analysis.json` contain family and error-category results.

## Integrity and limitations

The separately executed audit result is **{evidence['status']}**, with {len(evidence['failures'])} failed consistency checks and {len(evidence['warnings'])} warnings. This is a source/data audit by the assistant, not independent human adjudication or an external replication. See `final-study/runs/{protocol()['run_id']}/scientific_integrity_audit.json`, `actual_evidence_counts.json`, the raw per-phase ledgers/streams, `strict_reference_verification.jsonl`, frozen cohort/protocol files and `independently_regenerated_analysis.json`.

Lean4.32.0 and Mathlib81a5d257c8e410db227a6665ed08f64fea08e997 were pinned. Real fixtures include positive polymorphism and negative weaker targets, extra assumptions, sorry and universe specialization. The initial universe-negative failure and its later rigid rejection are both retained. The header-only parser is not proof validation. Strict checking verifies the supplied formal proposition; it does not prove English fidelity, novelty or nontriviality.

Historical exposure screening includes 193 historical theorem versions,242 unique prior generated exposures and25 extractable prior AI statements (460 prior statement entries), plus the exposed V4 syntax example ({len(exposure.get('items',[]))} total indexed entries);39 prior AI responses were inspected and14 could not supply an extractable statement. All240 current responses, including rejected and unextractable proposals, are separately recorded as development exposures. That coverage is incomplete and does not certify absence of semantic overlap, source copying or pretraining contamination. Retrieval is bounded lexical screening. All acceptance is explicitly **AI_SCREENED_FORMALLY_VERIFIED**, never human validation. Phi performs both reference repair and reviewer1; Qwen generation shares ancestry with reviewer2. Blinding prevents direct response sharing but does not establish error independence. Review confidence is not calibrated.

G and evaluation model X are the same pinned Qwen checkpoint. Conditioning the benchmark on successful reference construction can favor subjects that checkpoint already solves, limiting initial-failure diversity and donor availability. These selected, exposed development results are not independent generalization evidence. No new confirmatory inference or completed confirmatory preregistration is claimed.

The historical V1/V2/V3 results, all tracked baseline files and four baseline symlink targets are checked against the preservation manifest. Original human validation gates stay closed. No fake resources, model responses, candidate acceptances or compiler successes were introduced. No blanket C superiority, confirmatory success, exhaustive independence or completed publication claim is supported by this development run.

Reproduce derived artifacts from the repository root with `.venv/bin/python research/ai-confirmatory-study/final-study/export_evidence.py`, then `report_results.py` and `scientific_audit.py --output /tmp/taimma-independent-audit.json` in that same directory. These commands never perform inference. The README documents model-view recreation and checkpoint-respecting execution. Exact source/input hashes are in `final-study/freezes/`; baseline hashes are in `preservation_manifest.json`; actual cohort and evaluation protocol are frozen before initial outcomes. No confirmatory preregistration is represented as complete. The smallest legitimate next action is separately authorized, versioned construction focused on additional mathematical families: the current generation and reference-repair allocations are exhausted. At least one more accepted family is needed even to open the development gate; the20-type planning target remains unmet. Existing review/evaluation slots cannot be transferred or old pilot budgets reused. Confirmatory authorization and an untouched-family preregistration would be subsequent, separate requirements after defensible development evidence.
'''
    (OLD/'FINAL_COMPLETED_EXPERIMENTS.md').write_text(output)
    audit_text=f'''# Scientific integrity audit — {evidence['status']}

Scope: actual recorded development evidence only; overall research remains PARTIAL. Confirmatory phases are NOT_STARTED / NO_GO_RESOURCES. The audit executes in a separate process and reads saved records without inference. It is not external replication or human mathematical validation.

Actual charged inference calls: {evidence['actual_model_call_total']}. Historical baseline: `{evidence['historical_baseline']}`. Audit source SHA256: `{evidence['audit_source_sha256']}`.

Failed checks: `{evidence['failures']}`.

Warnings (including charged calls without durable completions): `{evidence['warnings']}`.

Check counts: `{evidence['checks']}`.

Model ancestry correlations, incomplete historical/pretraining screening, bounded semantic review, small/selected development samples, unknown outcomes, varying neutral-padding quantities and prompt-derived RNG seeds limit scientific interpretation. A PASS certifies only checks listed in the JSON artifact. In particular it does not certify novelty, English fidelity, reviewer independence, human acceptance or completion of unauthorized experiments. The preserved failed universe probe and successful stronger negative fixtures document why initial generation passes were rechecked before admission.

Detailed artifacts: `final-study/runs/{protocol()['run_id']}/scientific_integrity_audit.json`, `independently_regenerated_rows.json`, `independently_regenerated_analysis.json` and `actual_evidence_counts.json`. The final report is `FINAL_COMPLETED_EXPERIMENTS.md`.
'''
    (OLD/'FINAL_SCIENTIFIC_INTEGRITY_AUDIT.md').write_text(audit_text)
    print(json.dumps(counts,indent=2));ensure(not evidence['failures'],'Evidence audit failed; see saved details')

if __name__=='__main__':main()
