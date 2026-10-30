"""Offline stored-record checks; no model, tokenizer, or private originals needed."""
import hashlib
import json
from pathlib import Path
from .common import ROOT,OUT,read,category
from extensions.filename_normalization import assert_private_free,feedback
from extensions.donors import select_donor


def digest(value):return hashlib.sha256(value.encode()).hexdigest()


def main():
    root=OUT/'dev_placebo';assert (root/'execution_finished.json').exists()
    protocol=read(ROOT/'extensions/placebo_protocol.json');poolpath=ROOT/protocol['donor_pool_path'];pool=read(poolpath)
    assert hashlib.sha256(poolpath.read_bytes()).hexdigest()==protocol['donor_pool_sha256']
    reported=read(OUT/'post_hoc_dev_summary.json');observed={c:[] for c in ['A','B','C','C_placebo']};calls=donors=0
    for ident in protocol['development_ids']:
        folder=root/'runs'/ident;m=read(folder/'manifest.json');assert m['status'] in ['completed','incomplete']
        initial=m['initial']
        for c in observed:observed[c].append(m['conditions'].get(c,{}).get('success'))
        if initial is None:continue
        if m['conditions']['A']['success'] is not None:assert m['conditions']['A']['success']==initial['verification']['success']
        for c in ['B','C','C_placebo']:
            branch=m['conditions'][c];assert len(branch['attempts'])<=3
            if 'initial_candidate_sha256' in branch:assert branch['initial_candidate_sha256']==initial['candidate_sha256']
            else:assert not branch['attempts'] and branch['success'] is None
            prior=initial
            for after in branch['attempts']:
                assert not prior['verification']['success']
                if c=='C':assert after['feedback_payload']==feedback(prior['verification'])
                elif c=='C_placebo':
                    donor,selection=select_donor(pool,ident,m['family'],category(prior['verification']),after['selection']['target_diagnostic_tokens'])
                    assert after['selection']==selection and after['feedback_payload']==donor['payload'];donors+=1
                else:assert after['feedback_payload']=='No compiler diagnostics are provided in the blind-retry condition.'
                prior=after
            if branch['success'] is not None:assert branch['success']==any(s['verification']['success'] for s in [initial]+branch['attempts'])
        for cp in folder.glob('*/completion.json'):
            completion=read(cp);md=completion['metadata'];intent=read(cp.parent/'intent.json');v=read(cp.parent/'verification.json')
            code=(cp.parent/'candidate.lean').read_text();assert digest(code)==v['candidate_sha256']
            assert digest(completion['prompt'])==completion['prompt_sha256']==intent['prompt_sha256']
            assert md['generation_seed']==int.from_bytes(hashlib.sha256(f"2027:{completion['context']}:{completion['prompt_sha256']}".encode()).digest()[:4],'big')
            assert md['temperature']==.2 and md['top_p']==1 and md['max_completion_tokens']==2000
            assert md['prompt_tokens']+2000<=8192
            frames=[json.loads(line) for line in (folder/'streams'/(digest(completion['context'])+'.jsonl')).read_text().splitlines()]
            assert ''.join(f.get('text','') for f in frames)==completion['raw_response']
            assert frames[-1]['status']=='generation_finished' and frames[-1]['completion_tokens']==md['completion_tokens']
            for d in v.get('diagnostics') or []:
                if d.get('fileName'):assert not Path(d['fileName']).is_absolute()
            assert_private_free(completion);assert_private_free(v);calls+=1
    for c,values in observed.items():
        assert sum(v is True for v in values)==reported['conditions'][c]['verified_successes']
        assert sum(v is not None for v in values)==reported['conditions'][c]['observed_problems']
    assert calls==reported['physical_completed_model_responses']
    print(json.dumps({'valid':True,'development_problems':len(protocol['development_ids']),'completed_response_journals_checked':calls,
        'deterministic_donor_records_checked':donors,'scope':'Stored candidate/prompt/journal bindings, seeds, caps, shared initials, donor selection using recorded token counts, and reported success denominators.',
        'not_checked':'No fresh Lean execution or tokenizer recomputation; original donor ancestry and frozen implementation are established by the preserved private validation, not this offline check.'},indent=2))


if __name__=='__main__':main()
