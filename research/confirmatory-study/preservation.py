"""Hash every baseline tracked artifact; never rewrite an existing baseline manifest."""
import argparse
import os
import subprocess
from pathlib import Path
from common import ROOT,HERE,sha,dump,read,ensure

BASE='fcbda552eb734f4539c5a3d65ba263705bcba63b'

def snapshot():
    names=subprocess.check_output(['git','ls-tree','-r','--name-only',BASE],cwd=ROOT,text=True).splitlines()
    return {n:sha(ROOT/n) for n in names if (ROOT/n).is_file()}

def verify():
    frozen=read(HERE/'historical_hashes.json')
    for path,expected in frozen['files'].items():ensure((ROOT/path).is_file() and sha(ROOT/path)==expected,'Historical artifact changed: '+path)
    changed=subprocess.check_output(['git','diff','--name-only',BASE],cwd=ROOT,text=True).splitlines()
    ensure(all(p.startswith('research/confirmatory-study/') for p in changed),'Tracked changes outside new research directory')
    return {'baseline':BASE,'historical_files_verified':len(frozen['files']),'historical_changes':0}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--capture',action='store_true');a=p.parse_args()
    if a.capture:dump(HERE/'historical_hashes.json',{'baseline':BASE,'files':snapshot()},exclusive=True)
    print(verify())
