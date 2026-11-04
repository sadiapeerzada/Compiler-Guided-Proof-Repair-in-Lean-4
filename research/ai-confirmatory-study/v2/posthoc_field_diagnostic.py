"""Post-hoc alternate-label diagnosis, never a prospective intake success.

No inference. Only responses containing all six explicit colon-labelled fields in
order, with a completed stream, are inspectable. Marker framing is synthesized
solely to test existing parser invariants; mathematical field text is unmodified.
The original cohort and its zero parse successes are never changed.
"""
import re
from v2_common import *
from pipeline_v2 import root
from parser_v2 import FIELDS,MARKERS,parse_response,ParseError

def diagnose():
    from lean_adapter import LeanVerifier,live_environment
    from checkpoint import RunStore
    protocol=frozen();out=root()/'posthoc_alternate_labels';out.mkdir(exist_ok=True)
    evidence=[];candidates=[]
    for row in rows(root()/'v2_candidates.jsonl'):
        response=row['record'];entry=dict(index=row['index'],scope='POSTHOC_DIAGNOSTIC_ONLY_NOT_INTAKE_OR_AI_ACCEPTANCE',source_call=row['source_call'],original_raw_response_sha256=row.get('raw_response_sha256'))
        if response['status']!='completed' or response['metadata']['finish_reason']=='length':entry['status']='NOT_COMPLETE_RESPONSE';evidence.append(entry);continue
        text=response['content'];matches=list(re.finditer(r'^(ID|STATEMENT|TARGET|PROOF|CATEGORY|FAMILY):[ \t]*(.*)$',text,re.M))
        if [m.group(1) for m in matches]!=list(FIELDS) or text[:matches[0].start()].strip() if matches else True:
            entry['status']='NO_UNAMBIGUOUS_COMPLETE_COLON_LABEL_SET';evidence.append(entry);continue
        values={}
        for i,match in enumerate(matches):
            end=matches[i+1].start() if i+1<len(matches) else len(text)
            values[match.group(1)]=text[match.start(2):end].strip()
        canonical='\n'.join(part for field in FIELDS for part in (f'<<<{field}>>>',values[field]))+'\n<<<END>>>'
        try:
            candidate=parse_response(canonical.encode(),output_tokens=response['metadata']['completion_tokens'],finish_reason=response['metadata']['finish_reason'])
            candidate['scope']=entry['scope'];candidate['original_raw_response_sha256']=entry['original_raw_response_sha256'];candidate['diagnostic_canonical_framing_sha256']=candidate.pop('raw_response_sha256')
            entry['status']='COMPLETE_FIELDS_EXTRACTED_POSTHOC';entry['diagnostic_id']=candidate['id'];candidates.append(candidate)
        except ParseError as error:entry['status']='POSTHOC_STRUCTURE_REJECTED';entry['reason']=str(error)
        evidence.append(entry)
    dump(out/'field_extraction.json',dict(records=evidence,candidates=candidates,mathematical_content_not_edited=True,original_intake_not_modified=True))
    if not candidates:return
    environment=live_environment(protocol['environment']);verifier=LeanVerifier(['Mathlib'],timeout=protocol['reference_timeout_seconds'])
    store=RunStore(out/'reference_checks',dict(scope='POSTHOC_DIAGNOSTIC_ONLY',source_script_sha256=sha(HERE/'posthoc_field_diagnostic.py'),protocol_sha256=sha(HERE/'protocol_v2.json')),dict(max_runtime_seconds=1800))
    results=[]
    for candidate in candidates:
        folder=out/'reference_checks'/candidate['id'];folder.mkdir(exist_ok=True)
        result=store.verify_once(folder,candidate['reference_proof'],candidate['expected_lean_statement'],verifier)
        results.append(dict(id=candidate['id'],scope='POSTHOC_DIAGNOSTIC_ONLY',result=result,environment=environment,original_raw_response_sha256=candidate['original_raw_response_sha256']))
    dump(out/'formal_diagnostic.json',dict(results=results,not_prospective_intake_successes=True,no_AI_review_or_eligibility_claim=True))
    print('Post-hoc exact-field checks:',len(results),'; strictly verified:',sum(r['result']['success'] is True for r in results))

if __name__=='__main__':diagnose()
