# Editable research diagrams

[Main README](../README.md) · [Evidence index](MANUSCRIPT_EVIDENCE_INDEX.md) · [Repository guide](REPOSITORY_GUIDE.md)

These **Mermaid source diagrams** render directly in GitHub Markdown, are editable without proprietary design files, and visualize **documented protocols and evidence relationships**. They are not a rerun, new analysis or reproduction of manuscript figure pixels.

## 1. Bounded fixed-statement proof repair

```mermaid
flowchart TD
    T["Fixed Lean theorem type"] --> I["Generate shared initial proof"]
    I --> L["Strict Lean verification"]
    L -->|"Pass"| OK["Verified success: stop"]
    L -->|"Fail"| F["Record failed initial candidate"]
    F --> B["B: neutral retries"]
    F --> C["C: actual compiler diagnostics"]
    F -.-> S["Study 2: D shuffled / E padded / R resample"]
    B --> V["Strict verify after each attempt"]
    C --> V
    S --> V
    V -->|"Success or ≤ 3 repairs exhausted"| OUT["Record final outcome and cost"]
```

**Scope:** For Study 1 A simply stops after the initial verification and repair policy B/C is evaluated from the common failed candidate. Study 2 adds D/E/R and uses separate theorem types and model runs. Later histories diverge and the maximum retry count is not a total-token match.

## 2. Study / model / evaluation-unit map

```mermaid
flowchart TB
    Q["Feedback attribution in Lean proof repair"] --> P["Study 1: 60 held-out types"]
    Q --> F["Study 2: 24 constructed types"]
    P --> P1["Qwen2.5-7B, one seed"]
    P1 --> P2["A initial / B neutral / C matched"]
    F --> F1["V7: base Qwen2.5-7B"]
    F --> F2["V8: exploratory Coder-7B"]
    F -.-> F3["V9: 12 development-only cases"]
    F1 --> F4["3 reused seeds = 72 dependent cells"]
    F2 --> F5["3 reused seeds = 72 dependent cells"]
    F4 --> F6["A / B / C / D / E / R"]
    F5 --> F6
```

**Not permitted:** Combining all rows into one independent-problem count. V7 and V8 reuse the same constructed theorems; Study 1 uses its own separate cohort.

## 3. Evidence provenance and what verification means

```mermaid
flowchart TB
    H["Frozen protocols & held-out records"] --> V7["V7: outcomes.csv and plan.json"]
    H --> V8["V8/V9: indexed archive and hash manifest"]
    V7 --> A["Post-hoc paired / coverage / cost analyses"]
    V8 --> A
    A --> M["Manuscript tables and figures"]
    H --> S["Supervisor case and integrity audit"]
    S --> M
    H --> C["Lean overlap relationship certificates"]
    C --> M
    P["Historical release / redacted Study 1 views"] --> M
    M --> I["Table 10 evidence index"]
```

**Interpretation:** This is a documentation dependency map. A file path existing is not a hash check; a matching hash is not a regenerated response; a successful Lean certificate check is not full historical candidate replay; a formally related pair of statements is not proof of benchmark independence or human adjudication.

## 4. Interpretation hierarchy

```mermaid
flowchart LR
    T["Proof text changed"] --> E["Compiler error changed"]
    E --> V["Original target strictly verifies"]
    V --> K["Count unique solved theorem types"]
    K --> U["Consider paired dependence and uncertainty"]
    U --> C["Report actual tokens / resource cost"]
```

The arrows are **questions to check**, not causal or logical implications. Text and errors can change without verified success. Verification counts do not automatically represent broad theorem coverage, significant improvement, or matching-compute efficiency.

## Source links

The diagrams summarize [Study 1 public release](../publication/README.md), [Study 2 protocol](../research/study2-v7/test/plan.json), [V7/V8 analyses](../analysis/taimma_20261104/FINDINGS.md) and the [final validation scope](../analysis/taimma_final_professor_validation/README.md). They are not substitutes for the manuscript's original Figures 1–3 or audit input files.

*For publication-quality vector art, render/redraw only the conceptual protocol in the manuscript's chosen visual style. Do not turn this conceptual map into experimental outcome evidence.*