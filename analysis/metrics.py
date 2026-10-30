"""Post-hoc measurement definitions, independent of stored outcome labels."""
import re


def completed_repair_pairs(manifest):
    initial=manifest.get('initial')
    if initial is None:return
    for condition in ['B','C']:
        prior=initial;attempts=manifest.get('conditions',{}).get(condition,{}).get('attempts',[])
        if len(attempts)>3:raise ValueError('Repair budget exceeded')
        for index,after in enumerate(attempts,1):
            if prior['verification']['success']:raise ValueError('Completed repair after success')
            yield condition,index,prior,after
            prior=after


def levenshtein(a,b):
    """Exact Myers bit-vector distance on any hashable token sequence."""
    if a==b:return 0
    if len(a)>len(b):a,b=b,a
    if not a:return len(b)
    masks={}
    for i,symbol in enumerate(a):masks[symbol]=masks.get(symbol,0)|(1<<i)
    vp=(1<<len(a))-1;vn=0;score=len(a);high=1<<(len(a)-1)
    for symbol in b:
        x=masks.get(symbol,0)|vn
        d=(((x&vp)+vp)^vp)|x
        hp=vn|~(d|vp);hn=vp&d
        score+=bool(hp&high)-bool(hn&high)
        hp=(hp<<1)|1
        vn=d&hp;vp=(hn<<1)|~(d|hp)
    return score


def normalized_distance(a,b):
    return levenshtein(a,b)/max(len(a),len(b)) if a or b else 0.0


def unknown_names(verification):
    names=set()
    for diagnostic in verification.get('diagnostics') or []:
        if diagnostic.get('severity')!='error':continue
        kind=diagnostic.get('kind','').lower();message=diagnostic.get('data','')
        if 'unknown' not in kind and not re.match(r'(?i)^unknown (identifier|constant|namespace)\b',message):continue
        dedicated=next((diagnostic[k] for k in ['identifier','constant','name'] if isinstance(diagnostic.get(k),str) and diagnostic[k]),None)
        if dedicated:names.add(dedicated);continue
        match=re.match(r'(?i)^unknown (?:identifier|constant|namespace)\s+`([^`]+)`',message)
        if match:names.add(match.group(1))
    return names


def identifier_present(code,name):
    """Unicode word/prime boundaries; qualified names are literal, not resolved."""
    return re.search(r"(?<![\w'])"+re.escape(name)+r"(?![\w'])",code) is not None


def distinct_errors(v):
    if v.get('success'):return 0
    if v.get('diagnostic_state')!='available':return None
    return len({(d.get('kind',''),d.get('data','')) for d in v.get('diagnostics') or [] if d.get('severity')=='error'})


def targeted_fix(before_code,after_code,before_v,after_v):
    old=unknown_names(before_v);new=unknown_names(after_v);removed={n for n in old if not identifier_present(after_code,n)}
    introduced={n for n in new-old if identifier_present(after_code,n) and not identifier_present(before_code,n)}
    observed=bool(after_v.get('success')) or after_v.get('diagnostic_state')=='available'
    return {'unknown_prior_n':len(old),'unknown_removed_n':len(removed),
            'unknown_newly_reported_n':len(new-old) if observed else None,'unknown_newly_introduced_n':len(introduced) if observed else None,
            'any_unknown_removed':int(bool(removed)) if old else None,'all_unknown_removed':int(removed==old) if old else None,
            'hallucinated_substitution':int(bool(removed and introduced)) if old and observed else None,
            'unknown_removal_fraction':len(removed)/len(old) if old else None}


STAGE={'syntax_or_parser':0,'unknown_identifier_or_name':1,'type_mismatch_or_elaboration':2,'tactic_or_unsolved_goal':3}


def transition_direction(before,after):
    if after=='verified':return 'verified'
    if before==after:return 'same_category'
    if before not in STAGE or after not in STAGE:return 'unranked'
    return 'advanced' if STAGE[after]>STAGE[before] else 'regressed'
