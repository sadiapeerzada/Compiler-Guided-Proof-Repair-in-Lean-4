"""Read-only live counters. Intended allocations are never reported as actual calls."""
from study_common import *

if __name__=='__main__':
    for stage,spec in read(HERE/'resource_authorization.json')['stages'].items():
        out=run_root()/stage;ledger=rows(out/'calls/budget.jsonl');complete=list((out/'calls/calls').glob('*/completion.json'));records=rows(out/('reviews.jsonl' if spec['kind']=='review' else 'records.jsonl'))
        if ledger or records or (out/'phase_clock.json').exists():
            print(stage,dict(charged=len(ledger),durable_completions=len(complete),recorded_cases=len(records),strict_verified=sum(r.get('verification',{}).get('success') is True for r in records),qualified_AI_accepts=sum(r.get('decision')=='ACCEPT' for r in records),phase_limit=spec['max_calls']))
