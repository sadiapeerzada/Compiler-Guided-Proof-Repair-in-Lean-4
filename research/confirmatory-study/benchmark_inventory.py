"""Inventory historical evidence and prepare unapproved reviewer packets.

These exposed records are contamination-screening evidence, NOT a new test set.
"""
import importlib.util
import itertools
import json
import re
import subprocess
from collections import defaultdict
from pathlib import Path
from common import ROOT,HERE,STATUS,sha,content_hash,read,dump,csv_write,source_rows,normalize,clean


def reference_view(record):
    proof=record.get('reference_lean_proof','');path=record.get('lean_file','')
    if proof:return proof,'record field'
    if path and (ROOT/path).is_file():return clean((ROOT/path).read_text()),path
    return '', 'unavailable standalone proof; inspect recorded verification/source batch'


def records():
    paths=subprocess.check_output(['git','ls-files','--','data/','publication/dataset/'],cwd=ROOT,text=True).splitlines()
    selected=[p for p in paths if p.endswith('.json') and (p.startswith('publication/dataset/') or any(k in p for k in ('candidate_records','specifications','research_dataset_draft','seed_problems')))]
    found=[]
    for path in selected:
        value=read(ROOT/path)
        for r in source_rows(value):found.append((path,r))
        # Frozen compact curation specifications: id/category/family/NL/binders/proof script/library dependency.
        if '/curation_batches/' in path and '/specifications' in path and isinstance(value,list):
            for r in value:
                if not isinstance(r,list) or len(r)<6 or not isinstance(r[0],str):continue
                # This is a recorded specification, not a reconstructed historical outcome.
                found.append((path,dict(id=r[0],nl_statement=r[3],category=r[1],expected_lean_statement=r[4],curation=dict(problem_family=r[2]),reference_script_specification=r[5],recorded_library_dependency=r[6] if len(r)>6 else '')))
    spec=importlib.util.spec_from_file_location('frozen_runner',ROOT/'study2_supervisor_suite_v7.py')
    runner=importlib.util.module_from_spec(spec);spec.loader.exec_module(runner)
    for split in ('development','test'):
        for r in runner.bridge_rows(split):r['curation']['split']=split;found.append(('study2_supervisor_suite_v7.py::bridge_rows/'+split,r))
    return found,selected


def main():
    found,files=records();grouped={}
    original_exposure={r['id']:'Study1 test (executed)' for r in read(ROOT/'publication/dataset/test.redacted.json')}
    original_exposure.update({r['id']:'Study1 development pool (pilot execution only where separately recorded)' for r in read(ROOT/'publication/dataset/development.redacted.json')})
    for source,r in found:
        key=content_hash({'id':r['id'],'statement':r['expected_lean_statement'],'nl':r.get('nl_statement','')})
        if key not in grouped:grouped[key]=dict(record=r,sources=[])
        grouped[key]['sources'].append(source)
        # Prefer published metadata over an older duplicate with fewer fields.
        if source.startswith('publication/dataset/'):grouped[key]['record']=r
    inventory=[];semantic=[]
    for key,item in sorted(grouped.items()):
        r=item['record'];cur=r.get('curation',{});elig=r.get('study_eligibility',{})
        theorem=r['expected_lean_statement'];nl=r.get('nl_statement','');proof,proof_source=reference_view(r)
        placeholder='Synthetic controlled mathematical' in nl or 'placeholder' in nl.lower()
        flags=[]
        if placeholder:flags.append('PLACEHOLDER_ENGLISH_NO_SEMANTIC_GOLD')
        if not nl:flags.append('MISSING_NATURAL_LANGUAGE')
        if not re.search(r'\btheorem\b',theorem):flags.append('BINDER_BODY_SPECIFICATION_NOT_STANDALONE_THEOREM')
        if any(x in theorem for x in ('ℤ','Int')) and re.search(r'\bnatural numbers?\b',nl,re.I):flags.append('POSSIBLE_DOMAIN_MISMATCH_REQUIRES_REVIEW')
        if any(x in theorem for x in ('ℝ','Real')) and re.search(r'\bintegers?\b',nl,re.I):flags.append('POSSIBLE_DOMAIN_MISMATCH_REQUIRES_REVIEW')
        exposure=original_exposure.get(r['id'],'Historical repository candidate; inference exposure not inferred')
        if r['id'].startswith('bridge_d'):exposure='V7/V5 development; V8 development; V9 development (not independent test)'
        if r['id'].startswith('bridge_t'):exposure='V7 and V8 test; V9 screening; already inspected'
        verification=cur.get('theorem_verification',{})
        if r['id'].startswith('bridge_'):status='Recorded reference screens passed; see archived indexed records, not a new check'
        else:status=json.dumps(verification,sort_keys=True) if verification else 'No per-item strict reference outcome supplied here'
        family=elig.get('family',cur.get('problem_family','UNKNOWN_REQUIRES_REVIEW'))
        split=elig.get('split',cur.get('split','historical/proposed; review required'))
        dependencies=sorted(set(re.findall(r'\b(?:Nat|Int|Real|Finset|BigOperators)\.[A-Za-z_][\w.]*',proof)))
        if r.get('recorded_library_dependency'):dependencies.append(r['recorded_library_dependency'])
        row=dict(inventory_key=key,id=r['id'],natural_language=nl,formal_statement=theorem,statement_sha256=content_hash(theorem),reference_proof=proof,reference_script_specification=r.get('reference_script_specification',''),reference_source=proof_source,reference_verifier_status=clean(status),category=r.get('category','unknown'),difficulty=r.get('difficulty','unassessed'),difficulty_status='Recorded/provisional, not a measured model difficulty',source_provenance='; '.join(sorted(item['sources'])),source_url=cur.get('source_url','unavailable/author-constructed'),license=cur.get('source_license','UNASSESSED'),family=family,split=split,library_dependency_screen='; '.join(dependencies),library_dependency_caveat='Identifier screen only; not complete logical dependencies',existing_exposure=exposure,independent_review=STATUS,automated_semantic_flags='; '.join(flags),record_sha256=content_hash(r))
        inventory.append(row)
        semantic.append(dict(inventory_key=key,id=r['id'],natural_language=nl,formal_statement=theorem,automated_flags=flags,independent_status=STATUS,review_fields={k:None for k in ['quantifiers','domains','assumptions','boundary_conditions','operators','missing_premises','ambiguity','strengthening_or_weakening','semantic_gold_label','reviewer_name','independence_statement','evidence_artifact','signed_date']}))
    csv_write(HERE/'benchmark_inventory.csv',inventory)
    overlaps=[]
    for a,b in itertools.combinations(inventory,2):
        exact=normalize(a['formal_statement'])==normalize(b['formal_statement'])
        alpha=normalize(a['formal_statement'],True)==normalize(b['formal_statement'],True)
        same_family=a['family']==b['family'] and a['family']!='UNKNOWN_REQUIRES_REVIEW'
        same_id=a['id']==b['id']
        if not (exact or alpha or same_family or same_id):continue
        overlaps.append(dict(left_key=a['inventory_key'],right_key=b['inventory_key'],left_id=a['id'],right_id=b['id'],automated_relation='textual' if exact else 'alpha-normalized' if alpha else 'same recorded ID; version difference' if same_id else 'same declared family; not equivalence',cross_split=a['split']!=b['split'],human_status=STATUS,evidence='Deterministic lexical/family screen; not an exclusion decision'))
    # Preserve stronger, already kernel-checked relations without turning them into exclusions.
    for r in list(__import__('csv').DictReader((ROOT/'analysis/taimma_final_professor_validation/BENCHMARK_OVERLAP_EVIDENCE.csv').open())):
        overlaps.append(dict(left_key='see source inventory',right_key='see source inventory',left_id=r['left'],right_id=r['right'],automated_relation=r['relationship_under_examination'],cross_split=r['cross_split'],human_status=STATUS,evidence='analysis/taimma_final_professor_validation/OverlapCertificates.lean; '+r['certificate_status']))
    csv_write(HERE/'overlap_candidates.csv',overlaps)
    exposure={}
    def add_exposure(text,source):
        # Declaration-prefix extraction is lexical; malformed or multiple declarations need human review.
        match=re.search(r'\b(theorem|lemma)\s+',text)
        if match:text=text[match.start():].split(':=',1)[0].strip()
        if not text:return
        key=content_hash(normalize(text,True))
        if key not in exposure:exposure[key]=dict(alpha_fingerprint=key,text_fingerprint=content_hash(normalize(text)),formal_prefix=text,source_examples=[],observations=0)
        entry=exposure[key];entry['observations']+=1
        if len(entry['source_examples'])<3:entry['source_examples'].append(source)
    for row in inventory:add_exposure(row['formal_statement'],row['source_provenance'])
    for path in sorted((ROOT/'publication/evidence/redacted_runs').rglob('manifest.json')):
        record=read(path)
        initial=record.get('initial',{})
        if initial.get('candidate'):add_exposure(initial['candidate'],str(path.relative_to(ROOT)))
        for arm in record.get('conditions',{}).values():
            for step in arm.get('attempts',[]):
                if step.get('candidate'):add_exposure(step['candidate'],str(path.relative_to(ROOT)))
    for view in read(ROOT/'analysis/taimma_supervisor_final/sources/v7_trajectory_views.json'):
        t=view['trajectory']
        for step in [t['initial']]+[s for a in t['arms'].values() for s in a['steps']]:add_exposure(step['candidate'],view['original_path'])
    import zipfile
    with zipfile.ZipFile(ROOT/'research/study2-raw-v8-v9/evidence-part-001.zip') as archive:
        for name in sorted(archive.namelist()):
            if not name.endswith('/completion.json'):continue
            record=json.loads(archive.read(name));response=record.get('raw_response','')
            match=re.search(r'```lean\s*(.*?)```',response,re.S)
            add_exposure(match.group(1).strip() if match else response.strip(),'research/study2-raw-v8-v9/evidence-part-001.zip::'+name)
    dump(HERE/'historical_exposure_index.json',dict(status='HISTORICAL_EXPOSURE_NOT_FRESH_TEST',scope='All inventoried subjects; recorded Study1 and V7 candidates; archived V8/V9 completion prefixes; lexical screen is incomplete for semantic equivalence',items=sorted(exposure.values(),key=lambda x:x['alpha_fingerprint'])))
    dump(HERE/'semantic_review_packet.json',dict(status=STATUS,not_independent_human_review=True,items=semantic))
    csv_write(HERE/'human_adjudication_template.csv',[dict(inventory_key=r['inventory_key'],id=r['id'],statement_sha256=r['statement_sha256'],decision='PENDING',mathematical_correctness='',semantic_fidelity='',family_independence='',split_leakage='',licensing='',reviewer_name='',reviewer_affiliation='',independence_or_conflicts='',signed_date='',signed_evidence_path='',signed_evidence_sha256='',rationale='') for r in inventory])
    sources={p:sha(ROOT/p) for p in files};sources['study2_supervisor_suite_v7.py']=sha(ROOT/'study2_supervisor_suite_v7.py')
    dump(HERE/'benchmark_validation_manifest.json',dict(status=STATUS,independently_approved_items=0,historical_inventory_items=len(inventory),new_eligible_development=0,new_eligible_test=0,source_hashes=sources,output_hashes={n:sha(HERE/n) for n in ['benchmark_inventory.csv','overlap_candidates.csv','semantic_review_packet.json','human_adjudication_template.csv','historical_exposure_index.json']},limitations=['Every inventoried item is historically exposed; none is automatically a new confirmatory example.','Automated lexical/family and domain screens are incomplete.','Reference-script specifications are not fabricated completed proofs.']))
    (HERE/'benchmark_validation_report.md').write_text(f'''# Historical benchmark review infrastructure\n\nStatus: **{STATUS}**. Inventory: {len(inventory)} distinct ID/statement/NL versions from {len(files)} recorded source files plus the frozen 36-item bridge constructor. Duplicate historical file copies are coalesced by exact subject hash; differing statements or NL remain separate versions. All observed source hashes are in benchmark_validation_manifest.json.\n\nAll 75 published Study1 pool items and all 36 bridge items are included, alongside earlier seed/curation candidates. Specifications retain their recorded tactic script separately from a full reference proof; missing standalone proof/source/license fields are explicitly unavailable. Existing metadata and AI labels are observations, not independent decisions. Difficulty and library-dependency screens remain provisional/incomplete.\n\nThe five established bridge relationships link to the existing Lean certificates; lexical/alpha/family screens extend across the historical inventory. Shared families, implications or certificates are not automatic exclusions. The semantic packet explicitly requests quantifier, domain, premise, boundary/operator and strengthening checks. Blank signed-review fields are not approvals.\n\nNew eligible confirmatory count: **0**; new eligible development count: **0**. No independent external reviewer or fresh candidate source has been supplied. The existing items have already been exposed and cannot be recycled as untouched test data. New candidate intake and family-based split tooling must quarantine overlaps against this inventory before human review and freeze. Training contamination cannot be ruled out by repository screening.\n''')
    print('Historical inventory:',len(inventory),'versions; automated overlap candidates:',len(overlaps),'; independent approvals: 0')

if __name__=='__main__':main()
