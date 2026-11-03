"""One-time derivative capture from genuine local V7 trajectories, never inference.

Default analysis uses the committed views and does not run this file.
An existing snapshot is never overwritten. Original-file hashes identify the
captured bytes, not external historical authentication.
"""
import json
from pathlib import Path
from supplement import ROOT, OUT, sha, require, clean


def step_view(step):
    verification=step.get('verification') or {}
    return {**{k:step[k] for k in ('key','candidate','candidate_sha256','metadata')},
            'details':step.get('details',{}),
            'verification':{k:verification.get(k) for k in ('candidate_sha256','diagnostic_text','success','failure_kind','exit_code','axiom_dependencies')}}


def main():
    output=OUT/'sources/v7_trajectory_views.json'
    require(not output.exists(),'Refusing to overwrite committed derivative snapshot')
    views=[]
    for path in sorted((ROOT/'study2_outputs/bridge_v7_base/trajectories').glob('*/20*/test/*.json')):
        raw=path.read_bytes();t=json.loads(raw)
        view={k:t[k] for k in ('model','seed','id','family','category','order','split','terminal')}
        view['initial']=step_view(t['initial'])
        view['arms']={a:{'outcome':v['outcome'],'status':v['status'],'steps':[step_view(s) for s in v['steps']]} for a,v in t['arms'].items()}
        views.append(dict(original_path=str(path.relative_to(ROOT)),original_sha256=sha(raw),trajectory=view))
    require(len(views)==72,'Missing local V7 trajectories')
    text=json.dumps(views,indent=2,ensure_ascii=False,sort_keys=True)+'\n'
    require(clean(text)==text,'A sensitive path requires explicit review before derivative capture')
    output.parent.mkdir(exist_ok=True)
    with output.open('x') as f:f.write(text)

if __name__=='__main__':main()
