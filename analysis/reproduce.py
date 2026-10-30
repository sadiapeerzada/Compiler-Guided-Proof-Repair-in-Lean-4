"""Reproduce Tasks 0–2 into a fresh, explicitly named post_hoc subdirectory."""
import argparse
import importlib
from pathlib import Path
from . import common


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    out=args.output.resolve();root=common.OUT.resolve()
    if not out.is_relative_to(root) or out==root or out.exists():raise ValueError('Select a fresh subdirectory of outputs/post_hoc')
    common.OUT=out
    for name in ['reconcile','task1','task2','render']:
        module=importlib.import_module('analysis.'+name);module.OUT=out;module.main()


if __name__=='__main__':main()
