"""Reporting regressions: missingness must not silently change paired estimands."""
import importlib.util
from pathlib import Path
import pytest

spec=importlib.util.spec_from_file_location('review_analysis',Path(__file__).resolve().parents[1]/'eval/final_review_analysis.py')
review=importlib.util.module_from_spec(spec);spec.loader.exec_module(review)


def case(b,c,family):
    return {'family':family,'outcomes':{'A':False,'B':b,'C':c}}


def test_missing_c_is_excluded_from_primary_pair_but_retained_in_sensitivity():
    r=review.contrast([case(True,True,'shared'),case(False,False,'shared'),case(False,None,'missing')],'C','B',200)
    assert r['complete_pairs']==2
    assert r['risk_difference_complete_case']==0
    assert r['missing_as_failure_sensitivity']==0
    assert r['missingness_identification_bounds']==[0,1/3]
    assert r['exact_mcnemar_p'] is None
    assert r['conventional_mcnemar_p']==1


def test_nonzero_effect_uses_the_same_population_as_its_paired_test():
    r=review.contrast([case(False,True,'observed'),case(False,None,'missing')],'C','A',200)
    assert r['complete_pairs']==1
    assert r['risk_difference_complete_case']==1
    assert r['missing_as_failure_sensitivity']==.5
    assert r['problem_bootstrap_95_complete_case']==[1,1]
    assert r['family_bootstrap_95_complete_case']==[1,1]


def test_missing_baseline_also_enters_identification_bounds():
    r=review.contrast([case(False,False,'known'),case(None,False,'missing_baseline')],'C','B',200)
    assert r['missingness_identification_bounds']==[-.5,0]


def test_no_observed_pairs_cannot_produce_a_rate_or_confidence_interval():
    with pytest.raises(ValueError,match='No complete matched'):
        review.contrast([case(False,None,'missing')],'C','B',200)
