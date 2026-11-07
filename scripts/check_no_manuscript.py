#!/usr/bin/env python3
"""Fail when tracked manuscript sources or compiled paper artifacts reappear."""
from pathlib import PurePosixPath
import subprocess
import sys

FORBIDDEN_PREFIXES = (
    "paper/",
    "publication/paper/",
    "publication/post_hoc/paper/",
    "publication/source_snapshot/paper/",
    "submission_",
    "publication/post_hoc/outputs/post_hoc/manuscript/",
    "publication/post_hoc/outputs/post_hoc/manuscript_named/",
)
MANUSCRIPT_PDFS = {
    "main.pdf", "compiled_pre_results.pdf", "final_manuscript.pdf",
    "publication_review.pdf", "post_hoc_pilot.pdf", "post_hoc_pilot_anonymous.pdf",
}

def main() -> int:
    tracked = subprocess.check_output(["git", "ls-files", "-z"])
    paths = [p.decode("utf-8", "surrogateescape")
             for p in tracked.split(b"\0") if p]
    bad = [p for p in paths if (
        p.lower().endswith((".tex", ".bib"))
        or p.startswith(FORBIDDEN_PREFIXES)
        or PurePosixPath(p).name.lower() in MANUSCRIPT_PDFS
    )]
    if bad:
        print("FAIL: tracked manuscript materials remain:\n" + "\n".join(bad))
        return 1
    print("PASS: no tracked LaTeX sources, bibliographies, or manuscript PDFs")
    return 0

if __name__ == "__main__":
    sys.exit(main())
