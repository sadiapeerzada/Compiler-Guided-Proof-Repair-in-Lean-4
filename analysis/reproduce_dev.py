"""Reproduce dev analysis in a fresh directory; never execute a model."""
import argparse
import importlib
import os
from pathlib import Path
from . import common


def main(output):
    source=common.OUT/'dev_placebo';target=(common.ROOT/output).resolve()
    target.relative_to(common.OUT.resolve())
    if target.exists():raise ValueError('Use a fresh reproduction output directory')
    if not (source/'execution_finished.json').exists():raise ValueError('Dev execution unfinished')
    target.mkdir();(target/'latex').mkdir();(target/'figures').mkdir()
    (target/'SUMMARY.md').write_text('# Post-hoc development analysis reproduction\n\nNo model inference or record modification.\n')
    # Relative link keeps original records read-only and avoids copying private paths.
    (target/'dev_placebo').symlink_to(os.path.relpath(source,target),target_is_directory=True)
    common.OUT=target
    for name in ['dev_placebo','dev_figures','check_public_dev']:
        importlib.import_module('analysis.'+name).main()
    names=['post_hoc_dev_summary.json','post_hoc_dev_repair_metrics.csv','post_hoc_dev_donor_selections.csv',
           'post_hoc_dev_resources.csv','post_hoc_dev_grouped_repetition.csv','post_hoc_dev_transitions.csv','post_hoc_dev_feedback_length_bins.csv']
    same={name:(source.parent/name).read_bytes()==(target/name).read_bytes() for name in names}
    assert all(same.values()),'Numeric reproduction differs; preserve both outputs and inspect'
    common.write_json(target/'post_hoc_dev_reproduction.json',{'post_hoc':True,'no_model_execution':True,'numeric_outputs_byte_identical':same,
        'PDF_comparison':'Plots regenerated from identical numeric inputs; PDF timestamps/metadata are not claimed byte-identical.'})
    print('Development numeric outputs reproduced byte-for-byte:',len(same),'files')


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True);args=parser.parse_args();main(args.output)
