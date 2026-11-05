import sys,json
from pathlib import Path
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from review_protocol import review_prompt,parse_review,CHECKS
from study_common import authorize

def valid():
    return dict(decision='ACCEPT',explanation='Synthetic parser fixture only',concerns=[],unresolved_critical=[],confidence=.8,semantic_checks={k:'Synthetic check, not real approval' for k in CHECKS},historical_relationship='Fixture',family_assessment='Fixture')

def record(value):return dict(status='completed',content=json.dumps(value),metadata={'finish_reason':'stop'})

def test_parser_valid_fixture_is_not_production_evidence():
    assert parse_review(record(valid()))['decision']=='ACCEPT'

@pytest.mark.parametrize('mutation',[lambda r:r.update(concerns=['unresolved issue']),lambda r:r.update(unresolved_critical=['unknown quantifier']),lambda r:r.update(confidence=2),lambda r:r['semantic_checks'].pop('domains'),lambda r:r.update(explanation='')])
def test_incomplete_or_contradictory_acceptance_rejected(mutation):
    r=valid();mutation(r)
    with pytest.raises((ValueError,KeyError)):parse_review(record(r))

def test_truncated_review_not_accepted():
    r=record(valid());r['metadata']['finish_reason']='length'
    with pytest.raises(ValueError):parse_review(r)

def test_prompt_blinding(monkeypatch):
    import review_protocol
    monkeypatch.setattr(review_protocol,'neighbors',lambda c:[])
    c=dict(id='fixture',nl_statement='English',expected_lean_statement='theorem fixture : True',category='fixture',family='fixture',reference_proof='SECRET_REFERENCE',generation_provenance='SECRET_GENERATION',other_review='SECRET_REVIEW')
    p=review_prompt(c)
    assert all(s not in p for s in ('SECRET_REFERENCE','SECRET_GENERATION','SECRET_REVIEW'))

def test_no_confirmatory_authorization():
    for phase in ('confirmatory_generation','test','confirmatory_initial','confirmatory_repairs'):
        with pytest.raises(ValueError,match='NO_GO_RESOURCES'):authorize(phase)
