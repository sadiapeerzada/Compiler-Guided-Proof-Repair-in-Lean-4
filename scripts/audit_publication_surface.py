#!/usr/bin/env python3
"""Read-only public-facing audit and full historical inventory.

This does not establish human review, privacy clearance, license permissions,
scientific validity or independent model replay.
"""
from __future__ import annotations
import argparse
from collections import Counter
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parent.parent
PREFIX = "publication/curated-release-20261107/"
TEXT = {".md", ".txt", ".py", ".json", ".jsonl", ".csv", ".yaml", ".yml", ".tex", ".lean", ".toml", ".sh", ".ini"}
WORDS = re.compile(r"(?i)\b(?:codex|claude|chatgpt|prompts?)\b|human verification pending")
SENSITIVE = re.compile(r"(?i)(?:/Users/[^/\s]+|/home/[^/\s]+|ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----)")
EXPECTED = ("README.md EVIDENCE.md RELEASE_SCOPE.md manifest.json verify_release.py .gitignore "
            "data/V7_outcomes.csv data/V7_paired.csv data/V7_theorems.csv data/V7_costs.csv "
            "data/V7_budgets.csv data/V7_seeds.csv data/V8_paired.csv data/V8_theorems.csv "
            "data/V8_costs.csv data/V8_budgets.csv data/V8_seeds.csv").split()

def tracked():
    output = subprocess.run(["git", "ls-files", "-z"], cwd=ROOT, check=True, capture_output=True).stdout
    return [s.decode("utf-8", "surrogateescape") for s in output.split(b"\0") if s]

def privacy():
    path = ROOT / "research/study2-raw-v8-v9/PRIVACY_SCAN_WARNINGS.json"
    if not path.is_file():
        return {"present": False, "manual_review_required": True}
    doc = json.loads(path.read_text(encoding="utf-8"))
    ws = doc.get("warnings", [])
    return {"present": True, "warning_records": len(ws),
            "occurrences": sum(int(w.get("count", 0)) for w in ws),
            "warning_types": dict(Counter(str(w.get("type", "unknown")) for w in ws)),
            "manual_review_required": bool(doc.get("public_release_requires_manual_review", True))}

def audit(scope):
    all_paths = tracked()
    paths = [p for p in all_paths if p.startswith(PREFIX)] if scope == "curated" else all_paths
    scanned = skipped = 0
    terms = []
    private = []
    for p in paths:
        file = ROOT / p
        if not file.is_file() or (file.suffix.lower() not in TEXT and file.name != ".gitignore") or file.stat().st_size > 2000000:
            skipped += 1
            continue
        try:
            value = file.read_text(encoding="utf-8")
        except (UnicodeError, OSError):
            skipped += 1
            continue
        scanned += 1
        matches = sorted({m.group(0).lower() for m in WORDS.finditer(value)})
        if matches or WORDS.search(p):
            terms.append({"path": p, "terms": matches})
        if SENSITIVE.search(value):
            private.append(p)
    missing = [PREFIX + p for p in EXPECTED if not (ROOT / PREFIX / p).is_file()]
    return {"scope": scope, "tracked_in_scope": len(paths),
            "text_files_scanned": scanned, "skipped_binary_large_or_unreadable": skipped,
            "matched_files_count": len(terms), "matched_files_sample": terms[:20],
            "possible_private_files_count": len(private), "possible_private_files_sample": private[:20],
            "repository_prompt_named_paths": sum("prompt" in p.lower() for p in all_paths),
            "missing_curated_files": missing, "privacy_archive": privacy(),
            "rights_notice_exists": (ROOT / "publication/third_party/RIGHTS_AND_ATTRIBUTION.md").is_file(),
            "review_notice_exists": (ROOT / "analysis/taimma_final_professor_validation/HUMAN_ADJUDICATION_REQUIRED.md").is_file(),
            "publication_clearance": "NOT ESTABLISHED"}

def main():
    a = argparse.ArgumentParser(description=__doc__)
    a.add_argument("--scope", choices=["curated", "full"], default="curated")
    a.add_argument("--strict", action="store_true")
    a.add_argument("--report-json", type=Path)
    args = a.parse_args()
    if args.strict and args.scope != "curated":
        a.error("strict mode tests the selected curated surface, not archival records")
    result = audit(args.scope)
    report = json.dumps(result, indent=2, sort_keys=True) + "\n"
    print(report)
    if args.report_json:
        args.report_json.parent.mkdir(parents=True, exist_ok=True)
        args.report_json.write_text(report, encoding="utf-8")
    if args.strict and (result["matched_files_count"] or result["possible_private_files_count"] or result["missing_curated_files"]):
        print("FAIL: curated file hygiene or inventory")
        return 1
    if args.strict:
        print("PASS: limited curated file hygiene; human/privacy/rights gates remain OPEN")
    else:
        print("INVENTORY ONLY: historical records require contextual classification")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
