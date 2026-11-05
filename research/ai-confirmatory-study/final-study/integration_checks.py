"""Actual Lean parser/kernel fixtures; no model calls or benchmark admission."""
from study_common import *
from strict_verifier import StrictVerifier
from native_parser import NativeParser,ParseError

def main():
    out=run_root()/'offline_integration';out.mkdir(parents=True,exist_ok=True);results=[];verifier=StrictVerifier()
    target='theorem fixture {α : Type*} (l : List α) : l.reverse.reverse = l'
    cases=[('polymorphic_positive',target+' := by simp',target,True),('monomorphic_specialization','theorem fixture (l : List Nat) : l.reverse.reverse = l := by simp',target,False),('weakened_target','theorem fixture (n : Nat) : True := by trivial','theorem fixture (n : Nat) : n = n',False),('extra_assumption','theorem fixture (n : Nat) (h : False) : n = n := by rfl','theorem fixture (n : Nat) : n = n',False),('sorry',target+' := by sorry',target,False)]
    for name,source,type_,expected in cases:
        path=out/(name+'.json')
        if path.exists():r=read(path)
        else:r=verifier(source,type_,'final_fixture_'+name);dump(path,r,exclusive=True)
        ensure(r['success'] is expected,'Real strict fixture failed: '+name+': '+str(r.get('errors')));results.append(dict(name=name,expected=expected,actual=r['success']))
    parser=NativeParser(out/'native')
    try:
        for i,source in enumerate(['theorem fixture : True := by\n  let x := 2\n  trivial','theorem fixture : True := by\n  /- := ignored -/\n  trivial']):
            folder=out/('native_'+str(i));folder.mkdir(exist_ok=True);t,_=parser.split(source,'fixture',folder);ensure(t=='theorem fixture : True','Wrong native assignment boundary')
        try:
            folder=out/'native_multiple';folder.mkdir(exist_ok=True);parser.split('theorem fixture : True := by trivial\ntheorem second : True := by trivial','fixture',folder);raise AssertionError('Multiple commands accepted')
        except ParseError:pass
    finally:parser.close()
    dump(out/'integration_results.json',dict(actual_Lean_checks=results,native_batch_checks_passed=3,model_calls=0,synthetic_fixtures_not_benchmark_candidates=True));print('Real strict checks:',len(results),'; native batch checks:3; model calls:0')

if __name__=='__main__':main()
