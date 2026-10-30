"""Freeze the approved dev-only placebo implementation before any generation."""
import hashlib
import json
from pathlib import Path
from analysis.common import ROOT,OUT,read,write_json
from .donors import pool_from_originals


def main():
    path=ROOT/'extensions/placebo_protocol.json'
    if path.exists():raise ValueError('Refusing to replace an existing frozen extension protocol')
    original=read(ROOT/'configs/repair_experiment_local_v0.4.2.json')
    from transformers import AutoTokenizer
    tokenizer=AutoTokenizer.from_pretrained(Path.home()/original['model']['snapshot_home_relative'],local_files_only=True,trust_remote_code=False)
    pool=pool_from_originals(tokenizer);pool_path=OUT/'dev_placebo/donor_pool.json';write_json(pool_path,pool)
    prompt_text={key:(ROOT/source).read_text() for key,source in original['prompts'].items()}
    pinned=['extensions/run_placebo.py','extensions/filename_normalization.py','extensions/donors.py','extensions/build_placebo_protocol.py',
            'analysis/common.py','analysis/metrics.py','src/local_llm_client.py','src/verify.py','src/model_client.py','scripts/run_final_study.py']
    value={'protocol_version':'post_hoc_dev_placebo_v1','scope':'post_hoc_development_only','heldout_execution_allowed':False,
           'phase':'post_hoc_dev_placebo_v1','base_seed':2027,'decoding':original['decoding'],'model':original['model'],
           'lean_toolchain':original['lean_toolchain'],'mathlib_revision':original['mathlib_revision'],'maximum_repairs':3,'maximum_calls_per_problem':10,
           'development_ids':[r['id'] for r in read(ROOT/'data/final_study/v1/development.json')],
           'conditions':{'A':'One fresh shared initial; no repairs.','B':'blind_repair_1..3: previous own candidate and fixed generic blind feedback.',
                         'C':'real_repair_1..3: previous own candidate and normalized actual immediately preceding compiler diagnostics.',
                         'C_placebo':'placebo_repair_1..3: previous own candidate and a different problem/family genuine donor diagnostic payload.'},
           'condition_order':['B','C','C_placebo'],'shared_initial_key':'shared_initial','prompt_text':prompt_text,
           'donor_pool_path':str(pool_path.relative_to(ROOT)),'donor_pool_sha256':hashlib.sha256(pool_path.read_bytes()).hexdigest(),
           'donor_pool_size':len(pool),'donor_scope':'Only existing test shared-initial verification files, category and family; never reads repair outcomes or uses them to tune anything.',
           'donor_rule':'Exclude same problem or family; prefer same frozen primary error category; minimize absolute normalized diagnostic-payload token-count difference to own current diagnostic payload; ties by SHA256(donor_id + colon + payload_sha256). Fall back to any eligible real diagnostic and log fallback if category has no matches; stop if no eligible donor. Apply again at every repair.',
           'normalization_user_approved':True,'normalization':'Deep-copy diagnostics in original order. Only fileName metadata becomes resolved repository-relative POSIX path. All actual message data, severity, kind, locations and every other field remain equal. No non-filename private content is edited; stop if it cannot be exported unchanged. Compiler JSON serialization may change whitespace only after filename normalization.',
           'normalization_algorithm_file':'extensions/filename_normalization.py',
           'normalization_sha256':hashlib.sha256((ROOT/'extensions/filename_normalization.py').read_bytes()).hexdigest(),
           'pinned_implementation_files':{name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in pinned},
           'seed_policy':original['seed_policy'],'memory_schedule':original['memory_schedule'],
           'resident_memory':'resource.getrusage(RUSAGE_SELF).ru_maxrss peak bytes (not instantaneous RSS) and native MLX peak_memory_gb when available.',
           'stopping':'Verified success, three completed/consumed repair intents, preflight failure, missing generation, no genuine C diagnostics, or verifier infrastructure failure. No truncation, synthetic diagnostics, generation replay, or replacement of incomplete output. Complete outputs/verifications may be reused by durable checkpoints.',
           'output_root':'outputs/post_hoc/dev_placebo','proof_policy':'Existing strict verifier, exact-type check and allowed axioms unmodified, timeout 180 seconds.',
           'analysis_scope':'Exploratory n=15 one-seed counts, Wilson intervals and process metrics; no hypothesis-test or proof-of-content-use claims.',
           'interpretation':'Findings may be consistent/inconsistent with diagnostic-content sensitivity; cannot prove use or nonuse. Donor matching itself reveals error category/length, and donor mathematical content can be indirectly helpful.',
           'study2_execution':'Deferred pending separate approval; no new held-out execution.'}
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
    h=hashlib.sha256(path.read_bytes()).hexdigest();(ROOT/'extensions/placebo_protocol.sha256').write_text(h+'  placebo_protocol.json\n')
    write_json(OUT/'dev_placebo/protocol_freeze.json',{'post_hoc':True,'development_only':True,'protocol_sha256':h,'normalization_sha256':value['normalization_sha256'],
        'donor_pool_sha256':value['donor_pool_sha256'],'donor_pool_size':len(pool),'development_cases':15,'inference_calls_before_freeze':0,'implementation_must_be_committed_before_inference':True})
    print('New dev-only protocol frozen:',h,'; genuine donor initial errors:',len(pool))


if __name__=='__main__':main()
