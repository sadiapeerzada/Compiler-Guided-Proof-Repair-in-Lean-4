# Publication-safety and research-integrity review

Reviewed commit: `3b4909a20ed24cafd36cbe029a81f8946bc96d69`.
Review date: 29 October 2026. No inference, push, merge, or submission was performed.
Original study files, failed attempts, manifests, freeze, protocol and identifiable
12-page manuscript remain byte-for-byte preserved. The source branch is retained.
New material is confined to this review directory and a separate publication worktree.

## Safety scan

The read-only Git-blob scan covered all **5,632 tracked files / 52,140,883 bytes**:
5,620 UTF-8 files, five PDFs (text and metadata), and seven PNGs (metadata plus
visual inspection of all seven). Local results contain paths, categories, line
locations and hashes, not detected credential values. Raw outputs, compiler logs,
datasets, approval records, manifests and author metadata are included in that scope.

| Finding | Files | Assessment and release treatment |
|---|---:|---|
| Recognized credential tokens/private-key blocks | 0 | None detected; no available-environment credential value matched tracked bytes |
| Credential-assignment pattern | 4 | Two authorization-prose false positives; two test files use literal `test-key` placeholders; no real credential confirmed |
| Home-directory paths | 1,841 | Private username/home paths in diagnostics, nested prompts, manifests and logs; redact derivative final-study views, exclude original logs/history |
| Private study-owner identifier | 1,854 | Mostly repeated home-path identifiers, also author metadata; remove author/contact identifiers in the public copy |
| Email addresses | 12 | Repeated study contact and a published textbook contact; exclude original identifiable PDF/metadata and full textbook PDF; remove contact text in exported views |
| Confidentiality marker | 49 | All are upstream mathematical copyright headers with “All rights reserved” followed by explicit Apache-2.0 notice; no confidentiality requirement found |
| License/rights markers | 1,291 | Retain item-level terms/notices; exclude unneeded full archives and source-insufficient candidates |
| Temporary paths | 10 | Replace in derivative views where included |
| IP-like patterns | 3 | Third-party HTML; all three files excluded from the release |

Supplemental checks found no labeled phone/home-address/identity-document data or
signed/secret query parameters. No confidential research prose was identified.
Public scholarly author names and copyright attributions are retained rather than
mistakenly removed as private study-author information. This is a heuristic and
content review, not proof that arbitrary secrets or unlabelled personal data cannot exist.

Local details: `local/tracked_file_scan.json`, `local/supplemental_scan.json`.
Existing untracked `.DS_Store` files were left untouched and are excluded.

## Missing C outcomes: no safe recovery under the frozen protocol

The original tokenizer was loaded offline without loading model weights or generating
tokens. Reconstructed C1 prompts match the original durable intent hashes.

| Case | Input tokens | Evidence | Recovery decision |
|---|---:|---|---|
| `lib_a_trig_unit` | 9,653 | Explicit context-budget failure; no response or token stream | Input alone exceeds the 8,192 cap, before the 2,000 output reservation. Shortening diagnostics or changing limits changes frozen inputs. Do not replay. |
| `lib_i_bernoulli` | 2,205 | Durable intent and one stream-header frame; zero durable tokens; no completion/failure record | No candidate, token history, KV/RNG checkpoint or completed response is available to verify/resume. The frozen runner treats incomplete intent as consumed and terminal. Do not replay. |

No matching completed response exists elsewhere in final-run evidence for either
logical context. The worker interruption's cause is unknown; shared-host activity
does not establish causation. Both cases have completed failed B branches.
Selective reruns, repeating the same seed, smaller prompts/output caps, extra calls,
or resetting terminal states would violate the recorded no-replay protocol. New
inference belongs in a separately versioned follow-up study, never backfilled here.

Local evidence: `local/integrity_review.json`, `local/integrity_review.log`.

## Denominators and statistical interpretation

| Condition | Verified successes | Known failures | Unavailable | Observed denominator | Full eligible denominator |
|---|---:|---:|---:|---:|---:|
| A | 0 | 60 | 0 | 60 | 60 |
| B | 1 | 59 | 0 | 60 | 60 |
| C | 1 | 57 | 2 | 58 | 60 |

The reported C=1/60 (1.67%) and its Wilson interval are **missing-as-failure
sensitivity**, not 60 measured C outcomes. A and B each have 60 measured outcomes.
On the **58 complete pairs**, both B and C succeed on the same single problem:
each is 1/58 (1.72%), with zero discordant pairs. Complete-case selection does not
establish missing-at-random or family independence.

The frozen McNemar helper records `null` for zero discordance, documenting a
non-informative test. The conventional numerical value is p=1; neither means
equivalence. The Holm helper retains all three planned comparisons internally,
including the null slot as p=1 for multiplicity accounting. No significance is
established. The 412 generation-attempt count is a count of durable logical intents,
not 412 confirmed executions: one rejected during context preflight and another
has no durable completion. Exactly 410 completed held-out responses are evidenced. Wilson/problem-level tests assume independent problem units; 60 test
statements occupy 54 curated families, and family-cluster sensitivity is reported.

The C−B percentile interval [0,0] is conditional on missing-as-failure coding and
zero observed discordance. It is **not** an uncertainty bound for missing C results.
Because both missing cases failed in B, the logically possible full-cohort C−B
difference is **0 to +3.33 percentage points**. These are identification bounds,
not confidence limits. A C-vs-A gain of 1.67 points is likewise not statistically
supported (recorded exact p=1 and Holm p=1). The correct conclusion is an
inconclusive, very-low-success study, not evidence that compiler feedback is
generally ineffective or that the two repair strategies are equivalent.

## M3, M6 and M7

| Requirement | Status | Precisely what remains |
|---|---|---|
| M3 controlled A/B/C execution | PARTIAL | Shared initial/model/environment, latest C diagnostics, B isolation and call/output caps validate. Only 58 fully observed pairs; two C trajectories stopped under explicit protocol rules. The frozen final pilot planned and completed three cases, whereas the broader user request asked for every development example. One seed was frozen; three-seed replication is not claimed. Complete equal realized repair budgets cannot be claimed for unavailable C trajectories. No permissible backfill exists. |
| M6 verification and reproducibility | PARTIAL overall; local scientific checks PASS | Full suite 293 tests/28 subtests; Lean build 8,658 jobs; original dataset/protocol/artifact validators pass. Both successful model candidates freshly recompiled against exact targets and allowed axioms. Original whitespace findings are evidence formatting, not mathematical failures; no historical bytes were normalized. Public redacted views intentionally cannot pass original-byte prompt/source dependency hashes or exact inference replay; 172 C prompts changed through path redaction. Public aggregate/pairing checks pass and original full reproduction remains local. |
| M7 manuscript and public/submission readiness | PARTIAL | Original 12-page PDF accurately reports low success, missingness, one seed, related families, AI adjudication, fixed-type task, pretraining/library exposure, sequential B-before-C and shared-host timing. It needed explicit complete-case rates and missingness bounds beside its degenerate interval, and accurate public-data availability wording. A separate anonymized 12-page review revision supplies these. Original author/contact data remain excluded; final author/affiliation, submission category, final editorial/rights decisions and publication approval remain. No blanket project license existed; no license grant is invented. |

The original M1/M2/M4/M5 labels remain scoped to the frozen AI-assisted study,
not a certification of independent human semantics, legal clearance or an
unconstrained NL-to-statement benchmark. Automated tests do not complete M3 or M7.

## Manuscript and references

The separate public-review PDF retains A=0/60, B=C=1/60 sensitivity, 58 complete
pairs, the two named missing cases, one seed, five development/54 test family
clusters, genuine resource accounting, four main tables, two figures and five
post-hoc authentic examples. It adds complete-case 1/58, missingness bounds,
the 9,653/2,205-token forensic findings and the limits of redacted public replay.
PDF text checks confirm the numbers, anonymous author, no unresolved references
or placeholders, and no private author/home-path strings. Only bibliography
underfull-box warnings remain. The original source/PDF is untouched.

Previously listed but uncited directly relevant work was checked against primary
records and discussed in the review revision: [APRIL](https://arxiv.org/abs/2602.02990)
and [Beyond Compilation](https://arxiv.org/abs/2606.31002). Primary records also
confirm [ProofNet](https://arxiv.org/abs/2302.12433) and
[miniF2F](https://arxiv.org/abs/2109.00110). No reference was invented or replaced
with an unsupported result claim.

## Licensing and release policy

The 75 eligible records preserve item-level attribution/change notices: 16
textbook adaptations under CC BY-SA 4.0 and 59 formal-library derivations under
Apache-2.0. All 75 have nonempty required-attribution and change fields. The
release includes upstream license texts and copyright headers rather than full
archives. [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) requires
attribution, indication of changes and share-alike for adaptations;
[Apache-2.0](https://www.apache.org/licenses/LICENSE-2.0) requires its license and
applicable attribution/notice retention, including change notices. Their scopes
are not conflated with a blanket license for unrelated project code.

No root project license was present. No new reuse grant for original code or
manuscript, and no automatic legal clearance for model-generated material, is
asserted. Model weights/tokenizers, Springer class/style binaries and complete
publisher/provider archives are excluded. Publication approval must cover the
specific redacted evidence payload; the manuscript's final author details and
optional project-wide reuse license remain separate decisions.

## Exact release boundary and verification

`PUBLIC_RELEASE_MANIFEST.json` in the publication worktree assigns a disposition
and original SHA-256 to every one of the 5,632 source tracked files. Baseline
dispositions: 3,307 excluded, 781 exported unchanged and 1,544 exported as
redacted/derived views. Additional public-review reports and verifiers are newly
authored and enumerated in `PUBLIC_PAYLOAD_MANIFEST.json`; that final inventory,
not these baseline counts, defines the exact approval payload.

The final-protocol held-out/pilot evidence is exported under `evidence/redacted_runs/`.
Original candidates are encoded as JSON strings; all **410 held-out candidate
hashes still match**. Paths in diagnostics/prompts are redacted only in views.
Original embedded hashes, seeds and token counts remain unchanged and clearly
refer to private original bytes. Public validation checks all 60 case outcomes,
410 completed calls, B isolation and C immediately preceding feedback.
It does not falsely certify changed prompts as original-byte copies.

The separate branch is an **orphan root with anonymous Git author/committer**;
it has no ancestral research commits to leak when eventually pushed. The private
research branch and original Git objects remain local and untouched. No branch
or tag has been pushed. Approval will be requested for only this root branch's
hash-enumerated files, not private history, original logs or author metadata.

Verification evidence is in `local/`: fresh Python/Lean logs, artifact validation,
success reverification, public reanalysis, public manuscript build/text checks,
source-preservation checks and final public privacy/payload checks. These local
logs themselves are not part of the public payload.
