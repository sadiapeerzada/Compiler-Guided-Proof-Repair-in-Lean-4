#!/usr/bin/env python3
"""Stage and publish frozen Lean Study-2 V8/V9 evidence without touching main.

Usage:
  python3 study2_publish_v8_v9.py prepare --repo ~/NLP-to-Formal-Language-Proof --out ~/Desktop/Lean_V8_V9_Evidence_Review
  python3 study2_publish_v8_v9.py verify --packet ~/Desktop/Lean_V8_V9_Evidence_Review
  python3 study2_publish_v8_v9.py publish --repo ~/NLP-to-Formal-Language-Proof --packet ~/Desktop/Lean_V8_V9_Evidence_Review --confirm-public-release

IMPORTANT: This tool never edits frozen experiments. Its regex scan catches SOME
credentials but cannot decide whether data are safe/licensed for public posting.
Review the whole packet, including sample raw responses, before publishing.
"""
from __future__ import annotations
import argparse
import csv
import datetime as dt
import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path
from collections import Counter

BRANCH_DEFAULT = 'research/taimma-study2-v8-v9-evidence-20261103'
DEST_IN_REPO = Path('research/study2-raw-v8-v9')
V8_REL = Path('study2_outputs/bridge_items_1_4_6_v8_20261103')
V9_REL = Path('study2_outputs/bridge_items_1_6_v9_exploratory')
EXPECTED_V8_LOCKED_FILES = 40
MAX_SINGLE_BYTES = 35 * 1024 * 1024
MAX_CHUNK_BYTES = 30 * 1024 * 1024
MAX_TOTAL_BYTES = 250 * 1024 * 1024
ALLOWED_SUFFIXES = {'.json','.jsonl','.csv','.md','.txt','.py','.lean','.yaml','.yml','.toml','.log','.tsv','.lock','.svg','.tex','.sh','.ini','.cfg','.rst','.sha256'}
SKIP_DIRS = {'__pycache__','.git','.venv','.venv-study2','.cache','node_modules','models','model_weights','huggingface','snapshots'}
SKIP_FILES = {'.DS_Store','Thumbs.db','.gitkeep'}
SENSITIVE_PATTERNS = {
    'openai_or_other_sk_token': r'(?<![A-Za-z0-9_-])sk-[A-Za-z0-9_-]{20,}',
    'github_token': r'(?<![\w])(?:gh[pousr]_[A-Za-z0-9]{25,}|github_pat_[A-Za-z0-9_]{25,})',
    'huggingface_token': r'(?<![\w])hf_[A-Za-z0-9]{30,}',
    'aws_access_key_id': r'(?<![\w])(?:AKIA|ASIA)[A-Z0-9]{16}(?![\w])',
    'pem_private_key': r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',
    'credentialed_url': r'https?://[^\s/@:]+:[^\s/@]+@[^\s/]+',
}
WARNING_PATTERNS = {
    'email_address': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b',
    'local_mac_path': r'/Users/[A-Za-z0-9_.-]+/',
    'linux_home_path': r'/home/[A-Za-z0-9_.-]+/',
}


def fail(message):
    raise RuntimeError(message)


def sha256(data_path: Path) -> str:
    h = hashlib.sha256()
    with data_path.open('rb') as inp:
        for blob in iter(lambda: inp.read(1 << 20), b''):
            h.update(blob)
    return h.hexdigest()


def json_read(path: Path):
    return json.loads(path.read_text(encoding='utf-8'))


def json_write(path: Path, obj):
    path.write_text(json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=False)+'\n', encoding='utf-8')


def run(argv, *, cwd=None, acceptable=(0,)):
    p = subprocess.run([str(x) for x in argv], cwd=cwd, text=True, capture_output=True)
    if p.returncode not in acceptable:
        fail('Command failed: '+' '.join(str(x) for x in argv)+'\n'+(p.stderr or p.stdout)[-2400:])
    return p


def repo_root(path: Path) -> Path:
    path=path.expanduser().resolve()
    if not path.is_dir(): fail('Missing repository directory: '+str(path))
    root = Path(run(['git','rev-parse','--show-toplevel'],cwd=path).stdout.strip()).resolve()
    if root != path: fail('Use exact repository root, not a subdirectory: '+str(root))
    remote=run(['git','remote','get-url','origin'],cwd=root).stdout.strip()
    if 'sadiapeerzada/NLP-to-Formal-Language-Proof' not in remote and 'sadiapeerzada:NLP-to-Formal-Language-Proof' not in remote:
        fail('Unexpected Git remote; refusing to publish: '+remote)
    return root


def verify_v8_lock(root:Path):
    lockpath=root/V8_REL/'FINAL_1_4_6_LOCK.json'
    if not lockpath.is_file(): fail('V8 lock missing: '+str(lockpath))
    lock=json_read(lockpath)
    entries=lock.get('data_hashes',[])
    if len(entries)!=EXPECTED_V8_LOCKED_FILES or lock.get('do_not_edit_frozen_v7') is not True:
        fail('V8 lock entries/policy differ from the verified 40-file freeze')
    for item in entries:
        rel=Path(item['path'])
        if rel.is_absolute() or '..' in rel.parts: fail('Unsafe V8 locked path: '+str(rel))
        file=root/rel
        if not file.is_file(): fail('Missing locked V8 file: '+str(rel))
        if sha256(file)!=item['sha256']: fail('V8 lock SHA-256 mismatch: '+str(rel))
        if 'bytes' in item and file.stat().st_size!=item['bytes']:
            fail('V8 lock byte count mismatch: '+str(rel))
    return lockpath,len(entries)


def include_tree(root:Path,relative:Path):
    directory=root/relative
    if not directory.is_dir(): fail('Missing raw experiment directory: '+str(directory))
    included=[]
    excluded=[]
    for p in sorted(directory.rglob('*')):
        rel=p.relative_to(root)
        if p.is_symlink(): fail('Refusing symlink: '+str(rel))
        if any(x in SKIP_DIRS for x in rel.parts) or p.name in SKIP_FILES:
            if p.is_file():excluded.append((str(rel),'cache/os metadata'))
            continue
        if p.is_dir(): continue
        if not p.is_file() or not stat.S_ISREG(p.stat().st_mode):
            fail('Unexpected nonregular file: '+str(rel))
        if p.suffix.lower() in {'.png','.pdf'} and 'reports' in rel.parts:
            excluded.append((str(rel),'derived figure; excluded because the report data and source are archived'))
            continue
        if p.suffix.lower() not in ALLOWED_SUFFIXES:
            fail('Unexpected file type in evidence directory (review manually): '+str(rel))
        included.append((str(rel),p))
    if not included:fail('No evidence files in '+str(directory))
    return included,excluded


def validate_experiment_completeness(root:Path):
    """Check raw run journals, not just published aggregate table digests."""
    coder=root/V8_REL/'coder_exploratory'
    test=coder/'reports/test/outcomes.csv'
    dev=coder/'reports/development/outcomes.csv'
    expected={'A':11,'B_neutral':11,'C_real':11,'D_shuffled':11,
              'E_token_matched':11,'R_resample':14}
    for path,n in [(test,72),(dev,12)]:
        if not path.is_file():fail('Missing raw-model outcome table: '+str(path))
        with path.open(encoding='utf-8',newline='') as f:
            rows=list(csv.DictReader(f))
        if len(rows)!=n:fail(f'Expected {n} Coder {path.parent.name} outcome rows, got {len(rows)}')
        if n==72:
            observed={'A':sum(r['initial_success']=='True' for r in rows)}
            for arm in ('B_neutral','C_real','D_shuffled','E_token_matched','R_resample'):
                observed[arm]=sum(r[arm]=='True' for r in rows)
            if observed!=expected:fail('V8 outcome counts do not match frozen 11/11/11/11/11/14 results')
            keys={(r['id'],r['seed']) for r in rows}
            if len(keys)!=72:fail('V8 duplicate theorem/seed outcomes')
    traj=coder/'trajectories'
    if not traj.is_dir():fail('V8 raw trajectory journal directory is absent: '+str(traj))
    for name,n in [('test',72),('development',12)]:
        records=[p for p in traj.rglob('*.json') if name in p.relative_to(traj).parts]
        if len(records)!=n:fail(f'V8 {name} raw trajectory journal incomplete: {len(records)}/{n}')
        if not all(json_read(p).get('terminal') is True for p in records):
            fail(f'Nonterminal V8 {name} trajectory found')
    v9=root/V9_REL/'new_repair_arm/development_results.json'
    if not v9.is_file():fail('V9 development result missing: '+str(v9))
    result=json_read(v9)
    if not (result.get('planned')==12 and result.get('new_arm_verified')==5
            and result.get('original_v8_coder_guided_verified')==5
            and result.get('unknown_outcomes')==0 and len(result.get('records',[]))==12):
        fail('V9 results are not the audited 5/12 vs 5/12 development-only run')
    if (root/V9_REL/'new_repair_arm/test_results.json').exists():
        fail('Unexpected V9 held-out test results: this archive workflow documents a development-only V9')
    return {'coder_test_trajectories':72,'coder_development_trajectories':12,'v9_development_cases':12}


def files_to_publish(root:Path,downloads:Path):
    v8,excluded8=include_tree(root,V8_REL)
    v9,excluded9=include_tree(root,V9_REL)
    include=v8+v9
    scripts=['study2_final_146.py','study2_items_1_6_v9_fixed.py']
    for name in scripts:
        p=downloads/name
        if not p.is_file():
            fail('Reproducibility source missing: '+str(p)+' (download the exact run script; do not substitute a newer version)')
        include.append(('replay_scripts/'+name,p))
    paths=[s for s,_ in include]
    if len(paths)!=len(set(paths)):fail('Duplicate archive paths detected')
    return include,excluded8+excluded9,{'v8_files':len(v8),'v9_files':len(v9),'replay_scripts':len(scripts)}


def inspection(files):
    fatal=[]; warnings=[]
    compiled_sensitive={name:re.compile(pat) for name,pat in SENSITIVE_PATTERNS.items()}
    compiled_warnings={name:re.compile(pat) for name,pat in WARNING_PATTERNS.items()}
    for rel,path in files:
        size=path.stat().st_size
        if size>MAX_SINGLE_BYTES:fail('Oversized raw evidence file (>35 MiB): '+rel)
        try: source=path.read_text(encoding='utf-8')
        except UnicodeDecodeError: fail('Non-UTF-8 evidence: '+rel)
        for name,regex in compiled_sensitive.items():
            if regex.search(source):fatal.append({'file':rel,'type':name})
        for name,regex in compiled_warnings.items():
            n=len(regex.findall(source))
            if n:warnings.append({'file':rel,'type':name,'count':n})
    if fatal:
        # Never print matched token values.
        print('POTENTIAL CREDENTIALS DETECTED (not printing values):',json.dumps(fatal[:30],indent=2),file=sys.stderr)
        fail('Credential-like text found. Keep originals unchanged; perform authorized redaction into a new documented public copy before publishing.')
    return warnings


def make_packet(root:Path,out:Path,downloads:Path):
    if out.exists():fail('Output packet already exists; choose a fresh --out: '+str(out))
    lockpath,verified=verify_v8_lock(root)
    coverage=validate_experiment_completeness(root)
    files,excluded,counts=files_to_publish(root,downloads)
    warnings=inspection(files)
    sizes=[p.stat().st_size for _,p in files]
    if sum(sizes)>MAX_TOTAL_BYTES:fail('Evidence exceeds 250 MiB; use a separate reviewed release, not ordinary Git')
    out.mkdir(parents=True)
    entries=[];chunks=[];current=[];size=0
    for (rel,p),n in zip(files,sizes):
        entries.append({'path':rel,'sha256':sha256(p),'bytes':n})
        if current and size+n>MAX_CHUNK_BYTES:
            chunks.append(current);current=[];size=0
        current.append((rel,p));size+=n
    if current:chunks.append(current)
    archive_metadata=[]
    for ix,chunk in enumerate(chunks,1):
        name=f'evidence-part-{ix:03d}.zip'
        dest=out/name
        with zipfile.ZipFile(dest,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=8,allowZip64=False) as z:
            for rel,p in chunk:
                info=zipfile.ZipInfo(rel,date_time=(2026,11,3,0,0,0))
                info.compress_type=zipfile.ZIP_DEFLATED
                info.external_attr=0o644<<16
                with p.open('rb') as src,z.open(info,'w',force_zip64=False) as wr:
                    shutil.copyfileobj(src,wr,1<<20)
        if dest.stat().st_size > 45*1024*1024:
            fail('Archive part too large for prudent ordinary Git upload: '+name)
        archive_metadata.append({'filename':name,'sha256':sha256(dest),'bytes':dest.stat().st_size,'files':len(chunk)})
    summary={
        'schema':'study2-v8-v9-public-release-index/v1',
        'created_at_utc':dt.datetime.now(dt.timezone.utc).isoformat(),
        'source':'local_mac_originals_byte_preserved_in_zip',
        'base_repository':'sadiapeerzada/NLP-to-Formal-Language-Proof',
        'v8_locked_file_count_verified':verified,
        'v8_lock_sha256':sha256(lockpath),
        'counts':counts,
        'raw_coverage':coverage,
        'total_raw_bytes':sum(sizes),
        'total_files':len(entries),
        'entries':entries,
        'archives':archive_metadata,
        'disclaimer':'V8 exploratory; V9 development-only; AI review and theorem overlap unresolved; no NL-to-Lean semantic accuracy claim',
        'excluded_non_evidence_files':excluded,
    }
    json_write(out/'ARCHIVE_INDEX.json',summary)
    json_write(out/'PRIVACY_SCAN_WARNINGS.json',{
        'credential_regex_result':'No high-confidence credential matches found; NOT a general privacy audit',
        'warnings_count':len(warnings), 'warnings':warnings,
        'public_release_requires_manual_review':True,
    })
    readme='''# V8/V9 raw research evidence — public archive

## Contents
These archives contain byte-preserved **local** Study 2 V8 Coder experimental records,
AI reviewer raw responses, Lean reference checks, validation manifests, V9 development-only
repair records, and the exact replay scripts used locally. The archive index enumerates
SHA-256 for each evidence file, and each ZIP part has a separate SHA-256.

**Verification:** `python3 study2_publish_v8_v9.py verify --packet <this directory>`
validates the archive hashes and every file member against `ARCHIVE_INDEX.json`.
The 40 paths listed in the frozen V8 lock were verified against the original Mac
files *before packing*. Full model inference requires compatible MLX/Lean, model
weights and pinned dependencies; the model weights and system caches are **not** included.

The original 60-theorem study, base-model V7 and the V8/V9 follow-up are distinct.
Study 2 V8 was exploratory and not preregistered. Study 2 V9 used 12 development
cases only, not a fresh held-out test. The constructed benchmark's English text
is placeholder material and does not validate English-to-Lean semantic fidelity.
AI reviewer flags, possible test/dev family overlap and training contamination
remain unresolved; this evidence release does NOT sign off benchmark validity.

**Privacy:** High-confidence token patterns were automatically scanned; that scan
cannot detect all personal, secret, licensed or restricted material. Consult
`PRIVACY_SCAN_WARNINGS.json` and manually inspect the raw evidence before release.
Do not claim the full source experiment was independently rerun just because
archival checksums verify. No files in this package rewrite frozen originals.
'''
    (out/'README.md').write_text(readme,encoding='utf-8')
    shutil.copyfile(Path(__file__),out/'study2_publish_v8_v9.py')
    print('PREPARED PUBLIC-RELEASE PACKET:',out)
    print('VERIFIED V8 LOCK FILES:',verified)
    print('RAW FILES:',len(files),'V8:',counts['v8_files'],'V9:',counts['v9_files'])
    print('COMPRESSED ZIP PARTS:',len(archive_metadata))
    print('PRIVACY WARNINGS:',len(warnings),'(inspect the warnings and several raw records)')
    print('NO GIT CHANGES OR PUSH PERFORMED')


def verify_packet(packet:Path):
    packet=packet.expanduser().resolve()
    index=json_read(packet/'ARCHIVE_INDEX.json')
    archives=index['archives']; entries={item['path']:item for item in index['entries']}
    found=set();archives_bytes=0
    for archive in archives:
        p=packet/archive['filename']
        if not p.is_file() or sha256(p)!=archive['sha256'] or p.stat().st_size!=archive['bytes']:
            fail('ZIP archive checksum/size mismatch: '+str(p))
        archives_bytes+=p.stat().st_size
        with zipfile.ZipFile(p) as z:
            for member in z.infolist():
                n=member.filename
                rel=Path(n)
                if rel.is_absolute() or '..' in rel.parts or n in found or n not in entries:
                    fail('Unexpected/duplicate/unsafe member: '+n)
                h=hashlib.sha256();length=0
                with z.open(member) as inp:
                    for buf in iter(lambda:inp.read(1<<20),b''):
                        h.update(buf);length+=len(buf)
                exp=entries[n]
                if h.hexdigest()!=exp['sha256'] or length!=exp['bytes']:
                    fail('Archived source hash mismatch: '+n)
                found.add(n)
    if found!=set(entries):fail('Missing expected archived evidence files')
    if len(found)!=index['total_files']:fail('File count mismatch')
    if sum(item['bytes'] for item in entries.values())!=index['total_raw_bytes']:fail('Raw byte count mismatch')
    for n in ['README.md','PRIVACY_SCAN_WARNINGS.json','study2_publish_v8_v9.py']:
        if not (packet/n).is_file():fail('Missing packet metadata file: '+n)
    print('PACKET VERIFIED:',len(found),'files in',len(archives),'archives;',archives_bytes,'ZIP bytes')
    return packet,index


def publish(root:Path,packet:Path,branch:str):
    packet,index=verify_packet(packet)
    if not re.fullmatch(r'[a-zA-Z0-9_./-]+',branch) or '..' in branch or branch.startswith('-'):
        fail('Invalid branch name')
    if run(['git','show-ref','--verify','--quiet','refs/heads/'+branch],cwd=root,acceptable=(0,1)).returncode==0:
        fail('Local branch already exists: '+branch+' (never overwrite automatically)')
    check=run(['git','ls-remote','--exit-code','--heads','origin',branch],cwd=root,acceptable=(0,2))
    if check.returncode==0:fail('Remote branch already exists: '+branch+' (never overwrite automatically)')
    print('Fetching latest origin/main (no checkout of user main)...',flush=True)
    run(['git','fetch','origin','main'],cwd=root)
    tmpbase=Path(tempfile.mkdtemp(prefix='lean-evidence-push-'))
    worktree=tmpbase/'checkout'
    branch_created=False
    try:
        run(['git','worktree','add','-b',branch,str(worktree),'origin/main'],cwd=root)
        branch_created=True
        target=worktree/DEST_IN_REPO
        if target.exists():fail('Refusing overwrite: '+str(target))
        target.mkdir(parents=True)
        filenames=['README.md','ARCHIVE_INDEX.json','PRIVACY_SCAN_WARNINGS.json','study2_publish_v8_v9.py']+[x['filename'] for x in index['archives']]
        for name in filenames:shutil.copy2(packet/name,target/name)
        run(['git','add','--']+[str(DEST_IN_REPO/name) for name in filenames],cwd=worktree)
        print('Staged:',run(['git','diff','--cached','--stat'],cwd=worktree).stdout)
        run(['git','commit','-m','research: archive verified V8 and development-only V9 raw evidence'],cwd=worktree)
        sha=run(['git','rev-parse','HEAD'],cwd=worktree).stdout.strip()
        print('Pushing new evidence branch only...',flush=True)
        run(['git','push','-u','origin','HEAD:refs/heads/'+branch],cwd=worktree)
        print('PUSH COMPLETE:',sha)
        print('NEW BRANCH:',branch)
        print('COMPARE/CREATE PR: https://github.com/sadiapeerzada/NLP-to-Formal-Language-Proof/compare/main...'+branch+'?expand=1')
        print('Do NOT merge without reviewing privacy and the archive contents.')
    finally:
        if worktree.exists():
            try:run(['git','worktree','remove','--force',str(worktree)],cwd=root)
            except Exception as e:print('NOTE: Temporary worktree needs manual removal:',worktree,str(e),file=sys.stderr)
        try:tmpbase.rmdir()
        except OSError:pass


def main():
    ap=argparse.ArgumentParser(description=__doc__,formatter_class=argparse.RawDescriptionHelpFormatter)
    sub=ap.add_subparsers(dest='mode',required=True)
    for m in ('prepare','verify','publish'):
        p=sub.add_parser(m)
        if m in ('prepare','publish'):
            p.add_argument('--repo',type=Path,default=Path.cwd())
        if m=='prepare':
            p.add_argument('--out',type=Path,required=True)
            p.add_argument('--downloads',type=Path,default=Path.home()/'Downloads')
        else:p.add_argument('--packet',type=Path,required=True)
        if m=='publish':
            p.add_argument('--branch',default=BRANCH_DEFAULT)
            p.add_argument('--confirm-public-release',action='store_true',help='You manually audited the raw ZIP and approve public release')
    args=ap.parse_args()
    if args.mode=='prepare':make_packet(repo_root(args.repo),args.out.expanduser().resolve(),args.downloads.expanduser().resolve())
    elif args.mode=='verify':verify_packet(args.packet)
    else:
        if not args.confirm_public_release:fail('Public push requires --confirm-public-release after manual review')
        publish(repo_root(args.repo),args.packet,args.branch)

if __name__=='__main__':
    try:main()
    except Exception as ex:
        print('STOPPED:',type(ex).__name__+':',str(ex),file=sys.stderr)
        sys.exit(1)
