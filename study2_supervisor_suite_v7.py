#!/usr/bin/env python3
"""Study 2: independent, append-only, local Lean proof-repair follow-up.

For sadiapeerzada/NLP-to-Formal-Language-Proof at commit 7aeece8 (2026-11-02).
Does not edit the original/frozen experiment, paper, or publication directory.
Not independently executed on an Apple Silicon/Lean installation by the author.

Modes: restore-data, doctor, screen, screen-test, dev, study, all, report, self-test. Run --help.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
from contextlib import contextmanager
from datetime import datetime, timezone
import csv
from xml.sax.saxutils import escape as xml_escape
import gc
import hashlib
import itertools
import json
import math
import os
from pathlib import Path
import platform
import random
import re
import shutil
import statistics
import subprocess
import sys
import time
import traceback
from typing import Any

VERSION = "2026-11-03-study2-v7-t08-application-syntax"
V5_VERSION = "2026-11-02-study2-v5-bridge-reference-fix"
V5_SCRIPT_SHA256 = "44e1215de441526de44e3177e3b890273c3e1e4c4ff7ab66cf334a6676f3ac15"

# Separate Study 2 verification configurations; not original-study replay.
# These fixed imports are identical for all arms and all problems in a run.
LEAN_PROFILES = {
    "bridge-minimal": ("Mathlib.Data.Nat.Basic", "Mathlib.Tactic.Ring", "Mathlib.Tactic.Tauto"),
    "tactic": ("Mathlib.Tactic",),
    "original": ("Mathlib",),
}
ACTIVE_LEAN_PROFILE = "original"

DEFAULT_MODELS = ["mlx-community/Qwen2.5-7B-Instruct-4bit",
                  "mlx-community/Qwen2.5-Coder-7B-Instruct-4bit"]
ARMS = ["B_neutral", "C_real", "D_shuffled", "E_token_matched", "R_resample"]
REVIEW_CODES = {
  "1": "Run development calibration and separately frozen confirmatory sample; no guaranteed solution rate",
  "2": "Novelty must be argued against Li and Li, APRIL and Baldur (human writing)",
  "3": "Neutral, real, unrelated-diagnostic, token-matched, and independent-resampling arms",
  "4": "Original and coding-specialized models when both snapshots are supplied",
  "5": "At least three independent declared seeds by default",
  "6": "Statement/elaboration screening and source/proof metadata inventory; human semantic review remains required",
  "7": "Token-matched neutral controls measured and explicit token mismatches reported",
  "8": "Per-target shared initial, independent condition PRNG streams, rotating arm order",
  "9": "Failure taxonomy and transition counts",
  "10": "Automatic case-study packet with raw candidates and compiler diagnostics",
  "11": "Explicit missing, operational-failure, and full-cohort bounds",
  "12": "Declared diagnostic cap and context truncation tracking",
  "13": "Paired McNemar, Wilson and clustered bootstrap with limitations",
  "14": "Original post hoc findings not reclassified as confirmatory",
  "15": "Generation/compiler latency, tokens and available peak-memory records",
  "16": "Per-step success-at-budget curves",
  "17": "Category and family denominators with zero-success caveats",
  "18": "Manuscript abstract must be rewritten after results (human writing)",
  "19": "Motivation for small offline local model must be written (human writing)",
  "20": "Related-work table requires literature review (human writing)",
  "21": "Novelty framing depends on actual results (human writing)",
  "22": "Machine-readable prompts, seeds, model revisions, toolchain and stop rules",
  "23": "Figure needs manuscript-specific revision (human writing)",
  "24": "Results CSV and raw denominators produced for tables (human writing)",
  "25": "String/error/verification endpoints kept separate",
  "26": "Floor effect, reuse of old test items and confounding documented",
  "27": "Local append-only checkpoints, exact script and model revision hash inventory",
  "28": "References require manual verification (human writing)",
  "29": "Venue template and page-limit must be checked separately (human writing)",
}


def utc(): return datetime.now(timezone.utc).isoformat()
def htxt(s: str) -> str: return hashlib.sha256(s.encode('utf-8')).hexdigest()
def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda: f.read(4*1024*1024), b''): h.update(b)
    return h.hexdigest()
def dump(x: Any) -> str: return json.dumps(x, indent=2, ensure_ascii=False, sort_keys=True) + '\n'
def read(p: Path): return json.loads(p.read_text(encoding='utf-8'))
def put_once(p: Path, obj: Any):
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open('x', encoding='utf-8') as f:
        f.write(dump(obj)); f.flush(); os.fsync(f.fileno())
def atomic(p: Path, obj: Any):
    p.parent.mkdir(parents=True, exist_ok=True)
    q = p.with_name('.' + p.name + '.tmp.' + str(os.getpid()))
    with q.open('x', encoding='utf-8') as f:
        f.write(dump(obj)); f.flush(); os.fsync(f.fileno())
    os.replace(q, p)
def log(*args): print('[Study2]', *args, flush=True)
def fail(message): raise RuntimeError(message)
def safe_key(s): return re.sub(r'[^a-zA-Z0-9_-]', '_', s)[:96]


@contextmanager
def exclusive_run_lock(output: Path):
    """Never permit simultaneous workers writing the same study directory.

    A SIGKILL/power failure leaves the lock intact intentionally; a researcher
    must inspect the logged PID before manually clearing a genuinely stale lock.
    """
    output.mkdir(parents=True,exist_ok=True)
    lock=output/'.study2_worker.lock'
    try:
        fd=os.open(lock, os.O_WRONLY|os.O_CREAT|os.O_EXCL, 0o600)
    except FileExistsError:
        fail('Experiment worker lock already exists: '+str(lock)+
             '. Check its recorded PID, ensure no other worker is active, then remove the STALE lock manually if needed.')
    try:
        with os.fdopen(fd,'w',encoding='utf-8') as f:
            f.write(dump({'pid':os.getpid(),'start_utc':utc(), 'script':VERSION}))
            f.flush();os.fsync(f.fileno())
        yield
    finally:
        lock.unlink(missing_ok=True)


# Original, published, privacy-redacted files at the exact inspected Git commit.
# The Git object SHA-1 includes the binary Git `blob <length>\0` header.
PUBLIC_COMMIT = '7aeece8ba8166e129ea8c47e4ca7c42224abaea1'
PUBLIC_FILES = {
    'publication/dataset/development.redacted.json': {
        'git_blob_sha1': 'e1da5a9a1b7d59456483509a831a32e6be158872',
        'bytes': 108707, 'rows': 15},
    'publication/dataset/test.redacted.json': {
        'git_blob_sha1': 'a01c711e0c6483e72dd70e3a5846f8ce3c73760a',
        'bytes': 429538, 'rows': 60},
}


def git_blob_hash(data: bytes) -> str:
    return hashlib.sha1(b'blob ' + str(len(data)).encode('ascii') + b'\0' + data).hexdigest()


def validate_public_data(path: Path, spec: dict) -> None:
    data = path.read_bytes()
    if len(data) != spec['bytes'] or git_blob_hash(data) != spec['git_blob_sha1']:
        fail('Published dataset integrity mismatch at '+str(path)+
             '. Refusing to mix changed data with the inspected, published cohort.')
    rows = json.loads(data)
    if not isinstance(rows, list) or len(rows) != spec['rows']:
        fail('Published dataset structure/count mismatch at '+str(path))
    if len({r['id'] for r in rows}) != len(rows):
        fail('Published dataset has duplicate IDs at '+str(path))


def restore_public_datasets(repo: Path) -> None:
    """Restore missing, published redacted datasets from a pinned Git object.

    Prefer the local Git object database, then explicit public HTTPS retrieval.
    Never checkout/reset/merge/change branches; never overwrite existing files.
    """
    import urllib.request
    for rel,spec in PUBLIC_FILES.items():
        target=repo/rel
        if target.exists():
            if not target.is_file():fail('Expected regular file: '+str(target))
            validate_public_data(target,spec)
            log('Already verified:',rel)
            continue
        raw=None
        local=subprocess_capture(['git','cat-file','-e',spec['git_blob_sha1']],cwd=repo,timeout=30)
        # Check Git object existence without printing content; retrieve full bytes next.
        if local.get('ok'):
            p=subprocess.run(['git','cat-file','blob',spec['git_blob_sha1']],cwd=repo,
                             stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=35)
            if p.returncode==0:raw=p.stdout
        if raw is None:
            url=('https://raw.githubusercontent.com/sadiapeerzada/NLP-to-Formal-Language-Proof/'
                 +PUBLIC_COMMIT+'/'+rel)
            log('Retrieving pinned public dataset:',rel)
            try:
                req=urllib.request.Request(url,headers={'User-Agent':'Study2-dataset-recovery/1.0'})
                with urllib.request.urlopen(req,timeout=90) as response:
                    raw=response.read(spec['bytes']+1)
            except Exception as e:
                fail('Could not retrieve '+rel+' from published GitHub snapshot: '
                     +type(e).__name__+': '+str(e)[:240]
                     +'. Check network access and retry --mode restore-data.')
        if len(raw)!=spec['bytes'] or git_blob_hash(raw)!=spec['git_blob_sha1']:
            fail('Pinned Git blob SHA/size validation FAILED for '+rel+'. No file was written.')
        rows=json.loads(raw)
        if not isinstance(rows,list) or len(rows)!=spec['rows']:
            fail('Incorrect number of dataset rows in '+rel)
        target.parent.mkdir(parents=True,exist_ok=True)
        with target.open('xb') as f:
            f.write(raw);f.flush();os.fsync(f.fileno())
        validate_public_data(target,spec)
        log('Recovered and verified:',rel,'SHA-1',spec['git_blob_sha1'])
    log('Both public, redacted dataset files are verified. Original frozen experiments are untouched.')


def root_check(*, need_curated: bool=True) -> Path:
    root = Path.cwd().resolve()
    required = ['src/verify.py','src/model_client.py',
                'lean_project/lean-toolchain','lean_project/lake-manifest.json']
    absent=[x for x in required if not (root/x).is_file()]
    if absent:fail('Run from NLP-to-Formal-Language-Proof repository root. Missing: '+', '.join(absent))
    if need_curated:
        missing=[x for x in PUBLIC_FILES if not (root/x).is_file()]
        if missing:
            fail('Published public dataset files absent: '+', '.join(missing)+
                 '. Run: python study2_supervisor_suite_v4.py --mode restore-data')
        for rel,spec in PUBLIC_FILES.items():validate_public_data(root/rel,spec)
    sys.path.insert(0, str(root/'src'))
    return root

def bridge_rows(split):
    """Separately labeled constructed Lean-math stress-test; NOT new source-verified literature data.

    Reference proofs are hidden from every model prompt and must independently pass
    the exact-type, no-axioms strict local Lean verifier before ANY generation.
    Family split is defined here, before observing model outcomes.
    """
    dev = [
      ('d01','arithmetic','nat_add_laws','(a b : Nat) : a + b = b + a','omega'),
      ('d02','arithmetic','nat_add_laws','(a b c : Nat) : (a + b) + c = a + (b + c)','omega'),
      ('d03','arithmetic','nat_add_laws','(a : Nat) : a + 0 = a','omega'),
      ('d04','arithmetic','int_add_laws','(a b : Int) : a + b = b + a','omega'),
      ('d05','arithmetic','int_add_laws','(a : Int) : a + 0 = a','omega'),
      ('d06','algebra','nat_ring_squares','(a b : Nat) : (a+b)^2 = a^2 + 2*a*b + b^2','ring'),
      ('d07','algebra','nat_ring_squares','(a b : Nat) : a*(b+1)=a*b+a','ring'),
      ('d08','logic','prop_conjunction','(p q : Prop) : p ∧ q → q ∧ p','tauto'),
      ('d09','logic','prop_conjunction','(p q : Prop) : (p → q) → p → q','tauto'),
      ('d10','inequality','nat_bounds','(a b : Nat) (h : a ≤ b) : a+1 ≤ b+1','omega'),
      ('d11','inequality','nat_bounds','(a b : Nat) (h : a ≤ b) : a ≤ b+2','omega'),
      ('d12','inequality','nat_bounds','(a b : Nat) : a ≤ a+b','omega'),
    ]
    test = [
      ('t01','inequality','int_order','(x y : Int) (h : x ≤ y) : x+3 ≤ y+3','omega'),
      ('t02','inequality','int_order','(x y : Int) (h : x+2 ≤ y) : x ≤ y','omega'),
      ('t03','arithmetic','int_linear_cancel','(x : Int) : x-x=0','omega'),
      ('t04','arithmetic','int_linear_cancel','(x y : Int) : x+y-y=x','omega'),
      ('t05','inequality','int_order','(x y z : Int) (h : x ≤ y) (g : y ≤ z) : x ≤ z','omega'),
      ('t06','inequality','int_order','(x y : Int) (h : x < y) : x+1 ≤ y','omega'),
      ('t07','arithmetic','nat_successor','(a b : Nat) : Nat.succ (a+b) = Nat.succ a+b','omega'),
      ('t08','arithmetic','nat_successor','(a b : Nat) : a + Nat.succ b = Nat.succ (a + b)','rfl'),
      ('t09','inequality','nat_successor_bounds','(a : Nat) : a < a+1','omega'),
      ('t10','inequality','nat_successor_bounds','(a b : Nat) (h : a < b) : a+1 ≤ b','omega'),
      ('t11','algebra','nat_polynomial','(x y : Nat) : (x+y)*(x+y)=x*x+2*x*y+y*y','ring'),
      ('t12','algebra','nat_polynomial','(x y : Nat) : (x+y)^2=x^2+2*x*y+y^2','ring'),
      ('t13','algebra','nat_polynomial','(x y z : Nat) : x*(y+z)=x*y+x*z','ring'),
      ('t14','algebra','nat_polynomial','(x : Nat) : (x+1)*(x+1)=x*x+2*x+1','ring'),
      ('t15','algebra','int_polynomial','(x y : Int) : (x-y)^2=x^2-2*x*y+y^2','ring'),
      ('t16','algebra','int_polynomial','(x y : Int) : (x+y)*(x-y)=x^2-y^2','ring'),
      ('t17','algebra','int_polynomial','(x y : Int) : (x+y)^2=x^2+2*x*y+y^2','ring'),
      ('t18','algebra','int_polynomial','(x y z : Int) : (x+y)*z=x*z+y*z','ring'),
      ('t19','logic','prop_implications','(p q r : Prop) : (p → q) → (q → r) → p → r','tauto'),
      ('t20','logic','prop_implications','(p q : Prop) : p ∨ q → q ∨ p','tauto'),
      ('t21','logic','prop_implications','(p q : Prop) : p ∧ q → p','tauto'),
      ('t22','logic','prop_implications','(p : Prop) : (p ∧ True) ↔ p','tauto'),
      ('t23','modular','nat_modulo_two','(n : Nat) : (n+2)%2=n%2','omega'),
      ('t24','modular','nat_modulo_two','(n : Nat) : n%2 < 2','omega'),
    ]
    result=[]
    for label,cat,fam,theorem,tactic in dev if split=='development' else test:
        statement='theorem bridge_'+label+' '+theorem
        result.append({'id':'bridge_'+label,'category':cat,
            'nl_statement':'Synthetic controlled mathematical fixed theorem; not source-attributed natural-language translation.',
            'expected_lean_statement':statement,'reference_lean_proof':statement+' := by '+tactic,
            'study_eligibility':{'family':'bridge_'+fam,'human_review_completed':False},
            'curation':{'source_url':None,'source_license':'Author-constructed benchmark; manual mathematical review pending',
                        'problem_family':'bridge_'+fam}})
    return result

def rows_for(root, split, benchmark="curated"):
    if benchmark=="bridge": return bridge_rows(split)
    p = root/'publication'/'dataset'/(split+'.redacted.json')
    rows = read(p)
    if not isinstance(rows, list) or len({r['id'] for r in rows}) != len(rows):
        fail('Duplicate or malformed dataset rows: '+str(p))
    if len(rows) != (15 if split == 'development' else 60):
        fail('Unexpected publication cohort size. Refusing silent dataset substitution: '+str(p))
    for r in rows:
        if not r.get('expected_lean_statement','').lstrip().startswith('theorem '):
            fail('Missing canonical fixed theorem statement for '+r['id'])
    return rows


def family(row):
    return str(row.get('study_eligibility',{}).get('family') or row.get('curation',{}).get('problem_family') or row['id'])
def category(row): return str(row.get('category') or 'unspecified')


def chosen_test(rows, limit):
    """Fixed category-round-robin order, no outcome or difficulty filtering."""
    groups = defaultdict(list)
    for row in rows: groups[category(row)].append(row)
    for k in groups:
        groups[k].sort(key=lambda r: htxt('study2-20261102-test-selection/'+r['id']))
    result=[]
    for i in range(max(map(len,groups.values()))):
        for name in sorted(groups):
            if i < len(groups[name]): result.append(groups[name][i])
    return result[:limit]


def subprocess_capture(args, cwd=None, timeout=45):
    try:
        p=subprocess.run(args,cwd=cwd,text=True,capture_output=True,timeout=timeout)
        return {'command':' '.join(map(str,args)), 'ok':p.returncode==0,
                'stdout':p.stdout[-1800:], 'stderr':p.stderr[-1200:], 'exit_code':p.returncode}
    except Exception as e: return {'command':' '.join(map(str,args)), 'ok':False,'error_type':type(e).__name__,'message':str(e)[:250]}


def check_lean(root):
    lp = root/'lean_project'
    version = subprocess_capture(['lake','env','lean','--version'],cwd=lp)
    mathlib = subprocess_capture(['git','-C',str(lp/'.lake/packages/mathlib'),'rev-parse','HEAD'])
    manifest=read(lp/'lake-manifest.json')
    pack=next((p for p in manifest.get('packages',[]) if p.get('name')=='mathlib'),{})
    expected=pack.get('rev') or pack.get('revision')
    if not version['ok'] or not mathlib['ok'] or not expected:
        fail('Lean/Mathlib installation incomplete. Run: cd lean_project && lake exe cache get && lake build Nl2Lean')
    if '4.32.0' not in version.get('stdout',''):
        fail('Unexpected Lean version: '+version.get('stdout',''))
    if mathlib.get('stdout','').strip()!=expected:
        fail('Actual Mathlib commit disagrees with lake-manifest.json (not silently upgraded).')
    dirty=subprocess_capture(['git','-C',str(lp/'.lake/packages/mathlib'),'status','--porcelain'],cwd=lp)
    if not dirty['ok'] or dirty.get('stdout','').strip():
        fail('Mathlib checkout is dirty or cannot be inspected; do not mix edited Mathlib with frozen results.')
    return {'lean':version['stdout'].strip(),'mathlib_revision':expected,'lakefile_sha256':sha(lp/'lakefile.toml'),
            'manifest_sha256':sha(lp/'lake-manifest.json'),'toolchain_sha256':sha(lp/'lean-toolchain')}


def model_identity(path: Path, repository_id: str):
    if not path.is_dir(): fail('Model directory missing: '+str(path))
    weight_files=sorted(path.glob('*.safetensors'))
    if not weight_files: fail('Model weights (.safetensors) missing: '+str(path))
    if not (path/'tokenizer_config.json').exists() or not (path/'config.json').exists():
        fail('Model tokenizer/config missing: '+str(path))
    if list(path.glob('*.py')): fail('Custom Python model code prohibited for this experiment.')
    tokenizer=read(path/'tokenizer_config.json')
    if not tokenizer.get('chat_template'): fail('Model chat template missing')
    weights=[{'filename':f.name,'size':f.stat().st_size,'sha256':sha(f)} for f in weight_files]
    return {'repo':repository_id,'path':str(path.resolve()),'revision':path.resolve().name,
            'chat_template_sha256':htxt(str(tokenizer['chat_template'])),
            'files':weights,'model_config_sha256':sha(path/'config.json'),
            'tokenizer_config_sha256':sha(path/'tokenizer_config.json')}


def obtain_model(model_id, root, download):
    key=model_id.split('/')[-1]
    alt=root/'.study2-models'/key
    if alt.exists() and (alt/'config.json').exists(): return alt.resolve()
    # Prefer cached immutable Hugging Face snapshot; no paid endpoint or token needed.
    try:
        from huggingface_hub import snapshot_download
    except ImportError:
        fail('Install huggingface_hub in the active environment (see download instructions).')
    try:
        return Path(snapshot_download(repo_id=model_id, local_files_only=not download,
            allow_patterns=['*.json','*.safetensors','*.model','*.txt','*.tiktoken','*.merges','*.vocab'])).resolve()
    except Exception as error:
        fail('Could not locate/download '+model_id+': '+type(error).__name__+': '+str(error)[:400]+'; use --download-models when online')


def set_lean_profile(name: str):
    """Install a single predeclared import configuration for the NEW study.

    This changes the theorem environment, not the kernel's axiom/type checks.
    It MUST NOT be described as reproducing the frozen, full-Mathlib study.
    """
    global ACTIVE_LEAN_PROFILE
    if name not in LEAN_PROFILES:
        fail('Unknown new-study Lean import profile: '+name)
    ACTIVE_LEAN_PROFILE = name
    import verify
    if not hasattr(verify, '_study2_original_source_builder'):
        verify._study2_original_source_builder = verify._verification_source
    original = verify._study2_original_source_builder

    def source_builder(*args, **kwargs):
        source, theorem = original(*args, **kwargs)
        # Keep the proof/type equality and all #print axioms checks untouched.
        # Reconstruct ONLY the import header. A model cannot add new imports
        # in one arm and change the proof environment relative to another arm.
        marker = '\n\nnamespace Nl2LeanExpected\n'
        head, sep, tail = source.partition(marker)
        if not sep or not any(x.strip() == 'import Mathlib' for x in head.splitlines()):
            fail('Original verifier source layout changed; refusing to weaken proof checking.')
        if any(not x.startswith('import ') for x in head.splitlines() if x.strip()):
            fail('Unexpected original verifier header; refusing to transform it.')
        fixed = '\n'.join('import ' + m for m in LEAN_PROFILES[ACTIVE_LEAN_PROFILE])
        return fixed + marker + tail, theorem

    verify._verification_source = source_builder


def import_verifier():
    from verify import check_lean_file_detailed, VerificationPolicy

    def scoped_check(lean_code, lean_project_dir, scratch_name, **kwargs):
        # The original verifier's standalone statement-elaboration path adds
        # Mathlib if the candidate text contains no `import Mathlib` substring.
        # Only this reference-screen path needs a fixed import preamble.
        if kwargs.get('expected_statement') is None and ACTIVE_LEAN_PROFILE != 'original':
            lean_code = ('\n'.join('import '+m for m in LEAN_PROFILES[ACTIVE_LEAN_PROFILE])
                         + '\n\n' + lean_code)
        return check_lean_file_detailed(lean_code, lean_project_dir, scratch_name, **kwargs)
    return scoped_check, VerificationPolicy


def expected_theorem_for_verifier(row):
    """Construct the fixed reference theorem for a new Study 2 check.

    Bridge items were authored WITHOUT BigOperators, and their scoped imports
    do not provide that namespace.  Injecting `open scoped BigOperators` into
    them causes every reference proof (and every later candidate) to fail
    before theorem elaboration.  Original curated items retain the historical
    BigOperators scope when using the separately labeled curated protocol.
    The exact theorem declaration is otherwise unchanged, and the full strict
    type-equality / prohibited-token / axiom dependency checks remain active.
    """
    statement = row['expected_lean_statement'].rstrip()
    if row.get('reference_lean_proof'):
        return statement + ' := by sorry'
    scope = '' if 'open scoped BigOperators' in statement else 'open scoped BigOperators\n'
    return scope + statement + ' := by sorry'


def reference_screen(root, rows, output):
    """Check Lean fixed theorem elaboration and recorded source/proof evidence; not human semantic review."""
    check, Policy=import_verifier()
    results=[]
    for i,r in enumerate(rows):
        checkpoint=output/(r['id']+'.json')
        expected=expected_theorem_for_verifier(r)
        constructed=bool(r.get('reference_lean_proof'))
        if constructed and 'open scoped BigOperators' in expected:
            fail('Constructed benchmark unexpectedly requires BigOperators scope: '+r['id'])
        proof=r['reference_lean_proof'] if constructed else expected
        # A scoped theorem environment is part of the experiment protocol.
        # Never reuse V4 or other-profile checks merely because row IDs match.
        screen_fingerprint=htxt(dump({
            'script': VERSION, 'id':r['id'], 'expected':expected, 'proof':proof,
            'import_modules':list(LEAN_PROFILES[ACTIVE_LEAN_PROFILE]),
            'strict_verifier':'src/verify.py exact theorem type and allowed axiom policy',
        }))
        if checkpoint.exists():
            prior=read(checkpoint)
            if prior.get('screen_fingerprint')!=screen_fingerprint:
                fail('Stale or cross-profile reference checkpoint at '+str(checkpoint)+
                     '. Do not overwrite it; choose a NEW --out directory.')
            results.append(prior)
            continue
        v=check(proof,root/'lean_project','s2ref_'+htxt(r['id'])[:18],allow_sorry=not constructed,
                expected_statement=expected if constructed else None,
                policy=Policy(timeout_seconds=120)).to_record()
        proof_record=r.get('curation',{}).get('theorem_verification',{})
        if not proof_record: proof_record=r.get('study_eligibility',{}).get('theorem_verification',{})
        obj={'id':r['id'],'screen_fingerprint':screen_fingerprint,
             'lean_profile':ACTIVE_LEAN_PROFILE,'category':category(r),'family':family(r),
             'source_url':r.get('curation',{}).get('source_url'),
             'source_license':r.get('curation',{}).get('source_license'),
             'has_prior_reference_proof_evidence':bool(constructed and v['success'] or (proof_record.get('success') and proof_record.get('status')=='verified')),
             'constructed_reference_proof_kernel_verified':bool(v['success']) if constructed else None,
             'semantic_human_review':bool(r.get('study_eligibility',{}).get('human_review_completed')),
             'lean_statement_elaborates':bool(v['success'] or (v['failure_kind'] is None and v.get('exit_code')==0)),
             'verification':{'success':v['success'],'failure_kind':v.get('failure_kind'),'errors':v.get('errors',[])[:3]}}
        put_once(checkpoint,obj);results.append(obj)
        log('reference screen',i+1,'/',len(rows),r['id'],obj['lean_statement_elaborates'])
        if not obj['lean_statement_elaborates']:
            log('REFERENCE FAILURE DETAILS:',r['id'], 'kind=',v.get('failure_kind'), 'errors=',v.get('errors',[])[:5], 'stderr_tail=',str(v.get('compiler_stderr') or '')[-400:])
    return results


class MLXModel:
    def __init__(self,path,model_id,identity,max_context,max_output,temperature):
        self.path=path;self.model_id=model_id;self.identity=identity
        self.max_context=max_context;self.max_output=max_output;self.temperature=temperature
        self.model=None;self.tok=None
    def load(self):
        if self.model is not None:return
        os.environ['HF_HUB_OFFLINE']='1';os.environ['TRANSFORMERS_OFFLINE']='1'
        from mlx_lm import load
        self.model,self.tok=load(str(self.path),tokenizer_config={'trust_remote_code':False})
        if not hasattr(self.tok,'apply_chat_template'):fail('Tokenizer missing chat template')
    def unload(self):
        self.model=None;self.tok=None;gc.collect()
        try:
            import mlx.core as mx
            mx.clear_cache()
        except Exception:pass
    def encode(self,prompt):
        self.load()
        formatted=self.tok.apply_chat_template([{'role':'user','content':prompt}],tokenize=False,add_generation_prompt=True)
        return self.tok.encode(formatted,add_special_tokens=False)
    def count(self,prompt): return len(self.encode(prompt))
    def generate(self,prompt,seed,trace):
        self.load()
        from mlx_lm import stream_generate
        from mlx_lm.sample_utils import make_sampler
        import mlx.core as mx
        ids=self.encode(prompt)
        if len(ids)+self.max_output>self.max_context:
            raise ValueError('context_preflight_exceeded')
        mx.random.seed(seed)
        chunks=[];last=None;started=time.monotonic()
        with trace.open('x',encoding='utf-8') as f:
            f.write(json.dumps({'kind':'start','prompt_sha256':htxt(prompt),'seed':seed,
                'model':self.model_id,'prompt_tokens':len(ids)})+'\n')
            f.flush();os.fsync(f.fileno())
            try:
                for t in stream_generate(self.model,self.tok,prompt=ids,max_tokens=self.max_output,
                                         sampler=make_sampler(temp=self.temperature,top_p=1.0)):
                    chunks.append(t.text);last=t
                    f.write(json.dumps({'token':t.token,'text':t.text},ensure_ascii=False)+'\n')
                    if len(chunks)%20==0: f.flush();os.fsync(f.fileno())
                f.write(json.dumps({'kind':'finished','generations':len(chunks)})+'\n')
                f.flush();os.fsync(f.fileno())
            except BaseException as e:
                f.write(json.dumps({'kind':'unavailable','error_type':type(e).__name__})+'\n')
                f.flush();os.fsync(f.fileno());raise
        return {'content':''.join(chunks),'prompt_tokens':len(ids),
                'completion_tokens':getattr(last,'generation_tokens',None),
                'generation_seconds':time.monotonic()-started,
                'finish_reason':getattr(last,'finish_reason',None),
                'peak_memory_gb':getattr(last,'peak_memory',None)}


def initial_prompt(row):
    return ('Write a mathematically valid complete Lean 4 proof of exactly the fixed theorem below. '
      'Return ONLY one ```lean code block containing the full theorem with its exact statement and proof. '
      'No sorry, admit, axiom, constant, opaque or new theorem declarations. '\
      'Do not change binders, types, hypotheses or theorem name. You may use Mathlib tactics.\n\n'
      'Fixed theorem:\n```lean\n'+row['expected_lean_statement']+'\n```\n')

def repair_prompt(row,previous,feedback,arm):
    if arm=='R_resample':
        return initial_prompt(row)+'\nGenerate an independent fresh solution; do not rely on any earlier generated candidate.\n'
    return ('Repair the previous Lean 4 proof. Output ONLY one ```lean code block with the full exact theorem and proof. '
       'Keep theorem statement/binders identical. No sorry, admit, axiom, constant or opaque declarations. '
       'Do not add auxiliary theorems. Feedback is evidence only when genuine; reason independently.\n\n'
       'Fixed theorem:\n```lean\n'+row['expected_lean_statement']+'\n```\n'
       'Previous candidate:\n```lean\n'+previous+'\n```\n'
       'Feedback field:\n'+feedback+'\n')


def failure_class(v):
    if not v:return 'missing'
    if v.get('success'):return 'verified'
    kind=v.get('failure_kind')
    if kind not in ('compiler_error',None):return kind or 'unknown'
    s='\n'.join(v.get('errors') or []).lower()
    if any(k in s for k in ['unexpected token','unexpected identifier','expected token','parser','unexpected end']): return 'syntax'
    if any(k in s for k in ['unknown identifier','unknown constant','unknown tactic','unknown namespace']): return 'unknown_name'
    if any(k in s for k in ['type mismatch','failed to synthesize','application type mismatch','function expected']):return 'type_elaboration'
    if any(k in s for k in ['unsolved goals','unsolved goal','tactic failed','no goals to be solved']):return 'tactic_goals'
    return 'other_compiler'


def diagnostic(v,max_chars=1800):
    if not v or v.get('success'):return None
    if v.get('failure_kind')!='compiler_error':return None
    items=[]
    for d in v.get('diagnostics') or []:
        if d.get('kind')=='hasSorry' or d.get('severity')!='error':continue
        content=d.get('data')
        if isinstance(content,str) and content.strip():
            # Strip exact path prefixes only, preserving mathematical diagnostic content.
            content=re.sub(r'(/[^\s:]+/)+([^\s:]+\.lean)',r'\2',content)
            items.append({'severity':'error','message':content[:max_chars]})
        if len(items)>=3:break
    return dump(items) if items else None


def cap_feedback(model, row,prev,payload,arm,limit):
    """Predetermined prefix truncation; no feedback reordering or cherry-picking."""
    if payload is None:return None,{'reason':'no_structured_compiler_diagnostics'}
    original=payload; original_tokens=model.count(payload)
    # Prefix cap at fixed 384 tokens (not a reselected error); prefer whole JSON when possible.
    ids=model.tok.encode(payload,add_special_tokens=False)
    if len(ids)>limit:
        payload=model.tok.decode(ids[:limit],skip_special_tokens=True)
    # If predecessor is very long, a further deterministic prefix trim is permitted.
    while len(payload)>32 and model.count(repair_prompt(row,prev,payload,arm))+model.max_output>model.max_context:
        payload=payload[:int(len(payload)*.8)]
    n=model.count(repair_prompt(row,prev,payload,arm))+model.max_output
    if n>model.max_context:return None,{'reason':'context_exceeded_even_after_declared_truncation',
                                        'original_tokens':original_tokens}
    return payload, {'original_feedback_tokens':original_tokens,'used_feedback_tokens':model.count(payload),
                     'truncated':payload!=original,'policy':'prefix_384_then_fixed_fraction_80pct_to_fit'}


def neutral_pad(model,row,previous,target):
    """Search repetition of content-neutral token markers for near-equal input tokens."""
    prefix='No compiler diagnostics are provided. The following are inert length-control markers, not proof hints: '
    # Adding markers may tokenize differently near boundaries; measure actual rendered prompt each time.
    def mk(n): return repair_prompt(row,previous,prefix+(' [PAD]'*n),'E_token_matched')
    base=model.count(mk(0))
    if base>target:return mk(0),{'target':target,'actual':base,'delta':base-target,'matched':False}
    lo,hi=0,1
    while model.count(mk(hi))<target and hi<4096: lo,hi=hi,hi*2
    hi=min(hi,4096)
    for _ in range(16):
        if hi-lo<=1:break
        mid=(lo+hi)//2
        if model.count(mk(mid))<target:lo=mid
        else:hi=mid
    candidates=[(abs(model.count(mk(n))-target),n) for n in set([lo,hi,max(0,lo-1),hi+1]) if n<=4096]
    diff,n=min(candidates)
    actual=model.count(mk(n))
    return mk(n),{'target':target,'actual':actual,'delta':actual-target,'matched':abs(actual-target)<=3}


def get_previous(step):
    return step['candidate'] if step and step.get('candidate') else None


def step_path(root,model_key,seed,split,row_id,key):
    return root/'runs'/model_key/str(seed)/split/safe_key(row_id)/safe_key(key)


def invoke_step(output,repo,model,row,seed,model_key,split,key,prompt,ctx,extra=None):
    """Journal intent before generation, never regenerate an uncertain intent."""
    path=step_path(output,model_key,seed,split,row['id'],key);path.mkdir(parents=True,exist_ok=True)
    meta={'context':ctx,'prompt_sha256':htxt(prompt),'seed':seed,
          'model':model.model_id,'row':row['id'],'key':key,'extra':extra or {}}
    intent=path/'intent.json';complete=path/'completion.json';verification=path/'verification.json'
    fresh=not intent.exists()
    if fresh:put_once(intent,meta|{'started_at':utc()})
    elif any(read(intent).get(k)!=v for k,v in meta.items()):
        fail('Checkpoint inputs changed; refusing cross-protocol replay: '+str(path))
    if complete.exists(): c=read(complete)
    elif (path/'failed_generation.json').exists(): return {'state':'missing_generation','verification':None,'candidate':None,
                                                        'metadata':{},'key':key}
    elif not fresh:
        # A durable intent exists but no durable completed generation: NEVER replay.
        return {'state':'missing_generation','verification':None,'candidate':None,
                'metadata':{},'key':key}
    else: c=None
    if not complete.exists():
        # Fresh durable intent reserved by this invocation.
        try:
            callseed=int.from_bytes(hashlib.sha256((str(seed)+'/'+ctx+'/'+htxt(prompt)).encode()).digest()[:4],'big')
            gen=model.generate(prompt,callseed,path/'tokens.jsonl')
            c={'context':ctx,'prompt_sha256':htxt(prompt),'prompt':prompt,'raw_response':gen['content'],
               'metadata':{k:v for k,v in gen.items() if k!='content'},'call_seed':callseed,'completed_at':utc()}
            put_once(complete,c)
        except (KeyboardInterrupt,SystemExit):
            raise
        except BaseException as e:
            put_once(path/'failed_generation.json',{'reason':'no_durable_response',
                'error_type':type(e).__name__,'message':str(e)[:220], 'at':utc()})
            log('UNAVAILABLE generation',row['id'],key,type(e).__name__,str(e)[:120])
            return {'state':'missing_generation','verification':None,'candidate':None,'metadata':{},'key':key}
    from model_client import extract_lean_block
    candidate=extract_lean_block(c['raw_response'])
    if verification.exists():
        v=read(verification)
        if v.get('candidate_sha256') != htxt(candidate):
            fail('Verifier checkpoint candidate SHA mismatch: '+str(verification))
    else:
        check,Policy=import_verifier()
        expected=expected_theorem_for_verifier(row)
        result=check(candidate,repo/'lean_project',
                     's2_'+htxt(ctx)[:24],expected_statement=expected,
                     policy=Policy(timeout_seconds=180))
        v=result.to_record()
        put_once(verification,v)
    return {'state':'complete','candidate':candidate,'candidate_sha256':htxt(candidate),
            'verification':v,'metadata':c['metadata'],'key':key,'folder':str(path)}


def run_step(output,repo,model,row,seed,model_key,split,key,prompt,ctx,extra=None):
    return invoke_step(output,repo,model,row,seed,model_key,split,key,prompt,ctx,extra)



def rotating_arms(row_id,seed):
    n=int(htxt('arms/'+row_id+'/'+str(seed))[:8],16)%len(ARMS)
    return ARMS[n:]+ARMS[:n]


def load_initial(output,model_key,seed,split,row):
    path=step_path(output,model_key,seed,split,row['id'],'initial')
    cp=path/'completion.json'; vp=path/'verification.json'
    if not cp.exists() or not vp.exists():return None
    from model_client import extract_lean_block
    c=read(cp);cand=extract_lean_block(c['raw_response'])
    return {'state':'complete','candidate':cand,'candidate_sha256':htxt(cand),
            'verification':read(vp),'metadata':c['metadata'],'key':'initial','folder':str(path)}


def donor_for(row,initials,seed,step):
    options=[]
    for rid,(donor_row,other) in initials.items():
        if rid==row['id'] or family(row)==family(donor_row):continue
        pay=diagnostic(other.get('verification'))
        if pay:
            options.append((htxt(f'donor/{row["id"]}/{seed}/{step}/{rid}'),rid,pay))
    if not options:return None,None
    _,rid,content=min(options)
    return rid,content


def one_trajectory(output,repo,model,row,seed,model_key,split,initials,repairs):
    state_path=output/'trajectories'/model_key/str(seed)/split/(safe_key(row['id'])+'.json')
    if state_path.exists():
        state=read(state_path)
        if state.get('terminal'):return state
    else:
        state={'id':row['id'],'category':category(row),'family':family(row),
            'model':model.model_id,'seed':seed,'split':split,'initial':None,'arms':{},
            'order':rotating_arms(row['id'],seed),'terminal':False,'started_at':utc()}
        atomic(state_path,state)
    init=initials[row['id']][1]
    state['initial']=init
    infra={'infrastructure_error','timeout','verifier_error','input_error'}
    if init['state']!='complete' or init['verification'].get('failure_kind') in infra:
        for arm in ARMS:state['arms'][arm]={'outcome':None,'status':'initial_unavailable','steps':[]}
        state['terminal']=True;state['finished_at']=utc();atomic(state_path,state);return state
    for arm in state['order']:
        saved=state['arms'].get(arm)
        if saved and saved['status']!='running':continue
        branch=saved or {'outcome':bool(init['verification']['success']),'status':'running','steps':[]}
        state['arms'][arm]=branch
        if init['verification']['success']:
            branch['status']='initial_verified';atomic(state_path,state);continue
        prior=branch['steps'][-1] if branch['steps'] else init
        for k in range(len(branch['steps'])+1,repairs+1):
            if prior['state']!='complete' or prior.get('verification') is None:
                branch.update(outcome=None,status='prior_unavailable');break
            prev=get_previous(prior); v=prior['verification']; details={}
            if arm=='R_resample':prompt=repair_prompt(row,prev,'',arm)
            elif arm=='B_neutral':
                prompt=repair_prompt(row,prev,'No compiler diagnostics are provided.','B_neutral')
            elif arm=='E_token_matched':
                real=diagnostic(v)
                payload,d=cap_feedback(model,row,prev,real,'C_real',384)
                if payload is None:
                    branch.update(outcome=None,status='no_comparable_compiler_feedback',note=d);break
                target=model.count(repair_prompt(row,prev,payload,'C_real'))
                prompt,match=neutral_pad(model,row,prev,target);details.update(match)
            elif arm=='C_real':
                payload,d=cap_feedback(model,row,prev,diagnostic(v),'C_real',384)
                details.update(d)
                if payload is None:
                    branch.update(outcome=None,status='no_actual_compiler_feedback');break
                prompt=repair_prompt(row,prev,payload,arm)
            elif arm=='D_shuffled':
                donor_id,donor=donor_for(row,initials,seed,k)
                if donor is None:
                    branch.update(outcome=None,status='no_independent_diagnostic_donor');break
                payload,d=cap_feedback(model,row,prev,donor,arm,384)
                details.update(d);details['donor_id']=donor_id
                if payload is None:
                    branch.update(outcome=None,status='donor_context_exceeded');break
                prompt=repair_prompt(row,prev,payload,arm)
            else:fail('unknown arm '+arm)
            ctx=VERSION+'/'+model_key+'/'+str(seed)+'/'+split+'/'+row['id']+'/'+arm+'/'+str(k)
            r=run_step(output,repo,model,row,seed,model_key,split,arm+'_'+str(k),prompt,ctx,details)
            # Avoid duplication of heavy verification source in trajectory JSON.
            slim={x:r.get(x) for x in ('state','key','candidate_sha256','metadata','folder')}
            slim['candidate']=r.get('candidate');slim['verification']=r.get('verification')
            slim['details']=details
            branch['steps'].append(slim);prior=slim
            if r['state']!='complete':branch.update(outcome=None,status='missing_generation');break
            if r['verification'].get('failure_kind') in infra:
                branch.update(outcome=None,status='verification_unavailable');break
            branch['outcome']=bool(r['verification'].get('success'))
            atomic(state_path,state)
            if branch['outcome']:branch['status']='verified';break
        if branch['status']=='running':branch['status']='budget_exhausted'
        atomic(state_path,state)
    state['terminal']=True;state['finished_at']=utc();atomic(state_path,state)
    return state


def execute_phase(root,output,models,rows,split,seeds,repairs,max_context,max_output,temperature):
    for model_id,ident in models.items():
        key=safe_key(model_id.split('/')[-1]); path=Path(ident['path'])
        model=MLXModel(path,model_id,ident,max_context,max_output,temperature)
        try:
            for seed in seeds:
                # Make all initials before any condition calls, so placebo donors are frozen.
                initials={}
                for i,row in enumerate(rows):
                    ctx=VERSION+'/'+key+'/'+str(seed)+'/'+split+'/'+row['id']+'/initial'
                    init=run_step(output,root,model,row,seed,key,split,'initial',initial_prompt(row),ctx)
                    initials[row['id']]=(row,init)
                    log(split,model_id,'seed',seed,'initial',i+1,'/',len(rows),row['id'],
                        init['verification']['success'] if init.get('verification') else 'missing')
                for i,row in enumerate(rows):
                    result=one_trajectory(output,root,model,row,seed,key,split,initials,repairs)
                    log(split,model_id,'seed',seed,'case',i+1,'/',len(rows),row['id'],
                        {a:result['arms'][a]['outcome'] for a in ARMS})
        finally:model.unload()


def wilson(s,n):
    if n==0:return None
    z=1.95996398454; p=s/n; denominator=1+z*z/n
    center=(p+z*z/(2*n))/denominator
    half=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/denominator
    return [max(0,center-half),min(1,center+half)]

def mcnemar(b_only,c_only):
    n=b_only+c_only
    if n==0:return 1.0
    k=min(b_only,c_only)
    return min(1.0,2*sum(math.comb(n,j) for j in range(k+1)) / (2**n))

def family_bootstrap(items,arm_a,arm_b,rounds=10000,seed=20271102):
    fam=defaultdict(list)
    for case in items:
        va=case['arms'][arm_a]['outcome'];vb=case['arms'][arm_b]['outcome']
        if va is None or vb is None:continue
        fam[case['family']].append((int(va),int(vb)))
    if not fam:return None
    groups=list(fam.values());rng=random.Random(seed);dif=[]
    for _ in range(rounds):
        batch=[groups[rng.randrange(len(groups))] for _ in range(len(groups))]
        flat=list(itertools.chain.from_iterable(batch))
        dif.append(sum(y-x for x,y in flat)/len(flat))
    dif.sort();return {'cluster_count':len(groups),'interval':[dif[int(.025*(len(dif)-1))],dif[int(.975*(len(dif)-1))]],
                       'seed':seed,'resamples':rounds,'note':'conditional complete-pair family bootstrap, not equivalence evidence'}

def draw_budget_figures(report_dir: Path, budgets: list, repairs: int, phase: str):
    """Static, dependency-free SVG success curves, with denominators at every point.

    These figures use *observed-only* success rates, not missing=failed. They
    are diagnostic plotting aids, not a claim of statistically significant gain.
    """
    grouped=defaultdict(list)
    for row in budgets: grouped[(row['model'],row['seed'])].append(row)
    strokes={'B_neutral':'#2662ab','C_real':'#b24422','D_shuffled':'#548d52',
             'E_token_matched':'#915ab7','R_resample':'#666666'}
    for (model,seed),rows in grouped.items():
        stats={}
        for arm in ARMS:
            points=[]
            for k in range(repairs+1):
                available=[x for x in rows if x['arm']==arm and x['budget']==k and x['observed']]
                num=sum(x['verified'] is True for x in available)
                n=len(available)
                points.append((k,num/n if n else None,num,n))
            stats[arm]=points
        numeric=[y for seq in stats.values() for _,y,_,_ in seq if y is not None]
        if not numeric:continue
        max_y=max(.05, min(1.0, max(numeric)*1.25 if max(numeric) else .05))
        w,h=950,525; left,right,top,bottom=100,735,100,445
        dx=(right-left)/max(1,repairs)
        def sx(k): return left+k*dx
        def sy(y): return bottom-(bottom-top)*y/max_y
        parts=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">',
               '<rect width="100%" height="100%" fill="white"/>',
               f'<text x="40" y="40" font-size="20" font-family="sans-serif" font-weight="bold">{xml_escape(phase.title())}: verified proof success by repair budget</text>',
               f'<text x="40" y="66" font-size="13" font-family="sans-serif">{xml_escape(model)} • seed {seed} • observed-only denominator</text>',
               f'<line x1="{left}" y1="{top}" x2="{left}" y2="{bottom}" stroke="#444"/>',
               f'<line x1="{left}" y1="{bottom}" x2="{right}" y2="{bottom}" stroke="#444"/>']
        for j in range(5):
            val=max_y*j/4;y=sy(val)
            parts.extend([f'<line x1="{left}" y1="{y:.1f}" x2="{right}" y2="{y:.1f}" stroke="#dddddd"/>',
                          f'<text x="{left-9}" y="{y+4:.1f}" font-size="12" font-family="sans-serif" text-anchor="end">{val:.1%}</text>'])
        for k in range(repairs+1):
            parts.append(f'<text x="{sx(k):.1f}" y="{bottom+25}" font-size="13" font-family="sans-serif" text-anchor="middle">{k}</text>')
        parts.append(f'<text x="{(left+right)/2}" y="{bottom+52}" font-size="14" font-family="sans-serif" text-anchor="middle">Maximum allowed repair calls</text>')
        for i,arm in enumerate(ARMS):
            color=strokes[arm];valid=[(x,y,n) for x,y,_,n in stats[arm] if y is not None]
            if valid:
                coords=' '.join(f'{sx(x):.2f},{sy(y):.2f}' for x,y,_ in valid)
                parts.append(f'<polyline points="{coords}" fill="none" stroke="{color}" stroke-width="2.5"/>')
                for x,y,n in valid:
                    parts.append(f'<circle cx="{sx(x):.2f}" cy="{sy(y):.2f}" r="3.5" fill="{color}"><title>{xml_escape(arm)} budget {x}: {y:.2%}, n={n}</title></circle>')
            ly=125+i*46
            parts.append(f'<line x1="756" y1="{ly}" x2="786" y2="{ly}" stroke="{color}" stroke-width="3"/>')
            parts.append(f'<text x="793" y="{ly+4}" font-size="12" font-family="sans-serif">{xml_escape(arm)}</text>')
        parts.append('<text x="40" y="508" font-size="11" font-family="sans-serif">Missing trajectories excluded per budget; sample sizes can change. This figure does not establish equivalence or causality.</text>')
        parts.append('</svg>')
        dest=report_dir/('repair_success_'+safe_key(model)+'_seed'+str(seed)+'.svg')
        dest.write_text('\n'.join(parts)+'\n',encoding='utf-8')


def summarize(output, plan, split):
    cases=[]
    for p in (output/'trajectories').glob(f'*/*/{split}/*.json'):
        x=read(p)
        if x.get('terminal'):cases.append(x)
    if not cases:return None
    cases.sort(key=lambda x:(x['model'],x['seed'],x['id']))
    summary={'phase':split,'cases':len(cases),'planned_cases':len(plan['models'])*len(plan['dev_seeds'] if split=='development' else plan['seeds'])*len(plan['rows'][split]),
             'grouped':{},'warnings':[]}
    output_rows=[];cost_rows=[];error_rows=[];budgets=[]
    for x in cases:
        init=x['initial']; first=init.get('verification') or {}
        row={'model':x['model'],'seed':x['seed'],'id':x['id'],'family':x['family'],'category':x['category'],
             'initial_success':first.get('success') if first else None,'initial_error':failure_class(first)}
        if init['state']=='complete':
            m=init['metadata'];cost_rows.append({'model':x['model'],'seed':x['seed'],'id':x['id'],
                'arm':'A','index':0,'prompt_tokens':m.get('prompt_tokens'),'completion_tokens':m.get('completion_tokens'),
                'seconds':m.get('generation_seconds'),'compiler_seconds':first.get('elapsed_seconds'),
                'memory_gb':m.get('peak_memory_gb')})
        for a in ARMS:
            b=x['arms'][a];row[a]=b['outcome'];row[a+'_status']=b['status']
            successes=[bool(first.get('success'))] if first else [False]
            for k,s in enumerate(b['steps'],1):
                v=s.get('verification');m=s.get('metadata') or {}
                cost_rows.append({'model':x['model'],'seed':x['seed'],'id':x['id'],'arm':a,
                    'index':k,'prompt_tokens':m.get('prompt_tokens'),'completion_tokens':m.get('completion_tokens'),
                    'seconds':m.get('generation_seconds'),'compiler_seconds':v.get('elapsed_seconds') if v else None,
                    'memory_gb':m.get('peak_memory_gb')})
                if v:
                    error_rows.append({'model':x['model'],'seed':x['seed'],'id':x['id'],'category':x['category'],
                        'arm':a,'index':k,'previous_error':failure_class(first if k==1 else b['steps'][k-2].get('verification')),
                        'new_error':failure_class(v),'verified':v.get('success'),'candidate_repeated':
                        s.get('candidate_sha256') == (init.get('candidate_sha256') if k==1 else b['steps'][k-2].get('candidate_sha256')),
                        'token_control_matched':s.get('details',{}).get('matched')})
                    successes.append(bool(v.get('success')))
            for budget in range(plan['repairs']+1):
                # A success at step 0/1 carries forward at higher allowed budgets
                # because the stopping policy terminates verified branches early.
                preceding_success=any(successes[:budget+1])
                available = (init.get('state')=='complete' and (budget==0 or preceding_success or
                            (len(b['steps'])>=budget and all(st['state']=='complete' for st in b['steps'][:budget]))))
                verified=preceding_success if available else None
                budgets.append({'model':x['model'],'seed':x['seed'],'id':x['id'],'arm':a,'budget':budget,'observed':bool(available),
                                'verified':verified})
        output_rows.append(row)
    summary['cases_terminal']=len(cases)
    for (model,seed),group in itertools.groupby(cases,key=lambda x:(x['model'],x['seed'])):
        items=list(group);name=model+' / '+str(seed)
        counts={}
        for a in ARMS:
            observed=[x['arms'][a]['outcome'] for x in items if x['arms'][a]['outcome'] is not None]
            s=sum(observed)
            counts[a]={'success':s,'observed':len(observed),'missing':len(items)-len(observed),
                       'observed_rate':s/len(observed) if observed else None,
                       'wilson95':wilson(s,len(observed)),
                       'operational_rate_missing_as_failure':s/len(items)}
        complete=[x for x in items if x['arms']['B_neutral']['outcome'] is not None and x['arms']['C_real']['outcome'] is not None]
        bc=sum(x['arms']['B_neutral']['outcome'] and not x['arms']['C_real']['outcome'] for x in complete)
        cb=sum(x['arms']['C_real']['outcome'] and not x['arms']['B_neutral']['outcome'] for x in complete)
        diff=(cb-bc)/len(complete) if complete else None
        low=sum((int(x['arms']['C_real']['outcome']) if x['arms']['C_real']['outcome'] is not None else 0)-
                (int(x['arms']['B_neutral']['outcome']) if x['arms']['B_neutral']['outcome'] is not None else 1) for x in items)/len(items)
        high=sum((int(x['arms']['C_real']['outcome']) if x['arms']['C_real']['outcome'] is not None else 1)-
                (int(x['arms']['B_neutral']['outcome']) if x['arms']['B_neutral']['outcome'] is not None else 0) for x in items)/len(items)
        comparisons={}
        for baseline in ['B_neutral','D_shuffled','E_token_matched','R_resample']:
            paired=[x for x in items if x['arms']['C_real']['outcome'] is not None
                    and x['arms'][baseline]['outcome'] is not None]
            base_only=sum(bool(x['arms'][baseline]['outcome']) and not x['arms']['C_real']['outcome'] for x in paired)
            real_only=sum(bool(x['arms']['C_real']['outcome']) and not x['arms'][baseline]['outcome'] for x in paired)
            comparisons['C_real_minus_'+baseline]={
                'role':'primary' if baseline=='B_neutral' else 'secondary_exploratory',
                'complete_n':len(paired),'baseline_only':base_only,'C_only':real_only,
                'difference':(real_only-base_only)/len(paired) if paired else None,
                'mcnemar_p':mcnemar(base_only,real_only) if paired else None,
                'conditional_family_bootstrap':family_bootstrap(items,baseline,'C_real')}
        token_first=[s for x in items for s in x['arms']['E_token_matched']['steps']
                     if s['key']=='E_token_matched_1']
        token_first_match=[s for s in token_first if s.get('details',{}).get('matched') is True]
        summary['grouped'][name]={'arms':counts,'paired_B_C':{'complete_n':len(complete),'B_only':bc,'C_only':cb,
             'difference':diff,'exact_mcnemar_p':mcnemar(bc,cb),'family_bootstrap':family_bootstrap(items,'B_neutral','C_real'),
             'all_case_missingness_identification_bound':[low,high]},
             'paired_comparisons':comparisons,
             'first_step_token_matching':{'attempted':len(token_first),'matched_within_3_tokens':len(token_first_match),
                'note':'Only first repair shares predecessor with C. Later steps have different histories.'},
             'categories':{z:{a:{'success':sum(x['arms'][a]['outcome']==True for x in items if x['category']==z),
                        'observed':sum(x['arms'][a]['outcome'] is not None for x in items if x['category']==z)} for a in ['B_neutral','C_real']}
                        for z in sorted({x['category'] for x in items})}}
    # Seed-level descriptive stability, not pseudo-replicated theorem counts.
    summary['across_seeds_by_model']={}
    for model in sorted({x['model'] for x in cases}):
        names=[key for key in summary['grouped'] if key.startswith(model+' / ')]
        metrics={}
        for arm in ARMS:
            values=[summary['grouped'][name]['arms'][arm]['observed_rate'] for name in names]
            values=[v for v in values if v is not None]
            metrics[arm]={'seed_n':len(values),'mean_observed_success':statistics.mean(values) if values else None,
                          'sd_across_seeds':statistics.stdev(values) if len(values)>1 else None}
        diffs=[summary['grouped'][name]['paired_B_C']['difference'] for name in names]
        diffs=[v for v in diffs if v is not None]
        summary['across_seeds_by_model'][model]={'arms':metrics,'seedwise_paired_differences':diffs,
          'mean_paired_difference':statistics.mean(diffs) if diffs else None,
          'sd_paired_difference':statistics.stdev(diffs) if len(diffs)>1 else None,
          'warning':'Repeated problems across seeds are dependent; do not treat seed-problem cells as independent theorems.'}
    def csv_write(path,items):
        if not items:return
        columns=list(dict.fromkeys(k for row in items for k in row))
        with path.open('w',newline='',encoding='utf-8') as f:
            writer=csv.DictWriter(f,fieldnames=columns);writer.writeheader();writer.writerows(items)
    d=output/'reports'/split;d.mkdir(parents=True,exist_ok=True)
    csv_write(d/'outcomes.csv',output_rows);csv_write(d/'calls.csv',cost_rows)
    csv_write(d/'transitions.csv',error_rows);csv_write(d/'success_by_budget.csv',budgets)
    draw_budget_figures(d,budgets,plan['repairs'],split)
    # Per-call compute and token accounting: never count missing telemetry as zero.
    costgroups=defaultdict(list)
    for call in cost_rows: costgroups[(call['model'],call['seed'],call['arm'])].append(call)
    summary['costs_by_model_seed_arm']={}
    for (model,seed,arm),items in costgroups.items():
        def metric(field):
            observed=[float(x[field]) for x in items if isinstance(x.get(field),(int,float)) and not isinstance(x.get(field),bool)]
            return {'observed_calls':len(observed),'total':sum(observed) if observed else None,
                    'mean':statistics.mean(observed) if observed else None}
        summary['costs_by_model_seed_arm'][f'{model} / {seed} / {arm}']={
            'completed_calls':len(items),'prompt_tokens':metric('prompt_tokens'),
            'completion_tokens':metric('completion_tokens'),
            'generation_seconds':metric('seconds'), 'compiler_seconds':metric('compiler_seconds'),
            'peak_memory_gb':metric('memory_gb')}
    summary['token_control_matched_count']=sum(x.get('token_control_matched') is True for x in error_rows if x['arm']=='E_token_matched')
    summary['token_control_unmatched_count']=sum(x.get('token_control_matched') is False for x in error_rows if x['arm']=='E_token_matched')
    summary['environment_and_plan_sha256']=sha(output/'plan.json')
    summary['warning']=plan['testing_boundary']+' Calibration used only the development split. Any confirmatory inference is conditional on this follow-up design.'
    atomic(d/'summary.json',summary)
    # Local case packets: never share publicly without inspecting paths/licenses/privacy.
    examples=[]
    for x in cases:
        if len(examples)>=3:break
        if len(examples)==0 and not any(a['outcome'] for a in x['arms'].values()):continue
        examples.append(x)
    for x in cases:
        if len(examples)>=3:break
        if x not in examples:examples.append(x)
    blocks=['# Automatically selected illustrative case studies (successes first, then sorted remaining cases)','',
            'These contain raw local model output and compiler errors; check privacy/licensing before publication.','']
    for case in examples:
        blocks += ['## '+case['id']+' / '+case['model']+' / seed '+str(case['seed']),'',
                   'Initial verifier: '+failure_class(case['initial'].get('verification')),'',
                   'Initial compiler diagnostics:','```text',
                   '\n'.join((case['initial'].get('verification') or {}).get('errors') or [])[:2500],'```','',
                   '```lean',case['initial'].get('candidate') or '<unavailable>','```','']
        for arm in ['B_neutral','C_real','D_shuffled','E_token_matched','R_resample']:
            branch=case['arms'][arm]
            blocks.append('### '+arm+' — '+str(branch['outcome']))
            for s in branch['steps']:
                blocks += ['Repair '+s['key']+', verifier '+failure_class(s.get('verification')),
                           '```lean',s.get('candidate') or '<unavailable>','```','',
                           'Compiler diagnostics:','```text',
                           '\n'.join((s.get('verification') or {}).get('errors') or [])[:2500],'```','']
    (d/'CASE_STUDIES.md').write_text('\n'.join(blocks),encoding='utf-8')
    lines=['# Study 2 '+split+' report','',f"Terminal cases: {len(cases)} of {summary['planned_cases']}",
           '', '**Not results from the original frozen 60-case study.**','',
           'Primary endpoint: strict original-type proof verification, case-level B versus C.','',
           'The script does NOT provide independent human validation of English–Lean meaning.',
           'Benchmark: '+plan['benchmark']+'; '+plan['testing_boundary'],
           '', '## Model × seed results','']
    for name,v in summary['grouped'].items():
        lines+=['### '+name,'', '| Arm | Verified / observed | Missing | Wilson 95% |', '|---|---:|---:|---|']
        for a,t in v['arms'].items():lines.append(f"| {a} | {t['success']}/{t['observed']} | {t['missing']} | {t['wilson95']} |")
        p=v['paired_B_C'];lines+=['',f"Complete B/C pairs: {p['complete_n']}; B-only {p['B_only']}; C-only {p['C_only']};",
          f"C−B={p['difference']}; exact McNemar p={p['exact_mcnemar_p']} (NOT an equivalence test).",
          f"Full-cohort missingness identification interval: {p['all_case_missingness_identification_bound']}",'',
          'Paired control comparisons (C minus comparator):','',
          '| Comparator | Role | Complete pairs | Difference | Exact McNemar p |',
          '|---|---|---:|---:|---:|']
        for comp,c in v['paired_comparisons'].items():
            lines.append(f"| {comp} | {c['role']} | {c['complete_n']} | {c['difference']} | {c['mcnemar_p']} |")
        matching=v['first_step_token_matching']
        lines += ['',f"Token-matched first repairs: {matching['matched_within_3_tokens']}/{matching['attempted']} attempted ",
                  'Later repairs do not necessarily share the same previous candidate.', '']
    lines+=['## Between-seed variability (descriptive)','',
            'Same problems repeat across seeds; these rates are not independent task samples.','',
            '| Model | Arm | Mean verified rate | SD across seeds |',
            '|---|---|---:|---:|']
    for model,val in summary['across_seeds_by_model'].items():
        for arm,c in val['arms'].items():
            mean=c['mean_observed_success'];sd=c['sd_across_seeds']
            lines.append(f"| {model} | {arm} | {mean if mean is not None else 'NA'} | {sd if sd is not None else 'NA'} |")
    lines+=['','## Figures','',
            'See repair_success_*.svg for observed-only success-by-budget curves per model and seed.',
            'Each plotted point reports its observed denominator on hover; missing trajectories are excluded.',
            'The figures are an editorial aid, not a significance or equivalence claim.','']
    lines+=['','## Cost and resource accounting','',
            'All numeric costs are measured only for completed calls; missing telemetry remains missing.','',
            '| Model / seed / arm | Calls | Mean prompt tokens | Mean output tokens | Mean generation seconds |',
            '|---|---:|---:|---:|---:|']
    for key,val in summary['costs_by_model_seed_arm'].items():
        def fmt(metric):
            x=val[metric]['mean']
            return f'{x:.1f}' if x is not None else 'unavailable'
        lines.append(f"| {key} | {val['completed_calls']} | {fmt('prompt_tokens')} | {fmt('completion_tokens')} | {fmt('generation_seconds')} |")
    lines+=['','## Supervisor review coverage','', 'Experiment automation does not establish causality or guarantee any success-rate improvement.','',
          '| Item | Status / work still needed |','|---|---|']
    for k,v in REVIEW_CODES.items(): lines.append(f'| {k} | {v} |')
    lines+=['','## Limitations','', '- The frozen original experiment used full import Mathlib; Study 2 uses predeclared scoped imports when selected. Theorems and kernel checks are retained, but library visibility/tactics change; treat as a new experimental environment.\n- Original test material was already seen in pilot analysis, so follow-up is not an entirely new untouched benchmark.',
           '- Real, unrelated and neutral prompts differ in content; matched tokens alone do not remove all semantic confounding.',
           '- Developer-selected model/benchmark and exploratory tuning must be disclosed; do not label original results as Study 2.',
           '- Bootstrap conditions on complete cases and does not account for missing outcomes; report bounds separately.',
           '- Follow-up results are only defensible after all declared model–seed–case cells are complete, and human review.',
           '- Report memory only if the MLX backend exposes telemetry, never impute it.','','See outcomes.csv, calls.csv, transitions.csv, success_by_budget.csv and summary.json.']
    (d/'REPORT.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    log('Reports written:',d)
    return summary


def plan_or_load(root,output,args,models,env,dev_evidence=None):
    dev=rows_for(root,'development',args.benchmark);test=chosen_test(rows_for(root,'test',args.benchmark),args.test_count)
    devfam={family(r) for r in dev}; testfam={family(r) for r in test}
    overlap=sorted(devfam & testfam)
    if overlap: fail('Cross-split family overlap: '+str(overlap[:10]))
    record={'version':VERSION,'benchmark':args.benchmark,'created_at':utc(),'source_repo':'sadiapeerzada/NLP-to-Formal-Language-Proof',
       'repo_commit':subprocess_capture(['git','rev-parse','HEAD'],cwd=root).get('stdout','').strip(),
       'source_files':{p:sha(root/p) for p in (['src/verify.py','src/model_client.py',
          'lean_project/lean-toolchain','lean_project/lake-manifest.json'] +
          (list(PUBLIC_FILES) if args.benchmark=='curated' else []))},
       'script_sha256':sha(Path(__file__)), 'development_evidence':dev_evidence,
       'technical_reference_amendment':('Before any test model inference, bridge_t08 had invalid Lean function-application spelling `Nat.succ(a+b)`; fixed to `Nat.succ (a + b)` with spaces, retaining the intended mathematical proposition; reference proof omega -> rfl. This changes the exact theorem statement bytes and test prompt; all other 23 test theorem texts, all development items, target IDs and verifier rules unchanged. Earlier V5/V6 screens failed on bridge_t08; test model calls had not started.' if args.benchmark=='bridge' else None),
       'lean_profile':args.lean_profile, 'lean_import_modules':list(LEAN_PROFILES[args.lean_profile]), 'models':models,'lean_environment':env,
       'seeds':args.seeds,'dev_seeds':args.dev_seeds,'rows':{'development':[r['id'] for r in dev],'test':[r['id'] for r in test]},
       'selection':('12 constructed dev / 24 constructed test with strictly verified reference proofs' if args.benchmark=='bridge' else '15 original development and fixed-hash category round-robin sample from 60 former heldout problems'),
       'repairs':args.repairs,'max_output':args.max_output,'max_context':args.max_context,
       'temperature':args.temperature,'arms':ARMS,
       'primary_comparison':'C_real versus B_neutral on complete problem-model-seed pairs',
       'primary_endpoint':'strict kernel verified exact fixed theorem',
       'diagnostic_policy':'first three genuine compiler errors, 384-token prefix, then deterministic 80% prefix trim for context cap',
       'missingness_policy':'no automatic replay of interrupted intent; incomplete is unknown, not false',
       'analysis_plan':'per-model seed paired exact McNemar; family bootstrap conditional complete cases; missingness bounds; descriptive costs',
       'testing_boundary':('constructed synthetic theorems, possible near-duplicates and training contamination; not independent human semantic review' if args.benchmark=='bridge' else 'previously disclosed original test items reused; new model/seed evaluation not an untouched benchmark'),
       'human_approval_and_semantic_review':'not asserted or automated', 'not_original_study_replay':'New scoped-import Lean environment. Report as different from frozen full-Mathlib study.'}
    p=output/'plan.json'
    if p.exists():
        old=read(p)
        for x in record:
            if x!='created_at' and old.get(x)!=record[x]:
                fail('Previously frozen plan differs on '+x+'. Use original options and same files, or a NEW --out directory.')
        return old,dev,test
    output.mkdir(parents=True,exist_ok=True);put_once(p,record)
    log('Frozen protocol plan:',p,'sha256',sha(p))
    return record,dev,test


def validate_prior_development(root, output, args, models, env):
    """Reuse immutable V5 calibration as external evidence, never copy or relabel it.

    This is permitted ONLY because V7 leaves all development problem texts,
    initial and repair prompts, verifier rules, settings and model protocol
    unchanged. V5 is byte-for-byte pinned. The V7 TEST-only t08 theorem
    spelling fix changes its exact Lean source bytes (and test prompts),
    retaining the intended Nat.add_succ proposition; the reference proof
    changed from omega to rfl. No V5/V6 test model inference occurred.
    """
    if args.reuse_dev_from is None:
        return None
    if args.mode != 'study' or args.benchmark != 'bridge':
        fail('--reuse-dev-from is allowed only for --mode study --benchmark bridge')
    source=(root/args.reuse_dev_from).resolve()
    if source == output or not source.is_relative_to(root) or source.is_relative_to(root/'publication'):
        fail('External dev source must be a DIFFERENT study output folder under repository root.')
    oldscript=root/'study2_supervisor_suite_v5.py'
    if not oldscript.is_file() or sha(oldscript)!=V5_SCRIPT_SHA256:
        fail('Exact original V5 script (SHA-256 pinned) is missing or changed; cannot certify unchanged development protocol.')
    oldplan=source/'plan.json'
    oldsummary=source/'reports/development/summary.json'
    oldcsv=source/'reports/development/outcomes.csv'
    oldreport=source/'reports/development/REPORT.md'
    for item in (oldplan,oldsummary,oldcsv,oldreport):
        if not item.is_file():fail('Missing original development evidence: '+str(item))
    plan=read(oldplan)
    if plan.get('version')!=V5_VERSION or plan.get('script_sha256')!=V5_SCRIPT_SHA256:
        fail('Development evidence does not originate from the exact V5 protocol.')
    checks={
        'benchmark':'bridge', 'lean_profile':args.lean_profile,
        'models':models, 'lean_environment':env,
        'seeds':args.seeds,'dev_seeds':args.dev_seeds,
        'repairs':args.repairs,'max_output':args.max_output,
        'max_context':args.max_context,'temperature':args.temperature,'arms':ARMS,
    }
    for key,val in checks.items():
        if plan.get(key)!=val:
            fail('Incompatible external development run at '+str(source)+': '+key)
    want_ids=[r['id'] for r in bridge_rows('development')]
    if plan.get('rows',{}).get('development') != want_ids:
        fail('V5 development target IDs changed; refusing external reuse.')
    want_test_ids=[r['id'] for r in chosen_test(bridge_rows('test'),args.test_count)]
    if plan.get('rows',{}).get('test') != want_test_ids:
        fail('Test cohort/order differs from archived V5 plan; refusing external reuse.')
    expected_src={p:sha(root/p) for p in ['src/verify.py','src/model_client.py',
                  'lean_project/lean-toolchain','lean_project/lake-manifest.json']}
    if plan.get('source_files')!=expected_src:
        fail('Tracked verifier/toolchain files changed since V5 development; refusing external reuse.')
    summary=read(oldsummary)
    # V5 already completed one model/seed x 12 dev cases, but check the evidence.
    planned=len(want_ids)*len(args.dev_seeds)*len(models)
    if summary.get('cases')!=planned or summary.get('planned_cases')!=planned:
        fail('External development summary is incomplete or has unexpected denominator.')
    import csv as _csv
    with oldcsv.open(newline='',encoding='utf-8') as f: records=list(_csv.DictReader(f))
    if len(records)!=planned or {r.get('id') for r in records}!={r['id'] for r in bridge_rows('development')}:
        fail('External development CSV has missing/duplicated/unexpected case IDs.')
    if any(r.get('B_neutral') not in ('True','False') or r.get('C_real') not in ('True','False')
           or r.get('initial_success') not in ('True','False') for r in records):
        fail('External development primary paired outcomes are incomplete.')
    failed=sum(r['initial_success']=='False' for r in records)
    rescued=sum(r['initial_success']=='False' and (r['B_neutral']=='True' or r['C_real']=='True') for r in records)
    if not failed or not rescued:
        fail('V5 development evidence does not pass declared progress gate.')
    evidence={
        'type':'separately archived V5 development evidence; NOT V7 recalculated calibration',
        'source_relative':str(source.relative_to(root)),
        'source_version':V5_VERSION,
        'source_v5_script_sha256':V5_SCRIPT_SHA256,
        'source_plan_sha256':sha(oldplan),
        'source_development_summary_sha256':sha(oldsummary),
        'source_development_outcomes_sha256':sha(oldcsv),
        'source_development_report_sha256':sha(oldreport),
        'completed_dev_cases':planned,
        'V7_test_only_syntax_fix':'bridge_t08 source `Nat.succ(a+b)` -> `Nat.succ (a + b)` to correct function application; reference proof omega -> rfl; the corrected theorem goes to model prompts but the reference proof does not; only test item t08 changes',
        'caveat':'Development results are V5; test results V7. Test-only theorem spelling corrected after reference-screen failure and before model inference. Do not merge them into one identically scripted run.'
    }
    log('Certified external development evidence:',evidence['source_relative'],
        planned,'completed cases; B/C gate PASS. V5 outputs remain read-only.')
    return evidence


def model_import_checks():
    missing=[]
    for pkg in ['mlx','mlx_lm','huggingface_hub']:
        try: __import__(pkg)
        except Exception:missing.append(pkg)
    if missing:fail('Missing local packages '+str(missing)+'. Use .venv/bin/python and pip install -r requirements-local.txt && pip install huggingface_hub')


def preflight(root,args):
    if sys.platform!='darwin' or platform.machine()!='arm64':
        fail('Actual MLX generation requires an Apple Silicon Mac (darwin/arm64). --mode self-test works anywhere.')
    model_import_checks();env=check_lean(root)
    model_names=DEFAULT_MODELS if args.models=='both' else [DEFAULT_MODELS[0] if args.models=='base' else DEFAULT_MODELS[1]]
    models={}
    for mid in model_names:
        snapshot=obtain_model(mid,root,args.download_models)
        log('Fingerprinting local model:',mid,'(may read several GB)')
        models[mid]=model_identity(snapshot,mid)
    return models,env


def doctor(repo,args):
    log('Repository:',repo)
    env=check_lean(repo);log('Lean:',env['lean'],'Mathlib:',env['mathlib_revision'])
    check,Policy=import_verifier()
    candidate=('theorem study2_sanity (n : Nat) : n = n := by\n'
               '  have h_omega : (2 : Nat) + 3 = 5 := by omega\n'
               '  have h_ring : (n + 1) * (n + 1) = n*n + 2*n + 1 := by ring\n'
               '  have h_tauto : True → True := by tauto\n'
               '  rfl')
    result=check(candidate,repo/'lean_project','s2_sanity_probe',
        expected_statement='theorem study2_sanity (n : Nat) : n = n := by sorry',
        policy=Policy(timeout_seconds=120))
    if not result.success:fail('Strict Lean canary failed under import profile '+ACTIVE_LEAN_PROFILE+': '+str(result.errors[:4]))
    log('Strict kernel-verifier canary: PASS; new-study import profile:',ACTIVE_LEAN_PROFILE,LEAN_PROFILES[ACTIVE_LEAN_PROFILE])
    log('Dataset rows:',len(rows_for(repo,'development',args.benchmark)),'development;',len(rows_for(repo,'test',args.benchmark)),'test')
    return env


def self_test():
    assert git_blob_hash(b'hello world\n')=='3b18e512dba79e4c8300dd08aeb37f8e728b8dad'
    assert all(spec['bytes']>0 and len(spec['git_blob_sha1'])==40 for spec in PUBLIC_FILES.values())
    assert LEAN_PROFILES['bridge-minimal']==('Mathlib.Data.Nat.Basic','Mathlib.Tactic.Ring','Mathlib.Tactic.Tauto')
    # Both the reference-screen and the actual generated-proof checker MUST
    # use exactly the same expected theorem construction.
    assert all('BigOperators' not in expected_theorem_for_verifier(r)
               for r in bridge_rows('development') + bridge_rows('test'))
    assert all(expected_theorem_for_verifier(r).endswith(' := by sorry')
               for r in bridge_rows('development') + bridge_rows('test'))
    assert expected_theorem_for_verifier({'expected_lean_statement':'theorem t : True'}) == \
        'open scoped BigOperators\ntheorem t : True := by sorry'
    assert mcnemar(0,0)==1.0
    assert mcnemar(5,0)==0.0625
    assert round(wilson(1,60)[0],4)==.0029
    assert len(chosen_test([{'id':str(i),'category':str(i%3)} for i in range(60)],24))==24
    text='theorem xyz : True := by trivial'
    assert htxt(text)==hashlib.sha256(text.encode()).hexdigest()
    dummy={'verification':{'success':False,'failure_kind':'compiler_error','errors':['unknown identifier foo'],
            'diagnostics':[{'kind':'error','severity':'error','data':'unknown identifier foo'}]}}
    assert failure_class(dummy['verification'])=='unknown_name'
    assert 'unknown identifier foo' in diagnostic(dummy['verification'])
    assert rotating_arms('id',42)==rotating_arms('id',42)
    assert len(bridge_rows('development'))==12 and len(bridge_rows('test'))==24
    t08 = next(r for r in bridge_rows('test') if r['id']=='bridge_t08')
    assert t08['reference_lean_proof'].endswith(' := by rfl')
    assert t08['expected_lean_statement'].endswith('a + Nat.succ b = Nat.succ (a + b)')
    assert 'Nat.succ(' not in t08['expected_lean_statement']
    assert not ({family(r) for r in bridge_rows('development')} & {family(r) for r in bridge_rows('test')})
    # Fake model/tokenizer tests masking and context-truncation without MLX or Lean.
    class Tok:
        def encode(self,t,add_special_tokens=False):return list(t)
        def decode(self,t,skip_special_tokens=True):return ''.join(t)
    class Mock:
        tok=Tok();max_context=12000;max_output=100
        def count(self,t):return len(t)
    model=Mock(); row={'expected_lean_statement':'theorem sample (n : Nat) : n = n'}
    prompt,values=neutral_pad(model,row,text,990)
    assert values['actual']>=len(repair_prompt(row,text,'','E_token_matched'))
    assert '[PAD]' in prompt
    p,d=cap_feedback(model,row,text,'error text'*90,'C_real',50)
    assert d['truncated']
    print('PASS: self-test (algorithmic logic only; no Mac, model or Lean test performed)')


def main():
    parser=argparse.ArgumentParser(description=__doc__,formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--mode',choices=['restore-data','doctor','screen','screen-test','dev','study','all','report','self-test'],default='all')
    parser.add_argument('--models',choices=['both','base','coder'],default='both')
    parser.add_argument('--reuse-dev-from',type=Path,default=None,help='Use exact, verified completed V5 development results as EXTERNAL evidence to gate V7 test; keeps V5 frozen and avoids repeat dev inference')
    parser.add_argument('--benchmark',choices=['curated','bridge'],default='curated',help='curated=prior published test items, bridge=new constructed provable toy maths stress-test')
    parser.add_argument('--lean-profile',choices=list(LEAN_PROFILES),default=None,help='Frozen Study 2 verifier environment: bridge-minimal (constructed only), tactic, or original; requires NEW output for each profile')
    parser.add_argument('--download-models',action='store_true',help='Allow free public Hugging Face weight download (about 4.3 GB per model)')
    parser.add_argument('--test-count',type=int,default=24,help='Preselected test items from previously published 60 (not a newly hidden set)')
    parser.add_argument('--seeds',type=str,default='2027,2028,2029',help='Confirmatory test seeds')
    parser.add_argument('--dev-seeds',type=str,default='2027',help='Calibration seeds (one by default to conserve compute)')
    parser.add_argument('--repairs',type=int,default=3)
    parser.add_argument('--max-context',type=int,default=8192)
    parser.add_argument('--max-output',type=int,default=1200)
    parser.add_argument('--temperature',type=float,default=0.2)
    parser.add_argument('--force-study',action='store_true',help='Continue despite floor-effect warning on development sample')
    parser.add_argument('--out',type=Path,default=Path('study2_outputs')/'supervisor_20261102')
    args=parser.parse_args()
    if args.mode=='self-test':self_test();return
    if args.lean_profile is None:
        args.lean_profile = 'bridge-minimal' if args.benchmark=='bridge' else 'tactic'
    if args.lean_profile=='bridge-minimal' and args.benchmark!='bridge':
        parser.error('bridge-minimal only supports --benchmark bridge; the curated mathematical symbols require additional modules')
    if args.benchmark=='bridge' and args.test_count>24:parser.error('Bridge benchmark has 24 test theorems')
    if args.mode=='screen-test' and args.benchmark!='bridge': parser.error('--mode screen-test is restricted to the new constructed bridge benchmark')
    if not 1<=args.test_count<=60 or not 1<=args.repairs<=3 or not 32<=args.max_output<=2000:
        parser.error('test-count 1..60, repairs 1..3, max-output 32..2000 required')
    try:args.seeds=[int(x.strip()) for x in args.seeds.split(',') if x.strip()]
    except ValueError:parser.error('--seeds must be comma-separated integers')
    if not args.seeds or len(set(args.seeds))!=len(args.seeds):parser.error('distinct seeds required')
    try:args.dev_seeds=[int(x.strip()) for x in args.dev_seeds.split(',') if x.strip()]
    except ValueError:parser.error('--dev-seeds must be comma-separated integers')
    if not args.dev_seeds or len(set(args.dev_seeds))!=len(args.dev_seeds):parser.error('distinct development seeds required')
    if args.mode in ['all','study'] and len(args.seeds)<3:
        log('WARNING: Fewer than 3 seeds will not meet the multiple-seed recommendation')
    root=root_check(need_curated=(args.benchmark=='curated' and args.mode not in ('restore-data','report')))
    if args.mode=='restore-data':
        restore_public_datasets(root);return
    # Patch only the new Study 2 worker process, never src/verify.py on disk.
    set_lean_profile(args.lean_profile)
    output=(root/args.out).resolve()
    if output==root or not output.is_relative_to(root) or output.is_relative_to(root/'publication'):
        fail('--out must be a new directory beneath repo root, outside publication/')
    if args.mode=='doctor':doctor(root,args);return
    if args.mode in ('screen','screen-test'):
        # No model download, no model inference and no frozen protocol yet.
        # Reference checks here are reusable by the later dev phase with the
        # SAME V7 script, profile, benchmark, and output directory.
        doctor(root,args)
        if (output/'plan.json').exists():
            fail('Screen a new output folder before any study plan is frozen.')
        screen_split = 'test' if args.mode=='screen-test' else 'development'
        screened=reference_screen(root,rows_for(root,screen_split,args.benchmark),output/'reference_screen')
        failures=[r['id'] for r in screened if not r['lean_statement_elaborates']]
        if failures:
            fail('Reference-screen FAILED for '+', '.join(failures)+'. Inspect '+str(output/'reference_screen'))
        log('REFERENCE-SCREEN PASS:',len(screened),screen_split,'proofs; no model loaded; independent human semantic review is still missing.')
        return
    if args.mode=='report':
        if not (output/'plan.json').exists():fail('No frozen plan under '+str(output))
        p=read(output/'plan.json')
        for split in (['test'] if p.get('development_evidence') else ['development','test']):summarize(output,p,split)
        return
    with exclusive_run_lock(output):
        run_experiment_locked(root,output,args)


def run_experiment_locked(root,output,args):
    log('Preflight; no paid LLM APIs, no modifications to frozen study.')
    log('NEW STUDY ONLY: verifier import profile',args.lean_profile,'(not original full-Mathlib study)')
    doctor(root,args)
    models,env=preflight(root,args)
    dev_evidence=validate_prior_development(root,output,args,models,env)
    p,dev,test=plan_or_load(root,output,args,models,env,dev_evidence)
    log('REFERENCE SCREEN is compiler elaboration + provenance audit, not independent human theorem validation.')
    # The development phase must not perform test-side Lean compilation or
    # preflight screening before the study phase is authorized.
    screen_rows=dev if args.mode=='dev' else dev+test
    screens=reference_screen(root,screen_rows,output/'reference_screen')
    bad=[x['id'] for x in screens if not x['lean_statement_elaborates']]
    if bad:fail('Some fixed statements fail current Lean elaboration: '+', '.join(bad))
    if args.mode in ['dev','all']:
        execute_phase(root,output,models,dev,'development',args.dev_seeds,args.repairs,args.max_context,args.max_output,args.temperature)
        devs=summarize(output,p,'development')
        if args.mode=='all' and not args.force_study:
            # Stop if not a single case succeeds under either main comparator across the dev cohort.
            dev_outcomes=output/'reports'/'development'/'outcomes.csv'
            with dev_outcomes.open(newline='',encoding='utf-8') as f:
                dev_rows=list(csv.DictReader(f))
            failed_initials=sum(r['initial_success']=='False' for r in dev_rows)
            rescued=sum(r['initial_success']=='False' and
                        (r['B_neutral']=='True' or r['C_real']=='True') for r in dev_rows)
            if devs['cases'] != devs['planned_cases'] or rescued==0 or failed_initials==0:
                log('NO-GO: development incomplete, no failed initial, or no B/C repair rescues; test blocked.')
                log('Development report:',output/'reports/development/REPORT.md')
                log('If supervisor approves this pre-specified test despite no signal, rerun --mode study --force-study.')
                return
    if args.mode=='study' and not args.force_study and not dev_evidence:
        devreport=output/'reports/development/summary.json'
        if not devreport.exists():fail('Run --mode dev first, or supply --force-study to record waiver.')
        devsummary=read(devreport)
        with (output/'reports'/'development'/'outcomes.csv').open(newline='',encoding='utf-8') as f:
            devrows=list(csv.DictReader(f))
        failed_initials=sum(r['initial_success']=='False' for r in devrows)
        rescued=sum(r['initial_success']=='False' and (r['B_neutral']=='True' or r['C_real']=='True') for r in devrows)
        if devsummary['cases']!=devsummary['planned_cases'] or rescued==0 or failed_initials==0:
            fail('NO-GO: dev incomplete, no initial failures, or no B/C repair rescues; --force-study explicitly overrides gate.')
    if args.mode in ['study','all']:
        execute_phase(root,output,models,test,'test',args.seeds,args.repairs,args.max_context,args.max_output,args.temperature)
        summarize(output,p,'test')
        if dev_evidence:
            note=output/'reports'/'test'/'DEVELOPMENT_LINEAGE.md'
            note.write_text('# Study 2 development evidence lineage\n\nDevelopment calibration belongs to **V5**, not V7. Test inference belongs to **V7**. The bridge_t08 test theorem spelling was corrected after reference-screen failure but before any test-model inference. No development inferences were copied, replayed, or relabeled.\n\n'+dump(dev_evidence),encoding='utf-8')
    log('Completed requested phases. Do NOT revise main manuscript until reviewing completeness/limitations in REPORT.md.')


if __name__=='__main__':
    try:main()
    except (KeyboardInterrupt,SystemExit):raise
    except Exception as error:
        log('STOPPED:',type(error).__name__,str(error))
        if os.environ.get('STUDY2_DEBUG')=='1':traceback.print_exc()
        sys.exit(2)
