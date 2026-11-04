"""Read-only post-hoc diagnostics. Never emits eligible/new candidates."""
import json,re,sys,hashlib
from collections import Counter
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from ai_common import HERE as OLD,lines,read,sha,save
from parser_v2 import parse_response,ParseError
HERE=Path(__file__).resolve().parent

def diagnose():
    results=[]
    for proposal in lines(OLD/'runs/generation/candidate_generation.jsonl'):
        record=proposal['record']
        if record['status']!='completed':continue
        raw=record['content'];metadata=record['metadata'];folder=OLD/proposal['source_call']
        entry=dict(index=proposal['index'],source=str(folder.relative_to(OLD)),completion_file_sha256=sha(folder/'completion.json'),raw_response_sha256=hashlib.sha256(raw.encode()).hexdigest(),prompt_sha256=proposal['prompt_sha256'],finish_reason=metadata['finish_reason'],output_tokens=metadata['completion_tokens'],historical_failure=proposal['reason'],posthoc_only=True,eligibility='EXCLUDED_FROM_V2_AND_CONFIRMATORY')
        try:parse_response(raw.encode(),output_tokens=metadata['completion_tokens'],finish_reason=metadata['finish_reason']);entry['strict_V2_parse']='PARSED'
        except ParseError as error:entry['strict_V2_parse']=str(error)
        fenced=re.search(r'```(?:json)?\s*(.*?)```',raw,re.S)
        body=fenced.group(1) if fenced else raw
        entry['Markdown_fenced']=bool(fenced)
        # Diagnostic-only recovery doubles illegal JSON escapes; all altered bytes
        # remain separately disclosed. It never changes or validates mathematics.
        escaped=re.sub(r'\\(?!["\\/bfnrtu])',r'\\\\',body)
        try:
            fields=json.loads(escaped);entry['legacy_fields_inspectable']=isinstance(fields,dict)
            entry['diagnostic_invalid_escape_doubling_used']=escaped!=body
            target=fields.get('expected_lean_statement','');proof=fields.get('reference_proof','')
            entry['target_contains_assignment']=':=' in target
            entry['proof_uses_Lean3_begin_end']=bool(re.search(r'\bbegin\b',proof))
            entry['proof_contains_import']=bool(re.search(r'^\s*import ',proof,re.M))
            entry['proof_contains_placeholder']='...' in proof or '...' in target
        except (ValueError,AttributeError):entry['legacy_fields_inspectable']=False
        streams=list((folder/'stream').glob('*.jsonl'))
        chunks=[r['text'] for p in streams for r in lines(p) if 'token' in r and 'text' in r]
        entry['stream_reconstruction_matches_completion']=''.join(chunks)==raw
        results.append(entry)
    aggregate=dict(scope='OFFLINE_POSTHOC_ONLY_NOT_NEW_GENERATIONS',durable_responses=len(results),strict_V2_parses=sum(r['strict_V2_parse']=='PARSED' for r in results),legacy_fields_inspectable=sum(r['legacy_fields_inspectable'] for r in results),length_limited=sum(r['finish_reason']=='length' for r in results),all_streams_match=all(r['stream_reconstruction_matches_completion'] for r in results),flags={k:sum(r.get(k,False) for r in results) for k in ('Markdown_fenced','diagnostic_invalid_escape_doubling_used','target_contains_assignment','proof_uses_Lean3_begin_end','proof_contains_import','proof_contains_placeholder')},records=results)
    save(HERE/'offline/archived_response_diagnostics.json',aggregate)
    print({k:v for k,v in aggregate.items() if k!='records'})

if __name__=='__main__':diagnose()
