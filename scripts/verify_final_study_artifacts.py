"""Check all recorded generations, prompts, traces and exact compiled targets."""
from pathlib import Path
import hashlib
import json
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'eval'))
from final_study import BASE,read,sha,validate_protocol,validate_freeze
from final_study_analysis import validate_run
from model_client import extract_lean_block
from verify import _verification_source,_theorem_names,_diagnostics,_axioms_from_diagnostics

def main():
    path=ROOT/'configs/repair_experiment_local_v0.4.2.json';p=validate_protocol(path);p['_sha256']=sha(path)
    report=validate_freeze();rows=read(BASE/'test.json');root=ROOT/p['output_root']/'heldout'/'2027';checked=0;verified=0;attempts=0
    for r in rows:
        folder=root/r['id'];m=read(folder/'manifest.json');validate_run(m,p)
        if m['status'] not in ['completed','incomplete'] or m['dataset_sha256']!=p['dataset_sha256']['heldout']:raise ValueError('Unfinished/stale result')
        intents=list(folder.glob('*/intent.json'));attempts+=len(intents)
        if len(intents)>7 or any(x.parent.name not in {'initial','B1','B2','B3','C1','C2','C3'} for x in intents):raise ValueError('Illegal logical generation budget')
        if m['initial'] is None:continue
        initial=m['initial'];steps=[initial]
        prompts={'initial':(ROOT/p['prompts']['initial']).read_text().format(nl_statement=r['nl_statement'],theorem_statement=r['expected_lean_statement'])}
        for condition in ['B','C']:
            c=m['conditions'][condition];prior=initial;steps+=c['attempts']
            any_success=initial['verification']['success'] or any(a['verification']['success'] for a in c['attempts'])
            if (c['success'] is True)!=any_success:raise ValueError('Branch success disagrees with verified candidate evidence')
            for a in c['attempts']:
                template=(ROOT/p['prompts']['blind' if condition=='B' else 'guided']).read_text()
                prompts[a['key']]=template.format(theorem_statement=r['expected_lean_statement'],previous_candidate=prior['candidate'],feedback=a['feedback_payload'])
                prior=a
        for step in steps:
            cp=ROOT/step['completion_path'];c=read(cp);v=read(ROOT/step['verification_path']);code=extract_lean_block(c['raw_response'])
            if c['prompt']!=prompts[step['key']]:raise ValueError('Unlogged prompt information or blind leakage')
            if sha(cp.parent/'candidate.lean')!=step['candidate_sha256']:raise ValueError('Raw candidate file changed')
            md=c['metadata'];stream=folder/'streams'/(hashlib.sha256(c['context'].encode()).hexdigest()+'.jsonl')
            frames=[json.loads(line) for line in stream.read_text().splitlines()]
            if frames[0]['context']!=c['context'] or frames[0]['prompt_sha256']!=md['prompt_sha256'] or frames[-1].get('status')!='generation_finished' or frames[-1]['completion_tokens']!=md['completion_tokens']:
                raise ValueError('Missing/corrupted complete token stream')
            if md['prompt_tokens']+2000>8192 or md['completion_tokens']>2000 or md['chat_template_sha256']!=p['model']['chat_template_sha256']:
                raise ValueError('Context/token/template budget mismatch')
            if v['verification_source_text'] is not None:
                expected='open scoped BigOperators\n'+r['expected_lean_statement']+' := by sorry'
                name=_theorem_names(r['expected_lean_statement'])[0]
                source,target=_verification_source(code,expected,name,inspect_axioms=True)
                if source!=v['verification_source_text'] or hashlib.sha256(source.encode()).hexdigest()!=v['verification_source_sha256']:
                    raise ValueError('Compiled source does not contain the exact frozen target/candidate')
                messages,malformed=_diagnostics(v['compiler_stdout'] or '')
                if v['success'] and (malformed or any(d['severity']=='error' for d in messages) or _axioms_from_diagnostics(messages,target)!=v['axiom_dependencies']):
                    raise ValueError('Kernel/axiom success contradicts raw compiler JSON')
            if v['success']:verified+=1
            checked+=1
    summary={'valid':True,'dataset_validation':report,'frozen_protocol_sha256':p['_sha256'],'test_trajectories':len(rows),
        'logical_generation_attempts':attempts,'completed_generation_and_verification_records_checked':checked,
        'verified_successful_candidate_records':verified,'independent_human_reviews':0,'raw_sources_prompts_streams_and_compiler_evidence_consistent':True}
    (BASE/'final_result_validation.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
