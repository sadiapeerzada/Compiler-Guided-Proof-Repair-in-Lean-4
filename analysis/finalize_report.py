"""Link completed, checked post-hoc deliverables without changing raw records."""
import re
from .common import ROOT,OUT,read,write_json


def main():
    checks=read(OUT/'post_hoc_final_checks.json');assert checks['all_passed']
    assert read(OUT/'post_hoc_dev_validation.json')['valid']
    dev=read(OUT/'post_hoc_dev_summary.json');paper=read(OUT/'manuscript/post_hoc_build_manifest.json')
    log=(OUT/'post_hoc_python_suite.log').read_text();match=re.search(r'(\d+) passed(?:, (\d+) subtests passed)?',log);assert match
    reproduction={name:(OUT/name).read_bytes()==(OUT/'reproduced_run1'/name).read_bytes()
                  for name in ['reconciliation_summary.json','post_hoc_task1.json','post_hoc_calibrated_null.json']}
    assert all(reproduction.values())
    dev_reproduction=read(OUT/'dev_reproduced_run1/post_hoc_dev_reproduction.json')['numeric_outputs_byte_identical']
    assert all(dev_reproduction.values())
    record={'post_hoc':True,'tasks_0_to_3_complete':True,'reconciliation_mismatches':0,'Python_tests_passed':int(match[1]),
        'Python_subtests_passed':int(match[2] or 0),'Lean_build_exit_code':next(r['exit_code'] for r in checks['checks'] if r['check']=='lean_build'),
        'existing_data_reproduction_byte_identical':reproduction,'new_dev_responses':dev['physical_completed_model_responses'],
        'development_numeric_reproduction_byte_identical':dev_reproduction,
        'new_dev_intents':dev['logical_intents'],'new_dev_successes_observed':{c:[r['verified_successes'],r['observed_problems']] for c,r in dev['conditions'].items()},
        'development_process_counts':{c:{f:{'sum':r['repair_metrics'][f]['sum'],'denominator':r['repair_metrics'][f]['n']} for f in ['identical','any_unknown_removed']} for c,r in dev['conditions'].items() if c!='A'},
        'new_paper_pages':paper['pages'],'new_paper_path':paper['pdf'],'heldout_model_calls':0,
        'Study2_model_execution':'Deferred until separately approved; no model setting selected from unexecuted results.',
        'not_computable':['Outcomes and completed-response metrics for the two original unavailable C trajectories. No replay, imputation, or reconstruction.','Generalization, equivalence, or proof of diagnostic-content use/nonuse from one seed and five development families.'],
        'push_authorization':'User requested push after completion. Only a separate reviewed public-ancestry payload may be pushed; no merge authorized.'}
    write_json(OUT/'post_hoc_delivery.json',record)
    with (OUT/'SUMMARY.md').open('a') as stream:
        stream.write(f"\n## Final completion checks\n\nTasks 0–3 are complete. Reconciliation found zero mismatches. Existing-data reconciliation, process and calibrated-null JSON outputs reproduced byte-for-byte. The complete Python suite passed {match[1]} tests and {match[2] or '0'} subtests; the Lean build passed. The new anonymous manuscript has {paper['pages']} pages and uses the requested title.\n\n")
        stream.write('The dev worker interruption and no-replay recovery are recorded separately from the original execution log. All genuine model responses, streams and normalized compiler records are retained. Original held-out records and the two unavailable C outcomes are unchanged. Study 2 model execution remains deferred.\n\n')
        stream.write('Development process counts (descriptive completed repairs, with separate name-eligible denominators):\n\n')
        for c in ['B','C','C_placebo']:
            fields=dev['conditions'][c]['repair_metrics'];rep=fields['identical'];fix=fields['any_unknown_removed']
            stream.write(f"- {c}: identical {rep['sum']}/{rep['n']}; own-name removal {fix['sum']}/{fix['n']}.\n")
        stream.write('\n'+dev['interpretation']+' No new verified success was observed in any arm.\n\n')
        stream.write('Not computable: the unavailable original C outcomes and response-level metrics for those absent responses; broader equivalence or proof of diagnostic use/nonuse. No number is imputed for these. Public exact-byte reproduction of original held-out prompt/token metrics requires the preserved private originals.\n')
    for name in ['README.md','paper/README.md']:
        path=ROOT/name;text=path.read_text();lines=text.splitlines();relative='' if name=='README.md' else '../'
        current=(f"The latest [post-hoc manuscript]({relative}outputs/post_hoc/manuscript/post_hoc_pilot.pdf) ({paper['pages']} pages) uses the title above. "
                 f"[Post-hoc results and caveats]({relative}outputs/post_hoc/SUMMARY.md) include original-data process analyses, calibrated uncertainty and a separately frozen development-only placebo control. "
                 'The original held-out outcomes are unchanged; Study 2 model execution remains deferred.')
        marker='<!-- POST_HOC_CURRENT -->'
        if marker not in text:lines[1:1]=['',marker,current,marker,''];text='\n'.join(lines)+'\n'
        text=text.replace('No new model inference was executed.','No new model inference was executed for that earlier review revision.')
        if name=='paper/README.md':
            text=text.replace('Current source: `paper/main.tex`; current compiled PDF: `paper/compiled_final_review_v2.pdf` (14 pages).',
                'Current editable source is `paper/main.tex`; compile this revision with `python -m analysis.compile_paper`. The preceding review revision is retained in `paper/compiled_final_review_v2.pdf` (14 pages).')
            text=text.replace('Current quantitative claims are bound to','That earlier revision\x27s quantitative claims are bound to')
            text=text.replace('These commands document reproduction; they are not an instruction to rerun held-out inference.',
                'Those commands document the earlier revision. For this post-hoc revision use `analysis/README.md`; never rerun held-out inference.')
        path.write_text(text)
    print('Completed post-hoc report:',record['Python_tests_passed'],'tests;',paper['pages'],'paper pages')


if __name__=='__main__':main()
