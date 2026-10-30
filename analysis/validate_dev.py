"""Validate actual new dev journals, pairings and genuine placebo provenance."""
import hashlib
import json
from pathlib import Path
from .common import ROOT,OUT,read,write_json,category,sanitize
from extensions.filename_normalization import feedback,assert_private_free
from extensions.donors import select_donor


def sha(text):return hashlib.sha256(text.encode()).hexdigest()


def main():
    folder=OUT/'dev_placebo';protocol=read(ROOT/'extensions/placebo_protocol.json');phash=hashlib.sha256((ROOT/'extensions/placebo_protocol.json').read_bytes()).hexdigest()
    if not (folder/'execution_finished.json').exists():raise ValueError('Dev run unfinished; no completion claim')
    from transformers import AutoTokenizer
    tokenizer=AutoTokenizer.from_pretrained(Path.home()/protocol['model']['snapshot_home_relative'],local_files_only=True,trust_remote_code=False)
    pool=read(ROOT/protocol['donor_pool_path']);source_rows={r['id']:r for r in read(ROOT/'data/final_study/v1/development.json')}
    cases=[];checked=0;placebo=0;own=0;unavailable=[]
    for ident in protocol['development_ids']:
        casefolder=folder/'runs'/ident;m=read(casefolder/'manifest.json');assert m['protocol_sha256']==phash
        assert m['phase']==protocol['phase'] and m['status'] in ['completed','incomplete']
        initial=m['initial'];case_steps=[]
        if initial is None:
            unavailable.append({'id':ident,'scope':'initial'});continue
        row=source_rows[ident]
        prompts={'shared_initial':protocol['prompt_text']['initial'].format(nl_statement=row['nl_statement'],theorem_statement=row['expected_lean_statement'])}
        case_steps.append(initial)
        for condition in ['B','C','C_placebo']:
            branch=m['conditions'][condition]
            if 'initial_candidate_sha256' in branch:assert branch['initial_candidate_sha256']==initial['candidate_sha256']
            assert len(branch['attempts'])<=3
            prior=initial
            for after in branch['attempts']:
                assert not prior['verification']['success']
                payload=after['feedback_payload']
                if condition=='B':assert payload=='No compiler diagnostics are provided in the blind-retry condition.'
                elif condition=='C':
                    assert payload==feedback(prior['verification'])
                    assert after['feedback_source_candidate_sha256']==prior['candidate_sha256'];own+=1
                else:
                    real=feedback(prior['verification']);n=len(tokenizer.encode(real,add_special_tokens=False))
                    donor,selection=select_donor(pool,ident,m['family'],category(prior['verification']),n)
                    assert payload==donor['payload'] and after['selection']==selection
                    assert donor['id']!=ident and donor['family']!=m['family'];placebo+=1
                prompts[after['key']]=protocol['prompt_text']['blind' if condition=='B' else 'guided'].format(theorem_statement=row['expected_lean_statement'],previous_candidate=prior['candidate'],feedback=payload)
                case_steps.append(after);prior=after
            actual_success=initial['verification']['success'] or any(a['verification']['success'] for a in branch['attempts'])
            assert (branch['success'] is True)==actual_success
            if branch['success'] is None:unavailable.append({'id':ident,'condition':condition,'status':branch['status']})
        assert len(list(casefolder.glob('*/intent.json')))<=10
        for step in case_steps:
            key=step['key'];cp=ROOT/step['completion_path'];c=read(cp);v=read(ROOT/step['verification_path']);md=c['metadata'];intent=read(cp.parent/'intent.json')
            assert c['prompt']==prompts[key] and sha(c['prompt'])==c['prompt_sha256']==intent['prompt_sha256']
            assert c['context'].startswith('post_hoc_dev_') and not c['context'].startswith('heldout')
            seed=int.from_bytes(hashlib.sha256(f"2027:{c['context']}:{c['prompt_sha256']}".encode()).digest()[:4],'big')
            assert md['generation_seed']==seed and md['base_seed']==2027
            assert md['model']==protocol['model']['model_id'] and md['snapshot_revision']==protocol['model']['snapshot_revision']
            assert md['temperature']==.2 and md['top_p']==1 and md['max_completion_tokens']==2000 and md['prompt_tokens']+2000<=8192
            rendered=tokenizer.apply_chat_template([{'role':'user','content':c['prompt']}],tokenize=False,add_generation_prompt=True)
            assert rendered==md['rendered_chat_text'] and len(tokenizer.encode(rendered,add_special_tokens=False))==md['prompt_tokens']
            assert v==step['verification']
            code=(cp.parent/'candidate.lean').read_bytes().decode();assert code==step['candidate'] and sha(code)==step['candidate_sha256']==v['candidate_sha256']
            stream=casefolder/'streams'/(sha(c['context'])+'.jsonl');frames=[json.loads(line) for line in stream.read_text().splitlines()]
            assert frames[0]['context']==c['context'] and ''.join(f.get('text','') for f in frames)==c['raw_response']
            assert frames[-1].get('status')=='generation_finished' and frames[-1]['completion_tokens']==md['completion_tokens']
            for d in v['diagnostics'] or []:
                if d.get('fileName'):assert not Path(d['fileName']).is_absolute()
            if v['success']:assert v['exit_code']==0 and set(v['axiom_dependencies'])<={'propext','Classical.choice','Quot.sound'}
            assert_private_free(c);assert_private_free(v);checked+=1
        cases.append(ident)
    write_json(OUT/'post_hoc_dev_validation.json',{'valid':True,'development_only':True,'planned_cases':15,'cases_with_initial':len(cases),
        'completed_responses_checked':checked,'own_diagnostic_repairs_checked':own,'genuine_other_family_donor_repairs_checked':placebo,
        'unavailable_outcomes':unavailable,'heldout_execution':False,'filename_normalization_only':True,'protocol_sha256':phash,
        'proof_safety':'Unmodified original strict verifier; all recorded successful axiom dependencies checked.',
        'normalization_test_evidence':'outputs/post_hoc/tests_before_dev.log'})
    print('New dev records, exact shared initials, seeds, budgets and genuine diagnostic ancestry validated:',checked,'responses')


if __name__=='__main__':
    try:main()
    except Exception as error:print('Validation stopped:',type(error).__name__,sanitize(str(error)));raise SystemExit(1)
