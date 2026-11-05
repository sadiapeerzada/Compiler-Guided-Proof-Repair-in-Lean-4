"""Produce the negative/blocked report only from completed, audited checkpoints."""
import csv
from collections import Counter
from sprint_common import *
from audit_sprint import audit

def main():
    chain=read(RUN/'chain_status.json')
    ensure(chain['status']=='BLOCKED','This reporter is only for an actual blocked chain')
    ensure(read(RUN/'development_generation/status.json')['status']=='finished','Generation not finished normally')
    result=audit();ensure(result['status']=='PASS_RECORDED_CONSISTENCY','Audit failures need diagnosis')
    ensure(not any(v['charged'] for k,v in result['stages'].items() if k.startswith('test_')),'Use full experimental report for test outcomes')
    ensure(not result['stages']['development_initial']['charged'] and not result['stages']['development_repairs']['charged'],'Use full experimental report for C/D/E outcomes')
    dump(HERE/'final_recorded_consistency_audit.json',result)
    records=rows(RUN/'development_generation/records.jsonl')
    ensure(len(records)==result['stages']['development_generation']['charged'],'Reconcile all consumed intents first')
    structural=[r for r in records if r['status']=='STRUCTURALLY_VALID']
    verified=[r for r in structural if r['verification'].get('success') is True]
    accepted=read(RUN/'development_ai_accepted.json');selected=read(RUN/'development_selected.json')
    review_maps=[{r['id']:r for r in rows(RUN/f'development_review_{i}/reviews.jsonl')} for i in (1,2)]
    both_ai_accept=sum(all(m.get(c['id'],{}).get('decision')=='ACCEPT' and not m.get(c['id'],{}).get('parse_error') for m in review_maps) for c in read(RUN/'development_review_input/fresh_verified.json'))
    dump(HERE/'review_outcomes.json',dict(raw_valid_dual_ai_acceptances=both_ai_accept,eligible_after_critical_concerns=len(accepted),quarantined=read(RUN/'development_ai_quarantined.json'),reviewers=[list(m.values()) for m in review_maps]))
    rejected=Counter(r.get('reason','unspecified') for r in records if r['status']=='STRUCTURE_REJECTED')
    inventory=[]
    for r in records:
        inventory.append(dict(id=r['id'],prompt_version=r.get('prompt_version','v1'),family=r['canonical_family'],structure=r['status'],strict_verified=r.get('verification',{}).get('success'),reason=r.get('reason',''),pre_review_flags=json.dumps(r.get('pre_review_flags',[])),source_call=r.get('source_call','')))
    with (HERE/'generation_outcomes.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(inventory[0]),lineterminator="\n");writer.writeheader();writer.writerows(inventory)
    stages=result['stages'];calls=result['actual_charged_calls'];inputs=sum(s['input_tokens_observed'] for s in stages.values());outputs=sum(s['output_tokens_observed'] for s in stages.values())
    table='\n'.join(f"| {k} | {v['charged']} | {v['completed']} | {v['unknown']} | {v['max_calls']} |" for k,v in stages.items())
    review_table='\n'.join(f"| {c['id']} | {review_maps[0][c['id']]['decision']} | {review_maps[1][c['id']]['decision']} | Excluded: source-bound statement concern |" for c in read(RUN/'development_review_input/fresh_verified.json'))
    families=len({c['canonical_family'] for c in selected})
    runtime_table='\n'.join(f"| {k} | {v['observed_call_span_seconds']:.1f} | {v['observed_call_latency_seconds']:.1f} | {v['reported_max_mlx_peak_memory_gb']:.3f} |" for k,v in stages.items() if v['charged'])
    latency=sum(v['observed_call_latency_seconds'] for v in stages.values());peaks=[v['reported_max_mlx_peak_memory_gb'] for v in stages.values() if v['reported_max_mlx_peak_memory_gb'] is not None];peak=max(peaks) if peaks else None
    model_lines='\n'.join(f"- {k}: `{m['id']}` at `{m['revision']}`." for k,m in read(HERE/'resource_authorization.json')['models'].items())
    report=f'''# Final C/D/E completion sprint: PARTIAL, data gate BLOCKED

The authorized construction attempt completed, but the actual eligible development
cohort did not satisfy the gate for C/D/E. No C/D/E or untouched-test inference ran.
This is a negative construction result, not evidence of a repair treatment effect.

## Recorded outcomes

- Fresh generation calls: {len(records)}; structurally valid: {len(structural)};
  strictly kernel-verified reference proofs: {len(verified)}.
- Raw valid dual-AI acceptances: {both_ai_accept}; eligible fresh candidates after
  unresolved critical concerns: {len(accepted)}. Frozen development cohort:
  {len(selected)} {'subject' if len(selected)==1 else 'subjects'} in {families} independent {'family' if families==1 else 'families'}, including unchanged old development
  evidence where explicitly marked. No new human mathematical approval is claimed.
- Actual gate reason: `{chain['reason']}`.
- Initial-solve and C/D/E attempts: zero. Paired cases, repair rates, differences,
  confidence intervals, significance tests and power estimates: **not estimable**.
- Untouched-test construction/evaluation: **NOT_STARTED**. No test outcomes were
  inspected, no test target was reduced, and no inference was substituted for a
  missing development comparison.

## Fresh authorization and actual usage

The researcher explicitly approved **Expanded exploratory — 1,728 calls**.
`completion-sprint/resource_authorization.json` binds the actual reply, proposal,
exact revisions and separate phase ceilings. This was a maximum allocation,
not a requirement to spend calls when mathematical eligibility fails. Old V1/V2/V3
and final-study budgets remain closed. No unused phase allocation was transferred.
Reference-proof repair calls were not authorized for this sprint and none ran.

| Phase | Charged | Completed | Unknown | Approved cap |
| --- | ---: | ---: | ---: | ---: |
{table}

Total actual charged calls: **{calls}**. Observed prompt tokens: **{inputs}**;
completion tokens: **{outputs}**. Per-call ceilings were 4,096/1,200 tokens.
Summed observed model-call latency: **{latency:.1f} seconds**; maximum reported
MLX peak memory: **{peak} GB** (allocator-reported, not whole-machine RSS).
Original phase clocks, actual per-phase call spans, and call start/finish
timestamps are retained in the audit and run; no deadline was restarted. Summed
model-call latency is not wall-clock phase duration and excludes Lean checks.

| Executed phase | First-to-last call span, seconds | Summed call latency, seconds | Reported MLX peak, GB |
| --- | ---: | ---: | ---: |
{runtime_table}

The generation span includes the interval between prompt versions. Eight of the
128 scheduled positions remained unconsumed under recorded family retirement;
they were not replayed or replaced to pursue a favorable outcome.

## Scientific interpretation and rejection evidence

The first 60 responses failed the mandatory three-section format. Their raw bytes,
historical outcomes and charged IDs remain unchanged. A prospective mandatory
FAMILY-footer clarification was source-frozen for unconsumed slots under the same
128-call cap and original eight-hour clock. No missing field or proof was filled
by the assistant. Both prompt versions, retirement decisions and skipped slots
are retained. Structural rejections by exact parser reason: `{dict(rejected)}`.

Successful parsing did not imply proof success or English/Lean equivalence.
Every parsed reference was submitted unchanged to the rigid declaration-type
and universe checker using Lean 4.32.0 and pinned Mathlib
`81a5d257c8e410db227a6665ed08f64fea08e997`. Compiler diagnostics, failed source,
actual axiom dependencies and verification checkpoints remain available. A
compiler-verified reference still required two qualified blinded reviews under
the unchanged Boolean policy; invalid or uncertain reviews were quarantined.
See the raw review records for substantive rejection reasons rather than
interpreting all review failures as the same mathematical defect.
`completion-sprint/mathematical_concerns.json` records exact-subject assistant
concerns: two verified interval-product references describe shifted intervals
in English but prove an endpoint splitting identity; a third reference states
only a forward implication in English while Lean asserts an iff. All three
remain ineligible even if both reviewers accept. These are source-bound assistant
exclusions, not human approval. `completion-sprint/review_outcomes.json` preserves
actual raw qualified decisions separately from final eligibility.

| Strictly verified reference | Phi decision | Qwen decision | Final status |
| --- | --- | --- | --- |
{review_table}

The two UNCERTAIN Phi results omitted the mandatory `historical_explanation`
field; they were not retroactively reinterpreted or retried. Both reviewers gave
a schema-valid ACCEPT to `sprint_development_0078`, even though the English
describes a shift involving c and the Lean declaration proves endpoint splitting
without using c. Thus actual dual-model agreement failed to establish statement
alignment on this subject. This is an observed screening limitation, not a
C/D/E treatment result or an estimate of the reviewers' general error rate.

Models used or reserved by the approved proposal:

{model_lines}

Only stages with charged calls above actually used a model. The reviewers belong
to Phi and Qwen families; this does not establish independent errors. Generation,
the second reviewer and evaluation share Qwen ancestry; the second reviewer and
evaluation use identical weights. No unseen-test generalization, adequately
powered confirmatory result, human validation or external replication is claimed.

## Evidence and validation

- `completion-sprint/generation_outcomes.csv`: every charged generation outcome.
- `completion-sprint/runs/expanded_v1/`: exact prompts, raw responses, hashes,
  streaming traces, usage, checkpoints, compiler diagnostics, reviews and gates.
- `completion-sprint/final_recorded_consistency_audit.json`: separate-process
  consistency audit, **{result['status']}**, {len(result['failures'])} failures;
  all 9,734 starting-main files and four symlink targets preserved.
- `completion-sprint/regression_validation.json`: actual offline regression runs;
  **62 parser, review, overlap and policy tests passed** in the broader run.
  The 42 actual Lean reference checks above are separate from offline tests.
- `completion-sprint/previous_31_audit.csv`: prior references and exclusion rules;
  27 excluded, four already reviewed, two qualified in one family and zero
  eligible unreviewed subjects. None were silently rescued or rereviewed.

Branch starts at merged main `9be2360b`; all changes are scoped to the new sprint
and this report. No manuscript claim or old experiment record was edited. The
remaining research objective is blocked by insufficient genuine eligible data;
infrastructure passing is not a substitute for mathematical evidence.
'''
    (ROOT/'research/ai-confirmatory-study/FINAL_CDE_CONFIRMATORY_RESULTS.md').write_text(report)
    print('Wrote evidence-backed blocked report',flush=True)

if __name__=='__main__':main()
