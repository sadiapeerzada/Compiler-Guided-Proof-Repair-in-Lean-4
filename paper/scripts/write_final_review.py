"""Write the revised empirical pilot manuscript from validated review-v2 metrics."""
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'data/final_review/20261029_v2'


def main():
    results=BASE/'analysis_verified/results.json';r=json.loads(results.read_text());m=r['conditions'];pair=r['comparisons'][0]
    # Start from the already public, anonymized manuscript; never resurrect author metadata.
    text=subprocess.check_output(['git','show','b5c7a638db02b8f7c39a09be626cae583d5e89ac:paper/main.tex'],cwd=ROOT,text=True)
    text=text.replace(r'\title{Compiler-Guided Repair for Natural-Language-to-Lean Formalization}',r'\title{Compiler-Guided Repair for Natural-Language-to-Lean Formalization}\subtitle{A Fixed-Theorem Local-Model Pilot}')
    abstract=r'''\begin{abstract}
We compare no-repair generation (A), blind retry (B), and Lean-compiler-guided
repair (C) for English statements paired with fixed reviewed theorem types.
B and C start from identical failed candidates, use one hash-pinned 4-bit
Qwen2.5-7B instruction model, and allow at most three repair calls under common
context/output caps. Of 60 held-out statements, A verifies 0/60 and B 1/60;
C verifies 1/58 observed outcomes, with two unavailable outcomes. On the 58
complete paired trajectories, B and C each verify 1/58 (1.72\%): the paired
difference is 0.00 percentage points, with no discordant pairs. A degenerate
conditional bootstrap interval does not establish equivalence or account for
missingness. Full-cohort identification bounds are 0 to +3.33 points for C--B.
Counting unavailable C outcomes as failures yields the separately planned
1/60 sensitivity estimate. We report genuine outputs, compiler errors, resource
usage and failure cases rather than a demonstrated feedback benefit. One seed,
a three-case development pilot, low success, related families, author-assisted
AI review and privacy-limited public replay restrict the conclusions. The task
is fixed-type proof synthesis; autonomous NL-to-statement and end-to-end accuracy
are not measured.
\keywords{Lean 4 \and proof repair \and compiler diagnostics \and local inference \and negative results}
\end{abstract}'''
    text=re.sub(r'\\begin\{abstract\}.*?\\end\{abstract\}',lambda _:abstract,text,flags=re.S)
    text=text.replace('All texts were accessed for authorized curation, but no held-out primary-model',
        'All texts were accessed for authorized curation, but no held-out primary-model')
    text=text.replace('dataset bytes were frozen with cryptographic hashes.',
        'dataset bytes were frozen with cryptographic hashes. The source commit and local\nlaunch record precede held-out inference. No evidence establishes public publication\nof the IDs/hash before testing; this is an internal freeze, not external preregistration.')
    text=text.replace('three, with at most seven logical generations per problem including the shared',
        'three, with at most seven logical generation intents per problem including the shared')
    text=text.replace('All conditions use\nthe same model and environment.',
        'All conditions use\nthe same model and environment. The common caps are a prompt budget, not equal\nrealized input-token cost: genuine C diagnostics lengthen prompts, and one C\nprompt exceeds the cap before generation. A token-cost-matched effect is not measured.')
    text=text.replace('The final three-case pilot passed\nthe provenance/control audit,',
        'The final pilot covers only three of the fifteen development cases and passed\nthe provenance/control audit,')
    text=text.replace('generated/final_table1.tex','generated/review_v2/table1.tex')
    results_text=r'''\section{Results and Statistical Analysis}
Table~\ref{tab:abc} distinguishes observed outcomes from missingness. A succeeds
0/60 (0.00\%); B succeeds 1/60 (1.67\%); C succeeds 1/58 observed outcomes
(1.72\%), with 57 known failures and two unavailable outcomes. Wilson intervals
are [0.00,6.02]\% for A, [0.29,8.86]\% for B, and [0.31,9.14]\% for observed C.
They assume independent problem units; related family clusters limit that assumption.

\input{generated/review_v2/table2.tex}

\subsection{Matched effects and uncertainty}
On 58 complete pairs, B and C each succeed on the same single target,
\texttt{lib\_a\_exp\_add}. The C--B risk difference is 0.00 percentage points,
with zero discordant pairs. The frozen exact McNemar helper stores a null,
non-informative result; the conventional numerical value is $p=1$. Neither
convention supplies evidence of equivalence. Both problem and family-cluster
bootstrap intervals are [0.00,0.00] points, conditional on those observed pairs.
This degeneracy reflects identical observed outcomes, not high precision about
a general feedback effect.

\input{generated/review_v2/paired.tex}

The revised paired point estimates, intervals and tests use the same complete
cases for each contrast. For C--A this is 58 pairs (difference +1.72 points);
for B--A it is 60 (+1.67 points). Both exact $p$ values and Holm-adjusted values
are 1. The three planned comparisons remain in multiplicity accounting; the
non-informative C--B slot is conservatively treated as 1 internally, but still
reported as non-informative. Bootstrap sensitivity uses 10,000 resamples and
seed 20271021. The complete C contrasts have 52 represented family clusters;
the full test cohort has 54. Resampling cases or families does not remove
selection bias from unavailable outcomes. No statistically supported improvement
is claimed; low success and only one solved target give limited power.

\subsection{Unavailable outcomes and sensitivity}
The frozen protocol explicitly planned both complete-pair inference and a
full-denominator missing-as-failure sensitivity. The latter is C=1/60 (1.67\%),
with Wilson interval [0.29,8.86]\%, and is not the observed C rate. Both missing
C cases failed in B. If neither missing C outcome would succeed, the full-cohort
C--B difference is zero; if both would succeed it is +3.33 percentage points.
These are identification bounds, not confidence limits. The zero bootstrap
interval does not cover this missingness uncertainty.

For \texttt{lib\_a\_trig\_unit}, the exact C1 prompt has 9,653 input tokens,
already exceeding the 8,192-token context cap before reserving 2,000 output
tokens. The recorded preflight rejection produced no response. For
\texttt{lib\_i\_bernoulli}, C1 has 2,205 input tokens but only a stream header
survives, with zero durably observed generated tokens. No candidate is available
to verify. The terminal no-replay rule forbids either retry; changing diagnostics,
caps or the seed would change the frozen study. The interruption cause is unknown.

\begin{figure}[t]
\centering\includegraphics[width=.9\linewidth]{generated/review_v2/success_budget.pdf}
\caption{Verified success versus allowed repair calls on the same 58 complete
trajectories for all curves and budgets. B and C overlap. The displayed axis is
0--5\%. The two unavailable C trajectories are excluded at every budget; this
complete-case display does not assume they are missing at random.}
\label{fig:budget}
\end{figure}

\subsection{Attempts, tokens and latency}
The ledger contains 412 logical generation intents and 410 completed responses:
60 shared initial outputs, 178 B repairs and 172 C repairs. C has 174 repair
intents, including its preflight rejection and header-only interruption. An
intent is not a confirmed completed inference call. B completes a mean 2.97
repairs per eligible problem; C completes 2.87 (2.90 consumed intents). Both
repair-count medians are three. Physical completed-call totals count the shared
initial once: 362,035 input tokens, 130,401 output tokens and 11,233.6 native
generation seconds. Counterfactual condition rows each include their initial.
No unavailable response tokens or duration are invented.

\input{generated/review_v2/resources.tex}
\input{generated/review_v2/matched_resources.tex}

Call wall time includes model loading; native generation time excludes it.
The table reports completed-response costs only, not unknown full-run costs.
Sequential B-before-C execution, cache state and an observed unrelated MLX
workload confound causal latency comparisons. Recovery elapsed time includes an
inactive interval and is not continuous compute. The diagnostic input overhead
also prevents reading this as an equal-total-token-cost comparison.
'''
    text=re.sub(r'\\section\{Results and Statistical Analysis\}.*?(?=\\section\{Compiler Errors)',lambda _:results_text,text,flags=re.S)
    error_text=r'''\section{Compiler-Error Taxonomy}
Table~\ref{tab:errors} uses the frozen deterministic primary taxonomy: parser
errors take precedence, then unknown names, type/elaboration errors, tactic/goals,
and other errors. Each failed initial belongs to one group. It includes 26 parser,
20 unknown-name, nine tactic/goal, four type/elaboration and one other failure.
The only solved target is in the unknown-name group (B=C=1/20 there); all other
groups have zero observed repairs that verify. C is unavailable in one parser
and one tactic/goal case, so their observed denominators are 25 and eight.
These descriptive counts do not support error-specific superiority claims.

\input{generated/review_v2/table3.tex}
\begin{figure}[t]
\centering\includegraphics[width=.9\linewidth]{generated/review_v2/error_rates.pdf}
\caption{Observed repair-success fractions by primary initial error. B/C use
their observed denominators in Table~\ref{tab:errors}; the two missing C outcomes
remain explicit. No subgroup hypothesis tests are added.}
\label{fig:errors}
\end{figure}

Representative diagnostics identify unavailable symbols, malformed syntax,
ill-typed applications and unsolved proof obligations. Such messages identify an
obstacle but do not supply a correct mathematical argument or a working lemma.
Unknown identifiers and unknown theorem names are not reliably distinguishable
from compiler wording alone; tactic and unsolved-goal messages can co-occur.
A separate, explicitly post-hoc message-tag artifact records these overlapping
subtypes and genuine examples, without replacing the pre-specified primary groups.
No compiler timeout was observed among the completed candidates; the context
rejection is a generation resource failure, not a Lean error. Failed model
outputs and their actual diagnostics remain retained, including repeated errors.

\section{Qualitative Repair Cases}
Five authentic cases were selected post hoc for outcome, category and error
coverage. There is only one distinct solved test target; five successes are not
claimed. Each example displays the actual immediately preceding candidate,
its real compiler message, and the last recorded repair. A blind case's compiler
message is shown for analysis only: B did not receive it. Excerpts are limited
to five lines and 58 characters per line, with ASCII display transliteration;
full original candidate bytes and hashes remain in the evidence. A byte-identical
retry is a genuine observed non-change, not a manufactured repair.
\input{generated/review_v2/qualitative.tex}
'''
    text=re.sub(r'\\section\{Compiler Errors.*?(?=\\section\{Semantic Faithfulness)',lambda _:error_text,text,flags=re.S)
    text=text.replace('generated/final_table4.tex','generated/review_v2/table4.tex')
    text=text.replace('Successful proofs must have the exact reviewed reference type;',
        'Historical coding-AI assessments label 94 original references faithful, one\nnot faithful, and one uncertain. The unfaithful example, \\texttt{mod\\_001},\nomits the English positive-modulus restriction in Lean; the uncertain example,\n\\texttt{ind\\_001}, leaves summation endpoints ambiguous. Both were corrected\nand rechecked, but remain excluded for source provenance. Twenty nonduplicate\nsource-insufficient items and one exact duplicate are excluded overall. Selected\n75/75 faithful AI adjudications are eligibility decisions, not measured accuracy.\nThe reference-review labels are not model-generated statement translations;\nautonomous Stage-A and end-to-end semantic accuracy are not measured.\n\nSuccessful proofs must have the exact reviewed reference type;')
    text=text.replace('source/evidence hashes and a release build manifest accompany the review bundle. Original complete test logs and historical exploratory evidence remain local.',
        'source/evidence hashes and a release build manifest accompany the review bundle.\nOriginal complete test logs and historical exploratory evidence remain local.\nThe original reference batch was freshly recompiled, and both successful model\ncandidates were reverified against the exact targets and allowed axioms.\nReconstruction checks every completed token journal against its raw response,\nre-tokenizes all prompts offline, and regenerates metrics deterministically.\nRaw-evidence whitespace is preserved; editable source whitespace is checked separately.')
    text=text.replace('This study records a controlled local comparison',
        'This internally frozen, single-seed empirical pilot records a controlled local comparison')
    text=text.replace('not a claim of general superiority, independent human semantic validation, or',
        'not a claim of general superiority, equivalence, independent human semantic validation, or')
    # Check the values hand-formatted for prose against the actual generated evidence.
    assert [m[c]['successes'] for c in ['A','B','C']]==[0,1,1]
    assert [m[c]['observed_denominator'] for c in ['A','B','C']]==[60,60,58]
    assert pair['complete_pairs']==58 and pair['risk_difference_complete_case']==0
    for c in ['A','B','C']:
        ci=m[c]['wilson_95_observed'];expected=[f'{100*x:.2f}' for x in ci]
        # All displayed interval endpoints are explicitly checked before writing.
        assert expected=={'A':['0.00','6.02'],'B':['0.29','8.86'],'C':['0.31','9.14']}[c],(c,expected)
    (ROOT/'paper/main.tex').write_text(text)
    manifest={'analysis_sha256':hashlib.sha256(results.read_bytes()).hexdigest(),'main_tex_sha256':hashlib.sha256(text.encode()).hexdigest(),
              'primary_estimand':'Complete matched B/C cases','observed_rates':{c:[m[c]['successes'],m[c]['observed_denominator']] for c in m},
              'sensitivity_C':[1,60],'new_inference':False,'author_contact_withheld':True}
    (BASE/'manuscript_claims.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print('Revised anonymized pilot manuscript written with explicit observed and sensitivity denominators.')


if __name__=='__main__':main()
