"""Isolated harness correction: compare theorem constants with all arguments.

Historical src/verify.py and outcomes are untouched. Explicit @ prevents Lean
from inserting unresolved implicit type arguments before the type comparison.
The exact-type and axiom checks remain enabled for the full polymorphic theorem.
"""
from study_common import *
from lean_adapter import LeanVerifier

class StrictVerifier(LeanVerifier):
    def __init__(self,timeout=180):
        super().__init__(['Mathlib'],timeout=timeout)
        original=self.module._verification_source
        def explicit(lean_code,expected_statement,theorem_name,**kwargs):
            source,name=original(lean_code,expected_statement,theorem_name,**kwargs)
            old=f'example : Nl2LeanExpected.{theorem_name} = Nl2LeanCandidate.{theorem_name} := by'
            new=f'example : @Nl2LeanExpected.{theorem_name} = @Nl2LeanCandidate.{theorem_name} := by'
            ensure(source.count(old)==1,'Unexpected strict harness shape')
            return source.replace(old,new),name
        self.module._verification_source=explicit
    def __call__(self,candidate,target,key):
        # Malformed model output is a known rejected proof, not failed infrastructure.
        import re
        if len(re.findall(r'(?m)^\s*theorem\s+',candidate))!=1:
            return dict(success=False,failure_kind='proof_rejected',errors=['Expected exactly one complete theorem declaration'],diagnostics=[],candidate_sha256=text_hash(candidate),harness_variant='explicit_all_arguments_v1',variant_source_sha256=sha(HERE/'strict_verifier.py'))
        r=super().__call__(candidate,target,key);r['harness_variant']='explicit_all_arguments_v1';r['variant_source_sha256']=sha(HERE/'strict_verifier.py');return r
