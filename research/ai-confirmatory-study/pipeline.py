"""Versioned AI-only benchmark pilot. All model calls require explicit resource caps."""
import argparse
import csv
import hashlib
import json
import math
import os
import re
import time
from collections import Counter,defaultdict
from difflib import SequenceMatcher
from pathlib import Path
from ai_common import HERE,ROOT,LEGACY,read,save,sha,digest,text_hash,jsonlines,lines,table,parse_json,ensure,subject_hash
from resource_gate import authorize
from model_runtime import AuthorizedLocalModel
from prompts import generation_prompt,reviewer_prompt
from dataset_tools import screen,cohort_flags
from lean_adapter import LeanVerifier,live_environment

FIELDS=['id','nl_statement','expected_lean_statement','reference_proof','domain','category','family','difficulty','imports','generation_provenance']

def phase_root(phase):
    root=HERE/'runs'/phase;root.mkdir(parents=True,exist_ok=True)
    return root

def deadline(phase):
    # Both reviewer families share one review-phase deadline, never two fresh windows.
    stage='reviewer_1' if phase=='reviews' else phase
    spec,_=authorize(stage);root=phase_root(phase);path=root/'phase_clock.json'
    if not path.exists():save(path,dict(started_epoch=time.time(),max_runtime_seconds=spec['max_runtime_seconds']),exclusive=True)
    clock=read(path);return clock['started_epoch']+clock['max_runtime_seconds']

def checked_model(stage,key,root):return AuthorizedLocalModel(stage,key,root)

def generate():
    spec,_=authorize('generation');end=deadline('generation');root=phase_root('generation')
    model=checked_model('generation','generator',root)
    proposals=lines(root/'candidate_generation.jsonl');done={r['index'] for r in proposals}
    try:
        for i in range(spec['max_calls']):
            if i in done:continue
            if time.time()>=end:break
            prompt=generation_prompt(i);record,folder=model.generate(prompt,3037001,['candidate',i])
            entry=dict(index=i,prompt=prompt,prompt_sha256=text_hash(prompt),seed=3037001,model=model.model['id'],revision=model.model['revision'],record=record,source_call=str(folder.relative_to(HERE)),cohort_use='DEVELOPMENT_ONLY_ENGINEERING_PILOT_NOT_CONFIRMATORY')
            if record['status']=='completed':
                try:
                    c=parse_json(record['content']);ensure(isinstance(c,dict),'Candidate is not a JSON object')
                    ensure(all(k in c for k in ['nl_statement','expected_lean_statement','reference_proof','domain','category','family','difficulty','imports']),'Required candidate field missing')
                    ensure(all(isinstance(c[k],str) and c[k].strip() for k in ['nl_statement','expected_lean_statement','reference_proof','domain','category','family']),'Invalid text fields')
                    ensure(c['imports']==['Mathlib'],'Candidate import scope differs from frozen generation policy')
                    ensure(c['expected_lean_statement'].count('theorem ')==1 and ':=' not in c['expected_lean_statement'],'Expected bare single theorem declaration')
                    c['id']='ai_pilot_'+str(i).zfill(3)+'_'+digest(c)[:10]
                    c['generation_provenance']=dict(model=model.model['id'],revision=model.model['revision'],prompt_sha256=text_hash(prompt),response_sha256=text_hash(record['content']),base_seed=3037001,source_call=entry['source_call'],source='recorded_local_AI_generation',cohort_use=entry['cohort_use'])
                    c['statement_sha256']=text_hash(c['expected_lean_statement']);c['proof_sha256']=text_hash(c['reference_proof']);entry['candidate']=c;entry['parse_status']='PARSED'
                except (ValueError,TypeError,KeyError) as error:entry['parse_status']='REJECTED_PARSE';entry['reason']=str(error)
            else:entry['parse_status']='UNAVAILABLE_GENERATION'
            jsonlines(root/'candidate_generation.jsonl',entry)
            if entry['parse_status']!='PARSED':jsonlines(root/'candidate_generation_failures.jsonl',entry)
            if record['status']!='completed':raise RuntimeError('Generation infrastructure unavailable; consumed intent retained, no replacement call')
    finally:model.close();summarize_resources('generation')
    return root

def verify():
    protocol=read(HERE/'ai_protocol_v1.json');root=phase_root('formal_verification');outputs=lines(root/'formal_verification.jsonl');done={r['id'] for r in outputs}
    verifier=LeanVerifier(['Mathlib'],timeout=protocol['reference_timeout_seconds']);environment=live_environment(protocol['experiment'])
    started=time.time()
    for proposal in lines(phase_root('generation')/'candidate_generation.jsonl'):
        if proposal.get('parse_status')!='PARSED':continue
        c=proposal['candidate']
        if c['id'] in done:continue
        if time.time()-started>=1800:break
        result=verifier(c['reference_proof'],c['expected_lean_statement'],'ai_ref_'+subject_hash(c)[:24])
        jsonlines(root/'formal_verification.jsonl',dict(id=c['id'],subject_sha256=subject_hash(c),reference_sha256=c['proof_sha256'],target_sha256=c['statement_sha256'],result=result,environment=environment,verifier_sha256=sha(ROOT/'src/verify.py'),adapter_sha256=sha(LEGACY/'lean_adapter.py')))
    outputs=lines(root/'formal_verification.jsonl');byid={r['id']:r for r in outputs}
    verified=[];rejected=[]
    for proposal in lines(phase_root('generation')/'candidate_generation.jsonl'):
        if proposal.get('parse_status')!='PARSED':continue
        c=proposal['candidate'];v=byid.get(c['id'])
        (verified if v and v['result']['success'] is True else rejected).append(c)
    save(root/'verified_candidates.json',verified);save(root/'rejected_candidates.json',rejected)
    save(root/'reference_verification_manifest.json',dict(verified=len(verified),rejected_or_unavailable=len(rejected),records_sha256=sha(root/'formal_verification.jsonl') if (root/'formal_verification.jsonl').exists() else None,scope='Strict formal proof checking, not English semantic validation'))
    print('Formal references:',len(verified),'verified;',len(rejected),'rejected/unavailable')

def history_for(candidate):
    history=list(csv.DictReader((LEGACY/'benchmark_inventory.csv').open()))
    query=candidate['expected_lean_statement']
    ranked=sorted(history,key=lambda r:SequenceMatcher(None,query,r['formal_statement'],autojunk=False).ratio(),reverse=True)
    # A bounded retrieval, explicitly disclosed to both reviewers. No judgments are exposed.
    return [dict(id=r['id'],statement=r['formal_statement'],family=r['family']) for r in ranked[:5]]

def reviews():
    end=deadline('reviews');candidates=read(phase_root('formal_verification')/'verified_candidates.json')
    root=phase_root('reviews')
    for stage,key in [('reviewer_1','reviewer_1'),('reviewer_2','reviewer_2')]:
        spec,_=authorize(stage);done={r['id'] for r in lines(root/(stage+'.jsonl'))}
        model=None
        try:
            for c in candidates:
                if c['id'] in done:continue
                if time.time()>=end:break
                if len(lines(root/(stage+'.jsonl')))>=spec['max_calls']:break
                if model is None:model=checked_model(stage,key,root/stage)
                prompt=reviewer_prompt(c,history_for(c));record,folder=model.generate(prompt,4037001 if stage=='reviewer_1' else 5037001,[stage,c['id']])
                entry=dict(id=c['id'],subject_sha256=subject_hash(c),model=model.model['id'],revision=model.model['revision'],family=model.model['family'],prompt_sha256=text_hash(prompt),input_sha256=digest({k:c[k] for k in ('nl_statement','expected_lean_statement','domain','category','family')}),record=record,source_call=str(folder.relative_to(HERE)),blinding='No other reviewer judgment, reference proof or generation prompt supplied')
                entry['decision']='UNCERTAIN'
                if record['status']=='completed':
                    try:
                        review=parse_json(record['content']);ensure(review['decision'] in ['ACCEPT','REJECT','UNCERTAIN'],'Invalid decision');ensure(isinstance(review['problems'],list) and isinstance(review['unresolved_critical'],list),'Missing structured concerns');ensure(isinstance(review['explanation'],str) and isinstance(review['semantic_checks'],dict),'Missing rationale/checks')
                        entry['review']=review;entry['decision']=review['decision'];entry['response_sha256']=text_hash(record['content'])
                    except (ValueError,KeyError,TypeError) as error:entry['parse_error']=str(error)
                jsonlines(root/(stage+'.jsonl'),entry)
                if record['status']!='completed':raise RuntimeError('Reviewer infrastructure unavailable; no replacement response')
        finally:
            if model:model.close()
            summarize_resources(stage)
        if time.time()>=end:break
    adjudicate()

def adjudicate():
    root=phase_root('reviews');candidates=read(phase_root('formal_verification')/'verified_candidates.json')
    a={r['id']:r for r in lines(root/'reviewer_1.jsonl')};b={r['id']:r for r in lines(root/'reviewer_2.jsonl')}
    flags=cohort_flags(candidates);accepted=[];quarantined=[];decisions=[];overlap=[]
    for c,within in zip(candidates,flags):
        # Use repository-wide historical screens; generated provenance, not a fictitious URL/license approval.
        probe={**c,'source_url':'local-AI-generated proposal; pretraining sources unassessed','license':'Researcher-generated artifact; upstream/model/source rights unassessed','library_dependencies':[]}
        check=screen(probe);reasons=check['automated_flags']+within
        ra=a.get(c['id']);rb=b.get(c['id'])
        both=bool(ra and rb and ra['family']!=rb['family'] and ra['model']!=c['generation_provenance']['model'] and rb['model']!=c['generation_provenance']['model'])
        approved=both and all(r['decision']=='ACCEPT' and not r['review']['unresolved_critical'] and not r['review']['problems'] for r in [ra,rb])
        if not approved:reasons.append('two_distinct_family_AI_acceptances_not_established')
        row=dict(id=c['id'],reviewer_1=ra['decision'] if ra else 'NOT_REVIEWED',reviewer_2=rb['decision'] if rb else 'NOT_REVIEWED',status='AI_SCREENED_FORMALLY_VERIFIED' if not reasons else 'QUARANTINED',reasons='; '.join(reasons))
        decisions.append(row);overlap.append(dict(id=c['id'],known_historical_exposure=any('historical' in x for x in reasons),automated_flags='; '.join(check['automated_flags']+within),AI_relationships=json.dumps([r.get('review',{}).get('historical_relationship') for r in (ra,rb) if r]),pretraining_contamination='UNASSESSED'))
        if reasons:quarantined.append(dict(candidate=c,reasons=reasons))
        else:accepted.append(dict(**c,status='AI_SCREENED_FORMALLY_VERIFIED',review_evidence=[ra['source_call'],rb['source_call']]))
    save(root/'accepted_candidates.json',accepted);save(root/'quarantined_candidates.json',quarantined)
    table(root/'adjudication_decisions.csv',decisions,['id','reviewer_1','reviewer_2','status','reasons'])
    table(root/'historical_overlap_screen.csv',overlap,['id','known_historical_exposure','automated_flags','AI_relationships','pretraining_contamination'])
    paired=[c for c in candidates if c['id'] in a and c['id'] in b];agree=sum(a[c['id']]['decision']==b[c['id']]['decision'] for c in paired)
    save(root/'reviewer_agreement.json',dict(paired_reviews=len(paired),agreements=agree,agreement_rate=agree/len(paired) if paired else None,interpretation='Model agreement is not proof of semantic truth; generator shares family with reviewer2; review models differ in checkpoint and family from each other.'))
    save(root/'mathematical_family_registry.json',{c['id']:c['family'] for c in candidates})
    table(root/'benchmark_exclusion_registry.csv',[dict(id=r['candidate']['id'],reason='; '.join(r['reasons'])) for r in quarantined],['id','reason'])
    print('AI-screened accepted:',len(accepted),'; quarantined:',len(quarantined))

def summarize_resources(stage):
    root=phase_root('generation') if stage=='generation' else phase_root('reviews')/stage
    ledger=root/'calls'/'budget.jsonl';events=lines(ledger)
    completed=[]
    for path in (root/'calls'/'calls').glob('*/completion.json') if (root/'calls'/'calls').exists() else []:completed.append(read(path))
    save(root/('generation_resource_usage.json' if stage=='generation' else 'resource_usage.json'),dict(stage=stage,reserved_calls=len(events),durable_completed_calls=len(completed),unknown_consumed_calls=len(events)-len(completed),actual_input_tokens=sum(r['metadata']['prompt_tokens'] for r in completed) if completed else None,actual_output_tokens=sum(r['metadata']['completion_tokens'] for r in completed) if completed else None,recorded_generation_seconds=sum(r['metadata'].get('latency_seconds',0) for r in completed) if completed else None,caveat='Only durable actual metadata; unknown compute is not estimated. Intended limits are not actual expenditure.'))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('command',choices=['generate','verify','reviews','adjudicate']);a=p.parse_args()
    {'generate':generate,'verify':verify,'reviews':reviews,'adjudicate':adjudicate}[a.command]()
