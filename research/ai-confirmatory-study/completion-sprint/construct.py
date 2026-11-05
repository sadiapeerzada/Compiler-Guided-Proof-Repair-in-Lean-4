"""Direct source-grounded generation; existing native parser and rigid checker."""
import argparse,re
from sprint_common import *
from native_parser import NativeParser,ParseError,ParserUnavailable
from rigid_verifier import RigidVerifier
from overlap import fingerprint,transitivity_template
from lean_adapter import live_environment

def family(t):return 'list_relational_invariants' if t['family'] in ('list_pairwise','list_nodup') else t['family']
def reserved(text):
    return [r['namespace_marker'] for r in read(HERE/'heldout_reservations.json')['reservations'] if r['eligible_for_reserved_catalog'] and re.search(r'\b'+re.escape(r['namespace_marker'])+r'\b',text)]
def prompt(topic,identifier,attempt):
    return f'''Generate one genuinely mathematical, nontrivial Lean4.32.0 theorem about {topic['description']}. Import Mathlib is provided, pinned at81a5d257c8e410db227a6665ed08f64fea08e997. Use name {identifier}. You must supply the complete correct proof. Use the actual API facts below; compose a small relation rather than copy one fact verbatim. Prefer a short complete proof. Preserve exact quantifiers, domains and assumptions in English. No redundant/contradictory assumptions, reflexivity, plain transitivity, zero laws, ring identities, copied previous examples, helper declarations, imports or placeholders. Lean4 syntax only: := by with indentation, never begin/end, END BY, comma tactics or explanations. Case bullets are ·. Max1200 output tokens. Occurrence{attempt+1}: change the underlying relation, not just variable names. Return only:
STATEMENT: precise English
LEAN:
```lean
theorem {identifier} ... := by
  ...
```
FAMILY: specific mathematical relation
Replace all schematic dots with complete mathematics. Actual checked library signatures (not benchmark subjects; no proof is supplied):
'''+ '\n'.join(topic['api_facts'])

def basic_flags(c,scope,exposure):
    statement=c['expected_lean_statement'];result=[]
    if fingerprint(statement) in {fingerprint(x['statement']) for x in exposure['items']}:result.append('prior_exact_alias_alpha_exposure')
    if transitivity_template(statement):result.append('excluded_transitivity_template')
    # Broad reserved-domain separation, supplemented by semantic review later.
    hit=reserved(statement+' '+c['nl_statement'])
    if scope=='development' and hit:result.append('reserved_heldout_domain:'+','.join(hit))
    if scope=='test' and not hit:result.append('outside_reserved_heldout_domains')
    return result

def verify(c,verifier):
    out=RUN/'formal';store=RunStore(out,dict(scope='completion_sprint',authorization_sha256=sha(HERE/'resource_authorization.json')),dict(max_runtime_seconds=604800))
    folder=out/content_hash([c['id'],c['proof_sha256']]);folder.mkdir(parents=True,exist_ok=True)
    result=store.verify_once(folder,c['reference_proof'],c['expected_lean_statement'],verifier)
    record=dict(id=c['id'],source_sha256=c['proof_sha256'],target_sha256=c['statement_sha256'],result=result,record_path=str(folder.relative_to(HERE)))
    if not any(r['record_path']==record['record_path'] for r in rows(RUN/'formal_checks.jsonl')):append(RUN/'formal_checks.jsonl',record)
    return result

def execute(scope):
    stage=scope+'_generation';authorize(stage);lock=scope+'_construction.json';frozen(lock);out=RUN/stage;out.mkdir(parents=True,exist_ok=True)
    old=read(OLD/'protocol.json');dump(out/'environment.json',live_environment(old['environment']))
    plan=read(HERE/'family_schedule.json');topics=plan[scope];jobs=plan[scope+'_jobs'];seed=plan['seeds'][scope+'_generation'];exposure=read(HERE/('exposure_index.json' if scope=='development' else 'test_exposure_index.json'))
    records=rows(out/'records.jsonl');done={r['index'] for r in records};verifier=RigidVerifier();model=None;parser=None
    try:
        for index in range(jobs):
            if index in done:continue
            topic=topics[index%len(topics)];group=family(topic);prior=[r for r in records if r.get('canonical_family')==group]
            if len(prior)>=4 and not any(r.get('verification',{}).get('success') is True and not r.get('pre_review_flags') for r in prior):
                append(out/'skipped_jobs.jsonl',dict(index=index,family=group,status='FAMILY_RETIRED_AFTER_FOUR_NO_USABLE_VERIFICATIONS'));continue
            identifier=f'sprint_{scope}_{index:04d}';text=prompt(topic,identifier,index//len(topics))
            if model is None:model=Model(stage,lock)
            entry=dict(index=index,id=identifier,canonical_family=group,prompt=text,prompt_sha256=text_hash(text),scope=scope,status='PENDING')
            try:record,folder=model.call(text,dict(index=index,id=identifier),seed,release=True)
            except ValueError as error:
                if str(error)!='PROMPT_OVER_CAP_NO_CALL':raise
                entry.update(status='SKIPPED_NO_INFERENCE',reason=str(error));append(out/'records.jsonl',entry);records.append(entry);continue
            entry.update(record=record,source_call=str(folder.relative_to(HERE)))
            if record['status']!='completed':entry['status']='UNKNOWN_CONSUMED_INTENT';append(out/'records.jsonl',entry);raise ValueError('New unavailable generation; diagnose, no replay')
            try:
                if parser is None:parser=NativeParser(out/'native_parser')
                meta=record['metadata'];c=parser.candidate(record['content'].encode(),identifier,topic['description'],meta['completion_tokens'],meta['finish_reason'],folder)
                c['canonical_family']=group;c['generation_provenance']=dict(model=model.model,source_call=entry['source_call'],raw_response_sha256=text_hash(record['content']),prompt_sha256=text_hash(text),scope=scope,seed=seed)
                flags=basic_flags(c,scope,exposure);entry.update(candidate=c,pre_review_flags=flags,status='STRUCTURALLY_VALID',verification=verify(c,verifier))
            except ParseError as error:entry.update(status='STRUCTURE_REJECTED',reason=str(error))
            except ParserUnavailable as error:entry.update(status='PARSER_UNAVAILABLE',reason=str(error));append(out/'records.jsonl',entry);raise
            append(out/'records.jsonl',entry);records.append(entry)
            ensure(entry.get('verification',{}).get('success','not_checked') is not None,'New unavailable verifier; diagnose before unconsumed work')
    finally:
        if parser:parser.close()
        if model:model.close()
        valid=[dict(r['candidate'],reference_validation_variant='rigid_declaration_type_and_universe_v1',status='FORMALLY_VERIFIED_PENDING_AI_REVIEW') for r in rows(out/'records.jsonl') if r.get('verification',{}).get('success') is True and not r.get('pre_review_flags')]
        dump(RUN/(scope+'_verified.json'),valid)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('scope',choices=['development','test']);execute(p.parse_args().scope)
