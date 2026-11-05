import sys,hashlib
from pathlib import Path
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import parser_v3 as p

RAW=b'STATEMENT: A parser fixture.\nLEAN:\n```lean\ntheorem fixture : True := by trivial\n```\nFAMILY: fixture'

def test_three_sections_and_original_hash(monkeypatch):
    monkeypatch.setattr(p,'split_theorem',lambda source,name,evidence:('theorem fixture : True','by trivial'))
    result=p.parse(RAW,expected_id='fixture',category='synthetic_test_only',tokens=50)
    assert result['raw_response_sha256']==hashlib.sha256(RAW).hexdigest()
    assert result['reference_proof']=='theorem fixture : True := by trivial'

@pytest.mark.parametrize('raw',[RAW.replace(b'STATEMENT:',b'NO_ENGLISH:'),RAW.replace(b'FAMILY: fixture',b''),RAW+b'\nFAMILY: duplicate',RAW.replace(b'```\nFAMILY',b'FAMILY'),b'prose\n'+RAW])
def test_missing_ambiguous_or_extra_content_rejected(raw):
    with pytest.raises(p.ParseError):p.sections(raw,100)

def test_allocation_utf8_and_normalization():
    for raw,tokens,finish in [(RAW,1201,'stop'),(RAW,1200,'length'),(RAW+b'\xff',100,'stop'),(RAW.replace(b'A parser','e\u0301'.encode()),100,'stop')]:
        with pytest.raises(p.ParseError):p.sections(raw,tokens,finish)

def test_literal_json_escapes_not_interpreted():
    assert '\\(n\\)' in p.sections(RAW.replace(b'A parser fixture.',b'For \\(n\\).'),100)['STATEMENT']

@pytest.mark.parametrize('label',[b'**STATEMENT:**',b'**STATEMENT**:',b'### STATEMENT:',b'STATEMENT\n'])
def test_documented_harmless_header_variants(label):
    assert p.sections(RAW.replace(b'STATEMENT:',label),100)['STATEMENT']=='A parser fixture.'

def test_headers_in_Lean_fence_are_not_section_boundaries():
    source=RAW.replace(b'by trivial',b'by\n  /-\nFAMILY: inside comment\n-/\n  trivial')
    assert 'FAMILY: inside comment' in p.sections(source,100)['LEAN']

def test_duplicate_id_and_target_preserving_repair(monkeypatch):
    with pytest.raises(p.ParseError,match='duplicate'):p.parse(RAW,expected_id='fixture',category='test',tokens=50,seen_ids={'fixture'})
    candidate={'id':'fixture','expected_lean_statement':'theorem fixture : True'}
    monkeypatch.setattr(p,'split_theorem',lambda source,name,evidence:('theorem fixture : True','by trivial'))
    assert p.repair_source(b'by trivial',candidate=candidate,tokens=3)=='theorem fixture : True := by trivial'
    with pytest.raises(p.ParseError):p.repair_source(b'theorem altered : True := by trivial',candidate=candidate,tokens=10)
