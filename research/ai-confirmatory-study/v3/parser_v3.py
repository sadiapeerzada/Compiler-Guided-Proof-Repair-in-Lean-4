"""Three-section intake with native Lean command parsing, not assignment regexes."""
import re,subprocess,tempfile,unicodedata,json,hashlib
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]

class ParseError(ValueError):pass
class ParserUnavailable(RuntimeError):pass

def decode(raw,tokens,finish='stop'):
    if type(tokens) is not int or not 0<=tokens<=1200:raise ParseError('output_allocation_exceeded_or_unknown')
    if finish=='length':raise ParseError('truncated_response')
    try:text=raw.decode('utf-8','strict')
    except UnicodeDecodeError as error:raise ParseError('invalid_UTF8') from error
    if unicodedata.normalize('NFC',text)!=text:raise ParseError('non_NFC_response')
    return text

def split_theorem(source, expected_id, evidence=None):
    if not re.match(r'\s*theorem\s+'+re.escape(expected_id)+r'\b',source):raise ParseError('theorem_identifier_mismatch')
    with tempfile.TemporaryDirectory(prefix='lean_v3_parse_') as directory:
        inp=Path(directory)/'input.lean';out=Path(directory)/'output.json';inp.write_bytes(source.encode())
        command=['lake','env','lean','--run',str(HERE/'ParseTheorem.lean'),str(inp),str(out)]
        try:r=subprocess.run(command,cwd=ROOT/'lean_project',capture_output=True,text=True,timeout=180)
        except (subprocess.TimeoutExpired,OSError) as error:raise ParserUnavailable(str(error)) from error
        if not out.exists():raise ParserUnavailable(r.stderr or r.stdout or 'Native parser produced no result')
        result=json.loads(out.read_text())
        if evidence is not None:
            evidence.parent.mkdir(parents=True,exist_ok=True)
            payload=dict(source_sha256=hashlib.sha256(source.encode()).hexdigest(),result=result,stdout=r.stdout,stderr=r.stderr,exit_code=r.returncode,helper_sha256=hashlib.sha256((HERE/'ParseTheorem.lean').read_bytes()).hexdigest())
            if evidence.exists():
                old=json.loads(evidence.read_text());assert old['source_sha256']==payload['source_sha256']
            else:evidence.write_text(json.dumps(payload,indent=2)+'\n')
        if r.returncode or 'error' in result:raise ParseError('Lean_syntax: '+result.get('error',r.stderr))
        raw=source.encode();start=result['assignment_start'];end=result['assignment_end']
        if raw[start:end]!=b':=':raise ParserUnavailable('Native assignment token mismatch')
        target=raw[:start].decode().rstrip();proof=raw[end:].decode().lstrip()
        if not proof:raise ParseError('missing_proof')
        # Current reused strict verifier forbids assignments even inside target types.
        # Reject such unsupported targets explicitly; never take the wrong split.
        if ':=' in target:raise ParseError('nested_target_assignment_unsupported_by_existing_verifier')
        return target,proof

def sections(raw,tokens,finish='stop'):
    text=decode(raw,tokens,finish);body=text.strip()
    if body.startswith('```text\n') or body.startswith('```plaintext\n'):
        match=re.fullmatch(r'```(?:text|plaintext)\n(.*)\n```',body,re.S)
        if not match:raise ParseError('incomplete_outer_fence')
        body=match.group(1)
    # Headers are recognized only outside the one Lean code fence.
    parts={};current=None;fenced=False;fence_count=0;order=[]
    for line in body.splitlines():
        if re.fullmatch(r'```(?:lean|lean4)?\s*',line):
            if current!='LEAN':raise ParseError('fence_outside_Lean_section')
            fenced=not fenced;fence_count+=1;continue
        header=None
        if not fenced:
            for name in ('STATEMENT','LEAN','FAMILY'):
                for prefix in (name+':','**'+name+':**','**'+name+'**:', '### '+name+':'):
                    if line.startswith(prefix):header=(name,line[len(prefix):].lstrip());break
                if line in (name,'**'+name+'**','### '+name):header=(name,'')
                if header:break
        if header:
            current=header[0]
            if current in parts:raise ParseError('duplicate_section')
            order.append(current);parts[current]=[header[1]]
        elif current:parts[current].append(line)
        elif line.strip():raise ParseError('unexpected_prefix_or_missing_statement')
    if fenced or fence_count not in (0,2):raise ParseError('incomplete_or_multiple_Lean_fences')
    if order!=['STATEMENT','LEAN','FAMILY']:raise ParseError('missing_or_reordered_sections')
    parts={k:'\n'.join(v).strip() for k,v in parts.items()}
    if not all(parts.values()):raise ParseError('empty_required_section')
    return parts

def parse(raw, *, expected_id, category, tokens, finish='stop', seen_ids=(), evidence=None):
    parts=sections(raw,tokens,finish)
    if expected_id in seen_ids:raise ParseError('duplicate_identifier')
    source=parts['LEAN'];target,proof=split_theorem(source,expected_id,evidence)
    return dict(id=expected_id,nl_statement=parts['STATEMENT'],expected_lean_statement=target,proof_block=proof,reference_proof=source,category=category,domain=category,family=parts['FAMILY'],imports=['Mathlib'],raw_response_sha256=hashlib.sha256(raw).hexdigest(),statement_sha256=hashlib.sha256(target.encode()).hexdigest(),proof_sha256=hashlib.sha256(source.encode()).hexdigest())

def repair_source(raw, *, candidate,tokens,finish='stop',evidence=None):
    text=decode(raw,tokens,finish).strip()
    match=re.fullmatch(r'```(?:lean|lean4)?\n(.*)\n```',text,re.S)
    if match:text=match.group(1).strip()
    # The repair model supplies only a proof block; the target is immutable.
    if not re.match(r'by(?:\s|$)',text):raise ParseError('repair_must_supply_only_by_block')
    source=candidate['expected_lean_statement']+' := '+text
    target,_=split_theorem(source,candidate['id'],evidence)
    if target!=candidate['expected_lean_statement']:raise ParseError('repair_target_changed')
    return source
