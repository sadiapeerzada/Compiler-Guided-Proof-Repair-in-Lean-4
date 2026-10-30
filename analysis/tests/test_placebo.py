import copy
import hashlib
import json
from pathlib import Path
import pytest
from extensions.filename_normalization import normalize_diagnostics,normalize_verification,feedback,NormalizationError
from extensions.donors import select_donor


def message(path,data='Unknown identifier `foo`'):
    return {'fileName':str(path),'data':data,'kind':'lean.unknownIdentifier._namedError','severity':'error',
            'pos':{'line':7,'column':3},'endPos':{'line':7,'column':6},'isSilent':False}


def test_filename_normalization_preserves_all_other_fields_and_order(tmp_path):
    source=[message(tmp_path/'lean_project/generated/_scratch/a.lean'),message(tmp_path/'Mathlib/Foo.lean','unsolved goals\n⊢ True')]
    original=copy.deepcopy(source);actual=normalize_diagnostics(source,tmp_path)
    assert source==original
    assert [x['fileName'] for x in actual]==['lean_project/generated/_scratch/a.lean','Mathlib/Foo.lean']
    for before,after in zip(source,actual):assert {k:v for k,v in before.items() if k!='fileName'}=={k:v for k,v in after.items() if k!='fileName'}


def test_verification_export_only_changes_filename_and_json_representation(tmp_path):
    ds=[message(tmp_path/'candidate.lean')];v={'diagnostics':ds,'compiler_stdout':json.dumps(ds[0])+'\n','compiler_stderr':'','errors':['Unknown identifier `foo`'],'verification_source_text':'theorem t : True := by trivial'}
    out=normalize_verification(v,tmp_path)
    assert json.loads(out['compiler_stdout'])==out['diagnostics'][0]
    assert out['errors']==v['errors'] and out['verification_source_text']==v['verification_source_text']


def test_cannot_silently_redact_private_message_content_or_outside_filename(tmp_path):
    with pytest.raises(NormalizationError):normalize_diagnostics([message(tmp_path/'a.lean','error at /Users/private_user/secret.lean')],tmp_path)
    with pytest.raises(NormalizationError):normalize_diagnostics([message(tmp_path.parent/'outside.lean')],tmp_path)


def donor(ident,family,category,n,payload='real message'):
    return {'id':ident,'family':family,'category':category,'payload_tokens':n,'payload':payload,'payload_sha256':hashlib.sha256(payload.encode()).hexdigest()}


def test_donor_category_family_length_and_deterministic_hash_ties():
    pool=[donor('same','family','parser',20),donor('other_same_family','family','parser',20),donor('near','f2','parser',22),donor('wrong','f3','type',20)]
    chosen,record=select_donor(pool,'same','family','parser',20)
    assert chosen['id']=='near' and record['category_fallback'] is False
    assert chosen['payload']=='real message'
    assert select_donor(list(reversed(pool)),'same','family','parser',20)[0]==chosen


def test_real_diagnostic_fallback_logged_and_no_eligible_donor_stops():
    chosen,record=select_donor([donor('x','f2','type',10)],'target','f1','parser',8)
    assert record['category_fallback'] is True
    with pytest.raises(ValueError):select_donor([donor('target','f1','parser',8)],'target','f1','parser',8)


def test_missing_intent_never_reexecutes_model(tmp_path):
    from extensions.run_placebo import completed_step,MissingGeneration
    folder=tmp_path/'run';(folder/'real_repair_1').mkdir(parents=True);(folder/'real_repair_1/intent.json').write_text('{}')
    def forbidden_model(*args,**kwargs):raise AssertionError('Model replay forbidden')
    p={'phase':'post_hoc_dev_fixture','base_seed':2027};row={'id':'synthetic'}
    with pytest.raises(MissingGeneration):completed_step(forbidden_model,p,folder,row,'real_repair_1','a safe prompt')
