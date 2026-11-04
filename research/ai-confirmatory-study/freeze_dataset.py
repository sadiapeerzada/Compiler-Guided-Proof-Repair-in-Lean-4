"""Deterministic development-only pilot selection; no quota filling or test promotion."""
from collections import defaultdict
from ai_common import HERE,read,save,digest,sha
from test_vault import seal

def main():
    accepted=read(HERE/'runs/reviews/accepted_candidates.json');groups=defaultdict(list)
    for row in accepted:groups[row['family']].append(row)
    selected=[]
    for family in sorted(groups,key=lambda f:digest(['pilot-dev',f])):
        group=sorted(groups[family],key=lambda r:r['id'])
        if len(selected)+len(group)<=4:selected.extend(group)
    save(HERE/'runs/development.json',selected,exclusive=True)
    # Every engineering-pilot candidate is excluded from future confirmatory use.
    seal([])
    manifest=dict(development=dict(count=len(selected),content_sha256=digest(selected),ids=[r['id'] for r in selected]),test=dict(count=0,content_sha256=digest([]),ids=[]),pilot_exposure='ALL candidates in this bounded pilot are development-only, never recycled as untouched test',accepted_reserve=[r['id'] for r in accepted if r not in selected])
    save(HERE/'runs/dataset_manifest.json',manifest,exclusive=True)
    save(HERE/'runs/dataset_freeze.json',dict(status='AI_SCREENED_PILOT_FROZEN_NOT_CONFIRMATORY',protocol_sha256=sha(HERE/'ai_protocol_v1.json'),manifest_sha256=sha(HERE/'runs/dataset_manifest.json'),independent_human_review=False),exclusive=True)
    (HERE/'runs/sample_size_feasibility.md').write_text(f'# Pilot sample feasibility\n\nAccepted{len(accepted)} of at most24 proposed candidates; selected{len(selected)} development types, each with3 declared seeds. The48-call experimental ceiling allows at most4 types at worst-case4 calls/evaluation. No confirmatory subjects are created from this engineering pilot. The40/240 targets remain unmet; no independent human review is claimed.\n')
    print('Frozen pilot development types:',len(selected),'; confirmatory types:0')

if __name__=='__main__':main()
