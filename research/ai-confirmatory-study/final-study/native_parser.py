"""Same V3 section rules/Lean assignment semantics; amortize parser startup only."""
import re,subprocess,select,json
from study_common import *
sys.path.insert(0,str(OLD/'v3'))
from parser_v3 import sections,decode,ParseError,ParserUnavailable

class NativeParser:
    def __init__(self,log_root):
        log_root.mkdir(parents=True,exist_ok=True);self.log_root=log_root;self.ordinal=0
        self.stderr=(log_root/'native_server_stderr.log').open('a')
        self.process=subprocess.Popen(['lake','env','lean','--run',str(HERE/'NativeParserServer.lean')],cwd=ROOT/'lean_project',stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=self.stderr,text=True,bufsize=1)
    def split(self,source,identifier,folder):
        if not re.match(r'\s*theorem\s+'+re.escape(identifier)+r'\b',source):raise ParseError('theorem_identifier_mismatch')
        request=dict(source=source,request_id=self.ordinal);self.ordinal+=1
        try:
            self.process.stdin.write(json.dumps(request,ensure_ascii=False)+'\n');self.process.stdin.flush()
            ready,_,_=select.select([self.process.stdout],[],[],180)
            if not ready:raise ParserUnavailable('Native parser timeout')
            line=self.process.stdout.readline();response=json.loads(line)
        except (BrokenPipeError,ValueError,OSError) as error:raise ParserUnavailable(str(error)) from error
        ensure(response.get('request_id')==request['request_id'],'Native parser request mismatch')
        result=response['result'];path=folder/'native_parser.json'
        evidence=dict(request_source_sha256=text_hash(source),request_id=request['request_id'],result=result,helper_sha256=sha(HERE/'NativeParserServer.lean'),environment_reused=True)
        if path.exists():ensure(read(path)['request_source_sha256']==evidence['request_source_sha256'],'Native parser source changed')
        else:dump(path,evidence,exclusive=True)
        if 'error' in result:raise ParseError('Lean_syntax: '+result['error'])
        raw=source.encode();a=result['assignment_start'];b=result['assignment_end'];ensure(raw[a:b]==b':=','Native token mismatch')
        target=raw[:a].decode().rstrip();proof=raw[b:].decode().lstrip()
        if ':=' in target:raise ParseError('nested_target_assignment_unsupported_by_existing_verifier')
        if not proof:raise ParseError('missing_proof')
        return target,proof
    def candidate(self,raw,identifier,category,tokens,finish,folder):
        fields=sections(raw,tokens,finish);source=fields['LEAN'];target,proof=self.split(source,identifier,folder)
        return dict(id=identifier,nl_statement=fields['STATEMENT'],expected_lean_statement=target,proof_block=proof,reference_proof=source,category=category,domain=category,family=fields['FAMILY'],imports=['Mathlib'],raw_response_sha256=hashlib.sha256(raw).hexdigest(),statement_sha256=text_hash(target),proof_sha256=text_hash(source))
    def repair(self,raw,candidate,tokens,finish,folder):
        text=decode(raw,tokens,finish).strip();m=re.fullmatch(r'```(?:lean|lean4)?\n(.*)\n```',text,re.S)
        if m:text=m.group(1).strip()
        if not re.match(r'by(?:\s|$)',text):raise ParseError('repair_requires_only_by_block')
        source=candidate['expected_lean_statement']+' := '+text;target,_=self.split(source,candidate['id'],folder);ensure(target==candidate['expected_lean_statement'],'Repair changed fixed target');return source
    def close(self):
        if self.process.poll() is None:self.process.terminate()
        try:self.process.wait(timeout=10)
        except subprocess.TimeoutExpired:self.process.kill();self.process.wait()
        self.stderr.close()
