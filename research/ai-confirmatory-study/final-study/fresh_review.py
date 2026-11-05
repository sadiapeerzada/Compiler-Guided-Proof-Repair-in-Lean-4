"""Prospectively explicit boolean-check schema for new development subjects.

This does not reparse or change the original four V3 review outcomes.
"""
import json,re
from study_common import *
from review_protocol import CHECKS
from overlap import nearest as neighbors
from runtime_v2 import PhaseModelV2

POSITIVE=('mathematical_correctness','English_Lean_fidelity','quantifiers','domains','assumptions','boundaries','family_independence')
NEGATIVE=('strengthening_weakening','ambiguity','historical_overlap')

def prompt(c):
    pool=read(run_root()/'fresh_verified.json')+read(run_root()/'v3_input.json')
    from difflib import SequenceMatcher
    related=sorted([r for r in pool if r['id']!=c['id']],key=lambda r:SequenceMatcher(None,c['expected_lean_statement'],r['expected_lean_statement'],autojunk=False).ratio(),reverse=True)[:3]
    related=[{k:r[k] for k in ('id','expected_lean_statement','family')} for r in related]
    subject={k:c[k] for k in ('id','nl_statement','expected_lean_statement','category','family')}
    schema=dict(decision='ACCEPT or REJECT or UNCERTAIN',explanation='a specific explanatory sentence',concerns=[],unresolved_critical=[],confidence=0.0,semantic_checks={k:True if k in POSITIVE else False for k in CHECKS},historical_relationship='NO_DETECTED_RELATION or POSSIBLE_RELATION or KNOWN_RELATION or UNASSESSED',historical_explanation='specific reason',family_assessment='DISTINCT or RELATED or UNCERTAIN',family_explanation='specific reason')
    return '''Independently assess an AI-generated English/Lean theorem pair for mathematical correctness, exact semantic fidelity, quantifiers/domains/assumptions/boundaries, strengthening or weakening, ambiguity, historical equivalence/specialization and family independence. You are an AI screener, not a human. You see no reference proof, generator prompt, repair response or other reviewer judgment. Be conservative: missing evidence or possible overlap requires UNCERTAIN/REJECT. Reject tautological/trivial benchmark templates and unjustified family independence. family is a controller-defined broad grouping, not proof of originality. Retrieved excerpts are bounded lexical neighbors, not exhaustive semantic/pretraining coverage. All semantic_checks values MUST be JSON booleans, never arrays/strings/null. ACCEPT requires all correctness/fidelity/quantifier/domain/assumption/boundary/family-independence flags true; strengthening_weakening, ambiguity and historical_overlap false; empty concern lists; confidence at least0.8; historical_relationship NO_DETECTED_RELATION; family_assessment DISTINCT. Confidence is not a calibrated probability. Return only one concise JSON object with every field in this schema. Supply real rationale, not the sample labels. Plain English/Unicode, no LaTeX or backslashes.\nSCHEMA:\n'''+json.dumps(schema)+'\nSUBJECT:\n'+json.dumps(subject,ensure_ascii=False)+'\nHISTORICAL_NEIGHBORS:\n'+json.dumps(neighbors(c),ensure_ascii=False)+'\nOTHER_EXPOSED_PROPOSALS:\n'+json.dumps(related,ensure_ascii=False)

def parse_review(record):
    ensure(record['status']=='completed' and record['metadata']['finish_reason']!='length','Review absent/truncated')
    text=record['content'].strip();m=re.fullmatch(r'```(?:json)?\s*\n(.*)\n```',text,re.S)
    if m:text=m.group(1)
    r=json.loads(text);ensure(r['decision'] in ('ACCEPT','REJECT','UNCERTAIN'),'Invalid decision')
    ensure(all(isinstance(r[k],str) and r[k].strip() for k in ('explanation','historical_explanation','family_explanation')),'Missing exact rationale')
    ensure(r['historical_relationship'] in ('NO_DETECTED_RELATION','POSSIBLE_RELATION','KNOWN_RELATION','UNASSESSED') and r['family_assessment'] in ('DISTINCT','RELATED','UNCERTAIN'),'Invalid relation verdict')
    ensure(all(isinstance(r[k],list) and all(isinstance(s,str) for s in r[k]) for k in ('concerns','unresolved_critical')),'Invalid concerns')
    ensure(type(r['confidence']) in (int,float) and 0<=r['confidence']<=1,'Invalid confidence')
    ensure(all(type(r['semantic_checks'][k]) is bool for k in CHECKS),'Checks must be explicit booleans')
    if r['decision']=='ACCEPT':
        ensure(not r['concerns'] and not r['unresolved_critical'] and r['confidence']>=.8 and r['historical_relationship']=='NO_DETECTED_RELATION' and r['family_assessment']=='DISTINCT','ACCEPT has unresolved relation/concern')
        ensure(all(r['semantic_checks'][k] for k in POSITIVE) and not any(r['semantic_checks'][k] for k in NEGATIVE),'ACCEPT contradicts check flags')
    return r

def execute(stage):
    spec,_=authorize(stage);ensure(stage in ('development_review_1','development_review_2'),'Fresh development review only');frozen('fresh_review_v1.json');out=run_root()/stage;done={r['id'] for r in rows(out/'reviews.jsonl')};model=None
    try:
        for c in read(run_root()/'fresh_verified.json'):
            if c['id'] in done:continue
            if model is None:model=PhaseModelV2(stage,'fresh_review_v1.json')
            text=prompt(c);entry=dict(id=c['id'],subject_sha256=subject_hash(c),statement_sha256=c['statement_sha256'],prompt_sha256=text_hash(text),decision='UNCERTAIN',reviewer=spec['reviewer'],model=model.model,schema_version='explicit_boolean_v1')
            try:record,folder=model.call(text,dict(id=c['id'],subject_sha256=subject_hash(c)),4052001 if spec['reviewer']==1 else 5052001)
            except ValueError as error:
                if str(error)!='PROMPT_OVER_CAP_NO_CALL':raise
                entry['parse_error']=str(error);append(out/'reviews.jsonl',entry);continue
            entry.update(record=record,source_call=str(folder.relative_to(HERE)))
            if record['status']=='completed':
                entry['response_sha256']=text_hash(record['content'])
                try:entry['review']=parse_review(record);entry['decision']=entry['review']['decision']
                except (ValueError,KeyError,TypeError) as error:entry['parse_error']=str(error)
            append(out/'reviews.jsonl',entry)
            if record['status']!='completed':raise RuntimeError('Unavailable review, no replacement')
    finally:
        if model:model.close()

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('stage');execute(p.parse_args().stage)
