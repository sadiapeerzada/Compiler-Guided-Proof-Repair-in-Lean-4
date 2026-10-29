"""Prepare revised public files locally; never publish or change original evidence."""
import collections
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil

ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'data/final_review/20261029_v2'
DEST=Path('/private/tmp/nl2lean-publication-final-v2-20261029')
spec=importlib.util.spec_from_file_location('review_cleaner',ROOT/'publication_review/tools/prepare_release.py')
cleaner=importlib.util.module_from_spec(spec);spec.loader.exec_module(cleaner)


def digest(data):return hashlib.sha256(data).hexdigest()
def read(path):return json.loads(path.read_text())


def main():
    history=DEST/'provenance/history';history.mkdir(parents=True,exist_ok=True)
    sources=[]
    def preserve(source,destination):
        target=DEST/destination
        if not target.exists():target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(DEST/source,target)
    for source,destination in [('PUBLIC_RELEASE_MANIFEST.json','provenance/history/PUBLIC_RELEASE_MANIFEST_v1.json'),
                               ('PUBLIC_PAYLOAD_MANIFEST.json','provenance/history/PUBLIC_PAYLOAD_MANIFEST_v1.json'),
                               ('paper/main.tex','paper/history/main_v1.tex'),('paper/build_manifest.json','paper/history/build_manifest_v1.json'),
                               ('paper/references.bib','paper/history/references_v1.bib')]:preserve(source,destination)
    def export(source,relative,kind='SAFE TO PUBLISH'):
        path=ROOT/source;data=path.read_bytes();suffix=path.suffix
        if suffix=='.json':
            value=read(path)
            if relative=='paper/build_manifest.json':
                value={k:v for k,v in value.items() if k not in ['log']};value['pdf']='paper/final_manuscript.pdf'
            content=(json.dumps(cleaner.recursive(value),ensure_ascii=False,indent=2)+'\n').encode()
        elif suffix in {'.pdf','.png'}:content=data
        else:
            text=cleaner.clean(data.decode())
            text=text.replace('[professor checklist](NL2Lean_TAIMMA2027_Student_Revision_Report(10).md)','professor checklist supplied by the student (retained locally)')
            content=text.encode()
        target=DEST/relative;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(content)
        sources.append({'source_path':source,'release_path':relative,'source_sha256':digest(data),'release_sha256':digest(content),
                        'classification':kind if content==data else 'REQUIRES REDACTION','released_view_classification':'SAFE TO PUBLISH',
                        'transformed':content!=data,'reason':'Private strings removed / JSON serialized only in derivative views; original scientific evidence unchanged.' if content!=data else 'Reviewed scientific result/source or anonymized manuscript.'})
    docs=['FINAL_M1_M7_COMPLIANCE_REPORT.md','FINAL_EXPERIMENT_RESULTS.md','FINAL_PAPER_READINESS.md','REPRODUCIBILITY_CHECKLIST.md',
          'PAIRED_COMPARISON_AUDIT.md','MISSING_C_OUTCOME_INVESTIGATION.md','FINAL_SUBMISSION_GATE.md','COMPILER_ERROR_TAXONOMY.md']
    for name in docs:export('docs/'+name,'docs/'+name)
    export('paper/main.tex','paper/main.tex');export('paper/references.bib','paper/references.bib')
    export('paper/compiled_final_review_v2.pdf','paper/final_manuscript.pdf')
    for path in sorted((ROOT/'paper/generated/review_v2').iterdir()):
        if path.is_file():export(str(path.relative_to(ROOT)),str(path.relative_to(ROOT)))
    for name in ['analysis_verified/results.json','analysis_verified/case_outcomes.json','paired_resources.json','diagnostic_subtypes.json',
                 'qualitative_cases.json','missingness_recovery.json','environment_verification.json','reproducibility_verification.json',
                 'reference_axiom_validation.json','render_manifest.json','manuscript_claims.json','paper_build_manifest.json',
                 'citation_verification.json','compliance_matrix.json','call_environment_consistency.json','pdf_layout_checks.json']:
        export('data/final_review/20261029_v2/'+name,'results/review_v2/'+name)
    export('data/final_review/20261029_v2/paper_build_manifest.json','paper/build_manifest.json')
    for path in ['eval/final_review_analysis.py','tests/test_final_review_analysis.py','scripts/render_final_review.py',
                 'scripts/investigate_missing_final.py','scripts/verify_final_review.py','scripts/write_final_review_reports.py',
                 'paper/scripts/write_final_review.py','paper/scripts/build_final_review.py']:
        export(path,'source_snapshot/'+path)
    testlog=(BASE/'local/pytest_final.log').read_text()
    assert '297 passed, 28 subtests passed' in testlog
    qa={'review_revision':2,'python_tests':{'exit_code':0,'passed':297,'subtests_passed':28},'lean_build':{'exit_code':0,'jobs':8658},
        'reference_batch_exit_code':0,'reference_candidates':96,'model_successes_freshly_reverified':2,'new_inference_calls':0,
        'metric_regeneration_byte_identical':True,'original_final_study_artifacts_unchanged':2394,
        'scope':'Actual original-checkout verification; raw command logs remain private. Public aggregate and redacted pairing verifiers run separately.',
        'source_log_hashes':{str(p.relative_to(ROOT)):digest(p.read_bytes()) for p in [BASE/'local/pytest_final.log',BASE/'local/lean_build_final.log',BASE/'local/references_final.log']}}
    (DEST/'QA_SUMMARY.json').write_text(json.dumps(qa,indent=2)+'\n')
    oldreadme=(DEST/'README.md').read_text()
    heading='''# Final review revision: fixed-theorem empirical pilot

**Local revision awaiting fresh publication approval. No push or merge of this revision.**

The canonical revised manuscript is [paper/final_manuscript.pdf](paper/final_manuscript.pdf)
(14 pages). Observed rates are A=0/60, B=1/60, C=1/58 with two unavailable C
outcomes. On 58 complete pairs B=C=1/58 (1.72%); the paired difference is zero
without informative discordance. C=1/60 remains only the planned missing-as-failure
sensitivity. Missingness bounds for the full-cohort C−B effect are 0 to +3.33 points.

Run `python3 reanalyze_review_v2.py` for the revised observed/paired/sensitivity
analysis, and `python3 verify_payload.py` for exact payload and baseline redacted
evidence checks. Latest results: `results/review_v2/`; final evidence-backed gate:
[docs/FINAL_SUBMISSION_GATE.md](docs/FINAL_SUBMISSION_GATE.md).

M1/M2/M3 remain PARTIAL under the exact student-supplied requirements; M4/M5/M6/M7
are COMPLETE in their documented scopes. M6 local original-byte reproducibility
and M7 empirical manuscript rewrite do not imply submission authorization.
Recommendation is NO-GO for a full-compliance submission; the reduced pilot is
ready for supervisor/editorial review. The exact professor correspondence and
original raw logs remain local. Public replay limitations are unchanged.

The original 12-page public review PDF and original analysis remain historical
artifacts. Source/metric changes in this revision do not overwrite old experimental
records or add model attempts. All newly proposed files require fresh approval.

---

## Historical release-v1 description

'''
    if not oldreadme.startswith('# Final review revision:'): (DEST/'README.md').write_text(heading+oldreadme)
    oldreport=DEST/'RESEARCH_INTEGRITY_REVIEW.md';text=oldreport.read_text()
    if not text.startswith('> Historical release-v1'):oldreport.write_text('> Historical release-v1 review. The current revision and submission gate are in `docs/` and `results/review_v2/`.\n\n'+text)
    (DEST/'docs/PUBLIC_RELEASE_MANIFEST.md').write_text('''# Exact revised publication proposal

The machine-readable `PUBLIC_RELEASE_MANIFEST.json` classifies source material as
SAFE TO PUBLISH, REQUIRES REDACTION, PRIVATE / LOCAL ONLY, or LICENSING REVIEW
REQUIRED. `PUBLIC_PAYLOAD_MANIFEST.json` enumerates every final proposed file and
SHA-256 (excluding itself). These files, not the private research checkout, define
the requested public release. Approval is pending; no revised push/merge occurred.

Original final-study evidence is unchanged locally. Redacted final-run views and
all original candidate hashes remain included; exact original C prompt replay
requires private originals. New results, paper, taxonomy, compliance/gate reports
and source snapshots are reviewed derivative additions. The professor's supplied
correspondence, author contact details, raw verification logs, full source archives,
model weights and private research/audit Git history are excluded. Applicable
item-level CC BY-SA / Apache-2.0 terms and copyright notices remain attached.

The old release inventories are preserved under `provenance/history/`. A Git push
of this branch would include only already-public release-v1 ancestry and this
reviewed revision; private local study commits are not ancestors.
''')
    exclusions=[{'source_path':'docs/NL2Lean_TAIMMA2027_Student_Revision_Report(10).md','classification':'PRIVATE / LOCAL ONLY','reason':'Student-supplied supervisory review/correspondence; public matrix is a derived technical summary, not publication of the correspondence.'},
                {'source_path':'data/final_review/20261029_v2/local/','classification':'PRIVATE / LOCAL ONLY','reason':'Raw command output, absolute paths, forensic inventories and originals remain local; public summaries and hashes are provided.'},
                {'source_path':'data/final_study/v1/','classification':'REQUIRES REDACTION','reason':'Original exact prompts/logs/manifests retained privately; only labeled redacted final-run views are included.'},
                {'source_path':'data/source_archives/','classification':'LICENSING REVIEW REQUIRED','reason':'Full provider/publisher archives are unnecessary to redistribute; licenses/source URLs/hashes/attribution retained instead.'},
                {'source_path':'local model weights, tokenizer and TeX binaries/templates','classification':'LICENSING REVIEW REQUIRED','reason':'Not redistributed; restore pinned public upstream artifacts subject to their terms.'},
                {'source_path':'original author metadata and private Git ancestry','classification':'PRIVATE / LOCAL ONLY','reason':'No personal author/contact metadata or private research/audit commits in release history.'}]
    inventory={'schema_version':2,'approval_status':'AWAITING_EXACT_REVISED_PAYLOAD_APPROVAL_NO_PUSH',
               'source_study_commit':'3b4909a20ed24cafd36cbe029a81f8946bc96d69','public_parent_commit':'b5c7a638db02b8f7c39a09be626cae583d5e89ac',
               'allowed_classifications':['SAFE TO PUBLISH','REQUIRES REDACTION','PRIVATE / LOCAL ONLY','LICENSING REVIEW REQUIRED'],
               'new_or_revised_source_files':sources,'excluded_source_classes':exclusions,
               'unchanged_previously_approved_files':'Retained from public_parent_commit; enumerated and rescanned in the exact payload inventory.',
               'old_source_file_decisions':'provenance/history/PUBLIC_RELEASE_MANIFEST_v1.json',
               'all_original_final_study_artifacts_unchanged':True,
               'reproducibility':'Public redacted evidence/reanalysis plus privately preserved original-byte proof/prompt/metric validation. Do not relabel changed public prompt bytes with original hashes.'}
    (DEST/'PUBLIC_RELEASE_MANIFEST.json').write_text(json.dumps(inventory,indent=2)+'\n')
    print('Prepared revised local publication proposal; original evidence and prior public history retained.')


if __name__=='__main__':main()
