"""Deterministic donor selection reads only original shared-initial diagnostics."""
import hashlib
import json
from pathlib import Path
from analysis.common import ROOT,STUDY,read,category
from .filename_normalization import normalize_verification,feedback,assert_private_free


def pool_from_originals(tokenizer):
    pool=[]
    for row in read(STUDY/'test.json'):
        # Deliberately never reads trajectory manifests, repairs, or success outcomes.
        v=read(STUDY/'final_runs/heldout/2027'/row['id']/'initial/verification.json')
        if v['success']:continue
        normalized=normalize_verification(v,ROOT);payload=feedback(normalized)
        if payload is None:continue
        pool.append({'id':row['id'],'family':row['study_eligibility']['family'],'category':category(normalized),
                     'payload':payload,'payload_tokens':len(tokenizer.encode(payload,add_special_tokens=False)),
                     'payload_sha256':hashlib.sha256(payload.encode()).hexdigest(),
                     'source':'data/final_study/v1/final_runs/heldout/2027/'+row['id']+'/initial/verification.json'})
    assert_private_free(pool)
    return pool


def select_donor(pool,problem_id,family,current_category,target_tokens):
    eligible=[p for p in pool if p['id']!=problem_id and p['family']!=family]
    if not eligible:raise ValueError('No genuine donor from a different problem/family')
    matching=[p for p in eligible if p['category']==current_category];candidates=matching or eligible
    def tie(p):return hashlib.sha256((p['id']+':'+p['payload_sha256']).encode()).hexdigest()
    winner=min(candidates,key=lambda p:(abs(p['payload_tokens']-target_tokens),tie(p)))
    return winner,{'donor_id':winner['id'],'donor_family':winner['family'],'donor_category':winner['category'],
                   'target_category':current_category,'target_diagnostic_tokens':target_tokens,'donor_diagnostic_tokens':winner['payload_tokens'],
                   'token_length_difference':abs(winner['payload_tokens']-target_tokens),'category_fallback':not bool(matching),
                   'donor_payload_sha256':winner['payload_sha256'],'tie_break_sha256':tie(winner)}
