"""Diagnostic-only extraction of actual headers from rejected development sources.

It cannot produce a verified proof. Complete unchanged source goes to the kernel
verifier before any one-step repair eligibility is considered.
"""
import subprocess,re
from study_common import *
from native_parser import NativeParser,ParseError
from parser_v3 import decode

class NativeHeaderParser(NativeParser):
    def __init__(self,log_root):
        log_root.mkdir(parents=True,exist_ok=True);self.log_root=log_root;self.ordinal=0;self.stderr=(log_root/'native_header_stderr.log').open('a')
        self.process=subprocess.Popen(['lake','env','lean','--run',str(HERE/'NativeHeaderParserServer.lean')],cwd=ROOT/'lean_project',stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=self.stderr,text=True,bufsize=1)
    def split(self,source,identifier,folder):
        # Preserve the shared native RPC and exact-byte checks. The response helper
        # hash recorded by the original implementation is supplemented explicitly.
        try:return super().split(source,identifier,folder)
        finally:
            path=folder/'native_parser.json'
            if path.exists():
                evidence=read(path);evidence['helper_sha256']=sha(HERE/'NativeHeaderParserServer.lean');evidence['mode']='HEADER_ONLY_POSTHOC_CONSTRUCTION_NOT_PROOF_VALIDATION';dump(path,evidence)
    def repair(self,raw,candidate,tokens,finish,folder):
        text=decode(raw,tokens,finish).strip();m=re.fullmatch(r'```(?:lean|lean4|text|plaintext)?\n(.*)\n```',text,re.S|re.I)
        if m:text=m.group(1).strip()
        if re.match(r'theorem\s',text):
            declaration_folder=folder/'provided_declaration_parse';declaration_folder.mkdir(exist_ok=True)
            target,proof=self.split(text,candidate['id'],declaration_folder)
            if target!=candidate['expected_lean_statement']:raise ParseError('repair_target_changed')
        else:
            if not re.match(r'by(?:\s|$)',text):raise ParseError('repair_requires_by_block_or_exact_fixed_declaration')
            proof=text
        source=candidate['expected_lean_statement']+' := '+proof
        target,_=self.split(source,candidate['id'],folder)
        if target!=candidate['expected_lean_statement']:raise ParseError('repair_target_changed')
        return source
