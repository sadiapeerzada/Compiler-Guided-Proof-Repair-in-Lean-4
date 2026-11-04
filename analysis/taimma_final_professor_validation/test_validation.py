"""Offline regression checks on real frozen evidence; no invented proof examples."""
import csv
import hashlib
import importlib.util
import json
import random
import re
import subprocess
import unittest
from collections import defaultdict
from pathlib import Path

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('validation',HERE/'validate.py')
v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)

class ValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.results=json.loads((HERE/'verification_results.json').read_text())
        cls.tokens=list(csv.DictReader((HERE/'TOKEN_MATCHING_VERIFICATION.csv').open()))
        cls.rows=v.csvrows('research/study2-v7/test/outcomes.csv')
    def test_first_repair_matching_uses_actual_C(self):
        first=[r for r in self.tokens if r['step']=='1']
        self.assertEqual(len(first),129)
        self.assertEqual(sum(r['study']=='V7' for r in first),68)
        self.assertEqual(sum(r['study']=='V8' for r in first),61)
        for r in first:
            self.assertEqual(r['target_on_E_history'],r['actual_C_tokens'])
            self.assertLessEqual(abs(int(r['delta_E_actual_C'])),1)
            self.assertEqual(r['same_predecessor_as_C'],'True')
    def test_later_history_is_not_silently_matched(self):
        later=[r for r in self.tokens if r['step']!='1']
        self.assertTrue(any(r['same_predecessor_as_C']=='False' for r in later))
        self.assertTrue(any(r['actual_C_tokens']=='' for r in later))
        self.assertTrue(any(r['delta_E_actual_C'] and abs(int(r['delta_E_actual_C']))>3 for r in later))
        for r in self.tokens:
            self.assertEqual(int(r['actual_E_tokens'])-int(r['target_on_E_history']),int(r['delta_E_target']))
            self.assertEqual(r['matched_within_3'],str(abs(int(r['delta_E_target']))<=3))
    def test_independent_cluster_reconstruction(self):
        prior=v.load('analysis/taimma_20261104/results/results.json')['V7']['paired'][0]
        self.assertEqual(v.independent_cluster_interval(self.rows,'B_neutral','id'),prior['theorem_CI'])
        self.assertEqual(v.independent_cluster_interval(self.rows,'B_neutral','family'),prior['family_CI'])
    def test_family_resample_retains_unequal_sizes(self):
        groups=defaultdict(list)
        for r in self.rows:groups[r['family']].append(int(r['C_real']=='True')-int(r['B_neutral']=='True'))
        units=list(groups.values());self.assertEqual(len(units),8)
        self.assertGreater(len({len(x) for x in units}),1)
        rng=random.Random(0);chosen=[units[rng.randrange(len(units))] for _ in units]
        expected=sum(sum(g) for g in chosen)/sum(len(g) for g in chosen)
        actual=v.independent_cluster_interval(self.rows,'B_neutral','family',seed=0,replicates=1)
        self.assertEqual(actual,[expected,expected])
        self.assertNotEqual(expected,sum(sum(g)/len(g) for g in chosen)/len(chosen))
    def test_missingness_and_initial_successes(self):
        s=self.results['statistics']['Study1']
        self.assertEqual(s['complete_pairs'],58)
        self.assertEqual(s['counts']['C'],{'observed':58,'verified':1})
        self.assertEqual(s['missingness_bounds'],[0,2/60])
        for label in ('V7','V8'):
            self.assertEqual(self.results['statistics'][label]['theorem_types'],24)
        self.assertEqual(self.results['failure']['studies']['V8']['budget_curves']['C_real'],[11]*4)
    def test_frozen_checksum_rejects_modified_bytes(self):
        old=v.module('old_analysis','analysis/taimma_20261104/analyze.py')
        raw=(v.ROOT/'research/study2-v7/test/outcomes.csv').read_bytes()
        digest='e766a98ae53830e748da273aaace3ff958e15d53dd72cd92387f25928a3cc72a'
        old.checked(raw,digest)
        with self.assertRaises(ValueError):old.checked(raw+b' ',digest)
    def test_certificates_bind_checked_source_and_allowed_axioms(self):
        log=json.loads((HERE/'lean_certificate_check.json').read_text())
        self.assertEqual(log['status'],'passed')
        self.assertEqual(log['exit_code'],0)
        self.assertEqual(log['certificate_sha256'],hashlib.sha256((HERE/'OverlapCertificates.lean').read_bytes()).hexdigest())
        self.assertEqual(log['stdout'].count("'ProfessorOverlapAudit."),7)
        for deps in re.findall(r'depends on axioms: \[([^]]*)\]',log['stdout']):
            self.assertLessEqual(set(x.strip() for x in deps.split(',')),{'propext','Classical.choice','Quot.sound'})
    def test_benchmark_scope_and_relationships(self):
        b=self.results['benchmark']
        self.assertEqual(b['statements_checked'],36)
        self.assertEqual(b['normalized_text_pairs'],[])
        self.assertIn(['bridge_d06','bridge_t12'],b['alpha_pairs'])
        self.assertEqual([s['n'] for s in b['scopes']],[72,66,63,60])
        self.assertTrue(all([s[a] for a in ('B','C','D')]==[5,10,9] for s in b['scopes']))
    def test_provenance_counts_and_read_only_scope(self):
        p=self.results['provenance']
        self.assertEqual(p['archive_members_verified'],4736)
        self.assertEqual(p['frozen_lock_entries'],40)
        self.assertEqual((p['privacy_warning_records'],p['privacy_path_occurrences']),(1220,22882))
        self.assertTrue(p['privacy_manual_review_required'])
        self.assertTrue(all(x['status']=='matches frozen plan' for x in p['v7_source_files']))
        changed=subprocess.check_output(['git','diff','--name-only',v.BASE,'--','research/','publication/','paper/','submission_20261103/','*.tex','*.bib','*.pdf'],cwd=v.ROOT,text=True)
        self.assertEqual(changed,'')
    def test_raw_controls_and_authentic_cases(self):
        verified=v.load('publication/evidence/redacted_runs/heldout/2027/lib_a_exp_add/B1/verification.json')
        manifest=v.load('publication/evidence/redacted_runs/heldout/2027/lib_a_exp_add/manifest.json')
        candidate=manifest['conditions']['B']['attempts'][0]['candidate']
        v.recorded_acceptance(verified,candidate)
        with self.assertRaises(ValueError):v.recorded_acceptance({**verified,'axiom_dependencies':None},candidate)

        for label,repairs in [('V7',1006),('V8',910)]:
            c=self.results['controls']['studies'][label]['checks']
            self.assertEqual(c['raw_calls_verified'],repairs)
            self.assertEqual(c['raw_initial_calls_verified'],72)
        self.assertEqual(self.results['study1_controls']['checks'],{'shared_initial_evaluations':60,'completed_B_repairs':178,'completed_C_repairs':172})
        cases=self.results['failure']['cases']
        self.assertEqual({c['id'] for c in cases},{'lib_a_exp_add','div_008','bridge_t16'})
        self.assertTrue(all(c['candidate_and_diagnostic_bindings']=='passed' for c in cases))

if __name__=='__main__':unittest.main()
