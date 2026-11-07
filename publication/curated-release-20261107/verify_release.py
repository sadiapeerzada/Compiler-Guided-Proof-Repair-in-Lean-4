#!/usr/bin/env python3
"""Check copied CSV digests; does not check historical experiment validity."""
from pathlib import Path
import hashlib, json, sys
root = Path(__file__).resolve().parent
manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
failed = []
for item in manifest["copied_data"]:
    path = root / item["release_path"]
    if not path.is_file():
        failed.append(f"Missing: {item['release_path']}")
        continue
    data = path.read_bytes()
    if hashlib.sha256(data).hexdigest() != item["sha256"] or len(data) != item["size_bytes"]:
        failed.append(f"Digest/size mismatch: {item['release_path']}")
print("PASS: copied CSV digests match manifest" if not failed else "FAIL: " + "; ".join(failed))
print("Digest matching is NOT experiment replay or independent adjudication.")
sys.exit(bool(failed))
