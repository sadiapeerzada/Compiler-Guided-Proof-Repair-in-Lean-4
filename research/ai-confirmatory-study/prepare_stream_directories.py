"""Operational directory preparation only; no model invocation or intent editing."""
import argparse
from ai_common import HERE, read, save, digest, sha
from resource_gate import authorize

def prepare(stage):
    spec,_=authorize(stage)
    protocol=read(HERE/'ai_protocol_v1.json')
    model_key='generator' if stage=='generation' else 'experiment' if stage=='development' else stage
    model=protocol['models'][model_key]
    entries=[]
    if stage=='generation':
        root=HERE/'runs/generation'
        entries=[(3037001,['candidate',i]) for i in range(spec['max_calls'])]
    elif stage in ('reviewer_1','reviewer_2'):
        root=HERE/'runs/reviews'/stage
        rows=read(HERE/'runs/formal_verification/verified_candidates.json')
        entries=[(4037001 if stage=='reviewer_1' else 5037001,[stage,row['id']]) for row in rows[:spec['max_calls']]]
    elif stage=='development':
        root=HERE/'runs/development/model_calls'
        rows=read(HERE/'runs/development.json')
        for row in rows:
            for seed in protocol['experiment']['seeds']:
                for arm in ('A','C','D','E'):
                    outer=dict(phase=stage,protocol_sha256=sha(HERE/'ai_protocol_v1.json'),model_revision=protocol['experiment']['model']['revision'],model_id=protocol['experiment']['model']['model_id'],id=row['id'],seed=seed,arm=arm)
                    entries.append((seed,['experiment','confirmatory/'+digest(outer)]))
    else:raise ValueError('No test preparation in the development-only pilot')
    directories=[]
    for seed,context in entries:
        key=dict(stage=stage,key=context,seed=seed,model_id=model['id'],model_revision=model['revision'])
        folder=root/'calls/calls'/digest(key)/'stream'
        folder.mkdir(parents=True,exist_ok=True);directories.append(str(folder.relative_to(HERE)))
    save(HERE/'runs'/f'{stage}_stream_preparation.json',dict(stage=stage,prepared_directories=directories,inference_calls=0,existing_intents_or_outputs_modified=False))
    print('Prepared trace directories:',len(directories))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('stage',choices=['generation','reviewer_1','reviewer_2','development']);prepare(parser.parse_args().stage)
