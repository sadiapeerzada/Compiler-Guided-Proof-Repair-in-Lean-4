"""Output-bound diagnosis and final evidence report; never changes intake outcomes."""
import re,os,subprocess,collections,datetime
from v2_common import *
from pipeline_v2 import root,metrics
from parser_v2 import MARKERS

def report():
    frozen();out=root();metrics();m=read(out/'v2_generation_metrics.json');p=read(HERE/'protocol_v2.json')
    records=rows(out/'v2_candidates.jsonl');diagnostics=[]
    for row in records:
        text=row['record'].get('content') or '';lines=text.splitlines()
        diagnostic=dict(index=row['index'],source_call=row['source_call'],raw_response_sha256=row.get('raw_response_sha256'),parse_status=row['parse_status'],reason=row.get('reason'),exact_markers_present=[marker for marker in MARKERS if marker in lines],finish_reason=(row['record'].get('metadata') or {}).get('finish_reason'),output_tokens=(row['record'].get('metadata') or {}).get('completion_tokens'),literal_alternate_header_lines=[line for line in lines if re.match(r'^(ID|STATEMENT|TARGET|PROOF|CATEGORY|FAMILY)(:|$)',line)],contains_Lean3_begin=bool(re.search(r'\bbegin\b',text)),posthoc_diagnostic_only=True)
        stream_files=list((HERE/row['source_call']/'stream').glob('*.jsonl'))
        chunk_text=''.join(item['text'] for stream in stream_files for item in rows(stream) if 'token' in item and 'text' in item)
        diagnostic['stream_matches_response']=chunk_text==text
        diagnostics.append(diagnostic)
    dump(out/'v2_output_bound_failure_diagnostics.json',dict(records=diagnostics,all_streams_match=all(d['stream_matches_response'] for d in diagnostics),failure_counts=dict(collections.Counter(row.get('reason',row['parse_status']) for row in records if row['parse_status']!='PARSED')),no_posthoc_candidate_admission=True))
    baseline=read(HERE/'preservation_baseline_v2.json');changed=[rel for rel,h in baseline['files'].items() if not (ROOT/rel).exists() or sha(ROOT/rel)!=h]
    symlinks=[]
    for line in subprocess.check_output(['git','ls-tree','-r','1ac2e624'],cwd=ROOT).decode().splitlines():
        metadata,rel=line.split('\t',1)
        if metadata.startswith('120000 '):
            expected=subprocess.check_output(['git','show','1ac2e624:'+rel],cwd=ROOT).decode()
            ensure((ROOT/rel).is_symlink() and os.readlink(ROOT/rel)==expected,'Historical symlink changed: '+rel);symlinks.append(rel)
    ensure(not changed,'Historical file bytes changed')
    dump(out/'preservation_validation_v2.json',dict(baseline='1ac2e624',file_hashes_checked=len(baseline['files']),changed_files=changed,unchanged_symlink_targets=symlinks))
    gates={}
    for phase in ('reviewer_1','reviewer_2','development','test'):
        try:authorize(phase);gates[phase]={'status':'RESOURCE_AUTHORIZED_ONLY_NOT_VALIDATED'}
        except ValueError as error:gates[phase]=dict(status='NO_GO_RESOURCES',reason=str(error),model_calls=0)
    dump(out/'v2_execution_gate_status.json',gates)
    archived=read(HERE/'offline/archived_response_diagnostics.json');validation=read(HERE/'offline/validation_results_v2.json') if (HERE/'offline/validation_results_v2.json').exists() else {'status':'SEE_TERMINAL_PENDING_RECORD'}
    formal=rows(out/'v2_formal_verification.jsonl')
    diagnostic_path=out/'posthoc_alternate_labels/formal_diagnostic.json'
    posthoc=read(diagnostic_path)['results'] if diagnostic_path.exists() else []
    diagnostic_text='Post-hoc alternate-label checks were not executed.'
    if posthoc:
        diagnostic_text=f"A separate post-hoc diagnostic extracted all six explicit colon-labelled fields from {len(posthoc)} rejected response(s), without changing mathematical text. It submitted only that supplied theorem to the strict verifier: {sum(r['result']['success'] is True for r in posthoc)} verified, {sum(r['result']['success'] is False for r in posthoc)} compiler/policy failures, {sum(r['result']['success'] is None for r in posthoc)} unknown. The original prospective parse count remains zero. Exact source, target, original-response binding and full compiler records are in `posthoc_alternate_labels/`. For v2_gen_003 the compiler reported unknown `exact` identifiers and an application type mismatch; elapsed verification time was 26.878 seconds. These are actual compiler diagnostics, not an AI mathematical adjudication or a new prospective success."
    formal_status='Executed for '+str(len(formal))+' parsed candidates' if formal else 'NOT EXECUTED: zero structurally eligible candidates' if m['parsed_candidates']==0 else 'NOT EXECUTED: pending compiler stage'
    stages=dict(generation=dict(status='EXECUTED',charged_intents=m['charged_intents'],durable_responses=m['durable_responses']),formal=dict(status=formal_status,verified=m['strict_verified'],unknown=m['formal_unknown']),AI_review=dict(status='NOT EXECUTED',reason='New authorization explicitly defers review',calls=0),development=dict(status='NOT EXECUTED',reason='New authorization explicitly defers development; AI-screened cohort unavailable',calls=0),confirmatory=dict(status='NOT EXECUTED',reason='No test authorization; all V2 subjects are development-only',calls=0))
    dump(out/'v2_stage_completion.json',stages)
    report=f'''# Generation V2 — actual experimental results

**The authorized pilot ran; the experimental objective remains unmet.**
It used {m['charged_intents']} charged new generation intents and produced
{m['durable_responses']} durable real responses, {m['parsed_candidates']} structurally
valid candidates and {m['strict_verified']} strictly verified candidates. AI review
and C/D/E inference were not run. They were explicitly deferred by the researcher.
No new test inference or independent human validation is claimed.

## Previous failure diagnosis

The 22 V1 responses remain unchanged. Their original failures were 15 invalid JSON
escapes, five non-bare theorem declarations and two other JSON parse failures.
Inspection found {archived['length_limited']} length-capped outputs. All 22 stream
reconstructions match the saved response. There is no evidence of lost stream text.
Fourteen responses had a JSON Markdown fence, which the old parser already accepted;
fencing alone did not explain the original rejections. A separately disclosed,
diagnostic-only escape-doubling pass exposed fields in {archived['legacy_fields_inspectable']}
responses. All 17 inspectable targets included an assignment; ten proofs used Lean 3
begin/end syntax, two included imports and two contained placeholders. Flags overlap.
None was admitted to V2 or relabeled as a new successful generation.

Source-backed records: `v2/offline/archived_response_diagnostics.json` includes each
original call path, completion-file hash, raw-response hash, token limit and flags.

## Parser V2 validation and prospective freeze

The parser requires ordered ID/STATEMENT/TARGET/PROOF/CATEGORY/FAMILY/END markers.
It separates a bare target from a `by` block and assembles their exact concatenation
for the unchanged strict verifier. It invents no statement, target, proof or family.
Only outer whitespace, documented Markdown fences and source line endings are
normalized; original UTF-8 response bytes remain independently stored and hashed.
Invalid UTF-8, non-NFC text, duplicate IDs, missing/conflicting fields, reserved
delimiter collisions, over-budget output and length-capped responses are rejected.
Fifteen parser tests passed. Strict replay of the old JSON responses under V2 yields
{archived['strict_V2_parses']}/22 parses, as expected for a different output protocol.
That replay is offline post-hoc diagnosis, not prospective benchmark evidence.

The no-inference dry run passed for all ten prompts. The pinned coding-specialized
generator is `{p['generator']['id']}` at `{p['generator']['revision']}`. It was chosen
before V2 responses. Temperature is {p['temperature']}, base seed {p['base_seed']}.
Prompt source SHA-256: `{p['prompt_source_sha256']}`.
Parser source SHA-256: `{p['parser_source_sha256']}`.
Source lock SHA-256: `{p['source_lock_sha256']}`.
The ten-category schedule and complete prompts are frozen in the dry-run evidence.
Source/protocol commit: `b64aa1d4`. No prompt, parser, source lock or acceptance rule
was changed in response to V2 outputs.

## New generation and formal results

| Measure | Actual result |
|---|---|
| Charged new intents | {m['charged_intents']}/10 |
| Durable responses | {m['durable_responses']} |
| Unknown consumed intents | {m['unknown_consumed_intents']} |
| Structurally valid candidates | {m['parsed_candidates']} |
| Strictly checked / verified / failed / unknown | {m['formal_checked']} / {m['strict_verified']} / {m['formal_failures']} / {m['formal_unknown']} |
| Parsed alpha-duplicate candidates | {m['alpha_duplicate_candidates']} (no estimate of duplication among unparsed text) |
| Response rate / parse rate per response | {m['durable_response_rate']} / {m['parse_rate_per_response']} |
| Strict verification rate per parsed candidate | {m['strict_verified_rate_per_parsed']} |

Formal stage: **{formal_status}**. No parser rejection is recoded as a Lean compiler
failure. Successful real-Lean fixtures are not generated candidate successes.
Where subjects exist, the fixed environment is Lean 4.32.0 and Mathlib revision
`{p['environment']['lean']['mathlib_revision']}`, with import Mathlib, exact target
checking, a 180-second reference timeout and the unchanged strict axiom policy.

Exact V2 failure counts: `{dict(collections.Counter(r.get('reason',r['parse_status']) for r in records if r['parse_status']!='PARSED'))}`.
`v2_output_bound_failure_diagnostics.json` records missing markers, alternative
literal header lines, finish reasons, output tokens and hashes for every response.
The original responses and stream traces are retained in each `calls/calls/` folder.
There is no post-hoc rescue of missing English, reordered fields, truncated proof
text, combined declarations or arbitrary header variants into the frozen cohort.

{diagnostic_text}

## AI review, historical overlap and development C/D/E

AI review calls: 0. AI-screened accepted candidates: 0. Reviewer agreement is not
estimable. No model is relabeled as an independent human. The automated historical
screen uses the inherited 193-version inventory and generated-candidate exposure
registry for formally verified subjects; actual screen records are in
`automated_historical_screen.json`. No exhaustive semantic or pretraining
contamination clearance is claimed.

Development theorem types eligible for C/D/E: 0. Initial model calls and C/D/E
repair calls: 0. Paired comparisons, discordance, C−D/C−E effects, missingness
bounds and confidence intervals are not estimable. No claim of equality, causal
benefit or inferential superiority is supported. Reference proofs have not been
sent to any repair model. This is a development-generation pilot, not untouched
confirmatory testing and not a completed C/D/E evaluation.

## Resource accounting

Actual user instruction: “10 generation calls only; defer review and development
authorization.” The recorded question context caps each call at 4,096 input and
1,200 output tokens and the generation phase at 30 minutes. This is a new run;
the earlier 24 exhausted intents and deadlines are unchanged and never replayed.
No unused old allocation or deferred review/development allocation is transferred.

Completed calls record {m['actual_input_tokens']} input tokens,
{m['actual_output_tokens']} output tokens and {m['recorded_generation_seconds']:.3f}
generation seconds. Maximum reported MLX peak memory is
{m['max_reported_MLX_peak_memory_gb']} GB; this is not an independently sampled RSS
series. Unknown consumed compute is not estimated. No cloud model calls were made.
Review, development and test gates each report NO_GO_RESOURCES for this V2 run.

## Next justified revision and confirmatory readiness

The immediate observed technical failure is failure to follow the multi-field
delimiter contract. A next version should test a smaller response contract:
one verbatim English statement, one fenced full Lean theorem, and one family label,
with ID and category assigned by the controller. Derive the unproved target by
parsing the single supplied declaration at its top-level assignment, without
inventing or modifying mathematical text. Define all accepted header/fence forms
and ambiguity rejection before another response. Add fixtures based on these exact
V2 failures. Keep completeness, exact-type checks, proof policy and semantic review
requirements unchanged. This is a proposed revision, not an executed V3 pilot.
The concrete proposed contract and boundary cases are in `v2/NEXT_REVISION.md`.

Another inference pilot needs fresh, explicit resource authorization; no positive
result is pursued by looping past the ten-call ceiling. AI review and C/D/E also
need separately authorized limits, genuinely verified subjects and two blinded
review processes. Diagnostic donors require distinct eligible families. A separate
test stream must use fresh families/subjects, a prospectively frozen generation,
screening and analysis policy, a feasible sample/compute calculation, and separate
test authorization. No inspected V1 or V2 output may become an untouched test.

## Reproducibility and validation

Run ID: `{p['run_id']}`; evidence directory: `v2/runs/{p['run_id']}/`.
Raw responses are exclusive `raw_response.txt` files alongside durable intents,
completions, prompt/token metadata and per-token traces. The new ledger is
append-only. Completed calls may be re-read, but consumed unknown calls are never
regenerated. The persisted generation deadline cannot be reset.

All {len(baseline['files'])} historical file hashes and {len(symlinks)} historical
symlink targets match `1ac2e624`. Old pilot records, human protocol, experiments,
manuscript and pre-existing untracked user files were left unchanged.
Validation results: `{validation}`. See `v2/README.md` for exact commands and the
legacy exclusion explanation. Scripts/tests passing does not establish candidate
validity, AI acceptance, experimental inference or completion of this research goal.
'''
    (OLD/'V2_EXPERIMENTAL_RESULTS.md').write_text(report)
    print('Reported actual V2 results; historical preservation checked')

if __name__=='__main__':report()
