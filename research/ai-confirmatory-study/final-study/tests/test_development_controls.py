import sys
from pathlib import Path
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import development_experiment as d
from cde_verifier import CDEVerifier

def test_gate_closed_before_data_freeze(monkeypatch):
    # A missing freeze must fail even if real data later exists in this checkout.
    def missing(_):raise FileNotFoundError('Synthetic missing freeze')
    monkeypatch.setattr(d,'frozen',missing)
    state=d.gate()
    assert state['status']=='NO_GO_FREEZE'

def test_closed_gate_prevents_backend_initialization(monkeypatch):
    monkeypatch.setattr(d,'gate',lambda:dict(status='NO_GO_DATA',reason='synthetic negative fixture'))
    with pytest.raises(ValueError):d.Backend()

def test_model_format_failure_is_not_fake_compiler_diagnostic():
    r=CDEVerifier()('by trivial','theorem fixed : True','synthetic_format_only')
    assert r['success'] is False and r['failure_kind']=='proof_rejected'
    assert r['diagnostics']==[] and r['not_a_compiler_diagnostic'] is True
