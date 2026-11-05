from study_common import *
from rigid_verifier import RigidVerifier

def main():
    out=run_root()/'rigid_verifier_fixtures';out.mkdir(exist_ok=True);verifier=RigidVerifier();target='theorem fixture {α : Type*} (x : α) : x = x'
    cases=[('polymorphic_positive',target+' := by rfl',target,True),('universe_specialization','theorem fixture {α : Type} (x : α) : x = x := by rfl',target,False),('monomorphic_positive','theorem fixture (n : Nat) : n = n := by rfl','theorem fixture (n : Nat) : n = n',True),('weakened_target','theorem fixture (n : Nat) : True := by trivial','theorem fixture (n : Nat) : n = n',False)]
    results=[]
    for name,source,type_,expected in cases:
        path=out/(name+'.json')
        if path.exists():r=read(path)
        else:r=verifier(source,type_,'rigid_fixture_'+name);dump(path,r,exclusive=True)
        ensure(r['success'] is expected,'Rigid fixture failed: '+name+': '+str(r.get('errors')));results.append(dict(name=name,expected=expected,actual=r['success']))
    dump(out/'results.json',dict(actual_Lean_checks=results,model_calls=0,synthetic_fixtures_not_subjects=True));print('Rigid declaration-type fixtures:',len(results),'passed')

if __name__=='__main__':main()
