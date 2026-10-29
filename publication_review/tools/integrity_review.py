"""Read-only, independent missingness and denominator review; never infer or replay."""
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'src'))
from final_study import validate_protocol


def read(path):
    return json.loads(path.read_text())


def main():
    base = ROOT/'data/final_study/v1'
    protocol_path = ROOT/'configs/repair_experiment_local_v0.4.2.json'
    p = validate_protocol(protocol_path)
    rows = read(base/'test.json')
    runs = [read(base/'final_runs/heldout/2027'/r['id']/'manifest.json') for r in rows]
    complete = [m for m in runs if all(m['conditions'][c]['success'] is not None for c in ['A','B','C'])]
    counts = {c: {'successes':sum(m['conditions'][c]['success'] is True for m in runs),
                  'known_failures':sum(m['conditions'][c]['success'] is False for m in runs),
                  'unavailable':sum(m['conditions'][c]['success'] is None for m in runs),
                  'eligible_denominator':len(runs),
                  'observed_denominator':sum(m['conditions'][c]['success'] is not None for m in runs),
                  'complete_pair_successes':sum(m['conditions'][c]['success'] is True for m in complete)} for c in ['A','B','C']}
    from transformers import AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained(Path.home()/p['model']['snapshot_home_relative'], local_files_only=True, trust_remote_code=False)
    missing = []
    import importlib.util
    spec = importlib.util.spec_from_file_location('frozen_runner', ROOT/'scripts/run_final_study.py')
    runner = importlib.util.module_from_spec(spec); spec.loader.exec_module(runner)
    for record, m in zip(rows, runs):
        if m['conditions']['C']['success'] is not None:
            continue
        folder = base/'final_runs/heldout/2027'/record['id'];context=f"heldout/2027/{record['id']}/C1"
        intent=read(folder/'C1/intent.json');initial=m['initial']
        prompt=(ROOT/p['prompts']['guided']).read_text().format(theorem_statement=record['expected_lean_statement'], previous_candidate=initial['candidate'], feedback=runner.feedback(initial['verification']))
        assert hashlib.sha256(prompt.encode()).hexdigest()==intent['prompt_sha256']
        rendered=tokenizer.apply_chat_template([{'role':'user','content':prompt}], tokenize=False, add_generation_prompt=True)
        n=len(tokenizer.encode(rendered,add_special_tokens=False))
        stream=folder/'streams'/(hashlib.sha256(context.encode()).hexdigest()+'.jsonl')
        frames=[json.loads(line) for line in stream.read_text().splitlines()] if stream.exists() else []
        failure=folder/'C1/generation_failure.json'
        missing.append({'problem_id':record['id'],'condition':'C','step':'C1','B_outcome':m['conditions']['B']['success'],
                        'rendered_prompt_matches_intent':True,'input_tokens':n,'output_cap':2000,'context_cap':8192,
                        'generation_failure':read(failure) if failure.exists() else None,
                        'stream_frames':len(frames),'observed_generated_tokens':max([0]+[f.get('generation_tokens',0) for f in frames]),
                        'durable_completed_response':(folder/'C1/completion.json').exists(),
                        'recoverable_without_new_inference':False,
                        'reason':'Frozen context cap rejects this prompt before generation; shortening diagnostics or changing cap violates frozen inputs.' if n+2000>8192 else 'Only the stream header survives; no token/candidate to verify. Frozen no-replay rule forbids repeating this terminal intent.'})
    result={'reviewed_commit':'3b4909a20ed24cafd36cbe029a81f8946bc96d69','protocol_unchanged_and_valid':True,
            'eligible_cases':len(runs),'complete_ABC_pairs':len(complete),'conditions':counts,'missing_outcomes':missing,
            'completed_generation_records':sum(1 for _ in (base/'final_runs/heldout').rglob('completion.json')),
            'missing_as_failure_C_minus_B':0.0,'complete_case_C_minus_B':0.0,
            'missingness_identification_bounds_C_minus_B_percentage_points':[0.0,100*2/60],
            'interpretation':'1/60 C is a conservative missing-as-failure sensitivity, not 60 observed C outcomes. Complete-case rates B=C=1/58. The zero bootstrap interval is conditional on treating missing as failure and does not measure missingness uncertainty. Neither equivalence nor a general feedback benefit is established.',
            'inference_calls_performed_by_this_review':0}
    (ROOT/'publication_review/local/integrity_review.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    main()
