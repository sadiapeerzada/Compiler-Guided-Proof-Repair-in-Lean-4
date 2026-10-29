# Final paper readiness

Status: PARTIAL — a compiled pre-results draft, not submission-ready.

`paper/main.tex` now documents the current candidate inventory, source/proof preparation, independent review workflow, shared A/B/C design, proposed local Qwen/MLX model configuration, exact model identity and decoding/seed policy, statistics, compiler-error taxonomy, semantic faithfulness, qualitative evidence limitations, threats and reproducibility. The original Groq protocol is described as historical/proposed, not silently replaced by an approved local study.

Dataset Table 1 and semantic-review Table 4 are generated from current candidate records and validated automated proof overlays. They are construction/review inventories, not eligible-dataset results. Table 2, Figure 1, compiler-error results and inferential statistics remain explicitly unavailable. Historical manually authored snippets remain labeled as truncated ASCII-transliterated illustrations; none satisfies the requirement for five authentic model repair examples.

An actual PDF build succeeded with Tectonic 0.17.0 and the official Springer LNCS/CCIS class 2.25 (3 September 2026), retrieved from Springer's author-resource page. The release binary digest, template ZIP/class/style hashes and actual build logs are in `data/verification/m1_m7_20261027/`. Tool/template binaries remain local rather than assuming redistribution permission. Missing Lean glyphs and table/hash overflow observed in the first build were corrected. A first-page preview was inspected; remaining underfull-box warnings are recorded, not treated as empirical validation.

Sources: [Springer proceedings author resources](https://link.springer.com/series/558/information-for-authors-and-editors); [official Tectonic releases](https://github.com/tectonic-typesetting/tectonic/releases). The downloaded class is applicable to Springer computer-science proceedings including CCIS; conference-specific page limits and submission details still need confirmation.

Submission blockers: zero eligible/frozen/reviewed data, no approved local substitution/protocol, no genuine mathematical pilot or paired held-out results, no authentic model repair examples, missing author/affiliation/correspondence metadata and final independent claims review. PDF compilation is not submission readiness. Bibliographic sources from the earlier audit were retained; Qwen snapshot card and MLX-LM repository citations were added without invented authors, dates or DOIs.

The delivery draft reports 96 strict reference proofs and zero independent reviews/eligibility. The explicit geometric-sum context is included without claiming independent semantic approval. The final PDF is `paper/compiled_pre_results.pdf`; it remains a pre-results artifact. Final build/source hashes are recorded in the delivery build manifest.
