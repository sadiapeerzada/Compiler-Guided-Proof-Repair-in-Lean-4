"""Versioned AI-assisted eligibility and freeze gates; legacy human gates remain intact."""
from pathlib import Path
import hashlib
import json
import re
import importlib.metadata

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'data/final_study/v1'

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def canonical(value):return hashlib.sha256(json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()
def read(path):return json.loads(Path(path).read_text())
def binding(r):return canonical({k:r.get(k) for k in ('id','nl_statement','expected_lean_statement','required_imports','required_definitions')})

def validate_freeze(base=BASE):
    m=read(base/'freeze.json');policy=read(base/'ai_eligibility_policy.json');approval=read(base/'approvals/student_reported.json')
    if m['policy_sha256']!=sha(base/'ai_eligibility_policy.json') or m['approval_record_sha256']!=sha(base/'approvals/student_reported.json'):
        raise ValueError('Policy/approval provenance changed')
    if approval['evidence_status']!='direct_user_report_in_current_conversation_not_independently_verified' or approval['approved_substitutions_reported']!={
        'ai_assisted_semantic_review_replaces_independent_human_semantic_review':True,'free_local_mlx_replaces_groq_api':True}:
        raise ValueError('Reported methodological approval is absent or overstated')
    allrows={};families={};counts={}
    for split in ('development','test'):
        p=base/(split+'.json');rows=read(p)
        if sha(p)!=m['splits'][split]['sha256'] or [r['id'] for r in rows]!=m['splits'][split]['ordered_ids']:
            raise ValueError('Frozen dataset bytes/order changed')
        counts[split]=len(rows)
        for r in rows:
            if r['id'] in allrows:raise ValueError('Duplicate problem')
            allrows[r['id']]=r;e=r['study_eligibility']
            if e['policy_version']!=policy['version'] or e['subject_sha256']!=binding(r) or e['split']!=split:
                raise ValueError('Stale AI eligibility binding')
            if e['semantic_label']!='faithful' or e['remaining_semantic_uncertainties'] or e['reviewer_kind']!='ai_adjudication_not_human':
                raise ValueError('Unresolved/unfaithful item cannot be eligible')
            if e.get('human_review_completed') is not False:raise ValueError('AI review misrepresented as human')
            for source in e['source_evidence']:
                path=(ROOT/source['path']).resolve()
                if not path.is_relative_to(ROOT) or sha(path)!=source['sha256']:raise ValueError('Source evidence changed')
            if not e['source_evidence'] or not r['curation'].get('source_url') or not r['curation'].get('source_citation'):
                raise ValueError('Source provenance absent')
            proof=read(ROOT/e['proof_evidence_path'])
            if sha(ROOT/e['proof_evidence_path'])!=e['proof_evidence_sha256'] or proof['exit_code']!=0:
                raise ValueError('Strict reference proof evidence changed')
            comparison=next((x for x in proof['comparisons'] if x['candidate_id']==r['id']),None)
            if not comparison or not comparison['strict_verified'] or set(comparison['axioms'])-{'propext','Classical.choice','Quot.sound'}:
                raise ValueError('Missing or unsafe exact target reference proof')
            if proof['source_sha256']!=sha(ROOT/'data/ai_semantic_audit/20261028/lean_reference_check/all_references.lean'):
                raise ValueError('Reference verification source changed')
            if e['family'] in families and families[e['family']]!=split:raise ValueError('Theorem-family leakage')
            families[e['family']]=split
    if not 15<=counts['development']<=20 or counts['test']<60:raise ValueError('Required eligible counts not reached')
    if len({r['category'] for r in allrows.values()})<5:raise ValueError('Fewer than five categories')
    if sha(base/'adjudications.json')!=m['adjudications_sha256']:raise ValueError('Adjudications changed')
    decisions={d['candidate_id']:d for d in read(base/'adjudications.json')}
    for ident,r in allrows.items():
        if decisions[ident]['subject_sha256']!=binding(r) or decisions[ident]['final_label']!='faithful':raise ValueError('Invalid adjudication')
    return {'valid':True,'eligible_counts':counts,'independent_human_reviews':0,'approval_evidence_status':approval['evidence_status'],'families':len(families)}

def validate_protocol(path):
    p=read(path)
    if p['schema_version']!=4 or p['paid_inference_allowed'] is not False or p['seeds']!=[2027]:raise ValueError('Unsupported controlled protocol')
    if p['maximum_repairs']!=3 or p['decoding']!={'temperature':0.2,'max_tokens':2000,'max_context_tokens':8192,'top_p':1.0}:
        raise ValueError('Generation budgets changed')
    if sha(BASE/'freeze.json')!=p['freeze_sha256']:raise ValueError('Dataset freeze changed')
    for package,version in p['runtime_packages'].items():
        if importlib.metadata.version(package)!=version:raise ValueError('Pinned runtime package changed: '+package)
    for name,expected in p['pinned_files'].items():
        if sha(ROOT/name)!=expected:raise ValueError('Frozen protocol implementation/input changed: '+name)
    validate_freeze()
    return p
