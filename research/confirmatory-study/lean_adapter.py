"""Reuse strict verification with a private scoped-import module instance."""
import hashlib
import importlib.util
import sys
from common import ROOT,ensure

class LeanVerifier:
    def __init__(self,imports,timeout=180,project=None):
        name='_confirmatory_strict_verifier'
        spec=importlib.util.spec_from_file_location(name,ROOT/'src/verify.py')
        self.module=importlib.util.module_from_spec(spec);sys.modules[name]=self.module;spec.loader.exec_module(self.module)
        self.imports=imports;self.timeout=timeout;self.project=project or ROOT/'lean_project'
        original=self.module._verification_source
        def scoped(*args,**kwargs):
            source,theorem=original(*args,**kwargs);_,marker,tail=source.partition('\n\nnamespace Nl2LeanExpected\n')
            ensure(bool(marker),'Unexpected strict verifier harness format')
            return '\n'.join('import '+m for m in imports)+marker+tail,theorem
        self.module._verification_source=scoped
    def __call__(self,candidate,target,key):
        digest=hashlib.sha256(candidate.encode()).hexdigest()
        if any(line.lstrip().startswith(('import ','set_option ','#eval ','#check ')) for line in candidate.splitlines()):
            return dict(success=False,failure_kind='proof_rejected',candidate_sha256=digest,diagnostics=[],errors=['Generated candidate violates frozen command/import policy'])
        ensure(':=' not in target,'Target must be an unproved declaration')
        # Existing verifier expects a well-formed declaration in its expected namespace.
        # The placeholder is ONLY in the expected-type scaffold, never the candidate.
        result=self.module.check_lean_file_detailed(candidate,self.project,'confirmatory_'+key,expected_statement=target+' := by sorry',policy=self.module.VerificationPolicy(timeout_seconds=self.timeout)).to_record()
        if result['failure_kind'] in ('timeout','verifier_error','infrastructure_error','input_error'):
            result['strict_verified']=result['success'];result['success']=None
        return result

def live_environment(protocol):
    import subprocess
    project=ROOT/'lean_project'
    version=subprocess.run(['lake','env','lean','--version'],cwd=project,capture_output=True,text=True,timeout=30)
    revision=subprocess.run(['git','-C',str(project/'.lake/packages/mathlib'),'rev-parse','HEAD'],capture_output=True,text=True,timeout=30)
    dirty=subprocess.run(['git','-C',str(project/'.lake/packages/mathlib'),'status','--porcelain'],capture_output=True,text=True,timeout=30)
    ensure(version.returncode==0 and version.stdout.startswith(protocol['lean']['version_prefix']),'Actual Lean version differs')
    ensure(revision.returncode==0 and revision.stdout.strip()==protocol['lean']['mathlib_revision'],'Actual Mathlib revision differs')
    ensure(dirty.returncode==0 and not dirty.stdout.strip(),'Mathlib sources are dirty')
    return dict(lean_version=version.stdout.strip(),mathlib_revision=revision.stdout.strip())
