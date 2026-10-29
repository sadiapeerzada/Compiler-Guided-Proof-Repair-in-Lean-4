"""Prepare a privacy-minimized review copy, never alter original study evidence."""
import collections
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[2]
LOCAL = ROOT/'publication_review/local'
DEST = Path('/private/tmp/nl2lean-publication-ready-20261029')
COMMIT = '3b4909a20ed24cafd36cbe029a81f8946bc96d69'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def clean(text):
    text = re.sub(r'(?:/Users/|/home/)[^/\s"\x27<>]+', '/REDACTED_HOME', text)
    text = re.sub(r'/private/var/folders/[^\s"\x27<>\\]+', '/REDACTED_TEMP', text)
    text = re.sub(r'(?<![A-Za-z])(?:/private)?/tmp/', '/REDACTED_TEMP/', text)
    text = re.sub(r'[A-Za-z0-9.!#$%&\x27*+/=?^_`{|}~-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+', '[CONTACT REMOVED]', text)
    text = re.sub(r'(?i)Sadia Peerzada|sadiapeerzada(?:2006)?', '[AUTHOR REMOVED]', text)
    return text


def recursive(value):
    if isinstance(value, str):
        return clean(value)
    if isinstance(value, dict):
        return {clean(k):recursive(v) for k,v in value.items()}
    if isinstance(value, list):
        return [recursive(v) for v in value]
    return value


def read(rel):
    return json.loads((ROOT/rel).read_text())


def main():
    scan=read('publication_review/local/tracked_file_scan.json')
    # Fresh prepared tree only; build outputs are added later and independently sealed.
    if (DEST/'PUBLIC_RELEASE_MANIFEST.json').exists():
        raise ValueError('Refusing to replace an already sealed release')
    decisions={r['path']:{'path':r['path'],'original_sha256':r['sha256'],
               'disposition':'EXCLUDE','reason':'Historical/unnecessary artifact; excluded from this scoped release. Original remains local.',
               'review_flags':[h['category'] for h in r['findings']], 'release_paths':[]} for r in scan['files']}
    exported=[]

    def write(rel,data,source=None,reason='Derived public review artifact'):
        if isinstance(data,str):data=data.encode()
        path=DEST/rel;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
        item={'path':rel,'sha256':sha(data),'bytes':len(data),'reason':reason}
        if source:
            original=(ROOT/source).read_bytes();item['original_path']=source;item['original_sha256']=sha(original)
            item['byte_identical']=data==original
            d=decisions[source];d['disposition']='INCLUDE_UNCHANGED' if item['byte_identical'] else 'REDACT_OR_DERIVE'
            d['reason']=reason;d['release_paths'].append(rel)
        exported.append(item)

    def dump(rel,value,source=None,reason='Derived public review artifact'):
        write(rel,json.dumps(value,ensure_ascii=False,indent=2)+'\n',source,reason)

    # Reviewed implementation remains readable, separated from transformed evidence.
    prefixes=('src/','tests/','eval/','prompts/','configs/')
    for path in decisions:
        if path.startswith(prefixes) and Path(path).suffix in {'.py','.txt','.json'}:
            original=(ROOT/path).read_text()
            write('source_snapshot/'+path,clean(original),path,'Reviewed scientific source; transformed artifacts are not substituted for frozen execution inputs.')
    for path in ['scripts/run_final_study.py','scripts/verify_final_study_artifacts.py','scripts/resume_final_study.py',
                 'requirements.txt','requirements-local.txt','lean_project/lean-toolchain','lean_project/lakefile.toml','lean_project/lake-manifest.json']:
        write('source_snapshot/'+path,clean((ROOT/path).read_text()),path,'Scientific source/environment snapshot; original local inputs are required for exact frozen execution.')
    for path in ['data/final_study/v1/freeze.json','data/local_model/20261027/model_inventory.json',
                 'data/final_study/v1/ai_eligibility_policy.json']:
        write('provenance/'+Path(path).name,(ROOT/path).read_bytes(),path,'Nonpersonal immutable provenance commitment; original dependency bytes remain local where excluded.')

    dataset=[]
    for split in ['development','test']:
        path=f'data/final_study/v1/{split}.json';rows=read(path)
        dump(f'dataset/{split}.redacted.json',recursive(rows),path,'AI-eligible source-attributed dataset view only; historical human fields retained, not approvals.')
        for r in rows:
            dataset.append({'id':r['id'],'split':split,'category':r['category'],'difficulty':r['difficulty'],
                            'source_url':r['curation']['source_url'],'source_citation':r['curation']['source_citation'],
                            'source_license':r['curation']['source_license'],
                            'required_attribution':r['curation'].get('source_metadata',{}).get('required_attribution'),
                            'changes_made':r['curation'].get('source_metadata',{}).get('changes_made'),
                            'source_record_sha256':sha(json.dumps(r,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode())})
    dump('dataset/ATTRIBUTION.json',recursive(dataset))
    path='data/final_study/v1/adjudications.json'
    eligible={d['id'] for d in dataset}
    dump('dataset/ai_adjudications.redacted.json',recursive([r for r in read(path) if r['candidate_id'] in eligible]),path,
         'Only eligible-item AI adjudications; no fabricated independent human review or excluded source-insufficient statement.')
    # Only final-protocol, source-eligible held-out and pilot evidence. No historical prototypes.
    prefix='data/final_study/v1/final_runs/'
    for path in decisions:
        if not path.startswith((prefix+'heldout/',prefix+'development_pilot/')):
            continue
        rel=path[len(prefix):];suffix=Path(path).suffix
        if suffix=='.json':
            dump('evidence/redacted_runs/'+rel,recursive(read(path)),path,'Redacted evidence VIEW. Original embedded hashes/seeds refer to private original bytes, not this view.')
        elif suffix=='.jsonl':
            frames=[json.loads(line) for line in (ROOT/path).read_text().splitlines()]
            dump('evidence/redacted_runs/'+rel+'.json',recursive(frames),path,'Token journal represented as a JSON array; only private strings redacted. Original journal preserved locally.')
        elif suffix=='.lean':
            dump('evidence/redacted_runs/'+rel+'.json',{'candidate_view':clean((ROOT/path).read_text()),'original_sha256':decisions[path]['original_sha256']},path,
                 'Candidate text encoded in JSON to preserve whitespace without treating original evidence as maintained source code.')

    cases=[]
    for r in read('data/final_study/v1/test.json'):
        m=read(prefix+f"heldout/2027/{r['id']}/manifest.json")
        cases.append({'problem_id':r['id'],'category':r['category'],'family':r['study_eligibility']['family'],
                      'outcomes':{c:m['conditions'][c]['success'] for c in ['A','B','C']},
                      'initial_candidate_sha256':m['initial']['candidate_sha256'],
                      'manifest_original_sha256':decisions[prefix+f"heldout/2027/{r['id']}/manifest.json"]['original_sha256']})
    dump('results/cases.json',cases)
    result_path='data/final_study/v1/analysis/results.json';results=read(result_path)
    results.pop('approval_provenance',None)
    results['approval_evidence_summary']='Student-reported methodological substitutions; not independently verified. Private conversational wording excluded.'
    dump('results/results.redacted.json',recursive(results),result_path,'Aggregate analysis; private conversation provenance removed. Numerical outcomes are unchanged.')
    dump('results/integrity_review.json',recursive(read('publication_review/local/integrity_review.json')))

    for path in decisions:
        if path.startswith('paper/generated/final_') and Path(path).suffix in {'.tex','.png','.pdf'}:
            data=(ROOT/path).read_bytes()
            if path.endswith('.tex'):data=clean(data.decode()).encode()
            write(path,data,path,'Validated result table/figure or explicitly post-hoc qualitative excerpt; upstream attribution retained in dataset notices.')
    for name in ['references.bib']:
        path='paper/'+name;write(path,clean((ROOT/path).read_text()),path,'Scholarly citations retained; no private contact metadata.')
    paper=(ROOT/'paper/main.tex').read_text()
    paper=re.sub(r'\\author\{[^\n]*\}',r'\\author{Anonymous author}',paper)
    paper=re.sub(r'\\authorrunning\{[^\n]*\}',r'\\authorrunning{Anonymous author}',paper)
    paper=re.sub(r'\\institute\{[^\n]*\}',r'\\institute{Author details withheld for publication-safety review}',paper)
    paper=paper.replace('the observed verified\nsuccess counts are','the full-denominator, missing-as-failure sensitivity\nsuccess counts are')
    paper=paper.replace('the 95\\% family-cluster bootstrap interval is [+0.0, +0.0] points.',
        'the conditional 95\\% family-cluster bootstrap interval is [+0.0, +0.0] points. Two C outcomes are unavailable; among the 58 complete pairs, B and C each succeed once. This interval excludes missingness uncertainty.')
    marker=r'\input{generated/final_missingness.tex}'
    paper=paper.replace(marker,r'''The observed C denominator is 58 (one success, 57 known failures), whereas
the full-cohort sensitivity denominator is 60. On the 58 complete pairs, B and C
each succeed once (1.72\%). Both cases missing C outcomes failed in B.
If both unavailable C outcomes would succeed, the full-cohort C--B difference
would be +3.33 percentage points; if neither succeeds it is zero. These are
missingness identification bounds, not confidence limits. The degenerate
bootstrap interval is conditional on missing-as-failure coding and does not
capture uncertainty in those two unavailable outcomes.
The trigonometric case's C1 input is 9,653 tokens before the 2,000-token output
reservation, exceeding the frozen 8,192-token context cap. The Bernoulli C1
input is 2,205 tokens, but only its token-stream header survives. Neither has
a durable completion that can be verified without a forbidden replay.
\input{generated/final_missingness.tex}''')
    paper=paper.replace('authors. The supplied author name and correspondence are used without inventing\nan institutional affiliation.',
        'authors. Author identity and correspondence are withheld in this publication-safety review copy.')
    paper=paper.replace('complete test outputs, source/evidence hashes and PDF build manifest are included.\nOriginal Groq and exploratory local protocols remain available for provenance.',
        'source/evidence hashes and a release build manifest accompany the review bundle. Original complete test logs and historical exploratory evidence remain local.')
    paper=paper.replace('Unicode bytes, prompts and diagnostics remain in the run artifacts.',
        'Unicode bytes, prompts and diagnostics remain in the private original run artifacts. Public copies are labeled redacted views.')
    paper=paper.replace(r'\section{Conclusion}',r'''Public evidence is a privacy-redacted view. Paths inside compiler diagnostics,
prompts and metadata are replaced in exported copies; recorded original hashes,
token counts and seeds still describe the original private bytes. The original
frozen validators must not be applied to redacted views as though their bytes
were identical. Aggregate reanalysis is public; exact prompt replay and complete
source-evidence validation require the preserved originals. This is a disclosed
public reproducibility limit, not a replacement or revision of the experiment.

\section{Conclusion}''')
    paper=paper.replace('the reproducible paired evidence','the hash-committed paired evidence')
    # Directly relevant genuine work was already in the original bibliography, but uncited.
    paper=paper.replace(r'\section{System Architecture and Verification}',r'''Compiler-conditioned repair training is studied by APRIL~\cite{wang2026april};
our study instead compares bounded inference retries with one unfine-tuned local
model. Work on faithfulness beyond compilation~\cite{zhang2026beyond} also
motivates distinguishing fixed-type proof success from semantic fidelity.

\section{System Architecture and Verification}''')
    write('paper/main.tex',clean(paper),'paper/main.tex','Separate anonymized review revision; missingness caveat and public reproducibility scope clarified. Original 12-page manuscript remains unchanged locally.')

    for path in ['data/curation_batches/v0.2.0/source_archive/LEAN_LICENSE','data/curation_batches/v0.2.0/source_archive/MATHLIB_LICENSE','data/local_model/20261027/upstream_LICENSE']:
        write('third_party/'+Path(path).name,(ROOT/path).read_bytes(),path,'Upstream license text preserved; no model weights or full third-party source archive is shipped.')
    # Complete headers retain the authors of mathematical source adaptations without whole source archives.
    notices=[]
    for path in decisions:
        if '/source_archive/' in path and path.endswith('.lean'):
            text=(ROOT/path).read_text();header=text.split('-/',1)[0]+'-/' if text.startswith('/-') else ''
            notices.append({'original_path':path,'copyright_header':header,'original_sha256':decisions[path]['original_sha256']})
    dump('third_party/UPSTREAM_NOTICES.json',notices)
    write('third_party/RIGHTS_AND_ATTRIBUTION.md', '''# Rights and attribution

This bundle does not impose a blanket new license. No project-wide license was
present in the reviewed repository; public sharing approval is not a new grant
of unrestricted reuse rights for original project code or manuscript material.
Third-party rights remain applicable. Model outputs have no guaranteed legal
clearance merely because they were generated by a model.

Sixteen eligible statements adapt Oscar Levin's Discrete Mathematics: An Open
Introduction, third edition, fifth printing. Those statement adaptations and
corresponding copied/adapted statement material in evidence retain CC BY-SA 4.0,
with item-level source, credit and change notices in dataset/ATTRIBUTION.json.
License: https://creativecommons.org/licenses/by-sa/4.0/ . Share-alike applies to
adaptations; this notice does not assert that unrelated project code is CC BY-SA.

Fifty-nine eligible statements derive from Lean/Mathlib source. Preserve their
Apache-2.0 license texts, original copyright headers and item-level attribution.
UPSTREAM_NOTICES.json preserves headers without redistributing entire archives.
License: https://www.apache.org/licenses/LICENSE-2.0 . Modified public views are
explicitly identified in PUBLIC_RELEASE_MANIFEST.json.

The primary model's archived license is Apache-2.0. No weights, tokenizer files,
TeX binaries, Springer class/style files or publisher/provider HTML/PDF snapshots
are included. Source URLs and exact byte hashes identify privately preserved
evidence; redistribution of additional material requires a separate assessment.
Scholarly citation and copyright-holder names are retained as public attribution,
not confused with the private study author's contact details.
''')
    dump('PUBLIC_RELEASE_MANIFEST.json',{'schema_version':1,'source_commit':COMMIT,'approval_status':'AWAITING_USER_APPROVAL_NO_PUSH',
         'scope':'Privacy-redacted final eligible study evidence, scientific source snapshot, aggregate reanalysis and anonymized manuscript. Not exact original-byte replay.',
         'tracked_source_file_count':len(decisions),'source_file_decisions':list(decisions.values()),'prepared_exports':exported,
         'original_evidence_preserved':True,'original_history_must_not_be_pushed':True,
         'redaction_policy':['Local home/temp prefixes and private author/contact identifiers replaced only in derivative views.',
                             'Original hashes/seeds/token counts are not recomputed or relabeled as applying to the redacted prompts.',
                             'Original outputs, failed attempts and unavailable outcomes remain intact locally.'],
         'excluded_categories':['Original author metadata and Git ancestry','Private approval/conversation records','Historical prototypes and source-insufficient candidates',
                                'Full source archives/provider or publisher snapshots','Original unredacted logs/outputs','Original identifiable manuscript PDFs']})
    print(json.dumps({'prepared_files':len(exported)+1,'source_dispositions':dict(collections.Counter(x['disposition'] for x in decisions.values()))},indent=2))


if __name__=='__main__':
    main()
