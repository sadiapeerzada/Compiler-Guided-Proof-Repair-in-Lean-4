"""Read all prior AI responses as exposure, never as new successful candidates."""
import csv,re,json
from study_common import *
from header_parser import NativeHeaderParser
from native_parser import ParseError,ParserUnavailable
from overlap import fingerprint

def main():
    output=run_root()/'expanded_historical_exposure.json';ensure(not output.exists(),'Historical exposure view already frozen')
    items=[];coverage=[];unknown=[];server=None;folder=run_root()/'exposure_header_checks';folder.mkdir(exist_ok=True)
    for r in csv.DictReader((LEGACY/'benchmark_inventory.csv').open()):items.append(dict(id=r['id'],statement=r['formal_statement'],family=r['family'],source='historical_193_version_inventory',fingerprint=fingerprint(r['formal_statement'])))
    for i,r in enumerate(read(LEGACY/'historical_exposure_index.json')['items']):
        statement='theorem exposure_'+str(i)+' '+r['formal_prefix'];items.append(dict(id='historical_generated_'+str(i),statement=statement,family='UNASSESSED_HISTORICAL_EXPOSURE',source=r['source_examples'],fingerprint=fingerprint(statement)))
    sources=[('V1',OLD/'runs/generation/candidate_generation.jsonl',OLD),('V2',next((OLD/'v2/runs').glob('*/v2_candidates.jsonl')),OLD/'v2'),('V3',OLD/'v3/runs/20261104T163622Z_v3/generation/records.jsonl',OLD/'v3')]
    try:
        for version,path,base in sources:
            for r in rows(path):
                record=r.get('record',{});raw=record.get('content')
                if not isinstance(raw,str):continue
                tag=version+'_'+str(r['index']);coverage.append(dict(id=tag,raw_response_sha256=text_hash(raw),source=str(path.relative_to(ROOT))))
                candidate=r.get('candidate');statement=candidate.get('expected_lean_statement') if candidate else None;family=candidate.get('family','UNASSESSED') if candidate else 'UNASSESSED'
                if not statement:
                    text=raw.strip();m=re.search(r'```(?:json)?\s*(.*?)```',text,re.S);body=m.group(1) if m else text
                    try:
                        decoded=json.loads(re.sub(r'\\(?!["\\/bfnrtu])',r'\\\\',body));statement=decoded.get('expected_lean_statement');family=decoded.get('family',family)
                    except (ValueError,AttributeError):pass
                if statement and ':=' not in statement:
                    items.append(dict(id=tag,statement=statement,family=family,source='prior_AI_intake_target_unverified_exposure',raw_response_sha256=text_hash(raw),fingerprint=fingerprint(statement)));continue
                snippet=statement
                if not snippet:
                    m=re.search(r'\btheorem\s+([A-Za-z_][A-Za-z0-9_]*)\b',raw)
                    if not m:unknown.append(dict(id=tag,reason='No extractable theorem header'));continue
                    snippet=raw[m.start():]
                m=re.match(r'\s*theorem\s+([A-Za-z_][A-Za-z0-9_]*)\b',snippet)
                if not m:unknown.append(dict(id=tag,reason='No identifiable theorem declaration'));continue
                if server is None:server=NativeHeaderParser(folder/'server')
                case=folder/tag;case.mkdir(exist_ok=True)
                try:target,_=server.split(snippet,m.group(1),case)
                except (ParseError,ValueError) as error:unknown.append(dict(id=tag,reason=str(error)));continue
                items.append(dict(id=tag,statement=target,family=family,source='posthoc_header_exposure_only_not_proof_success',raw_response_sha256=text_hash(raw),fingerprint=fingerprint(target)))
    finally:
        if server:server.close()
    dump(output,dict(items=items,prior_AI_response_coverage=coverage,unextractable_AI_headers=unknown,original_historical_versions=193,prior_unique_exposure_entries=242,scope='Exact/type-alias/alpha and standard-transitivity checks plus bounded model relation screening; incomplete/exposure-only statements do not establish truth or exhaustive novelty'),exclusive=True)
    print('Expanded exposure statements:',len(items),'; prior AI responses inspected:',len(coverage),'; unextractable:',len(unknown))

if __name__=='__main__':main()
