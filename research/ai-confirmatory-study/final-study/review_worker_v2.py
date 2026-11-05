"""Identical blinded review policy, strict data-only model loading correction."""
from study_common import *
from review_protocol import candidates,review_prompt,parse_review
from runtime_v2 import PhaseModelV2

def execute(stage):
    spec,_=authorize(stage);ensure(spec['kind']=='review','Not a review stage')
    freeze='review_v2.json' if spec['stream']=='v3' else 'review_development_v2.json';frozen(freeze)
    out=run_root()/stage;done={r['id'] for r in rows(out/'reviews.jsonl')};model=None
    try:
        for c in candidates(spec['stream']):
            if c['id'] in done:continue
            if model is None:model=PhaseModelV2(stage,freeze)
            prompt=review_prompt(c);record,folder=model.call(prompt,dict(id=c['id'],subject_sha256=subject_hash(c)),4051001 if spec['reviewer']==1 else 5051001)
            entry=dict(id=c['id'],subject_sha256=subject_hash(c),statement_sha256=c['statement_sha256'],prompt_sha256=text_hash(prompt),record=record,source_call=str(folder.relative_to(HERE)),model=model.model,decision='UNCERTAIN',reviewer=spec['reviewer'],blinding='No other review, reference proof, generation or repair content supplied',loader_version='data-only-view-v2')
            if record['status']=='completed':
                entry['response_sha256']=text_hash(record['content'])
                try:entry['review']=parse_review(record);entry['decision']=entry['review']['decision']
                except (ValueError,KeyError,TypeError) as error:entry['parse_error']=str(error)
            append(out/'reviews.jsonl',entry)
            if record['status']!='completed':raise RuntimeError('Unavailable review; stop without retry')
    finally:
        if model:model.close()

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('stage');execute(p.parse_args().stage)
