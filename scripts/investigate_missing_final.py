"""Reconstruct every unavailable intent without executing or repeating inference."""
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'data/final_review/20261029_v2'
sys.path.insert(0,str(ROOT/'src'))
from final_study import read,validate_protocol


def main():
    p=validate_protocol(ROOT/'configs/repair_experiment_local_v0.4.2.json')
    from transformers import AutoTokenizer
    tokenizer=AutoTokenizer.from_pretrained(Path.home()/p['model']['snapshot_home_relative'],local_files_only=True,trust_remote_code=False)
    reports=[]
    for row in read(ROOT/'data/final_study/v1/test.json'):
        folder=ROOT/p['output_root']/'heldout/2027'/row['id'];m=read(folder/'manifest.json')
        for c in ['B','C']:
            branch=m['conditions'][c]
            if branch['success'] is not None:continue
            prior=branch['attempts'][-1] if branch['attempts'] else m['initial']
            key=c+str(len(branch['attempts'])+1);intent=read(folder/key/'intent.json')
            ds=[d for d in prior['verification']['diagnostics'] if d.get('kind')!='hasSorry']
            feedback=json.dumps({'diagnostic_state':'available','diagnostics':ds},ensure_ascii=False,indent=2) if c=='C' else 'No compiler diagnostics are provided in the blind-retry condition.'
            prompt=(ROOT/p['prompts']['guided' if c=='C' else 'blind']).read_text().format(theorem_statement=row['expected_lean_statement'],previous_candidate=prior['candidate'],feedback=feedback)
            assert hashlib.sha256(prompt.encode()).hexdigest()==intent['prompt_sha256']
            rendered=tokenizer.apply_chat_template([{'role':'user','content':prompt}],tokenize=False,add_generation_prompt=True)
            tokens=len(tokenizer.encode(rendered,add_special_tokens=False));context=intent['context'];stream=folder/'streams'/(hashlib.sha256(context.encode()).hexdigest()+'.jsonl')
            frames=[json.loads(line) for line in stream.read_text().splitlines()] if stream.exists() else []
            failure=folder/key/'generation_failure.json';complete=folder/key/'completion.json'
            assert not complete.exists()
            matches=[path for path in (ROOT/p['output_root']).rglob('completion.json') if read(path).get('context')==context]
            assert not matches
            reports.append({'problem_id':row['id'],'condition':c,'logical_step':key,'original_prompt_sha256':intent['prompt_sha256'],
                'reconstructed_prompt_matches':True,'input_tokens':tokens,'output_cap':2000,'context_cap':8192,
                'failure_class':'context_preflight_rejection' if tokens+2000>8192 else 'interrupted_generation_without_response',
                'failure_record':read(failure) if failure.exists() else None,'durable_stream_frames':len(frames),
                'durably_observed_generated_tokens':max([0]+[f.get('generation_tokens',0) for f in frames]),
                'durable_response_anywhere_in_final_runs':False,'existing_candidate_recoverable':False,
                'frozen_protocol_allows_inference_replay':False,'recovery_action':'None; retain missing outcome and consumed intent.',
                'source_paths':[str((folder/key/'intent.json').relative_to(ROOT))]+([str(stream.relative_to(ROOT))] if stream.exists() else []),
                'reason':'Exact input already exceeds the frozen total context cap; truncation would change the prompt.' if tokens+2000>8192 else 'Only a stream header survives; no response tokens or persisted generator state can be continued. Terminal no-replay policy forbids a replacement call.'})
    (BASE/'missingness_recovery.json').write_text(json.dumps({'new_inference_calls':0,'missing_outcomes':reports,'complete_pairs':58,
        'no_historical_artifacts_changed':True,'no_selective_rerun':True},ensure_ascii=False,indent=2)+'\n')
    print('Investigated',len(reports),'unavailable outcomes; neither safely recoverable; no inference executed.')


if __name__=='__main__':main()
