import copy
import json
from pathlib import Path
import random
import pytest
from analysis.metrics import levenshtein,normalized_distance,unknown_names,identifier_present,targeted_fix,distinct_errors,completed_repair_pairs,transition_direction
from analysis.common import category
from analysis.statistics import mcnemar,newcombe_paired,identification_bounds,approximate_mde,exact_mde,exact_power,bootstrap_difference


def verification(name='foo',success=False):
    return {'success':success,'failure_kind':None if success else 'compiler_error','diagnostic_state':'available',
            'diagnostics':[] if success else [{'kind':'lean.unknownIdentifier._namedError','severity':'error','data':f'Unknown identifier `{name}`'}],
            'errors':[] if success else [f'Unknown identifier `{name}`']}


def test_unknown_names_use_structured_field_before_data_fallback():
    v=verification();v['diagnostics'][0]['identifier']='explicit_name'
    assert unknown_names(v)=={'explicit_name'}
    assert unknown_names(verification('Real.foo'))=={'Real.foo'}
    v['diagnostics'][0]['severity']='warning';assert unknown_names(v)==set()


def test_name_removal_and_actual_new_unknown_introduction():
    result=targeted_fix('exact foo','exact bar',verification('foo'),verification('bar'))
    assert result['unknown_removed_n']==1 and result['hallucinated_substitution']==1
    result=targeted_fix('exact foo + bar','exact bar',verification('foo'),verification('bar'))
    assert result['unknown_newly_reported_n']==1 and result['unknown_newly_introduced_n']==0
    assert not identifier_present('foobar foo\x27','foo')
    assert identifier_present('Real.foo','foo')


def test_no_invented_zero_for_unavailable_diagnostics():
    v={'success':False,'failure_kind':'proof_rejected','diagnostic_state':'unavailable','diagnostics':None}
    assert distinct_errors(v) is None
    assert targeted_fix('foo','bar',verification('foo'),v)['hallucinated_substitution'] is None


def test_distinct_error_count_ignores_positions_and_warnings():
    v=verification();v['diagnostics']*=2;v['diagnostics'].append({'severity':'warning','kind':'hasSorry','data':'warning'})
    assert distinct_errors(v)==1


def test_frozen_classifier_wrapper_and_transition_order():
    assert category(verification())=='unknown_identifier_or_name'
    v=verification();v['errors']=['unexpected token','Unknown identifier `foo`'];assert category(v)=='syntax_or_parser'
    assert category({'success':False,'failure_kind':'timeout'})=='guard/infra/incomplete'
    assert transition_direction('syntax_or_parser','unknown_identifier_or_name')=='advanced'
    assert transition_direction('tactic_or_unsolved_goal','syntax_or_parser')=='regressed'
    assert transition_direction('other_compiler_error','type_mismatch_or_elaboration')=='unranked'


def test_distance_matches_independent_dynamic_programming():
    def reference(a,b):
        row=list(range(len(b)+1))
        for i,x in enumerate(a,1):
            cur=[i]
            for j,y in enumerate(b,1):cur.append(min(cur[-1]+1,row[j]+1,row[j-1]+(x!=y)))
            row=cur
        return row[-1]
    rng=random.Random(5)
    for _ in range(300):
        a=''.join(rng.choices('aλ≤',k=rng.randrange(12)));b=''.join(rng.choices('aλ≤',k=rng.randrange(12)))
        assert levenshtein(a,b)==reference(a,b)
    assert normalized_distance([],[])==0 and normalized_distance([1,2],[1,3])==.5


def test_missing_header_does_not_become_repair_or_failure():
    fixture=json.loads((Path(__file__).parent/'fixtures/tiny_trajectories.json').read_text())
    pairs=list(completed_repair_pairs(fixture['missing_header_only']))
    assert len(pairs)==1 and pairs[0][0]=='B'
    assert fixture['missing_header_only']['conditions']['C']['success'] is None


def test_success_stopping_and_repetition_fixture():
    fixture=json.loads((Path(__file__).parent/'fixtures/tiny_trajectories.json').read_text())['success_stopped']
    pairs=list(completed_repair_pairs(fixture));assert len(pairs)==2
    assert [before['candidate']==after['candidate'] for _,_,before,after in pairs]==[True,False]
    broken=copy.deepcopy(fixture);broken['conditions']['C']['attempts']*=2
    with pytest.raises(ValueError,match='after success'):list(completed_repair_pairs(broken))


def test_paired_score_matches_published_official_reference_example():
    assert newcombe_paired(10,5,2,20)['interval']==pytest.approx([-.0643926050711,.2211160178958],abs=1e-12)
    ci=newcombe_paired(1,0,0,57)['interval'];assert ci[0]<0<ci[1] and ci[1]>.06
    assert mcnemar(0,0)==1.0 and mcnemar(6,0)==pytest.approx(.03125)


def test_identification_bounds_keep_unknown_outcomes_unknown():
    rows=[{'outcomes':{'B':False,'C':None}},{'outcomes':{'B':True,'C':True}}]
    assert identification_bounds(rows)==[0,.5]
    assert rows[0]['outcomes']['C'] is None


def test_family_bootstrap_resamples_clusters_with_both_conditions():
    rows=[{'id':'p1','family':'f1','condition':'B','x':1},{'id':'p1','family':'f1','condition':'C','x':0},
          {'id':'p2','family':'f1','condition':'B','x':1},{'id':'p2','family':'f1','condition':'C','x':0},
          {'id':'p3','family':'f2','condition':'B','x':1},{'id':'p3','family':'f2','condition':'C','x':0}]
    result=bootstrap_difference(rows,'x',resamples=200);assert result['units']==2 and result['interval']==[-1,-1]
    assert result==bootstrap_difference(rows,'x',resamples=200)


def test_MDE_assumptions_and_discrete_feasibility():
    assert approximate_mde(58,.05)['feasible_under_q'] is False
    assert exact_mde(58,.05) is None
    assert exact_power(58,.2,.2)>exact_power(58,.2,0)
    with pytest.raises(ValueError):approximate_mde(58,0)
