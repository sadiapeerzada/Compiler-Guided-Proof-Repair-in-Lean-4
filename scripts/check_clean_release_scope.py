#!/usr/bin/env python3
"""Check supervisor clean-release path boundary without touching evidence."""
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
EXCLUDED = ("paper/", "submission_20261031/", "submission_20261103/",
            "publication/paper/", "publication/post_hoc/paper/")
EVIDENCE = ("research/study2-v7/test/outcomes.csv",
            "research/study2-v7/test/plan.json",
            "research/study2-raw-v8-v9/ARCHIVE_INDEX.json",
            "analysis/taimma_20261104/FINDINGS.md",
            "analysis/taimma_supervisor_final/CASE_STUDIES.md",
            "analysis/taimma_final_professor_validation/OverlapCertificates.lean")
NOTICES = ("docs/ARCHIVE_SCOPE.md", "docs/figures/README.md",
           "data/review_packets/ARCHIVE_STATUS.md",
           "data/analysis/ARCHIVE_STATUS.md",
           "research/ai-confirmatory-study/ARCHIVE_NOTICE.md")
FIGURES = ("docs/figures/pass_at_1_by_category.png",
           "docs/figures/pass_at_1_by_difficulty.png",
           "docs/figures/repair_attempts_histogram.png",
           "docs/figures/difficulty_vs_repairs.png")

def main() -> int:
    raw = subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT)
    paths = {p.decode("utf-8", "surrogateescape") for p in raw.split(b"\0") if p}
    violations = [p for p in paths if p == "RUN_REPORT.md" or p.startswith(EXCLUDED)
                  or p.lower().endswith((".tex", ".bib"))]
    missing = [p for p in (*EVIDENCE, *NOTICES, *FIGURES)
               if p not in paths or not (ROOT / p).is_file()]
    if violations or missing:
        if violations:
            print("FAIL excluded paths:", *sorted(violations)[:30], sep="\n")
        if missing:
            print("FAIL missing paths:", *missing, sep="\n")
        return 1
    print("PASS: obsolete report/manuscripts excluded; evidence and archive notices retained")
    print("Scope: path checks only — not verification of privacy, rights or model inference")
    return 0

if __name__ == "__main__":
    sys.exit(main())
