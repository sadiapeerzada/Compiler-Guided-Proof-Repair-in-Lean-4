import sys
from pathlib import Path
import hashlib
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from parser_v2 import parse_response,ParseError

def sample():
    # Synthetic parser fixture, never a prospective benchmark subject.
    return b'<<<ID>>>\nfixture\n<<<STATEMENT>>>\nFor every n, n equals n.\n<<<TARGET>>>\ntheorem fixture (n : Nat) : n = n\n<<<PROOF>>>\nby rfl\n<<<CATEGORY>>>\narithmetic\n<<<FAMILY>>>\nparser-fixture\n<<<END>>>'

def parse(raw,**kwargs):return parse_response(raw,output_tokens=100,**kwargs)

def test_valid_separation_and_raw_hash():
    raw=sample();r=parse(raw)
    assert ':=' not in r['expected_lean_statement']
    assert r['reference_proof']==r['expected_lean_statement']+' := '+r['proof_block']
    assert r['raw_response_sha256']==hashlib.sha256(raw).hexdigest()

def test_invalid_json_escape_is_literal_statement_text():
    r=parse(sample().replace(b'For every n',b'For \\(n\\)'))
    assert '\\(n\\)' in r['nl_statement']

def test_whole_response_fence_and_field_fence():
    raw=b'```text\n'+sample().replace(b'by rfl',b'```lean\nby rfl\n```')+b'\n```'
    r=parse(raw);assert r['proof_block']=='by rfl'
    assert len(r['format_normalizations'])==2

@pytest.mark.parametrize('old,new',[(b'theorem fixture (n : Nat) : n = n',b''),(b'by rfl',b''),(b'<<<END>>>',b''),(b'theorem fixture (n : Nat) : n = n',b'theorem fixture : True\ntheorem conflict : True'),(b'by rfl',b'theorem replacement : True := by trivial')])
def test_incomplete_or_conflicting_rejected(old,new):
    with pytest.raises(ParseError):parse(sample().replace(old,new))

def test_invalid_utf8_rejected():
    with pytest.raises(ParseError,match='utf8'):parse(sample()+b'\xff')

def test_unicode_not_silently_normalized():
    with pytest.raises(ParseError,match='NFC'):parse(sample().replace(b'arithmetic','e\u0301'.encode()))

def test_duplicate_id_rejected():
    with pytest.raises(ParseError,match='duplicate_identifier'):parse(sample(),seen_ids={'fixture'})

def test_reserved_delimiter_inside_source_rejected():
    with pytest.raises(ParseError):parse(sample().replace(b'by rfl',b'by\n<<<TARGET>>>\nrfl'))

def test_non_reserved_delimiter_text_is_not_deleted():
    assert '-- <<<not-a-field>>>' in parse(sample().replace(b'by rfl',b'by rfl -- <<<not-a-field>>>'))['proof_block']

def test_output_allocation_and_truncation():
    with pytest.raises(ParseError,match='allocation'):parse_response(sample(),output_tokens=1201)
    with pytest.raises(ParseError,match='truncated'):parse(sample(),finish_reason='length')

def test_no_target_proof_repair_or_prose_invention():
    with pytest.raises(ParseError):parse(sample().replace(b': n = n',b': n = n := by rfl'))
    with pytest.raises(ParseError):parse(b'Here is a theorem:\n'+sample())
