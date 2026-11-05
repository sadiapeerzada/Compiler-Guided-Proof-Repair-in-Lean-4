import sys
from pathlib import Path
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from overlap import fingerprint,transitivity_template
from header_parser import NativeHeaderParser
from native_parser import ParseError

def test_builtin_type_alias_alpha_exposure():
    assert fingerprint('theorem one (x : Int) : x = x')==fingerprint('theorem two (z : ℤ) : z = z')
    assert fingerprint('theorem one (x : Nat) : x = x')!=fingerprint('theorem two (z : ℤ) : z = z')

def test_transitivity_is_known_exposed_family():
    assert transitivity_template('theorem t (a b c : Int) (ha : a ≤ b) (hb : b ≤ c) : a ≤ c')
    assert not transitivity_template('theorem t (a b : Int) : a + b = b + a')

def test_reference_repair_preserves_fixed_declaration(monkeypatch,tmp_path):
    parser=object.__new__(NativeHeaderParser)
    def split(source,name,folder):
        # Isolated synthetic framing fixture; no source or mathematical proof is admitted.
        if source.startswith('theorem altered'):return 'theorem altered : True','by trivial'
        return 'theorem fixture : True','by trivial'
    monkeypatch.setattr(parser,'split',split)
    c=dict(id='fixture',expected_lean_statement='theorem fixture : True')
    assert parser.repair(b'```plaintext\nby trivial\n```',c,20,'stop',tmp_path)=='theorem fixture : True := by trivial'
    with pytest.raises(ParseError,match='target_changed'):parser.repair(b'theorem altered : True := by trivial',c,20,'stop',tmp_path)
