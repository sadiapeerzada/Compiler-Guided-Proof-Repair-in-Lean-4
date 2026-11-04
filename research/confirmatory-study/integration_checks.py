"""Real Lean and tokenizer-only checks, never model inference or held-out evaluation."""
import hashlib
import json
import os
from pathlib import Path
from common import HERE,ROOT,read,dump,clean,sha,content_hash
from lean_adapter import LeanVerifier,live_environment
from backend import RenderedTokenizer
from matching import matched_conditions


def main():
    protocol=read(HERE/'isolated_repair_protocol.json');log=dict(inference_calls=0,scope='Synthetic safety fixtures and tokenizer-only historical text; not research outcomes')
    log['verification_scope_sha256']=content_hash({'lean':protocol['lean'],'model_revision':protocol['model']['revision'],'chat_template_sha256':protocol['model']['chat_template_sha256'],'input_tokens':4096})
    log['environment']=live_environment(protocol)
    verifier=LeanVerifier(protocol['lean']['imports'],timeout=45)
    target='theorem confirmatory_integration (n : Nat) : n = n'
    cases={'valid':target+' := by rfl','placeholder':target+' := by sorry','weakened':'theorem confirmatory_integration : True := by trivial','diagnostic':target+' := by exact unknown_integration_identifier'}
    outputs={}
    for key,candidate in cases.items():outputs[key]=verifier(candidate,target,'offline_'+key)
    expected={'valid':True,'placeholder':False,'weakened':False,'diagnostic':False}
    log['lean_status']='passed' if all(outputs[k]['success'] is v for k,v in expected.items()) and outputs['diagnostic'].get('diagnostics') else 'unverified_or_failed'
    log['lean_cases']=outputs
    # Load tokenizer assets only. No mlx_lm load/generate or model weights are touched.
    snapshot=Path(os.environ.get('CONFIRMATORY_MODEL_SNAPSHOT',str(Path.home()/'.cache/huggingface/hub/models--mlx-community--Qwen2.5-7B-Instruct-4bit/snapshots'/protocol['model']['revision'])))
    try:
        inventory=read(ROOT/protocol['model']['inventory_path'])
        for name,item in inventory['files'].items():
            if name.endswith('.safetensors'):continue
            if not (snapshot/name).exists() or sha(snapshot/name)!=item['sha256']:raise ValueError('Tokenizer/config asset missing or changed: '+name)
        from transformers import AutoTokenizer
        tokenizer=RenderedTokenizer(AutoTokenizer.from_pretrained(str(snapshot),local_files_only=True,trust_remote_code=False))
        real=outputs['diagnostic'];previous=cases['diagnostic']
        other_candidate=target+' := by exact another_unknown_integration_identifier'
        other=verifier(other_candidate,target,'offline_donor')
        match=matched_conditions({'expected_lean_statement':target},previous,real,other,other_candidate,tokenizer,4096)
        log['tokenizer_status']='passed' if match['valid'] else 'invalid_matching'
        log['rendered_counts']={a:r.get('prompt_tokens') for a,r in match.get('conditions',{}).items()}
        log['tokenizer_revision']=protocol['model']['revision'];log['chat_template_sha256']=protocol['model']['chat_template_sha256']
    except (ImportError,ValueError,OSError) as error:log.update(tokenizer_status='unavailable',tokenizer_reason=str(error))
    # Human-facing derivative of real verifier output: preserve originals in local scratch, redact home prefixes only here.
    log=json.loads(clean(json.dumps(log,ensure_ascii=False)))
    dump(HERE/'offline_integration_results.json',log)
    print({k:v for k,v in log.items() if k not in ('lean_cases',)})

if __name__=='__main__':main()
