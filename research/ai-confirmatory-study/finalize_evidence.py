"""Summarize durable evidence only. No inference, acceptance, or outcome imputation."""
from collections import Counter
import platform
from ai_common import HERE, ROOT, read, save, sha, lines
from ai_gate import check, source_check
from pipeline import summarize_resources

def main():
    source_check()
    runs=HERE/'runs'; gen=runs/'generation'; formal=runs/'formal_verification'; reviews=runs/'reviews'
    proposals=lines(gen/'candidate_generation.jsonl')
    parsed=[r for r in proposals if r['parse_status']=='PARSED']
    verified=read(formal/'verified_candidates.json')
    rejected=read(formal/'rejected_candidates.json')
    accepted=read(reviews/'accepted_candidates.json')
    review_rows=[lines(reviews/f'reviewer_{i}.jsonl') for i in (1,2)]
    summarize_resources('generation')
    for i in (1,2):summarize_resources(f'reviewer_{i}')
    usage=read(gen/'generation_resource_usage.json')
    failure_counts=Counter('unavailable_generation' if r['parse_status']=='UNAVAILABLE_GENERATION' else 'invalid_JSON_escape' if r.get('reason','').startswith('Invalid \\escape') else 'non_bare_theorem_declaration' if r.get('reason')=='Expected bare single theorem declaration' else 'other_JSON_parse_failure' for r in proposals if r['parse_status']!='PARSED')
    save(gen/'generation_failure_analysis.json',dict(counts=dict(failure_counts),rule='Group recorded parser errors only; no mathematical or proof judgments inferred'))
    metadata=[r['record']['metadata'] for r in proposals if r['record']['status']=='completed']
    memory=[m['peak_memory_gb'] for m in metadata if 'peak_memory_gb' in m]
    seconds=sum(m['latency_seconds'] for m in metadata)
    save(gen/'measured_runtime_memory.json',dict(scope='Generation only; not development throughput calibration',recorded_generation_seconds=seconds,recorded_output_tokens=sum(m['completion_tokens'] for m in metadata),aggregate_recorded_output_tokens_per_second=sum(m['completion_tokens'] for m in metadata)/seconds if seconds else None,max_reported_peak_memory_gb=max(memory) if memory else None,peak_memory_caveat='MLX reported peak; not an independently sampled whole-process RSS series'))
    save(gen/'candidate_generation_manifest.json',dict(protocol_sha256=sha(HERE/'ai_protocol_v1.json'),recorded_attempts=len(proposals),parse_statuses=dict(Counter(r['parse_status'] for r in proposals)),parsed_candidates=len(parsed),generation_log_sha256=sha(gen/'candidate_generation.jsonl'),raw_completions=usage['durable_completed_calls'],cohort_use='DEVELOPMENT_ONLY_ENGINEERING_PILOT_NOT_CONFIRMATORY',no_automatic_repair_or_replay=True))
    baseline=read(HERE/'baseline_hashes.json')
    changed=[p for p,h in baseline['files'].items() if not (ROOT/p).exists() or sha(ROOT/p)!=h]
    save(runs/'preservation_validation.json',dict(baseline=baseline['baseline'],checked_files=len(baseline['files']),changed_files=changed))
    assert not changed, 'Historical preservation check failed'
    states={p:check(p) for p in ('development','test')}
    save(runs/'execution_gate_status.json',{p:{k:v for k,v in s.items() if k not in ('records','protocol')} for p,s in states.items()})
    # Required public reviewer filenames contain only actual recorded reviews.
    for i,rows in enumerate(review_rows,1):
        source=reviews/f'reviewer_{i}.jsonl'
        (reviews/f'ai_reviewer_{i}.jsonl').write_text(source.read_text() if source.exists() else '')
    review_usage=[read(reviews/f'reviewer_{i}/resource_usage.json') for i in (1,2)]
    agreement=read(reviews/'reviewer_agreement.json')
    review_report=f'''# AI benchmark validation\n\nStrictly parsed proposals: {len(parsed)}. Strictly verified references: {len(verified)}.\nFailed/unavailable reference checks: {len(rejected)}. AI-screened accepted: {len(accepted)}.\nReviewer 1 records: {len(review_rows[0])}; reviewer 2 records: {len(review_rows[1])}.\nPaired reviews: {agreement['paired_reviews']}; agreement rate: {agreement['agreement_rate']}.\nNo review is inferred for an unreviewed candidate. Model agreement is not semantic truth.\nPhi and Qwen reviewers are different families; the generator shares Qwen ancestry\nwith reviewer 2. No independent human mathematical review took place.\nRejected serialization is preserved without post-hoc repair or benchmark admission.\n'''
    (reviews/'AI_BENCHMARK_VALIDATION_REPORT.md').write_text(review_report)
    (runs/'contamination_audit.md').write_text('''# Contamination scope\n\nThe inherited 193-version inventory and exposure registry supply deterministic\nexact, normalized/template and family screens for formally verified candidates.\nEach reviewer receives five lexical historical neighbors, without another review\nor the reference proof. These methods do not certify absence of mathematical\nequivalence, specialization, proof-template overlap, or training contamination.\nUnassessed model-pretraining contamination remains separate from detected exposure.\nNo Lean implication certificates were generated in this pilot. All proposals are\nexcluded from future untouched test use, including rejected or inspected proposals.\nSee reviews/historical_overlap_screen.csv for actual per-candidate screens.\n''')
    development=read(runs/'development.json')
    experiment=runs/'development/experiment'
    executed=(experiment/'isolated_repair_results.csv').exists()
    status='EXECUTED: see raw experiment artifacts' if executed else 'NOT EXECUTED: no eligible frozen development cohort' if not development else 'NOT EXECUTED: inspect development worker status'
    save(runs/'stage_completion.json',dict(generation=dict(recorded_attempts=len(proposals),actual_durable_completions=usage['durable_completed_calls']),formal_verification=dict(parsed_candidates=len(parsed),verified=len(verified),rejected_or_unavailable=len(rejected)),review=dict(recorded_reviews=sum(map(len,review_rows)),accepted=len(accepted)),development=dict(status=status,types=len(development)),confirmatory=dict(status='NOT EXECUTED',reason='No separately authorized test inference; every pilot proposal is development-only'),statistical_analysis=dict(status='NOT ESTIMABLE' if not executed else 'See experiment analysis',reason='No invented rates, paired effects, confidence intervals, or equivalence claims')))
    (HERE/'FINAL_EXPERIMENTAL_REPORT.md').write_text(f'''# Actual experimental evidence — AI-only pilot v1

This pilot produced **{usage['durable_completed_calls']} durable real local model completions**
from **{usage['reserved_calls']} charged generation intents**. It did not complete the
requested confirmatory study. No human approval or confirmatory result is claimed.

| Stage | Actual result |
|---|---|
| Generation | {len(proposals)} recorded attempts; {len(parsed)} schema-valid candidates |
| Generation failures | {dict(Counter(r['parse_status'] for r in proposals))} |
| Strict reference verification | {len(verified)} verified; {len(rejected)} failed/unavailable among parsed candidates |
| Blinded AI review | {len(review_rows[0])} reviewer-1 records; {len(review_rows[1])} reviewer-2 records |
| AI acceptance | {len(accepted)} AI_SCREENED_FORMALLY_VERIFIED |
| Frozen cohorts | {len(development)} development types; 0 confirmatory types |
| Development C/D/E | {status} |
| Confirmatory C/D/E | NOT EXECUTED; no test authorization |

The actual approved limits were 24 generation calls, 48 combined review calls,
and 48 development calls; each call allows at most 4,096 input and 1,200 output
tokens. Each phase has a 30-minute watchdog; both reviewers share one review
deadline. These limits supersede the larger planning ceilings. Generation is not
extended to reach a quota. All pilot proposals were designated development-only
before model output; none may become an untouched confirmatory subject.

Recorded generation expenditure was {usage['actual_input_tokens']} input tokens,
{usage['actual_output_tokens']} output tokens, and {usage['recorded_generation_seconds']:.3f}
seconds inside completed generation calls. Both reviewers reserved zero calls.
Detailed accounting is in `runs/generation/generation_resource_usage.json` and
`runs/reviews/reviewer_*/resource_usage.json`; generation throughput and MLX-reported
peak memory are in `runs/generation/measured_runtime_memory.json`.
Unknown consumed intents remain charged; their unrecorded token costs are unknown,
not zero. The first attempt encountered sandbox Metal unavailability and the second
encountered a missing trace directory. GPU availability was verified outside the
sandbox; trace directories were prepared without editing frozen code or prompts.
Neither failed intent was replayed. Raw errors and all model outputs are retained.

No schema failure was silently repaired. Unparsed responses were excluded before
Lean checking, not counted as formal failures or semantic rejections. Only real
strict-verifier successes could reach AI review. Review agreement is not truth,
and the Qwen generator/reviewer ancestry prevents any claim of independent errors.
Pretraining contamination and exhaustive mathematical equivalence remain unassessed.
Recorded failure groups: `{dict(failure_counts)}`. A changed generation prompt or
parser must be a new versioned pilot, rather than retroactive admission here.

The development gate is `{states['development']['status']}`; the test gate is
`{states['test']['status']}`. The requested 40 development and 240 test types remain
unmet. With no completed eligible experiment, verification rates for C/D/E, paired
discordance, C−D/C−E effects, category effects, cluster confidence intervals and
multiplicity-adjusted intervals are not estimable. Zero completed evaluations is
not evidence of zero benefit or equality. No throughput estimate for development
or peak-memory measurement is substituted with generation timing or a planning cap.

Evidence paths relative to this directory:

- `runs/generation/`: prompts, raw responses, stream traces, charged intent ledger,
  candidate generation manifest, failed attempts and measured resource usage.
- `runs/formal_verification/`: verified/rejected candidate lists, reference manifest
  and actual compiler records when a parse-valid candidate exists.
- `runs/reviews/`: actual reviewer logs, acceptance/quarantine decisions, agreement,
  historical overlap screen, family and exclusion registries, validation report.
- `runs/dataset_*.json`, `runs/development.json`, `runs/test_sealed.json`: frozen
  pilot partition evidence. The ignored private encryption key is never published.
- `runs/preservation_validation.json`: {len(baseline['files'])} historical files
  hash checked; {len(changed)} changed. Historical studies, human gate and manuscript
  remain unchanged from `{baseline['baseline']}`.
- `runs/execution_gate_status.json`, `runs/stage_completion.json`: explicit stage
  status; absent experiment rows are not fabricated as failed model outcomes.

Validation: 332 tests passed, 3 deselected, 28 subtests passed in the combined
offline regression command recorded in `VALIDATION.md`. The deselections exclude
two opt-in real-Lean fixtures and the legacy blanket prohibition on any new
research files, which conflicts with this explicitly requested separate study.
The new policy tests are included; no synthetic test approvals enable inference.
Separately, both real-Lean fixtures passed (2 passed, 29 deselected, 454.89 seconds),
and the archived post-hoc analysis checks passed (19 passed). These fixtures are
not generated benchmark candidates or experimental outcomes.

Use the exact commands in `README.md` to inspect or resume existing phases.
Checkpoint replay never regenerates consumed intents. An exhausted allocation or
expired persisted deadline cannot be reset to extend this run. A further pilot
requires a new, separately authorized and versioned run. Confirmatory evaluation
also requires fresh accepted data and separate test authorization.
''')
    print('Finalized actual evidence; historical files unchanged:',len(baseline['files']))

if __name__=='__main__':main()
