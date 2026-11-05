"""Exact closed declaration-type equality, including universe parameter arity.

Trusted harness code inspects elaborated constant types before accepting a proof.
It neither changes the supplied theorem nor permits candidate-side metaprograms.
"""
from study_common import *
from strict_verifier import StrictVerifier

class RigidVerifier(StrictVerifier):
    def __init__(self,timeout=180):
        super().__init__(timeout)
        original=self.module._verification_source
        def rigid(lean_code,expected_statement,theorem_name,**kwargs):
            source,name=original(lean_code,expected_statement,theorem_name,**kwargs)
            guard=f'''\nrun_cmd do
  let expectedInfo ← Lean.getConstInfo `Nl2LeanExpected.{theorem_name}
  let candidateInfo ← Lean.getConstInfo `Nl2LeanCandidate.{theorem_name}
  unless expectedInfo.levelParams.length == candidateInfo.levelParams.length do
    throwError "Fixed theorem universe-parameter arity mismatch"
  let candidateType := candidateInfo.type.instantiateLevelParams candidateInfo.levelParams (expectedInfo.levelParams.map Lean.Level.param)
  Lean.Elab.Command.liftTermElabM do
    unless (← Lean.Meta.isDefEq expectedInfo.type candidateType) do
      throwError "Fixed theorem closed declaration types differ"
'''
            return source+guard,name
        self.module._verification_source=rigid
    def __call__(self,candidate,target,key):
        r=super().__call__(candidate,target,key);r['harness_variant']='rigid_declaration_type_and_universe_v1';r['rigid_variant_source_sha256']=sha(HERE/'rigid_verifier.py');return r
