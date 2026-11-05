"""Known model declaration-format violations are unverified, not infrastructure failures."""
import re
from study_common import *
from rigid_verifier import RigidVerifier as StrictVerifier

class CDEVerifier(StrictVerifier):
    def __call__(self,candidate,target,key):
        names=re.findall(r'(?m)^\s*theorem\s+([A-Za-z_][A-Za-z0-9_]*)\b',candidate);expected=re.match(r'\s*theorem\s+([A-Za-z_][A-Za-z0-9_]*)\b',target)
        if not expected or names!=[expected.group(1)]:
            return dict(success=False,failure_kind='proof_rejected',candidate_sha256=text_hash(candidate),errors=['Expected exactly the fixed named theorem declaration'],diagnostics=[],harness_variant='explicit_all_arguments_v1',not_a_compiler_diagnostic=True)
        return super().__call__(candidate,target,key)
