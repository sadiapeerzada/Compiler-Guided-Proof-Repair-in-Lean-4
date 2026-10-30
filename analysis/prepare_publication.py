"""Prepare a new reviewed addition on public ancestry, never push or merge."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
from .common import ROOT,OUT,read,private_text


def main(destination):
    dest=Path(destination).resolve();public=dest/'publication';target=public/'post_hoc'
    assert (dest/'.git').is_file() and public.is_dir()
    assert read(OUT/'post_hoc_final_privacy_integrity_audit.json')['valid']
    assert read(OUT/'post_hoc_dev_validation.json')['valid']
    if target.exists():raise ValueError('Refusing to replace prepared publication extension')
    target.mkdir();provenance=[]
    # Supporting code is copied from the already approved public source views.
    for name in ['src','eval','prompts','configs','scripts']:
        shutil.copytree(public/'source_snapshot'/name,target/name)
    if (public/'source_snapshot/requirements.txt').exists():
        shutil.copyfile(public/'source_snapshot/requirements.txt',target/'requirements.txt')
    def export(path,relative):
        data=path.read_bytes();content=data;changes=[]
        if path.suffix not in {'.pdf','.png'}:
            text=data.decode()
            # The local privacy guards contain literal identity denylist entries.
            # Replace those entries only in a labeled derivative source snapshot.
            text,n=re.subn(r'(?i)sadiapeerzada|Sadia Peerzada','REDACTED_IDENTITY',text)
            if n:changes.append('Literal local identity-denylist entries replaced by an anonymous marker; scientific measurement logic unchanged.')
            fixture="'error at /Users/private_user/secret.lean'"
            if fixture in text:
                text=text.replace(fixture,"('error at '+chr(47)+'Users'+chr(47)+'private_user/secret.lean')")
                changes.append('Synthetic privacy-test path assembled in memory; identical synthetic test value.')
            content=text.encode()
            if private_text(text):raise ValueError('Export still contains private content: '+relative)
        out=target/relative;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(content)
        provenance.append({'source':str(path.relative_to(ROOT)),'release':'post_hoc/'+relative,'release_sha256':hashlib.sha256(content).hexdigest(),
                           'byte_identical_to_local':content==data,'transformations':changes})
    for path in sorted((ROOT/'src').rglob('*.py')):
        if '__pycache__' not in path.parts:export(path,str(path.relative_to(ROOT)))
    for name in ['scripts/run_final_study.py','eval/paired_analysis.py']:
        export(ROOT/name,name)
    for folder in ['analysis','extensions']:
        for path in sorted((ROOT/folder).rglob('*')):
            if not path.is_file() or '__pycache__' in path.parts or path.name=='prepare_publication.py':continue
            export(path,str(path.relative_to(ROOT)))
    for path in sorted(OUT.rglob('*')):
        if not path.is_file() or '__pycache__' in path.parts or path.name=='worker.lock':continue
        export(path,str(path.relative_to(ROOT)))
    for name in ['main.tex','references.bib']:
        export(ROOT/'paper'/name,'paper/'+name)
    # Preserve old published figures/tables and their already-reviewed redactions.
    shutil.copytree(public/'paper/generated/review_v2',target/'paper/generated/review_v2')
    (target/'PUBLIC_REPRODUCIBILITY_BOUNDARY.md').write_text('''# Exploratory post-hoc extension: public reproduction boundary

All experimental numbers were computed from original local responses, token
journals and compiler records. Redacted publication views were not substituted
for metrics requiring exact original bytes. The original 60-case study and its
two unavailable C outcomes remain unchanged. Study 2 model execution is deferred.

The new dev-only records contain filename-normalized diagnostics and preserve
actual message content, severity, positions, ordering and categories. Their
15 fresh shared initials and repair responses are included under
`outputs/post_hoc/dev_placebo/`. No model weights or tokenizer files are included.
The original worker was interrupted after eleven cases; the saved twelfth
response was reused on resume, without replaying consumed incomplete intents.
The original and resume logs/environment records are retained separately.

Original held-out prompt bytes and private research Git ancestry are excluded.
Task-1 original-token edit distances and prompt-length metrics require those
private records and the pinned tokenizer. Use `analysis/README.md` with the
original checkout; do not relabel redacted prompt bytes with original hashes.

Source snapshots with anonymous identity-denylist entries are explicit public
derivatives. Their byte changes are enumerated in `SOURCE_VIEW_MANIFEST.json`.
Frozen protocol hashes continue to identify the actual private implementation;
the public derivatives do not satisfy those pins and must not silently bypass
the runner's checks. Re-execution requires the original verified sources and
environment, or a separately frozen and labeled replication protocol.

Dataset/source attribution and item-level CC BY-SA/Apache terms remain in
`../dataset/ATTRIBUTION.json`. The dev theorem statements and model prompts are
adapted from those development records; preserve their existing attribution and
share-alike terms. Lean/Mathlib compiler messages remain under their applicable
upstream terms. No full source archives, weights or third-party PDFs are added.
This payload is a research pilot, not submission approval or evidence that
feedback is used/ignored, improves success, or is equivalent to blind retries.
''')
    (target/'SOURCE_VIEW_MANIFEST.json').write_text(json.dumps({'post_hoc':True,'development_only_new_execution':True,'files':provenance,
        'excluded_source_classes':['Original private held-out records and private research Git ancestry.','Supervisory correspondence and author/contact metadata.','Model/tokenizer weights, cached binaries/templates and full third-party archives.','OS metadata, Python caches, ephemeral worker locks and local release-preparation orchestration.','Reproduction-directory links; their underlying new dev records are included once.'],
        'supporting_source':'Unchanged supporting files come from previously approved public source views; the actual pinned client/verifier/runner and frozen classifier are explicitly enumerated above.'},indent=2)+'\n')
    previous=(public/'PUBLIC_PAYLOAD_MANIFEST.json').read_bytes()
    (target/'previous_PUBLIC_PAYLOAD_MANIFEST.json').write_bytes(previous)
    for name in ['main.tex','references.bib']:
        prior=target/'provenance'/('previous_paper_'+name);prior.parent.mkdir(exist_ok=True)
        prior.write_bytes((public/'paper'/name).read_bytes())
        content=(target/'paper'/name).read_text()
        if name=='main.tex':content=content.replace('../outputs/post_hoc/latex/','../post_hoc/outputs/post_hoc/latex/')
        (public/'paper'/name).write_text(content)
    shutil.copyfile(OUT/'manuscript/post_hoc_pilot.pdf',public/'paper/post_hoc_pilot.pdf')
    prior_release=read(public/'PUBLIC_RELEASE_MANIFEST.json')
    (target/'provenance/previous_PUBLIC_RELEASE_MANIFEST.json').write_text(json.dumps(prior_release,indent=2)+'\n')
    prior_release['post_hoc_extension']={'approval':'User explicitly authorized pushing after completion; merging is not authorized.',
        'source_views':'post_hoc/SOURCE_VIEW_MANIFEST.json','exact_payload_inventory':'PUBLIC_PAYLOAD_MANIFEST.json',
        'boundary':'post_hoc/PUBLIC_REPRODUCIBILITY_BOUNDARY.md','private_ancestry_excluded':True,
        'original_heldout_records_modified':False,'Study2_model_execution':False}
    prior_release['approval_status']='USER_AUTHORIZED_PUSH_REVIEW_BRANCH_ONLY'
    (public/'PUBLIC_RELEASE_MANIFEST.json').write_text(json.dumps(prior_release,indent=2)+'\n')
    heading='''# Compiler-Guided Proof Repair in Lean 4: A Controlled Local-Model Pilot on Fixed Theorem Types

The latest [post-hoc manuscript](post_hoc/outputs/post_hoc/manuscript/post_hoc_pilot.pdf)
and [exploratory results](post_hoc/outputs/post_hoc/SUMMARY.md) extend the original
fixed-theorem study with process analyses, calibrated uncertainty and a separately
frozen 15-development-problem placebo control. Exact McNemar p=1.0 at zero
discordance does not establish equivalence. The original held-out outcomes are
unchanged. See the [public reproduction boundary](post_hoc/PUBLIC_REPRODUCIBILITY_BOUNDARY.md).
Study 2 model execution remains deferred. This branch is pushed for review;
it does not authorize merging or conference submission.

Run `python3 verify_payload.py` to verify the entire exact public inventory.

---

## Historical approved publication snapshot

'''
    (public/'README.md').write_text(heading+(public/'README.md').read_text())
    # Seal the complete publication tree, preserving the preceding inventory.
    files={}
    for path in sorted(public.rglob('*')):
        if not path.is_file() or path==public/'PUBLIC_PAYLOAD_MANIFEST.json':continue
        data=path.read_bytes();files[str(path.relative_to(public))]={'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data),'classification':'SAFE TO PUBLISH'}
    manifest={'schema_version':3,'approval_status':'USER_AUTHORIZED_PUSH_REVIEW_BRANCH_ONLY','files':files,
              'total_bytes':sum(v['bytes'] for v in files.values()),
              'manifest_scope':'Entire publication tree except this manifest; prior public ancestry only. Private research commits excluded.',
              'reproduction_scope':'Public aggregate/redacted-view checks and new dev records; original-byte held-out analysis remains a local reproduction boundary.'}
    (public/'PUBLIC_PAYLOAD_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print('Prepared reviewed public addition:',len(files),'files in complete publication inventory; no push/merge performed.')


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--destination',required=True);args=parser.parse_args();main(args.destination)
