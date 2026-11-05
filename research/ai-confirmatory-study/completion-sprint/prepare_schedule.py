"""Freeze source-grounded development topics and prospectively reserved domains."""
import re,subprocess
from sprint_common import *

DEV=[('nat_modular_congruence','natural congruences under addition/multiplication','Data/Nat/ModEq.lean'),('integer_quotient_remainder','integer quotient/remainder constraints','Data/Int/DivMod.lean'),('list_take_drop','composed take/drop identities with genuine index conditions','Data/List/TakeDrop.lean'),('list_zip_relations','list zip and projections/truncation','Data/List/Zip.lean'),('list_pairwise','pairwise list relations under transformations','Data/List/Pairwise.lean'),('list_nodup','nonduplication under list transformations','Data/List/Nodup.lean'),('list_subperm','subpermutation of lists','Data/List/Perm/Subperm.lean'),('finset_erase_card','finite-set erasure and cardinality','Data/Finset/Card.lean'),('finset_image_injective','finite-set images under injectivity','Data/Finset/Image.lean'),('finset_union_membership','finite-set union/disjointness implications','Data/Finset/Union.lean'),('integer_gcd_combination','integer gcd and divisibility combinations, not plain transitivity','Data/Int/GCD.lean'),('set_cartesian_products','membership/inclusions of Cartesian products of sets','Data/Set/Prod.lean'),('iteration_composition_fixedpoint','iteration and fixed-point implications','Logic/Function/Iterate.lean'),('logical_quantifier_relations','nontrivial quantified logical equivalences','Logic/Basic.lean'),('finite_interval_sums','finite interval sums and splitting','Algebra/BigOperators/Intervals.lean'),('rational_floor_bounds','rational floor/ceiling inequalities','Data/Rat/Floor.lean')]
RESERVED=[('Matrix','matrix_transpose_products','matrix_trace_cyclicity','matrix_diagonal_relations','matrix_blocks','matrix_determinant_products','matrix_inverse_relations'),('LinearMap','linear_kernel_composition','linear_range_composition','linear_injectivity_kernel','linear_surjectivity_range','linear_restriction','linear_projection'),('Submodule','submodule_span','submodule_map','submodule_comap','submodule_quotient','submodule_disjointness','submodule_complement'),('Subgroup','subgroup_map','subgroup_comap','subgroup_normality','subgroup_centralizer','subgroup_closure','subgroup_quotient'),('Ideal','ideal_map','ideal_comap','ideal_radical','ideal_prime','ideal_principal','ideal_quotient'),('closure','topological_closure','topological_interior','topological_frontier','topological_closed_sets','topological_dense_sets','topological_continuity'),('OrderIso','order_isomorphism','order_duality','complete_lattice_suprema','complete_lattice_infima','galois_connections','order_embeddings'),('Finsupp','finsupp_support','finsupp_single','finsupp_sum','finsupp_map','finsupp_domain_restriction','finsupp_products')]

def names(path,limit=8):
    stack=[];result=[]
    for line in path.read_text().splitlines():
        s=line.strip()
        m=re.match(r'namespace\s+([\w.]+)',s)
        if m:stack.append(m[1]);continue
        if re.match(r'(?:noncomputable\s+)?section\b',s):stack.append(None);continue
        if re.match(r'end(?:\s|$)',s):
            if stack:stack.pop()
            continue
        m=re.match(r'(?:@\[[^]]*\]\s*)*(?:(?:protected|nonrec)\s+)?(?:theorem|lemma)\s+([A-Za-z_][\w.\x27]*)',s)
        if m:
            name='.'.join([x for x in stack if x]+[m[1]])
            if name not in result:result.append(name)
        if len(result)>=limit:break
    return result

def main():
    ensure(not (HERE/'family_schedule.json').exists(),'Schedule already prepared; do not replace')
    oldrun=OLD/'runs/20261105T041720Z_development';index=read(oldrun/'expanded_historical_exposure.json');items=list(index['items']);raw=[]
    for r in read(oldrun/'reference_candidate_pool_v2.json'):
        c=r['candidate'];items.append(dict(id=c['id'],statement=c['expected_lean_statement'],family=c['canonical_family'],source='closed_development_proposal_including_rejected'))
    sources=[oldrun/'generation/records.jsonl',HERE.parent/'runs/generation/candidate_generation.jsonl',*list((HERE.parent/'v2/runs').glob('*/v2_candidates.jsonl')),HERE.parent/'v3/runs/20261104T163622Z_v3/generation/records.jsonl']
    for p in sources:
        for r in rows(p):
            content=r.get('record',{}).get('content')
            if isinstance(content,str):raw.append(dict(source=str(p.relative_to(ROOT)),index=r.get('index'),content=content,sha256=text_hash(content)))
    corpus='\n'.join([r['statement'] for r in items]+[r['content'] for r in raw]);reservations=[]
    for keyword,*families in RESERVED:
        hits=[r['id'] for r in items if re.search(r'\b'+re.escape(keyword)+r'\b',r['statement'])];raw_hits=[dict(source=r['source'],index=r['index']) for r in raw if re.search(r'\b'+re.escape(keyword)+r'\b',r['content'])]
        reservations.append(dict(namespace_marker=keyword,families=families,formal_keyword_hits=hits,raw_keyword_hits=raw_hits,eligible_for_reserved_catalog=not hits and not raw_hits,semantic_novelty_not_certified=True))
    ensure(sum(len(r['families']) for r in reservations if r['eligible_for_reserved_catalog'])>=32,'Cannot reserve enough unexposed candidate families')
    dump(HERE/'exposure_index.json',dict(items=items,raw_exposures=raw,unextractable_prior_headers=index['unextractable_AI_headers'],scope='All prior raw responses are exposures; keyword absence is not semantic independence'),exclusive=True)
    dump(HERE/'heldout_reservations.json',dict(reservations=reservations,locked_before_development_inference=True,rule='Reject all development proposals using reserved domains or mathematical equivalents. Test eligibility still requires two semantic reviews and cross-partition screening; labels never establish independence.'),exclusive=True)
    lib=ROOT/'lean_project/.lake/packages/mathlib/Mathlib';topics=[];queries=[]
    for group,description,rel in DEV:
        path=lib/rel;ensure(path.exists(),'Missing Mathlib API source '+rel);ns=names(path);topics.append(dict(family=group,description=description,module=rel,source_sha256=sha(path),query_names=ns));queries.extend(ns)
    scratch=ROOT/'lean_project/generated/_scratch/sprint_api_facts.lean';scratch.write_text('import Mathlib\n'+'\n'.join('#check '+n for n in queries)+'\n')
    try:r=subprocess.run(['lake','env','lean','--json',str(scratch)],cwd=ROOT/'lean_project',capture_output=True,text=True,timeout=180)
    finally:scratch.unlink(missing_ok=True)
    messages=[]
    for line in r.stdout.splitlines():
        try:messages.append(json.loads(line))
        except ValueError:pass
    facts={}
    for m in messages:
        line=m.get('pos',{}).get('line',0)
        if m.get('severity')=='information' and 2<=line<=len(queries)+1:facts[queries[line-2]]=m['data']
    for t in topics:t['api_facts']=[facts[n] for n in t['query_names'] if n in facts][:6];ensure(t['api_facts'],'No actual checked API facts: '+t['family'])
    dump(HERE/'api_lookup_evidence.json',dict(queries=queries,stdout=r.stdout,stderr=r.stderr,exit_code=r.returncode,actual_Lean_lookup=True,not_benchmark_proofs=True),exclusive=True)
    dump(HERE/'family_schedule.json',dict(development=topics,development_jobs=128,round_robin=True,max_no_usable_success_attempts=4,development_target=16,test_target=32,test_jobs=256,seeds=dict(development_generation=2026110511,test_generation=2026110611,development_eval=[31037,31038,31039],test_eval=[41037,41038,41039])),exclusive=True)
    print('Checked API facts:',len(facts),'; dev families:',len(topics),'; reserved candidate families:',sum(len(r['families']) for r in reservations if r['eligible_for_reserved_catalog']))

if __name__=='__main__':main()
