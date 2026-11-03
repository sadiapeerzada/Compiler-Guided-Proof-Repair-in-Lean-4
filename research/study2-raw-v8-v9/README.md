# V8/V9 raw research evidence — public archive

## Contents
These archives contain byte-preserved **local** Study 2 V8 Coder experimental records,
AI reviewer raw responses, Lean reference checks, validation manifests, V9 development-only
repair records, and the exact replay scripts used locally. The archive index enumerates
SHA-256 for each evidence file, and each ZIP part has a separate SHA-256.

**Verification:** `python3 study2_publish_v8_v9.py verify --packet <this directory>`
validates the archive hashes and every file member against `ARCHIVE_INDEX.json`.
The 40 paths listed in the frozen V8 lock were verified against the original Mac
files *before packing*. Full model inference requires compatible MLX/Lean, model
weights and pinned dependencies; the model weights and system caches are **not** included.

The original 60-theorem study, base-model V7 and the V8/V9 follow-up are distinct.
Study 2 V8 was exploratory and not preregistered. Study 2 V9 used 12 development
cases only, not a fresh held-out test. The constructed benchmark's English text
is placeholder material and does not validate English-to-Lean semantic fidelity.
AI reviewer flags, possible test/dev family overlap and training contamination
remain unresolved; this evidence release does NOT sign off benchmark validity.

**Privacy:** High-confidence token patterns were automatically scanned; that scan
cannot detect all personal, secret, licensed or restricted material. Consult
`PRIVACY_SCAN_WARNINGS.json` and manually inspect the raw evidence before release.
Do not claim the full source experiment was independently rerun just because
archival checksums verify. No files in this package rewrite frozen originals.
