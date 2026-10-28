"""Apply the expressly authorized AI policy, preserving all historical candidates."""
import copy
import json
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from candidate_inventory import load_candidates
from final_study import BASE,sha,canonical,binding,validate_freeze

DEV=set('ind_005 arith_005 ind_009 lib_a_choose_symmetry lib_i_vandermonde lib_i_alternating_binomial ind_006 div_012 lib_d_bezout lib_d_frobenius lib_m_gcd_obstruction lib_m_crt ind_008 ineq_004 mod_004'.split())
BINOM=set('ind_005 arith_005 ind_009 lib_a_choose_symmetry lib_i_vandermonde lib_i_alternating_binomial'.split())
LINEAR=set('ind_006 div_012 lib_d_bezout lib_d_frobenius lib_m_gcd_obstruction lib_m_crt'.split())
POWER=set('mod_005 lib_m_power lib_m_fermat lib_m_euler'.split())
RESOLUTIONS={
 'ineq_004':'The theorem type is exactly n+3<n+7 for natural n. Induction is a proof-method request, not a different proposition or quantifier. The study assesses proof validity, not compliance with an induction style.',
 'lib_a_log_product':'English explicitly says totalized real logarithm using absolute values on negative inputs; both nonzero hypotheses are explicit. Phi incorrectly says this convention is omitted.',
 'lib_a_min_max':'Neither English nor Lean requires distinct x,y. The alleged missing distinctness hypothesis is invented. Equality x=y satisfies min+max=x+y.',
 'lib_d_frobenius':'Both texts state the identical multiplication/addition inequality under coprimality and nonzero natural coefficients. No subtraction, division or remainder occurs; the judge objection cites absent operations.',
 'lib_q_exp_tangent':'The displayed conclusion is literally x+1 <= Real.exp x. The claim that there is no inequality in the Lean type is refuted by reading that conclusion.',
 'lib_q_log_tangent':'The Lean binder (hx : 0 < x) explicitly supplies the positive-real hypothesis the model alleges missing.',
 'lib_q_rearrangement':'Both texts use a<=b and c<=d, not strict order or distinctness. Equality cases are permitted by both; rearrangement orientation is the same.',
 'lib_q_reciprocal':'Variables are real, with 0<x and x<=y. Thus both denominators are positive. Natural truncated subtraction and zero remainder do not occur; the model objection is irrelevant.',
 'lib_d_euclid':'The explicit p.Prime premise excludes p=0. English also requires a prime. No zero-prime hypothesis is missing.',
 'lib_d_prime_parity':'The English explicitly says either two or odd, matching p=2 OR Odd p. The alleged omission of two is refuted by the actual English.',
 'lib_i_fibonacci':'English explicitly specifies F(0)=0 and F(1)=1; Nat.fib has those conventions. The alleged missing initial values are present.',
 'mod_004':'English and Lean both quantify integer inputs and require a positive modulus. Negative/zero modulus examples are outside both hypotheses.'}

def main():
    rows=load_candidates(ROOT);static=json.loads((ROOT/'data/ai_semantic_audit/20261028/coding_assistant_assessments.json').read_text())
    corrected={r['id']:r for r in json.loads((BASE/'corrections/corrected_candidates.json').read_text())}
    for r in corrected.values():
        if not (BASE/'corrections'/(r['id']+'.ai_review.json')).exists():raise ValueError('Corrected AI review missing')
    policy={'version':'ai-assisted-eligibility-1.0','approval_source':'student_reported_supervisor_methodological_approvals',
      'human_review_represented':False,'semantic_criteria':[
        'Explicit coding-AI adjudication of exact quantifiers, domains, assumptions, conclusion, strength and boundaries, bound to English/type/import/definition bytes.',
        'Separate-model raw reviews retained. Invalid/schema-placeholder outputs are not positive evidence; substantive objections require a candidate-specific reasoned resolution. No automatic majority vote.',
        'Reference theorem must have genuine strict Lean proof and exact-type evidence with approved axioms; numerical checks supplement but never prove English equivalence.',
        'Any remaining semantic uncertainty or unfaithfulness excludes the item. No human reviewer identity or decision is invented.'],
      'nonsemantic_criteria':['Pinned source bytes and item-level citation; published Apache-2.0 or CC BY-SA-4.0 evidence, retained attribution and per-item license. AI-assisted source/rights assessment, not an invented permission or independent legal clearance.',
        'Whole-family split assignment includes exact/equivalent, direct-specialization and conservative related binomial/linear-solvability groups; no family spans splits.',
        'Exclude exact duplicate and inadequate provenance; 15-20 development, at least 60 test, at least five categories.'],
      'limitations':['AI adjudicator is the authoring coding assistant and may share biases; separate Phi reviewers proved unreliable. No independent human semantic review is claimed.',
        'All candidates were exposed for authorized semantic curation; none was used for primary-model proof/prompt selection before freeze.',
        'Family independence is a documented mathematical curation judgment, not statistical proof; library pretraining and named-lemma exposure limit generalization.']}
    (BASE/'ai_eligibility_policy.json').write_text(json.dumps(policy,indent=2)+'\n')
    capture=json.loads((ROOT/'data/source_archives/20261027_curl/manifest.json').read_text())
    cc=[{'path':e['path'],'sha256':e['sha256']} for e in capture['entries'] if e['status']=='archived' and ('dmoi3' in e['path'])]
    proofpath='data/ai_semantic_audit/20261028/lean_reference_check/verification.json'
    proof=json.loads((ROOT/proofpath).read_text());assert proof['exit_code']==0 and proof['verified_count']==96
    proofby={x['candidate_id']:x for x in proof['comparisons']}
    selected=[];excluded=[];adjudications=[];history=[]
    for original in rows:
        ident=original['id'];r=copy.deepcopy(corrected.get(ident,original));c=r['curation']
        if ident in corrected:history+=r['correction_history']
        if ident=='arith_003_mathlib':excluded.append({'id':ident,'reason':'Exact semantic duplicate of arith_003.'});continue
        if not c.get('source_url'):
            excluded.append({'id':ident,'reason':'No adequate item-level source provenance; corrected examples are preserved but not admitted.'});continue
        assert ident in static['notes'] and proofby[ident]['strict_verified']
        note=static['notes'][ident];resolution=RESOLUTIONS.get(ident,
          'No substantive unresolved mismatch remains after comparing the actual English/type. '+note+' Invalid-format or generic/placeholder model output supplies no mathematical counterevidence; it is retained as an auditor failure, not accepted as a faithful vote.')
        family=('binomial_identities' if ident in BINOM else 'linear_integer_solvability' if ident in LINEAR else 'modular_power_preservation' if ident in POWER else c['problem_family'])
        split='development' if ident in DEV else 'test'
        metadata=c['source_metadata']
        if metadata.get('source_page_archive'):
            evidence=[{'path':metadata['source_page_archive'],'sha256':metadata['source_page_sha256']}]
            licensefile=c['source_license_evidence']['evidence_reference']
            evidence.append({'path':licensefile,'sha256':sha(ROOT/licensefile)})
        else:evidence=cc
        for e in evidence:assert sha(ROOT/e['path'])==e['sha256']
        d={'candidate_id':ident,'subject_sha256':binding(r),'reviewer_kind':'ai_adjudication_not_human','reviewed_on':'2026-10-28',
           'final_label':'faithful','semantic_comparison':note,'prior_model_concern_resolution':resolution,
           'quantifier_domain_assumption_evidence':r['expected_lean_statement'],'strength':'No unexplained restriction, hypothesis or conclusion difference identified.',
           'counterexample_scope':'Fresh strict reference/type checks plus existing manually specified bounded probes; absence of a finite counterexample is supplementary only.',
           'family':family,'split':split,'family_decision':'Binomial and linear-solvability relatives grouped conservatively; remaining families are distinct targets, not grouped by merely sharing a tactic or a broad subject.',
           'remaining_uncertainties':[],'limitations':policy['limitations']}
        adjudications.append(d)
        r['study_eligibility']={'policy_version':policy['version'],'subject_sha256':binding(r),'split':split,'family':family,
            'reviewer_kind':'ai_adjudication_not_human','semantic_label':'faithful','remaining_semantic_uncertainties':[],
            'human_review_completed':False,'source_evidence':evidence,'proof_evidence_path':proofpath,'proof_evidence_sha256':sha(ROOT/proofpath),
            'source_assessment':'AI-assisted published-license evidence assessment; retain attribution and each original item license, including CC BY-SA adaptations. No independent human/source permission claimed.'}
        selected.append(r)
    assert len(selected)==75 and len(DEV)==15 and DEV<={r['id'] for r in selected}
    (BASE/'adjudications.json').write_text(json.dumps(adjudications,ensure_ascii=False,indent=2)+'\n')
    (BASE/'excluded.json').write_text(json.dumps(excluded,indent=2)+'\n')
    (BASE/'correction_history.json').write_text(json.dumps(history,ensure_ascii=False,indent=2)+'\n')
    freeze={'schema_version':1,'status':'frozen_under_ai_assisted_policy','frozen_on':'2026-10-28',
       'approval_record_sha256':sha(BASE/'approvals/student_reported.json'),'policy_sha256':sha(BASE/'ai_eligibility_policy.json'),
       'adjudications_sha256':sha(BASE/'adjudications.json'),'splits':{},'historical_curation_human_fields':'preserved_not_used_as_AI_approval',
       'split_selection_basis':'Chosen before any primary model proof generation; entire related families allocated together; earlier assignments were provisional, never frozen or used for primary proof tuning.'}
    for split in ['development','test']:
        subset=sorted([r for r in selected if r['study_eligibility']['split']==split],key=lambda r:r['id']);path=BASE/(split+'.json')
        path.write_text(json.dumps(subset,ensure_ascii=False,indent=2)+'\n')
        freeze['splits'][split]={'ordered_ids':[r['id'] for r in subset],'sha256':sha(path),'count':len(subset)}
    (BASE/'freeze.json').write_text(json.dumps(freeze,indent=2)+'\n')
    report=validate_freeze();(BASE/'dataset_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))

if __name__=='__main__':main()
