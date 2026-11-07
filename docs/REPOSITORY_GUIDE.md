# Repository guide and safe cleanup policy

[Main README](../README.md) · [Manuscript evidence index](MANUSCRIPT_EVIDENCE_INDEX.md) · [Release readiness](RELEASE_READINESS.md) · [Historical documents](HISTORICAL_DOCUMENTS_INDEX.md) · [Diagrams](RESEARCH_DIAGRAMS.md)

## Purpose

This repository has accumulated a pilot, multiple frozen experimental records, historical publication candidates, analysis supplements, development scripts, and reviewer handoffs. A clean **research** repository should not mean deleting old evidence or making the file tree appear simpler at the cost of traceability. Instead, it should:

1. Give a reviewer an unambiguous starting point for the **current two-study** manuscript.
2. Provide stable paths for every manuscript Table 10 artifact.
3. Separate frozen/test evidence, development-only trials, derivative analyses, and historical material.
4. Explain what can and cannot be independently reproduced.
5. Preserve original checksums, commits, provenance, rights and known uncertainties.

The [root README](../README.md) is the paper-facing overview. [MANUSCRIPT_EVIDENCE_INDEX.md](MANUSCRIPT_EVIDENCE_INDEX.md) is the auditable map. This page is the maintainer's orientation and cleanup checklist.

## Recommended navigation

| Path | Classification | Use for the current manuscript? | Notes |
|---|---|---|---|
| [research/study2-v7/test/](../research/study2-v7/test/) | Frozen Study 2 base-model evidence | **Yes** | Plan, outcomes, calls, transitions and report |
| [research/study2-raw-v8-v9/](../research/study2-raw-v8-v9/) | Archived exploratory V8 and development V9 records | **Yes, with scope qualification** | V8 held-out vs V9 dev-only; indexed ZIP and privacy warnings |
| [analysis/taimma_20261104/](../analysis/taimma_20261104/) | Derived post-hoc statistical analysis | **Yes** | Paired/cluster comparisons, coverage, costs, overlap sensitivities |
| [analysis/taimma_supervisor_final/](../analysis/taimma_supervisor_final/) | Supervisor-integrity supplement | **Yes, with provenance qualification** | Cases, tokens, input-context analysis and case excerpts |
| [analysis/taimma_final_professor_validation/](../analysis/taimma_final_professor_validation/) | Scoped mathematical and control-integrity validation | **Yes, with limitations** | Certificates do not independently adjudicate benchmarks |
| [publication/](../publication/) | Historical Study 1 public payload | **Yes for Study 1; historical documentation** | Contains frozen/redacted records and prior submission snapshots |
| Dated submission manuscripts (removed) | Not distributed in current checkout | **No** | Paper source and PDFs are maintained outside this repository |
| Previous paper drafts (removed) | Not distributed in current checkout | **No** | Older Git history may retain copies |
| [docs/reproducibility.md](reproducibility.md) | Original pre-freeze planning instructions | **Historical, not current experiment status** | Opening statement about zero eligible records does not describe current V7/V8 evidence |
| [docs/architecture.md](architecture.md) | Historical prototype figures/notes | **Historical** | Early prototype plots and instructions are not final experiment findings |
| [RUN_REPORT.md](../RUN_REPORT.md) | Early Lean demonstration | **No** | Hand-authored/partly simulated demonstration, not held-out LLM evidence |
| [src/](../src/), [eval/](../eval/), [scripts/](../scripts/), [tests/](../tests/) | Implementation and testing | **With command-specific scope** | Do not assume every historical entry point matches the current study |
| [data/](../data/), [configs/](../configs/), [prompts/](../prompts/) | Multiple snapshots and protocol inputs | **Only with matched manifest/version** | Avoid modifying frozen bytes |
| [lean_project/](../lean_project/) | Lean / Mathlib project | **With pinned toolchain** | Build is distinct from independent experiment replication |

### What was actually cleaned

- Replaced the obsolete pilot-first root README with an accurate **two-study** entry point, verified results tables, current evidence links and two compact Mermaid figures.
- Added [a dedicated Table 10 index](MANUSCRIPT_EVIDENCE_INDEX.md) and [editable diagrams](RESEARCH_DIAGRAMS.md).
- Added a **non-destructive, standard-library-only** documentation/path checker to catch missing evidence links.
- Classified the misleading historical pre-freeze and pilot documents *in navigation* instead of deleting or silently rewriting them.
- **No scientific datasets, model results, archived ZIP members, analysis outputs, protocols, manifests, paper files or validation certificates were removed or rewritten in this cleanup.**

## Maintain a frozen scientific record

**Do not rewrite or casually rename** these classes of files:

- Study 1/publication data views, archived manifests, hashes and associated source attribution.
- V7 plan, held-out outcomes, calls/transitions, or benchmark members.
- V8 indexed ZIP, member index, privacy-warning manifests and V9 development journals.
- Post-hoc CSV/JSON outputs, especially those cited by the manuscript.
- Formal Lean relationship certificate source and recorded check outputs.
- Any file whose digest is referenced in an archived plan or evidence manifest.

If an error is found, document it in a **new**, clearly named erratum or independent follow-up analysis. State the old and new provenance; do not mutate the frozen baseline to make a number appear better.

### Historical versus current papers

The repository contains early, anonymous, reviewed and dated manuscript candidates. Some READMEs still say *Study 2 deferred* or link to an older repository name. Those phrases describe their original **historical snapshot**; they should not be adopted in the current top-level README as up-to-date research status.

The supplied manuscript titled *Compiler Feedback Versus Retry Controls in Lean 4 Proof Repair: Two Local-Model Studies* is the current paper-facing reference for this documentation change. The manuscript source and compiled PDFs are no longer in this checkout; old Git history and external copies need separate handling. Check document title, version, author order and compiled text before calling a file canonical.

## Reviewer tour: six steps

1. Read [root overview and limitations](../README.md).
2. Review the [Table 10 path index](MANUSCRIPT_EVIDENCE_INDEX.md) and confirm the six links.
3. Open [V7 outcomes](../research/study2-v7/test/outcomes.csv) and [V7 plan](../research/study2-v7/test/plan.json).
4. Open [paired results](../analysis/taimma_20261104/results/V7_paired.md), [theorem coverage](../analysis/taimma_20261104/results/V7_theorems.md) and [token costs](../analysis/taimma_20261104/results/V7_costs.md).
5. Inspect [V8 archive/readme](../research/study2-raw-v8-v9/README.md), then [case provenance](../analysis/taimma_supervisor_final/README.md).
6. Inspect [benchmark-validation limits](../analysis/taimma_final_professor_validation/README.md) and [privacy/provenance scope](../analysis/taimma_final_professor_validation/REPRODUCIBILITY_FINAL_VERIFICATION.md).

### Read-only local audit

```bash
git clone https://github.com/sadiapeerzada/Compiler-Guided-Proof-Repair-in-Lean-4.git
cd Compiler-Guided-Proof-Repair-in-Lean-4
python3 scripts/check_manuscript_evidence.py
git status --short
```

This checker requires Python 3 and no optional dependencies, MLX, Lean, tokenizer or inference account. It checks **presence and local documentation links**, not authenticates every scientific record.

## Privacy and publication review

**Existing repository presence does not imply clearance for further sharing.** The indexed archive documents automated local-path warnings and pending manual review. Before any later release, a responsible human should examine warning contexts and licensing/attribution of included third-party material. Do not upload raw, unreviewed local inference files to fix a link.

The historical [rights notice](../publication/third_party/RIGHTS_AND_ATTRIBUTION.md) and [final reproducibility scope](../analysis/taimma_final_professor_validation/REPRODUCIBILITY_FINAL_VERIFICATION.md) constrain what can be claimed. Do not add badges such as "fully reproducible", "independently validated", "all data open", or "accepted" without supporting evidence.

## If further cleanup is proposed

Consider these changes **only in a separate reviewable PR**, after inspecting how they interact with old manifests:

- An archive-specific index for older pre-freeze planning docs, without moving hashed artifacts.
- Separate dependency setup guides for optional MLX vs historical Groq code, with no hidden provider calls.
- Narrow tests for crosslinks, manuscript-to-evidence table consistency and archive metadata.
- The no-manuscript guard (`python3 scripts/check_no_manuscript.py`) to prevent tracking new `.tex`, `.bib`, or manuscript PDFs.

**Avoid** history rewriting, deleting duplicate-looking frozen artifacts, changing seed/denominator labels, moving ZIP files, mass-formatting JSON/CSV, auto-redacting already-published research files without preserving the referenced versions, and replacing a missing original with reconstructed or fabricated data.

## Pre-merge publication checklist

- [ ] All six Table 10 targets are reachable.
- [ ] README explicitly reports 1/58 observed Study 1 C, with two missing.
- [ ] Study 2 outcomes show V7 and exploratory V8 separately; V9 is dev-only.
- [ ] C–D is labeled post hoc and intervals including zero are not called equivalence.
- [ ] "Strict verification" is not misdescribed as NL-to-Lean semantic fidelity.
- [ ] Archive integrity is not conflated with full inference/candidate replay.
- [ ] Unresolved privacy/manual-license review remains prominent.
- [ ] New files are only documentation and read-only checkers; archived data are unchanged.
- [ ] Any CI/check commands actually run are reported with their outcome; do not infer success from a checklist.

*Keep the evidence immutable; make it easier to understand.*

## Presentation hygiene and historical records (November 2026)

The [compact curated release](../publication/curated-release-20261107/) is the reader-facing selection, whereas this full repository also retains original model-input templates, historical development records and independently reviewable experimental provenance. See the [historical document index](HISTORICAL_DOCUMENTS_INDEX.md) for stage-specific instructions and [release readiness](RELEASE_READINESS.md) for the independent review, archive privacy, attribution and supervisor gates that are **not** closed by documentation work. The read-only [audit script](../scripts/audit_publication_surface.py) checks the curated surface separately from the full historical source tree. Do not remove exact experimental inputs or change unresolved outcomes to make a keyword scan pass.
