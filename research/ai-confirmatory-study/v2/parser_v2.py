"""Strict delimited intake: no theorem edits, JSON repairs, or Unicode rewriting."""
import hashlib
import re
import unicodedata

FIELDS=('ID','STATEMENT','TARGET','PROOF','CATEGORY','FAMILY')
MARKERS=[f'<<<{f}>>>' for f in FIELDS]+['<<<END>>>']

class ParseError(ValueError):pass

def parse_response(raw, *, output_tokens, max_output_tokens=1200, finish_reason='stop', seen_ids=()):
    if not isinstance(raw,bytes):raise TypeError('Raw response must be original UTF-8 bytes')
    raw_hash=hashlib.sha256(raw).hexdigest()
    try:text=raw.decode('utf-8',errors='strict')
    except UnicodeDecodeError as error:raise ParseError('invalid_utf8') from error
    if type(output_tokens) is not int or not 0<=output_tokens<=max_output_tokens:raise ParseError('output_allocation_exceeded_or_unknown')
    if finish_reason=='length':raise ParseError('output_truncated_at_allocation')
    if unicodedata.normalize('NFC',text)!=text:raise ParseError('non_NFC_unicode_rejected_without_normalization')
    # Only harmless outer whitespace and whole-response Markdown fencing are removed.
    body=text.strip(); normalization=[]
    if body.startswith('```'):
        m=re.fullmatch(r'```(?:text|lean)?\r?\n(.*)\r?\n```',body,re.S)
        if not m:raise ParseError('ambiguous_or_incomplete_outer_fence')
        body=m.group(1);normalization.append('outer_Markdown_fence_removed')
    raw_lines=body.splitlines()
    positions=[(i,line) for i,line in enumerate(raw_lines) if line in MARKERS]
    if [line for _,line in positions]!=MARKERS:raise ParseError('missing_duplicate_or_out_of_order_delimiter')
    if positions[0][0]!=0 or positions[-1][0]!=len(raw_lines)-1:raise ParseError('unexpected_text_outside_delimiters')
    values={}
    for index,field in enumerate(FIELDS):
        start=positions[index][0]+1;end=positions[index+1][0]
        value='\n'.join(raw_lines[start:end]).strip()
        if not value:raise ParseError('missing_'+field.lower())
        # An isolated fence around source fields is permitted; no other content edits.
        if value.startswith('```'):
            match=re.fullmatch(r'```(?:lean|text)?\n(.*)\n```',value,re.S)
            if not match:raise ParseError('invalid_field_fence_'+field.lower())
            value=match.group(1).strip();normalization.append(field+'_Markdown_fence_removed')
        values[field]=value
    identifier=values['ID']
    if not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*',identifier):raise ParseError('invalid_identifier')
    if identifier in seen_ids:raise ParseError('duplicate_identifier')
    target=values['TARGET'];proof=values['PROOF']
    if not re.match(r'theorem\s+'+re.escape(identifier)+r'\b',target):raise ParseError('target_identifier_mismatch')
    if len(re.findall(r'\btheorem\b',target))!=1 or ':=' in target:raise ParseError('target_must_be_one_unproved_declaration')
    if not proof.startswith('by') or not re.match(r'by(?:\s|$)',proof):raise ParseError('proof_must_be_a_by_block')
    if re.search(r'\b(theorem|lemma|def|axiom|constant|opaque|namespace|import)\b',proof):raise ParseError('proof_contains_top_level_declaration')
    source=target+' := '+proof
    return dict(id=identifier,nl_statement=values['STATEMENT'],expected_lean_statement=target,proof_block=proof,reference_proof=source,category=values['CATEGORY'],domain=values['CATEGORY'],family=values['FAMILY'],imports=['Mathlib'],raw_response_sha256=raw_hash,statement_sha256=hashlib.sha256(target.encode()).hexdigest(),proof_sha256=hashlib.sha256(source.encode()).hexdigest(),format_normalizations=normalization)
