"""Offline policy checks; no fabricated production approvals or inference."""
import json
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ai_common import HERE, ROOT, read, sha
from resource_gate import authorize
from ai_gate import check, source_check
from test_vault import load_test
from prompts import reviewer_prompt

def test_frozen_sources_match():
    assert source_check()['pilot_development_only'] is True

def test_explicit_pilot_limits():
    assert authorize('generation')[0]['max_calls'] == 24
    assert sum(authorize(s)[0]['max_calls'] for s in ('reviewer_1','reviewer_2')) == 48
    assert authorize('development')[0]['max_calls'] == 48

def test_test_phase_is_not_authorized():
    assert check('test')['status'] == 'NO_GO_RESOURCES'
    with pytest.raises(ValueError):
        load_test('test')

def test_development_cannot_open_test():
    with patch('test_vault.authorize', side_effect=AssertionError('must reject role first')):
        with pytest.raises(ValueError, match='cannot open'):
            load_test('development')

def test_ai_cannot_authorize_compute():
    record=read(HERE/'resource_authorization.json')
    record['actor_kind']='AI_reviewer'
    with TemporaryDirectory() as directory:
        path=Path(directory)/'synthetic.json'
        path.write_text(json.dumps(record))
        with pytest.raises(ValueError, match='wrong actor'):
            authorize('generation',path)

def test_synthetic_authorization_is_rejected():
    record=read(HERE/'resource_authorization.json'); record['unit_test_only']=True
    with TemporaryDirectory() as directory:
        path=Path(directory)/'synthetic.json'; path.write_text(json.dumps(record))
        with pytest.raises(ValueError, match='Synthetic'):
            authorize('generation',path)

def test_review_prompt_excludes_reference_and_generation_prompt():
    candidate=dict(nl_statement='English theorem',expected_lean_statement='theorem check : True',domain='logic',category='test',family='family',reference_proof='SECRET_REFERENCE',generation_provenance={'prompt':'SECRET_GENERATION'})
    prompt=reviewer_prompt(candidate,[])
    assert 'SECRET_REFERENCE' not in prompt and 'SECRET_GENERATION' not in prompt
    assert 'English theorem' in prompt and 'theorem check' in prompt

def test_reviewers_are_different_families_and_checkpoints():
    models=read(HERE/'ai_protocol_v1.json')['models']
    assert models['reviewer_1']['family'] != models['reviewer_2']['family']
    assert models['reviewer_1']['revision'] != models['reviewer_2']['revision']

def test_historical_human_protocol_is_unchanged():
    baseline=read(HERE/'baseline_hashes.json')
    paths={p:h for p,h in baseline['files'].items() if p.startswith('research/confirmatory-study/')}
    assert paths
    assert all(sha(ROOT/p)==h for p,h in paths.items())
