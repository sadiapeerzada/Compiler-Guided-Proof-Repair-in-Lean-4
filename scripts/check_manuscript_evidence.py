#!/usr/bin/env python3
"""Read-only navigation check for the two-study manuscript evidence bundle.

No model calls, Lean execution, network access, hashing, data modifications or
claims of scientific reproducibility. A successful run means referenced local
paths exist and selected Markdown links are not broken.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]

# Exact Table 10 paths, kept in manuscript order.
MANUSCRIPT_TABLE_10 = (
    "research/study2-v7/test/outcomes.csv",
    "research/study2-v7/test/plan.json",
    "research/study2-raw-v8-v9",
    "analysis/taimma_20261104",
    "analysis/taimma_supervisor_final",
    "analysis/taimma_final_professor_validation",
)

# Supporting navigation used in the paper-facing README.
SUPPORTING_PATHS = (
    "research/study2-v7/test/REPORT.md",
    "research/study2-raw-v8-v9/ARCHIVE_INDEX.json",
    "research/study2-raw-v8-v9/PRIVACY_SCAN_WARNINGS.json",
    "analysis/taimma_20261104/FINDINGS.md",
    "analysis/taimma_20261104/results/V7_paired.md",
    "analysis/taimma_20261104/results/V7_theorems.md",
    "analysis/taimma_20261104/results/V7_costs.md",
    "analysis/taimma_final_professor_validation/OverlapCertificates.lean",
    "analysis/taimma_final_professor_validation/REPRODUCIBILITY_FINAL_VERIFICATION.md",
)

DOCUMENTATION = (
    "README.md",
    "docs/MANUSCRIPT_EVIDENCE_INDEX.md",
    "docs/REPOSITORY_GUIDE.md",
    "docs/ARCHIVE_SCOPE.md",
    "docs/RESEARCH_DIAGRAMS.md",
    "docs/RELEASE_READINESS.md",
    "docs/HISTORICAL_DOCUMENTS_INDEX.md",
)

LINK_PATTERN = re.compile(r"\[[^\]\n]+\]\(([^\s)]+)(?:\s+[^)]*)?\)")


def find_link_issues(source: Path) -> list[str]:
    """Check local Markdown link destinations without following external URLs."""
    problems: list[str] = []
    for match in LINK_PATTERN.finditer(source.read_text(encoding="utf-8")):
        destination = match.group(1)
        if destination.startswith(("#", "https://", "http://", "mailto:")):
            continue
        destination = unquote(destination.split("#", 1)[0].split("?", 1)[0])
        if not destination:
            continue
        target = (source.parent / destination).resolve()
        if not target.is_relative_to(ROOT.resolve()):
            problems.append(f"{source.relative_to(ROOT)}: link leaves repository: {destination}")
        elif not target.exists():
            problems.append(f"{source.relative_to(ROOT)}: broken link: {destination}")
    return problems


def main() -> int:
    problems: list[str] = []
    for label, paths in (("Table 10", MANUSCRIPT_TABLE_10), ("supporting", SUPPORTING_PATHS)):
        for relative in paths:
            exists = (ROOT / relative).exists()
            print(f"{'PASS' if exists else 'FAIL'} [{label}] {relative}")
            if not exists:
                problems.append(f"Missing {label} path: {relative}")

    for relative in DOCUMENTATION:
        source = ROOT / relative
        if not source.is_file():
            problems.append(f"Missing documentation file: {relative}")
            continue
        broken = find_link_issues(source)
        print(f"{'FAIL' if broken else 'PASS'} [local Markdown links] {relative}")
        problems.extend(broken)

    if problems:
        print("\nFailed checks:")
        for problem in problems:
            print(f"  - {problem}")
        return 1
    print("\nAll Table 10 paths and checked local documentation links exist.")
    print("This is NOT a statistical, hash, privacy, Lean, or inference verification.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
