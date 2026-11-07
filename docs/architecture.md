# Architecture and figures — historical prototype

> **Historical stage document.** The four PNGs at [docs/figures/](figures/README.md)
> came from an early manually authored Lean example; they are not LLM pass@1,
> controlled-repair results or the three figures in the current paper. The old
> `RUN_REPORT.md` is excluded from the current checkout; its historical
> content is [available at the pre-cleanup commit](https://github.com/sadiapeerzada/Compiler-Guided-Proof-Repair-in-Lean-4/blob/a201fbd38ff730eacaf0025b874192285debd9ca/RUN_REPORT.md). Old statements
> about missing study results below describe that prototype phase only; use
> the [current manuscript evidence index](MANUSCRIPT_EVIDENCE_INDEX.md).

## Pipeline diagram
Already in the main README as a Mermaid diagram. For a paper/slide deck,
re-render it as a clean vector figure (draw.io or a quick matplotlib/graphviz
box diagram) — reviewers don't render Mermaid.

## Figures already generated (n=20, core-Lean run)

Real PNGs, built directly from `data/results/run1_core_lean.jsonl`, live in
`docs/figures/`:
- `pass_at_1_by_category.png`
- `pass_at_1_by_difficulty.png`
- `repair_attempts_histogram.png`
- `difficulty_vs_repairs.png`

All four are currently flat 100%-solved bars (see `RUN_REPORT.md` for why
that number needs an asterisk at this scale) — they'll become genuinely
informative once you're running at n=50+ with a real API-driven pipeline,
where pass@1 should actually vary by category and difficulty. Regenerate
them any time with:

```bash
python3 -c "
import json, matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from collections import defaultdict
results = [json.loads(l) for l in open('data/results/run1_core_lean.jsonl')]
# ... see git history / RUN_REPORT.md for the exact plotting code used
"
```
(or just re-run the eval pipeline on a new results file and adapt the four
plotting blocks — they're short and not worth turning into a CLI flag until
there's a second dataset to compare against).

## Figures to generate once you have `results/run_n500.jsonl`

1. **Pass@1 by category** — grouped bar chart, x-axis = category
   (arithmetic_identity, divisibility, modular_arithmetic, induction, ...),
   y-axis = % solved. This is the single most important chart in the writeup.

2. **Pass@k curve** — line chart, x-axis = k (1, 2, 3, 5, 8), y-axis = % of
   problems solved within k total attempts (initial + repairs count as
   attempts here, OR run k independent full pipelines per problem and take
   best-of-k — decide which definition you're using and say so explicitly,
   these are different metrics).

3. **Repair-attempts-to-success histogram** — x-axis = number of repair
   attempts needed (0 through 5), y-axis = count of problems. A pipeline
   that's actually adding value should show most solved problems needing
   1-3 repairs, not 0 (0 repairs everywhere across a hard set is suspicious —
   check you're not accidentally testing on easy problems only).

4. **Failure taxonomy pie/bar** — statement-wouldn't-elaborate vs.
   wrong-tactic vs. unfinished-goal vs. timeout vs. exhausted-repairs. Compute
   this from `eval/metrics.py` output plus manual inspection of a sample of
   `data/results/attempts/*.jsonl`.

5. **Difficulty vs. pass@1** — scatter or line, x = difficulty (1-5),
   y = % solved. Expect a downward trend; if it's flat, your difficulty
   labels aren't discriminating and should be recalibrated.

Generate these with matplotlib directly from `eval/metrics.py` output (add a
`--plot` flag once the pipeline has run at n=500) or in a throwaway notebook —
either way, save the raw numbers alongside the images so someone can
regenerate the chart without re-running the whole pipeline.
