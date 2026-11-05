# Consolidated fresh compute request — no inference authorized yet

Starting point: `83f1d564`. Old V1/V2/V3 allocations and clocks are never reused.
The master task explicitly requires researcher approval of new ceilings. This file
is a proposal, not an approval, resource signature or permission to load models.

Proposed cohorts are 20 independent development types and 60 fresh confirmatory
types, each with seeds 2037, 2038 and 2039. These meet the lower ends of the requested
ranges. Candidate acceptance is not guaranteed. Actual independent counts and
precision must be assessed before confirmatory outcomes; quotas never justify
duplication or weaker validation. Worst-case paired unit differences in [-1,1]
give an approximate 95% half-width of 25.3 percentage points at 60 independent
theorem clusters, or 28.9 points using the two-contrast Bonferroni normal benchmark.
These are conservative precision planning approximations, not power guarantees
or the bootstrap intervals that will be computed from actual outcomes.

Every model call: **at most 4,096 input / 1,200 output tokens**. C/D/E repair inputs
must be exactly 4,096 rendered tokens under the pinned tokenizer. No truncation is
used to force a candidate or diagnostic into the allocation.

| # | Separately capped phase | Maximum calls | Phase wall-clock limit | Model key |
|---|---|---:|---:|---|
| 1 | Fresh development benchmark generation | 240 | 24 hours | G |
| 2 | Development reference-proof repair, at most one per candidate | 120 | 12 hours | P |
| 3 | Reviewer 1: V3 subphase2 calls plus fresh-development subphase240 calls | 242 | 30 minutes +8 hours, separate predeclared clocks | R1 |
| 4 | Reviewer 2: V3 subphase2 calls plus fresh-development subphase240 calls | 242 | 30 minutes +8 hours, separate predeclared clocks | R2 |
| 5 | Development initial proof generation, at most20 types ×3 seeds | 60 | 6 hours | X |
| 6 | Development C/D/E repairs, at most one per arm/unit | 180 | 12 hours | X |
| 7 | Confirmatory benchmark construction, separately capped below | 2,100 total | 78 hours summed subphase ceilings | G/P/R1/R2 |
| 8 | Confirmatory initial proof generation, at most60 types ×3 seeds | 180 | 18 hours | X |
| 9 | Confirmatory C/D/E repairs, at most one per arm/unit | 540 | 36 hours | X |

Phase 7 sublimits are **600 generation calls /36h**, **300 one-step reference
repairs /18h**, **600 reviewer-1 calls /12h**, and **600 reviewer-2 calls /12h**.
Each subphase has its own persisted clock and ledger. No sublimit can borrow from
another. All 2,100 are benchmark construction calls, never evaluation calls.

Likewise, phases3/4 each have a two-call V3-review subphase with a30-minute clock,
then a separately declared240-call fresh-development-review subphase with an8-hour
clock. This lets V3 review happen first without resetting an elapsed review clock
after intervening generation. Each distinct subphase starts once; none transfers
unused calls or renews the other. Both are included in the242-call aggregate cap.

Full proposal: **3,904 calls maximum**, up to 15,990,784 input and 4,684,800 output
tokens at the per-call ceilings. Development-only approval covers phases 1–6,
**1,084 calls maximum**. Approval for V3 review only means precisely **two R1 and
two R2 calls**, each reviewer phase limited to **30 minutes**, and no fresh
generation, proof repair, development evaluation or confirmatory inference.

## Pinned models

| Key | Model | Exact cached revision |
|---|---|---|
| G | mlx-community/Qwen2.5-7B-Instruct-4bit | c26a38f6a37d0a51b4e9a1eb3026530fa35d9fed |
| P | mlx-community/Phi-4-mini-instruct-4bit | ac1c269cb4222a4e136a3d09edad301056c1f36a |
| R1 | mlx-community/Phi-4-mini-instruct-4bit | ac1c269cb4222a4e136a3d09edad301056c1f36a |
| R2 | mlx-community/Qwen2.5-Coder-7B-Instruct-4bit | 019cc73c45c770444708a6dd8690c66243cc5c80 |
| X | mlx-community/Qwen2.5-7B-Instruct-4bit | c26a38f6a37d0a51b4e9a1eb3026530fa35d9fed |

P changes the repair model from the unsuccessful V3 coding-model repairs; this is
a prospective development choice, not a claim that Phi repairs will succeed.
Reviewers have different model families, but G shares Qwen ancestry with R2 and
P shares weights with R1. Their error independence is not established. Review
processes receive neither another review nor a reference proof, generation prompt
or proof-repair response. AI-only review is never represented as human validation.

## Estimated local usage and uncertainty

All models are local cached 4-bit checkpoints; no cloud-model fees, API transport
or model downloads are proposed. V3 observed MLX-reported peaks were approximately
4.7–5.2GB for its Qwen models. Phi weights occupy about2.2GB; live Phi memory and
review throughput have not yet been measured. Whole-process/RSS usage can be higher
than MLX memory. A planning allowance of roughly12–16GB available RAM for one model
plus Lean is an estimate, not a measured requirement or guarantee. Use one model
at a time and release it between stages.

The full capped workflow is a multi-day local workload: a rough planning range is
50–150 hours, highly dependent on parse yield, strict-verifier timeouts, accepted
counts, initial-success rates and actual review/C/D/E throughput. Per-phase hard
limits above bound it even if this estimate is wrong. The sum of full phase limits
is203 hours. Development-only work is also substantial. The four-call V3 review
subset is expected to take minutes, with two independent30-minute phase ceilings.
Electricity cost and system-wide memory are unmeasured. Limits are ceilings, not
promises to spend the entire allowance or guarantees of a completed cohort.

## Checkpoints, gates and failure policy — applies to every phase

- Approval must be recorded from the actual researcher response. Proposal files,
  test fixtures, mathematical AI judgments and previous approvals cannot open a gate.
- Freeze phase prompts, model revisions, source hashes, cohort/input bindings and
  donor rules before the affected calls. Freeze the confirmatory protocol and
  final sample size before evaluation outcomes. No inspected V3 subject enters test.
- Reserve each logical call before inference in an exclusive append-only ledger;
  preserve raw prompt/response bytes, hashes, stream, seed, token counts and timing.
- An interrupted intent remains charged and cannot be regenerated. A completed
  response may be reread. Unknown formal checks remain unknown. No automatic
  transport/model retry or replacement response is permitted.
- A phase clock starts once, on that phase's first actual launch. It is never reset,
  including after suspension/interruption. Kill the active inference worker at
  expiry; launch no more calls. No phase transfers unused calls to another.
- Stop an affected phase on new unavailable model/verifier infrastructure or
  nonconforming metadata. Diagnose it, preserve the complete outstanding grid,
  and resume only unconsumed work within the original limits after resolution.
- Invalid or over-budget records are rejected/skipped with exact reasons; do not
  silently truncate. Ordinary mathematical/semantic rejection does not trigger a
  new approval request or an artificial stop after each success.
- No AI adjudication beyond the approved review limits; no development without
  strictly verified, AI-screened accepted subjects; no D arm without a genuine
  eligible disjoint-family donor; no confirmatory inference without approved
  confirmatory limits and a valid prospective freeze. Gates take precedence over
  numerical targets, even when the researcher approves the full ceilings.

The consolidated approval choices are: all proposed ceilings, phases1–6 only, or
only the four blinded V3 reviews under their smaller30-minute phase limits. The
researcher may instead specify narrower per-phase limits in free text. No option
is assumed approved until an explicit response is received.
