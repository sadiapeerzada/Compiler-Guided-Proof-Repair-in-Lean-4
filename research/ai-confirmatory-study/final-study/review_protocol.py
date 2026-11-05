import json,re,csv
from difflib import SequenceMatcher
from study_common import *

CHECKS=('mathematical_correctness','English_Lean_fidelity','quantifiers','domains','assumptions','boundaries','strengthening_weakening','ambiguity','historical_overlap','family_independence')

def neighbors(c):
    historical=list(csv.DictReader((LEGACY/'benchmark_inventory.csv').open()))
    ranked=sorted(historical,key=lambda r:SequenceMatcher(None,c['expected_lean_statement'],r['formal_statement'],autojunk=False).ratio(),reverse=True)
    return [dict(id=r['id'],statement=r['formal_statement'],family=r['family']) for r in ranked[:5]]

def review_prompt(c):
    subject={k:c[k] for k in ('id','nl_statement','expected_lean_statement','category','family')}
    return '''Independently review this paired English mathematical statement and Lean theorem type. You are an AI screener, not a human reviewer. No reference proof, generation prompt, other reviewer judgment or repair response is supplied. Assess correctness, semantic fidelity, quantifiers/domains, every assumption and boundary, hidden strengthening/weakening, ambiguity, historical equivalence/specialization, and mathematical-family independence. Reject trivial benchmark templates or unjustified novelty/family claims; uncertainty or possible unresolved overlap must not be accepted. Retrieved history is only five lexical neighbors, not exhaustive mathematics or pretraining coverage. Return one concise JSON object only, with decision ACCEPT/REJECT/UNCERTAIN, explanation (string), concerns (list of specific strings), unresolved_critical (list), confidence (0..1), semantic_checks (object with all keys '''+json.dumps(CHECKS)+'''), historical_relationship (string), family_assessment (string). Use plain English and Unicode symbols, no LaTeX or backslash escapes. Do not claim independent human validation. Agreement is not mathematical truth.\nSUBJECT:\n'''+json.dumps(subject,ensure_ascii=False)+'\nHISTORICAL_NEIGHBORS:\n'+json.dumps(neighbors(c),ensure_ascii=False)

def parse_review(record):
    ensure(record['status']=='completed','No completed reviewer response')
    ensure(record['metadata']['finish_reason']!='length','Review truncated at output cap')
    text=record['content'].strip();m=re.fullmatch(r'```(?:json)?\s*\n(.*)\n```',text,re.S)
    if m:text=m.group(1)
    r=json.loads(text)
    ensure(r['decision'] in ('ACCEPT','REJECT','UNCERTAIN'),'Invalid decision')
    ensure(all(isinstance(r[k],str) and r[k].strip() for k in ('explanation','historical_relationship','family_assessment')),'Missing explicit rationale')
    ensure(all(isinstance(r[k],list) and all(isinstance(s,str) for s in r[k]) for k in ('concerns','unresolved_critical')),'Invalid concern lists')
    ensure(type(r['confidence']) in (int,float) and 0<=r['confidence']<=1,'Invalid confidence')
    ensure(isinstance(r['semantic_checks'],dict) and all(k in r['semantic_checks'] and isinstance(r['semantic_checks'][k],str) and r['semantic_checks'][k].strip() for k in CHECKS),'Missing semantic checks')
    if r['decision']=='ACCEPT':ensure(not r['concerns'] and not r['unresolved_critical'],'Acceptance contains unresolved concerns')
    return r

def candidates(stream):
    if stream=='v3':return read(run_root()/'v3_input.json')
    ensure(stream=='development','No confirmatory stream authorization')
    return read(run_root()/'fresh_verified.json')

def execute(stage):
    from local_runtime import PhaseModel
    spec,_=authorize(stage);ensure(spec['kind']=='review','Not a review stage')
    freeze='review_v1.json' if spec['stream']=='v3' else 'review_development_v1.json';frozen(freeze);out=run_root()/stage;done={r['id'] for r in rows(out/'reviews.jsonl')};model=None
    try:
        for c in candidates(spec['stream']):
            if c['id'] in done:continue
            if model is None:model=PhaseModel(stage,freeze)
            prompt=review_prompt(c);record,folder=model.call(prompt,dict(id=c['id'],subject_sha256=subject_hash(c)),4051001 if spec['reviewer']==1 else 5051001)
            entry=dict(id=c['id'],subject_sha256=subject_hash(c),statement_sha256=c['statement_sha256'],prompt_sha256=text_hash(prompt),record=record,source_call=str(folder.relative_to(HERE)),model=model.model,decision='UNCERTAIN',reviewer=spec['reviewer'],blinding='No other review, reference proof, generation or repair content supplied')
            if record['status']=='completed':
                entry['response_sha256']=text_hash(record['content'])
                try:entry['review']=parse_review(record);entry['decision']=entry['review']['decision']
                except (ValueError,KeyError,TypeError) as error:entry['parse_error']=str(error)
            append(out/'reviews.jsonl',entry)
            if record['status']!='completed':raise RuntimeError('Unavailable reviewer generation; stop, no replacement')
    finally:
        if model:model.close()

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('stage');execute(p.parse_args().stage)
