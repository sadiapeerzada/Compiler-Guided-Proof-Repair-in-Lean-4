import copy
import importlib.util
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('evidence',ROOT/'analysis/taimma_20261104/analyze.py')
a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)

class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.rows=a.csvrows((ROOT/'research/study2-v7/test/outcomes.csv').read_bytes())
    def test_denominators(self):
        a.validate(self.rows)
        self.assertEqual(len({r['id'] for r in self.rows}),24)
        self.assertEqual(len({r['family'] for r in self.rows}),8)
    def test_duplicate_missing_and_unknown(self):
        for rows in (self.rows[:-1],self.rows[:-1]+[self.rows[0]]):
            with self.assertRaises(ValueError):a.validate(rows)
        rows=copy.deepcopy(self.rows);rows[0]['C_real']=''
        with self.assertRaises(ValueError):a.validate(rows)
    def test_family_integrity(self):
        rows=copy.deepcopy(self.rows);rows[0]['family']='wrong'
        with self.assertRaises(ValueError):a.validate(rows)
    def test_counts_and_pairs(self):
        self.assertEqual([sum(a.yes(r,arm) for r in self.rows) for arm in a.ARMS],[5,10,9,5,5])
        self.assertEqual(sum(a.yes(r,'C_real') and not a.yes(r,'B_neutral') for r in self.rows),6)
        self.assertEqual(sum(a.yes(r,'B_neutral') and not a.yes(r,'C_real') for r in self.rows),1)
    def test_trace_matching(self):
        base=ROOT/'research/study2-v7/test'
        calls=a.csvrows((base/'calls.csv').read_bytes())
        trans=a.csvrows((base/'transitions.csv').read_bytes())
        with self.assertRaises(ValueError):a.analyze('invalid',self.rows,calls[:-1],trans)
        with self.assertRaises(ValueError):a.analyze('invalid',self.rows,calls+[calls[0]],trans)
        bad=copy.deepcopy(trans);bad[0]['id']='unknown'
        with self.assertRaises(ValueError):a.analyze('invalid',self.rows,calls,bad)
    def test_audit_targets(self):
        self.assertEqual(sum(a.yes(r,'C_real') and not a.yes(r,'D_shuffled') for r in self.rows),4)
        self.assertEqual(sum(a.yes(r,'D_shuffled') and not a.yes(r,'C_real') for r in self.rows),3)
        self.assertEqual([len({r['id'] for r in self.rows if a.yes(r,arm)}) for arm in a.ARMS[:3]],[3,4,7])
    def test_checksum(self):
        a.checked(b'abc','ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad')
        with self.assertRaises(ValueError):a.checked(b'changed','ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad')
    def test_resampling(self):
        for unit in ('id','family'):
            x=a.bootstrap(self.rows,'C_real','B_neutral',unit,rounds=200)
            self.assertEqual(x,a.bootstrap(self.rows,'C_real','B_neutral',unit,rounds=200))
            self.assertEqual(a.bootstrap(self.rows,'C_real','C_real',unit,rounds=200),[0,0])

if __name__=='__main__':unittest.main()
