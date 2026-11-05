import sys,json
from pathlib import Path
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from fresh_review import parse_review,POSITIVE,NEGATIVE

def fixture():
    return dict(decision='ACCEPT',explanation='Synthetic fixture only, never production evidence',concerns=[],unresolved_critical=[],confidence=.9,semantic_checks={k:True for k in POSITIVE}|{k:False for k in NEGATIVE},historical_relationship='NO_DETECTED_RELATION',historical_explanation='Fixture',family_assessment='DISTINCT',family_explanation='Fixture')

def record(r):return dict(status='completed',content=json.dumps(r),metadata={'finish_reason':'stop'})

def test_explicit_boolean_contract():assert parse_review(record(fixture()))['decision']=='ACCEPT'

@pytest.mark.parametrize('mutate',[lambda r:r['semantic_checks'].update(quantifiers=['all']),lambda r:r['semantic_checks'].update(ambiguity=True),lambda r:r.update(historical_relationship='POSSIBLE_RELATION'),lambda r:r.update(family_assessment='UNCERTAIN'),lambda r:r.update(confidence=.4),lambda r:r.update(concerns=['Unresolved mismatch'])])
def test_uncertain_or_contradictory_accept_rejected(mutate):
    r=fixture();mutate(r)
    with pytest.raises(ValueError):parse_review(record(r))
