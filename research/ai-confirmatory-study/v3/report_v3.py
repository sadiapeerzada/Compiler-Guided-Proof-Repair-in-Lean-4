"""Rebuild actual evidence summaries without changing canonical model outcomes."""
import subprocess,collections,importlib.metadata
from common_v3 import *
from pipeline_v3 import summarize
from dataset_tools import screen,cohort_flags

def main():
    p=freeze_check();summarize();out=root();metrics=read(out/'metrics.json');verified=read(out/'verified_candidates.json')
    records={phase:rows(out/phase/'records.jsonl') for phase in ('generation','reference_repair')}
    amendment_note=''
    amendment=out/'repair_prompt_amendment'
    if (amendment/'protocol.json').exists():
        manifest=read(amendment/'protocol.json');extra=rows(amendment/'records.jsonl')
        dump(out/'original_prompt_variant_summary.json',dict(metrics=metrics,verified_candidates=verified,scope='Original frozen prompt variant; shared-ledger expenditure also includes amended calls; see merged metrics for effective outcomes'))
        original={r['index']:r for r in records['reference_repair']};initial={r['index']:r for r in records['generation']}
        for r in extra:
            ensure(r['index'] in manifest['eligible_indices'],'Unexpected amended index')
            ensure(original[r['index']]['status']=='SKIPPED_NO_INFERENCE','Amendment cannot retry an attempted repair')
            original[r['index']]=r
        records['reference_repair']=list(original.values())
        effective=metrics['phases']['reference_repair'];effective['structurally_valid']=sum(r['status']=='STRUCTURALLY_VALID' for r in original.values())
        effective['strict_verified']=sum(r.get('verification',{}).get('success') is True for r in original.values())
        effective['strict_failed']=sum(r.get('verification',{}).get('success') is False for r in original.values())
        effective['strict_unknown']=sum('verification' in r and r['verification']['success'] is None for r in original.values())
        effective['rejection_reasons']=[dict(index=r['index'],status=r['status'],reason=r.get('reason'),failure_kind=r.get('verification',{}).get('failure_kind')) for r in original.values() if r.get('verification',{}).get('success') is not True]
        for r in extra:
            if r.get('verification',{}).get('success') is True:
                c=dict(initial[r['index']]['candidate']);c.update(reference_proof=r['evaluated_source'],proof_sha256=text_hash(r['evaluated_source']),status='FORMALLY_VERIFIED_PENDING_AI_REVIEW',construction_path='one_compiler_guided_repair_diagnostic_projection_amendment',verification_source_call=r['source_call'],repair_amendment_sha256=sha(amendment/'protocol.json'));verified.append(c)
        ensure(len({c['id'] for c in verified})==len(verified),'Duplicate merged verified IDs')
        metrics.update(unique_verified_candidates=len(verified),repair_prompt_amendment=dict(protocol_sha256=sha(amendment/'protocol.json'),effective_records_include_amendment=True,original_skips_preserved=True))
        dump(out/'metrics.json',metrics);dump(out/'verified_candidates.json',verified)
        amendment_note='''The original repair prompt serialized the entire verifier record. After one
actual failed repair, three other indices were skipped before inference because
that record exceeded the input cap. A separately frozen development-only prompt
amendment projected complete structured error messages (data, kind, severity and
positions), omitting duplicated stdout, verifier harness source and warnings.
No error message was truncated. Offline token checks were 854/909/908 for the three
prompts, with exact preservation of every error message. This was an explicitly
recorded technical change after original outcomes, not a prospective unchanged
prompt comparison. Original source locks and skip records remain untouched.
Only previously unattempted indices4/5/6 were eligible. The amended calls used the
same original ledger, ten-call cap, per-candidate one-call limit and original
30-minute repair deadline; index3 was not retried. See repair_prompt_amendment/.
Merged outcome views include amended records; original_prompt_variant_summary.json
preserves the separate original prompt variant summary. Rebuild using this report
script after pipeline summarization, not the original summarizer alone.
'''
    initial_by_index={r['index']:r for r in records['generation']}
    change_audit=[]
    for r in records['reference_repair']:
        if r.get('evaluated_source'):
            c=initial_by_index[r['index']]['candidate'];prefix=c['expected_lean_statement']+' := '
            ensure(r['evaluated_source'].startswith(prefix),'Repair target changed')
            proof=r['evaluated_source'][len(prefix):]
            change_audit.append(dict(index=r['index'],target_sha256=c['statement_sha256'],initial_source_sha256=c['proof_sha256'],repair_source_sha256=text_hash(r['evaluated_source']),identical_proof_block=proof.strip()==c['proof_block'].strip(),strict_success=r.get('verification',{}).get('success')))
    dump(out/'repair_change_audit.json',dict(records=change_audit,scope='Byte equality of trimmed proof blocks, not mathematical-equivalence analysis'))
    screens=[]
    for c,within in zip(verified,cohort_flags(verified)):
        r=screen(dict(c,source_url='Locally AI generated in V3; upstream sources unassessed',license='Model/upstream rights unassessed',library_dependencies=[]))
        screens.append(dict(id=c['id'],automated_flags=sorted(set(r['automated_flags']+within)),pretraining_contamination='UNASSESSED',status='FORMALLY_VERIFIED_PENDING_AI_REVIEW',not_eligibility_or_human_approval=True))
    dump(out/'automated_historical_screen.json',dict(records=screens,scope='193-version inventory and historical generated-candidate exact/normalized/family screen; not exhaustive semantic-equivalence proof'))
    baseline=read(HERE/'preservation_baseline.json');changed=[rel for rel,h in baseline['files'].items() if not (ROOT/rel).exists() or sha(ROOT/rel)!=h];ensure(not changed,'Historical files changed')
    symlinks=[]
    for line in subprocess.check_output(['git','ls-tree','-r','14e9a450'],cwd=ROOT).decode().splitlines():
        metadata,rel=line.split('\t',1)
        if metadata.startswith('120000 '):
            expected=subprocess.check_output(['git','show','14e9a450:'+rel],cwd=ROOT).decode();ensure((ROOT/rel).is_symlink() and os.readlink(ROOT/rel)==expected,'Historical symlink changed');symlinks.append(rel)
    dump(out/'preservation_validation.json',dict(baseline='14e9a450',unchanged_file_hashes=len(baseline['files']),unchanged_symlinks=symlinks,changed_files=[]))
    trace_checks=[]
    for phase in records:
        for completion in (out/phase/'calls/calls').glob('*/completion.json'):
            record=read(completion);folder=completion.parent;raw=(folder/'raw_response.txt').read_bytes();chunks=''.join(r['text'] for stream in (folder/'stream').glob('*.jsonl') for r in rows(stream) if 'token' in r and 'text' in r)
            ensure(raw==record['content'].encode()==chunks.encode(),'Raw response/stream mismatch')
            trace_checks.append(dict(source=str(folder.relative_to(HERE)),raw_sha256=text_hash(record['content']),stream_matches=True))
    dump(out/'response_integrity.json',dict(records=trace_checks,all_streams_and_raw_bytes_match=True))
    gates={}
    for phase in ('AI_adjudication','CDE','test'):
        try:authorize(phase);raise AssertionError('Unexpected authorization')
        except ValueError as error:gates[phase]=dict(status='NO_GO_RESOURCES',reason=str(error),model_calls=0)
    dump(out/'remaining_phase_gates.json',gates)
    dump(out/'runtime_packages.json',{name:importlib.metadata.version(name) for name in ('mlx','mlx-lm','transformers','pytest')})
    validation=read(HERE/'offline/validation_results.json')
    archive=read(HERE/'offline/archived_v2_replay.json')
    g=metrics['phases']['generation'];r=metrics['phases']['reference_repair']
    example='No strictly verified candidate is available.'
    if verified:
        c=verified[0];example=f"First real verified example, `{c['id']}` ({c['construction_path']}):\n\n{c['nl_statement']}\n\n```lean\n{c['reference_proof']}\n```\n\nProof SHA-256: `{c['proof_sha256']}`. This is a formal proof, not AI semantic or originality acceptance."
    table=[]
    repairs={x['index']:x for x in records['reference_repair']}
    for initial in records['generation']:
        repair=repairs.get(initial['index'],{});table.append(f"| {initial['index']} | {initial['status']} | {initial.get('verification',{}).get('success')} | {repair.get('status','NOT_ATTEMPTED')} | {repair.get('verification',{}).get('success')} |")
    total_tokens=sum(x['actual_input_tokens']+x['actual_output_tokens'] for x in (g,r))
    compiler_seconds=sum(x.get('verification',{}).get('elapsed_seconds',0) or 0 for phase in records.values() for x in phase)
    reconciliation=read(out/'generation/interruption_reconciliation.json') if (out/'generation/interruption_reconciliation.json').exists() else None
    interruption_note=''
    if reconciliation:
        interruption_note=f'''Generation was interrupted before a worker completion status was saved. Its
original 30-minute window had expired by the continuation, so the remaining
{10-g['charged_intents']} generation slots were not launched and no clock was reset.
The cause of interruption is not established. A durable seventh completion was
reconciled offline using the unchanged parser and verifier, with zero additional
model calls. The separately authorized repair phase had not started; its own
original phase clock began only when that phase was actually launched. See
`generation/interruption_reconciliation.json`. Unlaunched slots are not failures
or missing model outcomes. This run was not a completed ten-generation sample.
'''
    text=f'''# Generation V3 — actual mathematical evidence and remaining limits

V3 used **{g['charged_intents']} generation intents** and **{r['charged_intents']} separately
counted reference-repair intents**, producing **{g['structurally_valid']} structurally
valid initial candidates** and **{len(verified)} unique strictly verified reference
proofs**. Initial strict successes: {g['strict_verified']}; additional repaired
successes: {r['strict_verified']}. No AI adjudication, C/D/E or confirmatory inference
ran. Formal success alone is not semantic fidelity, novelty or benchmark eligibility.

## Prospective protocol and authorization

Starting commit: `14e9a450`; pre-inference implementation commit: `1b3b85c8`.
Run: `{p['run_id']}`. The user explicitly authorized “10 generation calls and up
to 10 reference-proof repair calls,” each at most 4,096 input/1,200 output tokens,
with a 30-minute generation phase and a separate 30-minute repair phase. At most one
repair is allowed per candidate. No V1/V2 budget or expired deadline was reused.
{interruption_note}
Protocol SHA-256: `{sha(HERE/'protocol_v3.json')}`.
Source lock SHA-256: `{p['source_lock_sha256']}`.
Generation model: `{p['models']['generation']['id']}` at
`{p['models']['generation']['revision']}`. Repair model:
`{p['models']['reference_repair']['id']}` at
`{p['models']['reference_repair']['revision']}`. No reviewer independence is claimed.
Temperature .2, seed {p['base_seed']}; complete prompts, categories, models and
decoding metadata are retained. All outputs are development-only, never untouched test.

## Parser and offline validation

Three explicit sections replace six-field serialization: STATEMENT, LEAN and FAMILY.
IDs and categories come from the controller; mathematical content always comes from
the actual response. Documented heading/fence variants are accepted, but missing
content, ambiguity, truncation, invalid UTF-8 and non-NFC text are rejected.
Raw bytes are independently preserved; no JSON escaping or reconstructed English is
needed. Lean's native command parser consumes the complete command and locates the
theorem's own assignment in its direct declValSimple syntax node. It does not split
at an assignment inside a let, string or comment. Supplied syntax is not elaborated
or executed by this parser. The unchanged strict adapter cannot handle assignments
inside an unproved target; such targets are explicitly rejected, never mis-split.

All ten archived V2 responses were replayed offline: {archive['parsed']} parsed under
the frozen V3 contract. These are post-hoc diagnostics, not new prospective results.
V2 outcomes and ledgers remain unchanged. Four real native-parser checks passed,
including a proof-local let, comment delimiters, multiple-command rejection and a
correctly located but unsupported nested-let target. Fourteen parser unit tests
passed. Validation: `{validation}`. The broader regression excludes the two real
Lean tests run separately and the unchanged historical blanket test forbidding new
research files. Synthetic fixtures never count as benchmark candidates.

## Actual generation and repair outcomes

| Index | Initial structure | Initial strict result | Repair structure | Repair strict result |
|---|---|---|---|---|
{chr(10).join(table)}

`None` means not checked or unknown, never false. Phase metrics distinguish these
cases. No repair is attempted for a missing/truncated candidate or an unknown
initial verification. Only structurally valid, known failed references can receive
one repair. Full initial compiler diagnostics, failed source and immutable target
are passed to the repair model. The repair model supplies only a by-block; joining
it to the original exact declaration is recorded explicitly. Each resulting proof
is parsed and strictly checked again. No reference from a different theorem is
substituted, and no assumption or theorem target is weakened.

Initial structure/verification rejections: `{g['rejection_reasons']}`.
Repair rejections: `{r['rejection_reasons']}`.

Of {len(change_audit)} structurally valid repair responses,
{sum(c['identical_proof_block'] for c in change_audit)} repeat the original proof
block exactly after boundary-whitespace removal. See repair_change_audit.json.
An additional response is not counted as an improvement without strict verification.

{amendment_note}

Strict verification uses pinned Lean4.32.0/Mathlib
`{p['environment']['lean']['mathlib_revision']}`, import Mathlib, the unchanged
exact-type harness and axiom policy, and a 180-second check timeout. Syntax acceptance
alone is not kernel acceptance. Every exported proof is labelled
FORMALLY_VERIFIED_PENDING_AI_REVIEW; repaired proofs retain their construction path.

{example}

## Actual resource accounting

| Phase | Charged | Durable | Unknown consumed | Input tokens | Output tokens | Model generation seconds |
|---|---|---|---|---|---|---|
| Generation | {g['charged_intents']} | {g['durable_responses']} | {g['unknown_consumed_intents']} | {g['actual_input_tokens']} | {g['actual_output_tokens']} | {g['generation_seconds']:.3f} |
| Reference repair | {r['charged_intents']} | {r['durable_responses']} | {r['unknown_consumed_intents']} | {r['actual_input_tokens']} | {r['actual_output_tokens']} | {r['generation_seconds']:.3f} |

Recorded total tokens: {total_tokens}; recorded compiler-check seconds:
{compiler_seconds:.3f}. Native-parser startup time is separate from compiler and
model metadata and is not estimated here. MLX-reported peaks are
{g['max_MLX_peak_memory_gb']}GB for generation and {r['max_MLX_peak_memory_gb']}GB for
repair, not a whole-process RSS time series. Unknown consumed compute is not zero
and is not estimated. Over-budget repair prompts are skipped without truncation or
inference. Separate ledgers prevent transferring or replaying exhausted calls.

## Remaining scientific and authorization conditions

Automated historical/exposure/cohort flags for actual verified subjects are in
automated_historical_screen.json. This is not exhaustive equivalence screening,
semantic validation or pretraining contamination clearance. No candidate is yet
AI_SCREENED_FORMALLY_VERIFIED or independently human-approved. Two blinded model
reviews, conservative overlap adjudication and separately authorized compute are
still required. No AI-review inference is inferred from this generation budget.

C/D/E needs accepted subjects, eligible diagnostics from distinct families, a
frozen execution protocol and separate authorization. Its calls, paired outcomes,
effects and confidence intervals are absent, not fabricated as zero benefit. A
future untouched test needs a fresh separately frozen stream and authorization;
no inspected V1, V2 or V3 output may be promoted to it. The immediate formal-proof
objective is met for {len(verified)} development candidates; the larger benchmark
and C/D/E study remain incomplete. Reference repair added no verified proofs in
this run. Failed/truncated responses and exact compiler records define any next
version rather than an unlimited generation or repair loop.

## Reproducibility and preservation

All raw responses, prompts, seed/model metadata, token traces, native parser
offsets/errors, strict compiler diagnostics, checkpoints and source hashes are in
`v3/runs/{p['run_id']}/`. `metrics.json` and `verified_candidates.json` are rebuildable
views of canonical phase records. `formal_checks/` preserves consumed verification
intents. `response_integrity.json` confirms {len(trace_checks)} actual completions
match raw response bytes and stream reconstruction. Existing outcomes are never
silently repaired or recoded. Expired clocks cannot be reset; unfinished consumed
calls/checks remain unknown on resume.

All {len(baseline['files'])} historical file hashes and {len(symlinks)} historical
symlink targets match `14e9a450`. Historical manuscripts, studies and human approval
protocol remain unchanged. Exact commands are in `v3/README.md`. The branch is pushed
without merging; passing scripts/tests alone is not completion of the scientific study.
'''
    (OLD/'V3_EXPERIMENTAL_RESULTS.md').write_text(text)
    print('Actual V3 report:',len(verified),'unique strictly verified candidates')

if __name__=='__main__':main()
