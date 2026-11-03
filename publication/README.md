# Compiler-Guided Proof Repair in Lean 4: A Controlled Local-Model Pilot on Fixed Theorem Types

The latest [post-hoc manuscript](paper/post_hoc_pilot.pdf)
and [exploratory results](post_hoc/outputs/post_hoc/SUMMARY.md) extend the original
fixed-theorem study with process analyses, calibrated uncertainty and a separately
frozen 15-development-problem placebo control. Exact McNemar p=1.0 at zero
discordance does not establish equivalence. The original held-out outcomes are
unchanged. See the [public reproduction boundary](post_hoc/PUBLIC_REPRODUCIBILITY_BOUNDARY.md).
Study 2 model execution remains deferred. This branch is pushed for review;
it does not authorize merging or conference submission.

Run `python3 verify_payload.py` to verify the entire exact public inventory.

---

## Historical approved publication snapshot

# Final review revision: fixed-theorem empirical pilot

**Local revision awaiting fresh publication approval. No push or merge of this revision.**

The canonical revised manuscript is [paper/final_manuscript.pdf](paper/final_manuscript.pdf)
(14 pages). Observed rates are A=0/60, B=1/60, C=1/58 with two unavailable C
outcomes. On 58 complete pairs B=C=1/58 (1.72%); the paired difference is zero
without informative discordance. C=1/60 remains only the planned missing-as-failure
sensitivity. Missingness bounds for the full-cohort C−B effect are 0 to +3.33 points.

Run `python3 reanalyze_review_v2.py` for the revised observed/paired/sensitivity
analysis, and `python3 verify_payload.py` for exact payload and baseline redacted
evidence checks. Latest results: `results/review_v2/`; final evidence-backed gate:
[docs/FINAL_SUBMISSION_GATE.md](docs/FINAL_SUBMISSION_GATE.md).

M1/M2/M3 remain PARTIAL under the exact student-supplied requirements; M4/M5/M6/M7
are COMPLETE in their documented scopes. M6 local original-byte reproducibility
and M7 empirical manuscript rewrite do not imply submission authorization.
Recommendation is NO-GO for a full-compliance submission; the reduced pilot is
ready for supervisor/editorial review. The exact professor correspondence and
original raw logs remain local. Public replay limitations are unchanged.

The original 12-page public review PDF and original analysis remain historical
artifacts. Source/metric changes in this revision do not overwrite old experimental
records or add model attempts. All newly proposed files require fresh approval.

---

## Historical release-v1 description

# Compiler-guided Lean proof repair: publication review bundle

**Local candidate awaiting approval. No push, merge or conference submission.**

The reviewed study has 15 eligible development statements and 60 eligible test
statements, one primary seed, and 58 complete A/B/C comparisons. A succeeds 0/60,
B 1/60, and C 1/60 under missing-as-failure sensitivity. C has only 58 observed
outcomes, with one success and 57 known failures. Among complete pairs B and C
each succeed once (1/58). No advantage or equivalence is established. Unknown C
outcomes leave a full-cohort C−B identification range of 0 to +3.33 percentage
points; the degenerate conditional bootstrap interval does not capture that
missingness uncertainty.

Run `python3 reanalyze.py` for offline outcome, pairing, blind-feedback isolation,
guided-feedback ancestry, original candidate hashes and seed checks. Run
`python3 verify_payload.py` to verify the exact approved payload inventory and
privacy checks. These tools do not invoke model inference or paid services.

- `paper/publication_review.pdf`: anonymized 12-page review revision. Original
  author/contact details and original identifiable PDF are excluded.
- `results/`: case-level outcomes, original numeric analysis with private approval
  wording removed, and the missing-outcome investigation.
- `evidence/redacted_runs/`: final-protocol held-out and pilot evidence views.
  Local home/temp prefixes and private author/contact identifiers are removed.
  Token journals are JSON arrays and candidate source is encoded in JSON.
  Failed attempts and unavailable outcomes remain visible.
- `dataset/`: all 75 eligible source-attributed dataset views and AI adjudications.
  Historical excluded/source-insufficient candidates are not redistributed.
- `source_snapshot/`: scientific source, tests, prompts and environment pins for
  inspection. This is archival source, not a claim that the entire original
  research test suite runs using transformed evidence. The original complete
  suite and Lean build were run against the preserved research checkout.
- `provenance/`: original freeze and model-inventory commitments.
- `third_party/`: upstream license texts, copyright notices and per-item rights.
- `PUBLIC_RELEASE_MANIFEST.json`: decision for every original tracked file.
- `PUBLIC_PAYLOAD_MANIFEST.json`: exact file hashes for this release (excludes
  itself), with the recorded check scope. Release Git history has one anonymous
  root commit and does not inherit private research commits.

**Reproducibility boundary.** No original research bytes were deleted or changed.
Hashes, seeds and token counts embedded in redacted evidence still refer to the
original private prompts/diagnostics. Paths in C feedback affect prompt bytes,
tokenization and context-derived seeds: do not pretend the redacted view is the
original, silently rewrite frozen hashes, or run original validators on it as an
exact copy. Public aggregate reanalysis and redacted trace inspection work;
exact prompt replay, full semantic/source evidence validation and original-byte
artifact validation require privately retained originals. This is an explicit
public reproducibility limitation. The two missing C outputs cannot be filled
under the frozen no-replay protocol. A new study would need a new version.

No weights, personal author/contact data, private approval quotations, full
publisher/provider archives, raw historical logs/prototypes, or private Git
ancestry are included. Redacted final-protocol model/diagnostic views ARE included
in this exact proposed payload and require explicit release approval.

Original project code had no blanket repository license. See
`third_party/RIGHTS_AND_ATTRIBUTION.md`; publication approval does not silently
relicense code or textbook adaptations. CC BY-SA and Apache conditions remain
attached to their respective material. No affiliation, legal clearance,
independent human review or new supervisor approval is invented.

To rebuild the paper, supply Tectonic 0.17.0 and the official Springer proceedings
template externally (class/style binaries are not redistributed). Use
`paper/main.tex`, `paper/references.bib`, and `paper/generated/`; the build manifest
records actual engine/class and input hashes. It does not contain local command
paths or private build logs. Page count is an artifact fact, not venue acceptance.
