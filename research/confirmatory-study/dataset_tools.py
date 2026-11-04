"""Prospective candidate intake. No historical item becomes a fresh test by relabeling."""
import argparse
import csv
from collections import defaultdict
from common import HERE,content_hash,read,dump,ensure,normalize,csv_write

SUBJECT_FIELDS=('id','nl_statement','expected_lean_statement','reference_proof','family','source_url','license','library_dependencies')

def subject_hash(row):return content_hash({k:row.get(k) for k in SUBJECT_FIELDS})

def screen(row,history=None,exposure=None):
    history=history if history is not None else list(csv.DictReader((HERE/'benchmark_inventory.csv').open()))
    exposure=exposure if exposure is not None else read(HERE/'historical_exposure_index.json')['items']
    flags=[]
    for k in SUBJECT_FIELDS[:-1]:
        if not isinstance(row.get(k),str) or not row[k].strip():flags.append('missing_'+k)
    statement=row.get('expected_lean_statement','')
    if statement.count('theorem ')!=1 or ':=' in statement:flags.append('target_must_be_one_unproved_fixed_theorem_declaration')
    if 'placeholder' in row.get('nl_statement','').lower() or 'Synthetic controlled mathematical' in row.get('nl_statement',''):flags.append('placeholder_english')
    norm=normalize(statement,True)
    if any(normalize(r['formal_statement'],True)==norm for r in history):flags.append('historical_statement_overlap')
    if any(r['alpha_fingerprint']==content_hash(norm) for r in exposure):flags.append('historical_generated_candidate_overlap')
    if row.get('family') and any(r['family']==row['family'] for r in history):flags.append('historical_declared_family_overlap')
    if any(r['id']==row.get('id') for r in history):flags.append('historical_identifier_reuse')
    return dict(id=row.get('id'),subject_sha256=subject_hash(row),automated_flags=sorted(set(flags)),quarantine=bool(flags),independent_review_required=True,pretraining_contamination='UNKNOWN')

def cohort_flags(records):
    flags=[[] for _ in records]
    for i,a in enumerate(records):
        for j in range(i):
            b=records[j]
            if a.get('id')==b.get('id'):
                flags[i].append('duplicate_prospective_id');flags[j].append('duplicate_prospective_id')
            if normalize(a.get('expected_lean_statement',''),True)==normalize(b.get('expected_lean_statement',''),True):
                flags[i].append('prospective_alpha_duplicate');flags[j].append('prospective_alpha_duplicate')
    return flags


def partition(records,seed='2037000',development_target=40,test_target=240):
    """Whole-family allocation fixed before outcomes; reserve excess/oversize families."""
    ids=[r['id'] for r in records];ensure(len(ids)==len(set(ids)),'Duplicate candidate IDs')
    groups=defaultdict(list)
    for row in records:ensure(bool(row.get('family')),'Missing family');groups[row['family']].append(row)
    output={'development':[],'test':[],'reserve':[]}
    for family in sorted(groups,key=lambda f:content_hash([seed,f])):
        group=sorted(groups[family],key=lambda r:r['id'])
        if len(output['development'])<development_target:dest='development'
        elif len(output['test'])+len(group)<=test_target:dest='test'
        else:dest='reserve'
        output[dest].extend(group)
    return output

def manifest_entry(path,records):
    from common import sha
    return dict(path=path.name,sha256=sha(path),count=len(records),families=sorted({r['family'] for r in records}),subject_hashes={r['id']:subject_hash(r) for r in records},statement_fingerprints={r['id']:content_hash(normalize(r['expected_lean_statement'],True)) for r in records})

def intake(candidates,output):
    output.mkdir(parents=True,exist_ok=False)
    screening=[screen(r) for r in candidates]
    for result,flags in zip(screening,cohort_flags(candidates)):
        result['automated_flags']=sorted(set(result['automated_flags']+flags));result['quarantine']=bool(result['automated_flags'])
    allowed=[r for r,s in zip(candidates,screening) if not s['quarantine']]
    # Passing a lexical screen is NOT human approval or eligibility.
    split=partition(allowed)
    manifest={'status':'UNAPPROVED_CANDIDATE_PARTITION','independent_status':'PENDING_INDEPENDENT_HUMAN_ADJUDICATION'}
    for phase,rows in split.items():
        path=output/(phase+'.json');dump(path,rows,exclusive=True);manifest[phase]=manifest_entry(path,rows)
    dump(output/'screening.json',screening,exclusive=True)
    dump(output/'dataset_manifest.json',manifest,exclusive=True)
    csv_write(output/'exclusion_registry.csv',[dict(id=s['id'],subject_sha256=s['subject_sha256'],reason='; '.join(s['automated_flags']),decision='QUARANTINED_AUTOMATED_PENDING_HUMAN_REVIEW') for s in screening if s['quarantine']],['id','subject_sha256','reason','decision'])
    return manifest

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('candidates');parser.add_argument('output');a=parser.parse_args()
    from pathlib import Path
    print(intake(read(a.candidates),Path(a.output)))
