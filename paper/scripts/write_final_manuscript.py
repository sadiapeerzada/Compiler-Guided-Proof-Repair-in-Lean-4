"""Write the empirical manuscript only from completed validated study artifacts."""
from pathlib import Path
import json
import sys
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'src'))
from final_study import BASE,read,sha,validate_protocol

def main():
    protocol=ROOT/'configs/repair_experiment_local_v0.4.2.json';p=validate_protocol(protocol);r=read(BASE/'analysis/results.json')
    if r['protocol_sha256']!=sha(protocol):raise ValueError('Empirical analysis does not match final frozen protocol')
    author=read(BASE/'author_metadata.json');m=r['conditions'];pair=r['comparisons'][0]
    hardware=read(BASE/'hardware_runtime.json');rendered=read(BASE/'analysis/rendered_evidence.json')
    repetition=rendered['posthoc_repeated_candidate_diagnostic']
    percent=lambda x:f'{100*x:.1f}'
    pvalue=lambda x:'non-informative' if x is None else f'{x:.5g}'
    rates=', '.join(f'{c}: {m[c]["successes"]}/60 ({percent(m[c]["success_rate"])}\\%)' for c in ['A','B','C'])
    ci=pair['family_cluster_bootstrap_95']
    if pair['concordant_problem_test_and_cluster_interval_evidence']:
        conclusion=('The observed C--B difference favors '+('compiler-guided' if pair['difference_missing_as_failure']>0 else 'blind')+' repair, with concordant problem-test and cluster-interval evidence under the stated assumptions.')
    else:conclusion='The recorded experiment does not establish a robust advantage for compiler feedback; a non-significant or non-informative test is not evidence of equivalence.'
    replacements={'AUTHOR':author['author_name'],'EMAIL':author['corresponding_email'],'RATES':rates,
       'DIFF':f'{100*pair["difference_missing_as_failure"]:+.1f}','LO':f'{100*ci[0]:+.1f}','HI':f'{100*ci[1]:+.1f}',
       'P':pvalue(pair['exact_mcnemar_p']),'PHOLM':pvalue(pair['holm_adjusted_p']),'COMPLETE':str(pair['complete_pairs']),
       'CONCLUSION':conclusion,'CALLS':f'{r["actual_unique_generation_calls"]:,}',
       'ATTEMPTS':f'{r["actual_unique_generation_attempts"]:,}',
       'PARTIALTOK':str(rendered['observed_partial_generation_tokens']),
       'INTOK':f'{r["actual_unique_prompt_tokens"]:,}','OUTTOK':f'{r["actual_unique_completion_tokens"]:,}',
       'INCOMPLETE':str(r['incomplete_trajectories']),'PROTOCOLHASH':sha(protocol),
       'EXAMPLES':str(len(read(BASE/'analysis/rendered_evidence.json')['selected_examples'])),
       'CPU':hardware['cpu_brand'],'RAM':str(hardware['physical_memory_bytes']//(1024**3)),
       'REPEATB':str(repetition['byte_identical_to_previous']['B']),'REPEATC':str(repetition['byte_identical_to_previous']['C']),
       'REPAIRB':str(repetition['completed_repair_generations']['B']),'REPAIRC':str(repetition['completed_repair_generations']['C']),
       'FREEZEHASH':p['freeze_sha256'],'MODELREV':p['model']['snapshot_revision'],
       'INVENTORYHASH':p['model']['inventory_sha256'],'MATHLIB':p['mathlib_revision']}
    text=r'''\documentclass[runningheads,a4paper]{llncs}
\usepackage[T1]{fontenc}
\usepackage{graphicx,booktabs,url,xurl}
\setlength{\emergencystretch}{3em}
\begin{document}
\title{Compiler-Guided Repair for Natural-Language-to-Lean Formalization}
\titlerunning{Compiler-Guided Lean Proof Repair}
\author{@@AUTHOR@@}
\authorrunning{S. Peerzada}
\institute{\email{@@EMAIL@@}}
\maketitle

\begin{abstract}
We execute a paired local-model study of one-shot proof generation (A), blind
repair (B), and compiler-guided repair (C) for natural-language statements
paired with fixed Lean theorem types. B and C reuse exactly the same failed
initial candidate and permit at most three repairs each. The frozen dataset
contains 60 test statements and 15 development statements across five
categories, screened under an explicitly AI-assisted semantic policy.
Using one hash-pinned 4-bit Qwen2.5-7B instruction model, the observed verified
success counts are @@RATES@@. The C--B difference is @@DIFF@@ percentage points;
the 95\% family-cluster bootstrap interval is [@@LO@@, @@HI@@] points.
@@CONCLUSION@@ We preserve raw model responses, compiler diagnostics, token
streams, stopping events and checkpoints. The evidence concerns fixed-type
proof synthesis, not unrestricted generation of faithful formal statements.
Single-seed inference, related theorem families, author-assisted AI adjudication,
and library/pretraining exposure limit generalization.
\keywords{Lean 4 \and compiler feedback \and proof repair \and local inference \and semantic review}
\end{abstract}

\section{Introduction and Research Questions}
An informal mathematical statement can be paired with a formal theorem type
yet still lack a proof accepted by a theorem prover. A generated proof may fail
because of syntax, unavailable names, type mismatches, an incomplete tactic
argument, or a mathematical mistake. A compiler supplies concrete evidence about
these failures, but additional generation alone may also repair them. A useful
comparison must distinguish diagnostic feedback from the benefit of more calls.

Our primary question is whether compiler-guided repair improves verified
success over equally budgeted blind repair, conditioned on the same initial
candidate. Secondary questions compare each repair condition with one-shot
generation and describe outcomes by initial error category. We do not assume
that feedback helps, or interpret a failure to reject as equivalence. The
experimental unit is a theorem trajectory, not an individual repair attempt.

The evaluated stage receives both English and a fixed AI-reviewed Lean type.
It therefore tests proof synthesis and repair within an NL-to-Lean workflow.
It does not measure unconstrained English-to-theorem translation, independent
semantic-review accuracy, or state-of-the-art mathematical problem solving.

\section{Related Work}
Lean 4 provides a dependently typed language and kernel-checked proof
infrastructure~\cite{demoura2021lean4}; Mathlib supplies the mathematical
library used here~\cite{mathlib2020}. Benchmarks such as
miniF2F~\cite{zheng2022minif2f} support formal theorem-proving evaluation,
while ProofNet studies paired informal and formal
mathematics~\cite{azerbayev2023proofnet}. LeanDojo studies tool-supported
theorem proving and retrieval~\cite{yang2023leandojo}. These settings motivate
careful separation of problem statements, proof generation, library access and
verification. Our experiment is a bounded paired comparison using a general
local instruction model. It includes no retrieval service, proof search tree,
fine-tuning, or paid hosted inference, and should not be compared directly with
systems using different tasks, data or compute budgets.

\section{System Architecture and Verification}
The pipeline loads immutable English/type pairs, renders an initial prompt,
generates one candidate, extracts the requested Lean block, and verifies it
against the fixed reference type. A and both repair branches share the exact
initial bytes and SHA-256. Each repair uses a fresh model conversation and
independent context-derived random stream. B receives the theorem, its current
candidate and fixed blind-feedback text. C receives the same template structure
with structured diagnostics from its immediately preceding failed compilation.
Neither branch receives the other branch's candidates or conversation.

The strict verifier rejects placeholder proofs and unauthorized declarations,
checks the exact elaborated theorem type, and inspects target axiom dependencies.
Only the standard \texttt{propext}, \texttt{Classical.choice} and
\texttt{Quot.sound} dependencies are accepted. A reference placeholder is used
only to compare types in a separate namespace; it is never counted as a target
proof, and a target depending on \texttt{sorryAx} is rejected. Compiler JSON,
source text, exit status, failure kind and elapsed time are stored. Compilation
proves neither the English interpretation nor the quality of explanatory prose.

Source-token and declaration guards run before compilation; axiom-policy
rejection can also occur afterward. Such events are not relabeled as compiler
errors. C stops if genuine candidate diagnostics are unavailable;
it is never supplied an invented compiler message. Timeouts, context-limit
failures and interrupted calls remain explicit missing/incomplete outcomes.

\section{Dataset, Provenance and Semantic Audit}
Starting from 96 prepared candidates, we exclude one exact duplicate and 20
nonduplicate records lacking adequate item-level provenance. The resulting 75
records comprise 16 textbook-derived statements~\cite{levin2021dmoi} and 59
adaptations of pinned formal-library statements. Citations, original source
bytes, license notices and item-level attribution are retained. Textbook
adaptations retain CC BY-SA 4.0 attribution; formal-library material retains
Apache-2.0 notices. These are evidence-based AI-assisted source assessments,
not invented publisher permissions or independent legal clearance.

Two original records were corrected: a positive-modulus premise was restored,
and ambiguous summation endpoints were made explicit. Both proofs were
reverified and both pairs were reviewed again with a separate Phi-4 model.
They remain excluded for source-provenance reasons; corrections were not used
to inflate eligible counts. Original records and before/after histories remain
available.

\input{generated/final_table1.tex}

The approved replacement policy uses explicit AI adjudication of quantifiers,
domains, assumptions, strength, endpoints and equivalent encodings. Phi-3.5 and
Phi-4 audit responses are retained, including schema failures and unsupported
objections. The authoring coding assistant adjudicated the exact selected pairs
using candidate-specific mathematical comparisons and reference evidence. It
is not author-independent human review. An uncertain or unfaithful final
adjudication is inadmissible; unreliable raw AI output is not a faithful vote.

The independent reviewer models were demonstrably fallible: for example, one
claimed that $1(1+1)$ was odd. Exact arithmetic refutes that alleged
counterexample. Generic placeholders, hallucinated hypotheses and proof-method
confusion were separately flagged. All 96 original reference types have strict
Lean evidence; handwritten bounded probes cover 26,467 accepted finite
assignments, with 88 exact predicates and eight approximate numerical probes.
These checks supplement, rather than establish, English equivalence.

Whole binomial, linear-solvability and modular-power families were grouped before
primary-model test access. No curated family crosses splits. The 15 development
statements occupy five conservative family clusters; the 60 test statements
occupy 54. These are not claimed to be 75 independent topic families.
All texts were accessed for authorized curation, but no held-out primary-model
proof outcome was used to select prompts or settings. Ordered IDs and exact
dataset bytes were frozen with cryptographic hashes.

\section{Frozen Experimental Design}
The primary model is \texttt{mlx-community/Qwen2.5-7B-Instruct-4bit}, run
offline with MLX~\cite{qwenmlx,mlxlm}. Its immutable converted snapshot is
\path{@@MODELREV@@}. Inventory hashes bind all weights, tokenizer files and
the native chat template. Quantization is 4-bit with group size 64. MLX 0.32.4,
MLX-LM 0.32.2 and Transformers 5.21.0 are recorded. Decoding uses temperature
0.2, top-$p$ 1, at most 2,000 output tokens and an 8,192-token total context cap.
One primary seed, 2027, is used; three-seed robustness is not claimed.
The local host uses an @@CPU@@ processor with @@RAM@@ GiB physical memory.

The per-call seed is the first unsigned 32-bit word of SHA-256 of the base
seed, phase/problem/condition/step context and exact prompt hash. Consequently,
B's stopping behavior does not shift C's random stream. All conditions use
the same model and environment. A has zero repairs; B and C each permit up to
three, with at most seven logical generations per problem including the shared
initial call. Success stops a branch. Model weights are released during the
memory-heavy Lean check and reloaded from the same verified bytes on the next
call. This preserves independent KV state and incurs measurable loading overhead.

Exploratory development pilots exposed Lean 3-style syntax and high resident
memory cost. Before any held-out generation, the final protocol added the same
explicit Lean 4 syntax instruction to all three conditions and fixed the memory
schedule. This was syntax/implementation development, not test-outcome tuning;
the format diagnostic still failed mathematical verification. Prototypes are
preserved and excluded from study estimates. The final three-case pilot passed
the provenance/control audit, and an actual resume invocation generated no new
calls. No model, prompt, dataset or budget changed after held-out execution began.

Conditions execute B before C rather than in randomized order. Each call has a
durable intent, raw response and token stream; each verification and branch
transition has a checkpoint. Resume reuses completed outputs. An incomplete
generation intent consumes its logical call and is not silently regenerated.
The environment is Lean 4.32.0 with clean Mathlib commit
\path{@@MATHLIB@@}. There is no provider fallback or paid inference path.

\section{Results and Statistical Analysis}
Across all 60 frozen test statements, observed verified success is @@RATES@@.
There are @@INCOMPLETE@@ incomplete trajectories. Table~\ref{tab:abc} uses the
full eligible denominator, treating unavailable outcomes as failures for the
conservative sensitivity estimate; incomplete outcomes are also reported
separately in the artifacts. Figure~\ref{fig:budget} shows cumulative observed
success against the repair budget. Repair calls are adaptive attempts, not
independent samples or additional benchmark problems.
\input{generated/final_missingness.tex}

\input{generated/final_table2.tex}
\begin{figure}[t]
\centering\includegraphics[width=.88\linewidth]{generated/final_success_budget.pdf}
\caption{Observed verified success by maximum repair budget. The budget-zero
point is identical across all conditions because the initial candidate is shared.
Missing outcomes count as failures in this full-denominator display.}
\label{fig:budget}
\end{figure}

The primary C--B comparison has @@COMPLETE@@ complete matched pairs. Its
full-denominator difference is @@DIFF@@ percentage points, with family-cluster
95\% interval [@@LO@@, @@HI@@]. The exact two-sided McNemar $p$ is @@P@@;
the Holm-adjusted value over three planned comparisons is @@PHOLM@@.
@@CONCLUSION@@ Problem-level Wilson intervals and exact McNemar tests assume
independent problem units; related within-family targets limit that assumption.
We therefore report the pre-specified family-cluster sensitivity interval and
do not make an unqualified significance claim. Zero discordance is
non-informative; a degenerate bootstrap interval would not prove equivalence.

\input{generated/final_paired_tests.tex}

Intervals use 10,000 bootstrap resamples and seed 20271021, at problem and
family-cluster levels. Category summaries and error-conditioned outcomes are
descriptive, with actual denominators; no post-hoc subgroup significance claim
is made. The physical run used @@ATTEMPTS@@ generation attempts and @@CALLS@@
completed generations, with @@INTOK@@ known prompt tokens and @@OUTTOK@@
completion tokens from completed generations. Partial streams additionally
preserve @@PARTIALTOK@@ observed generated tokens; those are not completed
responses and are excluded from the completed-call totals. Physical totals count the initial call once; each
counterfactual condition's resource total includes that shared initial cost.
Raw wall, generation and compiler timings are retained. Generation timings
exclude model-loading overhead; trajectory wall times include it. Sequential
condition order, cache state and host activity limit causal latency comparisons.
A read-only process observation during execution also identified a separate
local MLX workload on the same host; its duration and attributable overhead
were not measured, and the unrelated workload was not modified.
A worker interruption required checkpoint recovery. The incomplete generation
was not replayed. Trajectory elapsed time for that case includes the inactive
interval before recovery, so it cannot be interpreted as continuous compute time.
The resource matrix reports known input/output tokens, model-call wall seconds
(including reload overhead), and Lean seconds. An interrupted call without a
recorded endpoint has no invented duration; its trace and missingness remain
explicit in the supplementary resource data.
\input{generated/final_resources.tex}
\input{generated/final_resource_distributions.tex}
\input{generated/final_repair_calls.tex}

\section{Compiler Errors and Qualitative Analysis}
Table~\ref{tab:errors} groups failed initial candidates into a single primary
category using a fixed message taxonomy; Figure~\ref{fig:errors} shows verified
repair outcomes. Parser, unknown-name, type/elaboration and tactic/goal failures
are distinguished. Safety guards and infrastructure failures are separate from
compiler errors. The artifact also records all attempted-candidate error events;
those repeated events are not independent problem observations.
As a post-hoc process diagnostic, @@REPEATB@@ of @@REPAIRB@@ completed B repairs
and @@REPEATC@@ of @@REPAIRC@@ completed C repairs were byte-identical to the
preceding candidate. These counts describe repetition, not additional tests or
independent samples.

\input{generated/final_table3.tex}
\begin{figure}[t]
\centering\includegraphics[width=.88\linewidth]{generated/final_error_outcomes.pdf}
\caption{Verified B/C repair outcomes by primary initial failure category.
The denominator for each group is given in Table~\ref{tab:errors}; small groups
are illustrative rather than inferential.}
\label{fig:errors}
\end{figure}

The following @@EXAMPLES@@ examples are authentic recorded outputs, selected post hoc
to cover available outcome types, initial error classes and mathematical
categories, then dataset order. Selection does not
change the statistical sample. A blind-only success displays its last B output;
otherwise the last available C output is displayed, followed by B or the shared
initial when C made no attempt. The branch and verifier outcome are explicit.
Code/diagnostic snippets are
truncated and ASCII-transliterated for typesetting only; complete original
Unicode bytes, prompts and diagnostics remain in the run artifacts.
\input{generated/final_qualitative.tex}

\section{Semantic Faithfulness and Threats to Validity}
\input{generated/final_table4.tex}
Successful proofs must have the exact reviewed reference type; changing a
quantifier, adding a hypothesis or weakening the conclusion cannot substitute
for solving that target. Nevertheless, faithfulness to English remains
conditional on the AI-adjudicated reference. We report review coverage and
provenance, not independently measured semantic accuracy. No AI output is
represented as an independent human judgment.

The authoring/adjudicating assistant can share systematic biases with the
dataset construction process. Separate Phi reviewers were unreliable, and
bounded mathematical probes are not exhaustive proofs of informal meaning.
Source/library exposure and direct named-lemma reuse may affect performance;
the dataset is not a contamination-free benchmark. Curated family boundaries
are mathematical judgments, not guarantees of statistical independence. The
development set has only five family clusters, and results use one model,
one quantization, one primary seed and one local hardware setting. The model's
knowledge can predate the pinned Lean/Mathlib interfaces. Fixed call and context
caps can stop repair without exhausting mathematical possibilities. These
limits preclude broad claims about compiler feedback, larger models or
unrestricted NL-to-formal translation.

\section{Reproducibility and Authorization Provenance}
All results derive from the frozen protocol and ordered dataset, with durable
raw generations, compiler JSON, exact sources, token counts, timings, failures
and resume checkpoints. Protocol SHA-256 is
\path{@@PROTOCOLHASH@@}; dataset-freeze SHA-256 is
\path{@@FREEZEHASH@@}; model inventory SHA-256 is
\path{@@INVENTORYHASH@@}. The pre-held-out source commit and launch time,
complete test outputs, source/evidence hashes and PDF build manifest are included.
Original Groq and exploratory local protocols remain available for provenance.

The student reported supervisor approval of AI-assisted semantic review and
free local MLX substitution on 28 October 2026. The original decision date,
document and signature were not supplied; approval is not claimed independently
verified. Exact implementation choices were frozen under the user's execution
authorization. No publisher permission or human review was fabricated. AI tools
assisted construction, adjudication and inference; they are not credited as
authors. The supplied author name and correspondence are used without inventing
an institutional affiliation.

\section{Conclusion}
This study records a controlled local comparison of one-shot, blind and
compiler-guided proof repair for 60 fixed theorem targets with shared initial
candidates. @@CONCLUSION@@ The contribution is the reproducible paired evidence
and its failure analysis under a clearly delimited low-resource configuration,
not a claim of general superiority, independent human semantic validation, or
complete unconstrained natural-language formalization.

\bibliographystyle{splncs04}
\bibliography{references}
\end{document}
'''
    for name,value in replacements.items():text=text.replace('@@'+name+'@@',value)
    if '@@' in text:raise ValueError('Unfilled empirical manuscript placeholder')
    (ROOT/'paper/main.tex').write_text(text)
    evidence={'results_sha256':sha(BASE/'analysis/results.json'),'protocol_sha256':sha(protocol),
        'rendered_evidence_sha256':sha(BASE/'analysis/rendered_evidence.json'),'hardware_metadata_sha256':sha(BASE/'hardware_runtime.json'),
        'source_commit_before_heldout':read(BASE/'heldout_launch.json')['source_git_commit'],
        'quantitative_substitutions':replacements,'main_tex_sha256':sha(ROOT/'paper/main.tex'),
        'author_metadata_sha256':sha(BASE/'author_metadata.json')}
    (ROOT/'paper/generated/final_claims_manifest.json').write_text(json.dumps(evidence,indent=2)+'\n')
    print('Empirical manuscript written from actual validated results.')

if __name__=='__main__':main()
