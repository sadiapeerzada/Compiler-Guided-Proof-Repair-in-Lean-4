"""Read-only regression checks use actual frozen records, never invented proofs."""
import importlib.util
import json
import unittest
from pathlib import Path

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('supplement',HERE/'supplement.py')
s=importlib.util.module_from_spec(spec);spec.loader.exec_module(s)

class SupplementTests(unittest.TestCase):
    def test_all_cases_are_bound_to_candidate_hashes(self):
        cases=json.loads((HERE/'case_excerpts.json').read_text())
        self.assertEqual(len(cases),3)
        for case in cases:
            for step in [case['initial']]+case['steps']:
                self.assertEqual(s.sha(step['candidate'].encode()),step['candidate_sha256'])
        exp=next(c for c in cases if c['id']=='lib_a_exp_add')
        self.assertEqual([v['verified'] for v in exp['steps']],[True,True])
        fail=next(c for c in cases if c['id']=='div_008')
        self.assertFalse(any(v['verified'] for v in fail['steps']))
        discord=next(c for c in cases if c['id']=='bridge_t16')
        self.assertTrue(any(v['verified'] for v in discord['steps'] if v['arm']=='C_real'))
        self.assertFalse(any(v['verified'] for v in discord['steps'] if v['arm'] in ('B_neutral','D_shuffled')))
    def test_source_views_have_complete_grid_and_real_hashes(self):
        views=json.loads((HERE/'sources/v7_trajectory_views.json').read_text())
        keys={(v['trajectory']['seed'],v['trajectory']['id']) for v in views}
        self.assertEqual(len(keys),72)
        self.assertEqual({k[0] for k in keys},{2027,2028,2029})
        for v in views:
            t=v['trajectory']
            for step in [t['initial']]+[step for arm in t['arms'].values() for step in arm['steps']]:
                s.check_candidate(step)
    def test_recorded_resource_totals_and_memory(self):
        resources=s.rows((HERE/'resources.csv').read_bytes())
        self.assertEqual(len(resources),12)
        c=next(r for r in resources if r['study']=='V7' and r['arm']=='C_real')
        self.assertEqual(float(c['generation_elapsed_seconds']),1061.7029009649996)
        self.assertEqual(float(c['compiler_elapsed_seconds']),309.46)
        self.assertEqual(float(c['max_recorded_peak_memory_gb']),4.77981581)
        self.assertEqual(float(c['input_per_new_verified_repair']),8973)
        self.assertTrue(all(r['input_per_new_verified_repair']=='undefined' for r in resources if r['study']=='V8' and r['arm'] in s.ARMS[:4]))
    def test_observation_denominators_and_no_truncation_in_recorded_test(self):
        obs=s.rows((HERE/'repair_observations.csv').read_bytes())
        self.assertEqual(len(obs),1916)
        keys={(r['study'],r['seed'],r['theorem'],r['arm'],r['step']) for r in obs}
        self.assertEqual(len(keys),len(obs))
        self.assertFalse(any(r['payload_truncated']=='True' for r in obs))
        self.assertEqual(sum(r['verified']=='True' for r in obs if r['study']=='V8' and r['arm'] in s.ARMS[:4]),0)
    def test_checksum_rejection(self):
        case=json.loads((HERE/'case_excerpts.json').read_text())[0]['initial']
        with self.assertRaises(ValueError):s.check_candidate({**case,'candidate':case['candidate']+' '})
    def test_redaction_preserves_math(self):
        case=json.loads((HERE/'case_excerpts.json').read_text())[0]['initial']['candidate']
        self.assertEqual(s.clean(case),case)
        # Build a machine path without publishing a real user's name.
        self.assertNotIn('/Users/',s.clean('/Users/'+'example/project/file.lean'))
    def test_report_completeness_and_privacy(self):
        names=['CASE_STUDIES.md','CONTEXT_WINDOW_ANALYSIS.md','RESOURCE_ANALYSIS.md','FAILURE_ANALYSIS.md','INDEPENDENT_BENCHMARK_REVIEW_PACKET.md','RELATED_WORK_COMPARISON.md','FINAL_SCIENTIFIC_AUDIT.md','SUPERVISOR_29_POINT_STATUS.md']
        for name in names:
            text=(HERE/name).read_text();self.assertGreater(len(text),300)
            self.assertNotIn('/Users/',text)
        text=(HERE/'SUPERVISOR_29_POINT_STATUS.md').read_text()
        self.assertEqual(sum(line.startswith('| '+str(n)+' |') for line in text.splitlines() for n in range(1,30)),29)
    def test_raw_source_view_is_deterministic_and_does_not_need_local_files(self):
        views=json.loads((HERE/'sources/v7_trajectory_views.json').read_text())
        self.assertEqual(len({v['original_path'] for v in views}),72)
        self.assertTrue(all(len(v['original_sha256'])==64 for v in views))
        frozen=s.rows((s.ROOT/'research/study2-v7/test/outcomes.csv').read_bytes())
        bykey={(r['seed'],r['id']):r for r in frozen}
        for v in views:
            t=v['trajectory'];r=bykey[str(t['seed']),t['id']]
            for arm in s.ARMS:self.assertEqual(t['arms'][arm]['outcome'],r[arm]=='True')

if __name__=='__main__':unittest.main()
