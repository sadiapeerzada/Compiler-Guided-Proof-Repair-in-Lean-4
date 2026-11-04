"""Synthetic fixtures only; temporary outputs are never experimental evidence."""
import copy
import hashlib
import json
import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path
from unittest.mock import patch

HERE=Path(__file__).resolve().parents[1];sys.path.insert(0,str(HERE))
from common import normalize,content_hash,text_hash,dump,read,ensure
from matching import matched_conditions,diagnostic_payload,donor_order,planned_orders
from checkpoint import RunStore
from dataset_tools import partition,screen,cohort_flags

from isolated_repair_runner import run_core,analyze
from isolated_repair_validation import gate,relative,check_source_lock
from backend import LocalBackend

class FixtureTokenizer:
    def count(self,prompt):return len(prompt.split())+5  # synthetic tokenizer, not model-token evidence

class FixtureBackend:
    tokenizer=FixtureTokenizer()
    def __init__(self):self.calls=[]
    def generate(self,prompt,seed,context,folder):
        self.calls.append((prompt,seed,context))
        target=prompt.split('```lean\n')[1].split('\n```')[0]
        repair='Previous candidate:' in prompt
        candidate=target+(' := by rfl' if repair else ' := by exact bad_initial')
        return dict(content='```lean\n'+candidate+'\n```',metadata=dict(prompt_tokens=self.tokenizer.count(prompt),completion_tokens=12,model='unit-model',snapshot_revision='unit-revision',base_seed=seed,prompt_sha256=text_hash(prompt),latency_seconds=.001,unit_test_only=True))

def fixture_verify(candidate,target,key):
    bad='bad_initial' in candidate
    return dict(success=not bad,candidate_sha256=text_hash(candidate),failure_kind='compiler_error' if bad else None,errors=['synthetic unknown identifier'] if bad else [],diagnostics=[dict(severity='error',kind='unit_fixture',data='synthetic error for '+target,pos={'line':1,'column':1})] if bad else [],axiom_dependencies=[] if not bad else None,exit_code=1 if bad else 0,elapsed_seconds=.001,unit_test_only=True)

def limits(total=10):return dict(max_total_calls=total,max_initial_calls=total,max_repair_calls=total,max_input_tokens=4096,max_output_tokens=1200,max_runtime_seconds=100)

def fixture_permit():
    records=[dict(id='fixture_'+str(i),family='fixture_family_'+str(i),expected_lean_statement='theorem fixture_'+str(i)+' (n : Nat) : n = n',reference_proof='HIDDEN_REFERENCE_SENTINEL') for i in range(2)]
    p=dict(model=dict(revision='unit-revision',model_id='unit-model'),seeds=[2037],order_seed=0,forbidden_donor_pairs=[],budget=dict(max_total_calls=8,max_initial_calls=2,max_repair_calls=6,input_tokens_per_call=4096,output_tokens_per_call=1200),statistics=dict(replicates=20,bootstrap_seed=2037001))
    return dict(phase='development',protocol=p,records=records,protocol_sha256='unit-protocol',source_lock_sha256='unit-lock',authorization=dict(unit_test_only=True,resource_limits=dict(max_calls=8,max_runtime_seconds=100)),manifest=dict(development=dict(sha256='unit-data')))

class ConfirmatoryTests(unittest.TestCase):
    def test_identical_predecessor_and_exact_input_budget(self):
        permit=fixture_permit();row=permit['records'][0];other=permit['records'][1]
        a=row['expected_lean_statement']+' := by exact bad_initial';b=other['expected_lean_statement']+' := by exact bad_initial'
        match=matched_conditions(row,a,fixture_verify(a,row['expected_lean_statement'],'a'),fixture_verify(b,other['expected_lean_statement'],'b'),b,FixtureTokenizer(),4096)
        self.assertTrue(match['valid'])
        self.assertEqual({v['prompt_tokens'] for v in match['conditions'].values()},{4096})
        for value in match['conditions'].values():self.assertIn(a,value['prompt']);self.assertFalse(value['truncated'])
    def test_diagnostic_candidate_binding_and_identical_donor_rejection(self):
        candidate='synthetic-candidate';record=fixture_verify(candidate,'synthetic-target','k');record['success']=False;record['failure_kind']='compiler_error';record['diagnostics']=[dict(severity='error',kind='fixture',data='message',pos={})]
        self.assertIsNotNone(diagnostic_payload(record,candidate))
        with self.assertRaises(ValueError):diagnostic_payload(record,candidate+'changed')
        match=matched_conditions({'expected_lean_statement':'theorem fixture : True'},candidate,record,record,candidate,FixtureTokenizer(),4096)
        self.assertFalse(match['valid'])
    def test_family_and_explicit_donor_exclusion(self):
        rows=[dict(id='a',family='one'),dict(id='b',family='one'),dict(id='c',family='two'),dict(id='d',family='three')]
        self.assertEqual(donor_order(rows[0],rows,2037,[['a','d']]),['c'])
    def test_matching_invalidation_does_not_truncate(self):
        p=fixture_permit();a=p['records'][0];b=p['records'][1]
        ca=a['expected_lean_statement']+' := by exact bad_initial';cb=b['expected_lean_statement']+' := by exact bad_initial'
        m=matched_conditions(a,ca,fixture_verify(ca,a['expected_lean_statement'],'a'),fixture_verify(cb,b['expected_lean_statement'],'b'),cb,FixtureTokenizer(),4)
        self.assertFalse(m['valid']);self.assertTrue(all(not x['truncated'] for x in m['conditions'].values()))
    def test_source_policy_and_no_gate_inference(self):
        class Bomb:
            def __init__(self,*args,**kwargs):raise AssertionError('Weights must not be initialized')
        with patch('isolated_repair_validation.require_go',side_effect=ValueError('NO_GO')):
            with self.assertRaises(ValueError):LocalBackend(HERE/'execution_bundle.json','test')
        self.assertEqual(gate(HERE/'execution_bundle.json','test')['status'],'NO_GO')
    def test_deterministic_whole_family_split(self):
        rows=[dict(id=str(i),family=str(i//2)) for i in range(10)]
        a=partition(rows,development_target=2,test_target=4);b=partition(list(reversed(rows)),development_target=2,test_target=4)
        self.assertEqual(a,b)
        self.assertFalse({r['family'] for r in a['development']}&{r['family'] for r in a['test']})
    def test_config_lock_detects_mutation(self):
        with tempfile.TemporaryDirectory() as t:
            lock=Path(t)/'lock.json';dump(lock,dict(files={'research/confirmatory-study/common.py':'wrong'}))
            with self.assertRaises(ValueError):check_source_lock(lock)
    def test_historical_statement_quarantined(self):
        row=dict(id='fresh-looking-id',nl_statement='For all n, n=n.',expected_lean_statement='theorem renamed (x y : Nat) : (x+y)^2=x^2+2*x*y+y^2',reference_proof='not an approved proof',family='new_label',source_url='fixture',license='fixture',library_dependencies=[])
        report=screen(row)
        self.assertTrue(report['quarantine']);self.assertIn('historical_statement_overlap',report['automated_flags'])
    def test_no_test_file_opened_during_calibration_gate(self):
        calls=[]
        from isolated_repair_validation import read as original
        def track(path):calls.append(str(path));return original(path)
        with patch('isolated_repair_validation.read',side_effect=track):result=gate(HERE/'execution_bundle.json','development')
        self.assertEqual(result['status'],'NO_GO')
        self.assertFalse(any(p.endswith('test_candidates.json') for p in calls))
        with self.assertRaises(ValueError):relative(HERE,'../outside.json')
    def test_counterbalanced_planned_order(self):
        rows=[dict(id=str(i)) for i in range(12)]
        orders=planned_orders(rows,[2037],7)
        self.assertEqual(set(Counter(tuple(v) for v in orders.values()).values()),{2})
    def test_resume_never_repeats_interrupted_generation(self):
        with tempfile.TemporaryDirectory() as t:
            store=RunStore(Path(t),{'fixture':1},limits());calls=[]
            def failed(*a):calls.append(1);raise RuntimeError('synthetic interruption')
            a,_=store.call_once('key','text',6,20,'initial',failed)
            b,_=store.call_once('key','text',6,20,'initial',failed)
            self.assertEqual(len(calls),1);self.assertEqual(a['status'],b['status']);self.assertEqual(len(store.events()),1)
            with self.assertRaises(ValueError):store.call_once('key','changed',6,20,'initial',failed)
    def test_orphan_reservation_never_regenerates(self):
        with tempfile.TemporaryDirectory() as t:
            store=RunStore(Path(t),{'fixture':1},limits())
            intent=dict(key='k',prompt_sha256=text_hash('text'),prompt_tokens_reserved=6,output_tokens_reserved=20,kind='initial',binding=store.binding)
            with store.lock():store.append(dict(key='k',kind='initial',run_binding=content_hash(store.binding),intent_sha256=content_hash(intent),input_reserved=6,output_reserved=20))
            result,_=store.call_once('k','text',6,20,'initial',lambda *a:self.fail('No replay'))
            self.assertEqual(result['status'],'unknown_consumed_intent')
    def test_call_caps_and_unknown_costs(self):
        with tempfile.TemporaryDirectory() as t:
            store=RunStore(Path(t),{},limits(total=1))
            fn=lambda *a:dict(content='fixture',metadata=dict(prompt_tokens=6,completion_tokens=2))
            result,_=store.call_once('a','text',6,20,'initial',fn);self.assertEqual(result['status'],'completed')
            with self.assertRaises(ValueError):store.call_once('b','text',6,20,'initial',fn)
            self.assertEqual(store.events()[0]['output_reserved'],20)
    def test_nonconforming_response_preserved_not_success(self):
        with tempfile.TemporaryDirectory() as t:
            store=RunStore(Path(t),{},limits())
            result,folder=store.call_once('a','text',6,20,'initial',lambda *a:dict(content='fixture evidence',metadata=dict(prompt_tokens=7,completion_tokens=2)))
            self.assertEqual(result['status'],'unknown_consumed_intent');self.assertEqual(read(folder/'nonconforming_generation.json')['content'],'fixture evidence')
    def test_paired_completeness_and_known_synthetic_effect(self):
        rows=[dict(id=str(i//2),family=str(i//2),seed=i%2,phase='development',model_revision='fixture',initial_success=False,C=True,D=False,E=True,initial_error='fixture') for i in range(4)]
        result=analyze(rows,replicates=50,expected_keys=[(r['id'],r['seed']) for r in rows])
        self.assertEqual(result['comparisons'][0]['difference'],1);self.assertEqual(result['comparisons'][0]['theorem_95'],[1,1])
        with self.assertRaises(ValueError):analyze(rows[:-1],replicates=50,expected_keys=[(r['id'],r['seed']) for r in rows])
        with self.assertRaises(ValueError):analyze(rows+[rows[0]],replicates=50)
    def test_missing_is_unknown_and_not_equivalence(self):
        rows=[dict(id='a',family='a',seed=1,phase='test',model_revision='fixture',initial_success=False,C=None,D=False,E=None)]
        result=analyze(rows,replicates=10)
        self.assertEqual(result['comparisons'][0]['missingness_identification_bounds'],[0,1]);self.assertIsNone(result['comparisons'][0]['theorem_95'])
        self.assertEqual(analyze([])['status'],'NO_EXECUTED_DATA')
    def test_whole_core_synthetic_resume_and_reference_hidden(self):
        with tempfile.TemporaryDirectory() as t:
            permit=fixture_permit();backend=FixtureBackend();store=run_core(permit,backend,fixture_verify,Path(t))
            self.assertEqual(len(backend.calls),8)
            self.assertTrue(all('HIDDEN_REFERENCE_SENTINEL' not in c[0] for c in backend.calls))
            again=FixtureBackend();run_core(permit,again,lambda *a:self.fail('Durable verification must not replay'),Path(t))
            self.assertEqual(len(again.calls),0)
            exports=list((store.root/'exports').glob('*/rows.json'));self.assertEqual(len(exports),1)
            rows=read(exports[0]);self.assertTrue(all(r['C'] is True for r in rows));self.assertTrue(all(r['initial_success'] is False for r in rows))
    def test_initial_interruption_stops_and_resume_preserves_unknown(self):
        with tempfile.TemporaryDirectory() as t:
            permit=fixture_permit()
            class Failed(FixtureBackend):
                def generate(self,*args):self.calls.append(args);raise RuntimeError('synthetic device unavailable')
            failed=Failed()
            with self.assertRaises(ValueError):run_core(permit,failed,fixture_verify,Path(t))
            self.assertEqual(len(failed.calls),1)
            resumed=FixtureBackend();store=run_core(permit,resumed,fixture_verify,Path(t))
            self.assertEqual(len(resumed.calls),1)
            versions=list((store.root/'exports').glob('*/rows.json'))
            self.assertTrue(any(any(r['initial_success'] is None for r in read(v)) for v in versions))
    def test_real_offline_checks_are_not_mock_inference_results(self):
        log=read(HERE/'offline_integration_results.json')
        self.assertEqual(log['inference_calls'],0)
        self.assertEqual(log['lean_status'],'passed')
        self.assertTrue(log['lean_cases']['valid']['success'])
        self.assertFalse(log['lean_cases']['placeholder']['success'])
        self.assertFalse(log['lean_cases']['weakened']['success'])
        self.assertEqual(log['rendered_counts'],{'C':4096,'D':4096,'E':4096})
    def test_authorized_development_path_scope_with_mocked_human_checks(self):
        # Positive gate-path fixture mocks human authentication and historical screening;
        # it is NEVER passed to a model backend or treated as a genuine approval.
        from common import sha
        from dataset_tools import subject_hash
        from isolated_repair_validation import read as original_read
        with tempfile.TemporaryDirectory() as t:
            base=Path(t);row=dict(id='unit_dev',family='unit_family_dev',nl_statement='unit fixture',expected_lean_statement='theorem unit_dev (n : Nat) : n = n',reference_proof='theorem unit_dev (n : Nat) : n = n := by rfl',source_url='unit-fixture',license='unit-fixture',library_dependencies=[])
            proof=dict(success=True,exit_code=0,reference_sha256=text_hash(row['reference_proof']),target_sha256=text_hash(row['expected_lean_statement']),axiom_dependencies=[],verifier_implementation_sha256=sha(HERE.parents[1]/'src/verify.py'),adapter_sha256=sha(HERE/'lean_adapter.py'),unit_test_only=True)
            dump(base/'proof.json',proof);row['reference_verification']=dict(path='proof.json',sha256=sha(base/'proof.json'));dump(base/'development.json',[row]);(base/'sealed_test.json').write_text('UNREADABLE SEALED UNIT FIXTURE')
            protocol=read(HERE/'isolated_repair_protocol.json');protocol['status']='FROZEN_FOR_EXECUTION';protocol['sample_size']={'development':1,'test':1};dump(base/'protocol.json',protocol)
            manifest=dict(development=dict(path='development.json',sha256=sha(base/'development.json'),count=1,families=[row['family']],subject_hashes={row['id']:subject_hash(row)},statement_fingerprints={row['id']:content_hash(normalize(row['expected_lean_statement'],True))}),test=dict(path='sealed_test.json',sha256=sha(base/'sealed_test.json'),count=1,families=['opaque_test_family'],subject_hashes={'opaque_test_id':'opaque'},statement_fingerprints={'opaque_test_id':'opaque_test_fingerprint'}));dump(base/'manifest.json',manifest)
            review=dict(subject_sha256=subject_hash(row),**{k:'APPROVED' for k in ['mathematics','semantic_fidelity','family_independence','source_license','historical_overlap_clearance']})
            dump(base/'benchmark.json',dict(dataset_manifest_sha256=sha(base/'manifest.json'),subjects={row['id']:review},unit_test_only=True));dump(base/'lock.json',{'unit_test_only':True})
            bindings=dict(protocol_sha256=sha(base/'protocol.json'),dataset_manifest_sha256=sha(base/'manifest.json'),source_lock_sha256=sha(base/'lock.json'),benchmark_approval_sha256=sha(base/'benchmark.json'))
            dump(base/'freeze.json',dict(**bindings,no_test_outcomes_observed=True,test_statements_not_used_for_calibration_or_tuning=True,unit_test_only=True))
            dump(base/'log.json',read(HERE/'offline_integration_results.json'));dump(base/'evidence.json',dict(status='REAL_LEAN_INTEGRATION_PASSED',source_lock_sha256=sha(base/'lock.json'),log_artifact=dict(path='log.json',sha256=sha(base/'log.json'))))
            auth=dict(**bindings,phase='development',freeze_sha256=sha(base/'freeze.json'),verification_evidence_sha256=sha(base/'evidence.json'),model_revision=protocol['model']['revision'],resource_limits=dict(max_calls=12,max_runtime_seconds=100),unit_test_only=True);dump(base/'authorization.json',auth)
            bundle=dict(protocol='protocol.json',dataset_manifest='manifest.json',source_lock='lock.json',benchmark_approval='benchmark.json',authorization='authorization.json',freeze='freeze.json',verification_evidence='evidence.json');dump(base/'bundle.json',bundle)
            paths=[]
            def tracked(path):
                paths.append(str(path))
                if Path(path).name=='sealed_test.json':self.fail('Calibration read test content')
                return original_read(path)
            with patch('isolated_repair_validation.human'),patch('isolated_repair_validation.check_source_lock'),patch('isolated_repair_validation.screen',return_value={'quarantine':False}),patch('isolated_repair_validation.read',side_effect=tracked):
                self.assertEqual(gate(base/'bundle.json','development')['status'],'GO')
                auth['protocol_sha256']='tampered';dump(base/'authorization.json',auth)
                self.assertEqual(gate(base/'bundle.json','development')['status'],'NO_GO')
            self.assertFalse(any(p.endswith('sealed_test.json') for p in paths))
            self.assertEqual(gate(base/'bundle.json','development')['status'],'NO_GO')
    def test_damaged_ledger_fails_closed(self):
        with tempfile.TemporaryDirectory() as t:
            store=RunStore(Path(t),{},limits());(Path(t)/'budget.jsonl').write_text('{incomplete crash record')
            with self.assertRaises(ValueError):store.call_once('k','text',6,20,'initial',lambda *a:self.fail('Damaged ledger cannot grant calls'))
    def test_new_cohort_alpha_duplicates_are_not_independent_items(self):
        rows=[dict(id='one',expected_lean_statement='theorem one (a : Nat) : a=a'),dict(id='two',expected_lean_statement='theorem two (b : Nat) : b=b')]
        self.assertTrue(all('prospective_alpha_duplicate' in f for f in cohort_flags(rows)))
    def test_no_real_research_rows_manufactured(self):
        self.assertEqual(len(list(__import__('csv').DictReader((HERE/'isolated_repair_results.csv').open()))),0)
        self.assertEqual(read(HERE/'prospective_dataset_manifest.json')['test']['count'],0)

if __name__=='__main__':unittest.main()
