#!/usr/bin/env bash
# Safe launch interface for V7. Invoked as: bash study2_v7_launcher.sh screen|study|status
# Runs in a CHILD Bash shell. Errors do not terminate the user's interactive zsh.
set -euo pipefail

ACTION="${1:-status}"
case "$ACTION" in screen|study|status) ;; *)
  printf 'Usage: bash %s [screen|study|status]\n' "${0##*/}" >&2
  exit 64;;
esac

REPO="${STUDY2_REPO:-$HOME/NLP-to-Formal-Language-Proof}"
if [[ ! -d "$REPO/lean_project" || ! -f "$REPO/src/verify.py" ]]; then
  printf 'Repository not found at: %s\nSet STUDY2_REPO to the correct local path.\n' "$REPO" >&2
  exit 2
fi
cd "$REPO"
SCRIPT=study2_supervisor_suite_v7.py
EXPECTED_SHA=a5cc110d387331e9aaf4a2909c52a3cf9a87c5a6daa9feadf01eb5b438359edc
OUT=study2_outputs/bridge_v7_base

if [[ ! -f "$SCRIPT" && -f "$HOME/Downloads/$SCRIPT" ]]; then
  cp "$HOME/Downloads/$SCRIPT" "$SCRIPT"
  echo 'Copied V7 from ~/Downloads.'
fi
if [[ ! -f "$SCRIPT" ]]; then
  printf 'Missing %s. Download the V7 script and place it in the repository root or ~/Downloads.\n' "$SCRIPT" >&2
  exit 2
fi
ACTUAL_SHA="$(shasum -a 256 "$SCRIPT" | awk '{print $1}')"
if [[ "$ACTUAL_SHA" != "$EXPECTED_SHA" ]]; then
  printf 'V7 SHA-256 mismatch: expected %s, found %s. Not running a modified/incorrect V7 file.\n' "$EXPECTED_SHA" "$ACTUAL_SHA" >&2
  exit 2
fi

if [[ ! -f .venv-study2/bin/activate ]]; then
  echo 'Missing .venv-study2. Do not reinstall blindly; inspect your repository setup.' >&2
  exit 2
fi
# shellcheck disable=SC1091
source .venv-study2/bin/activate

echo "V7: $EXPECTED_SHA"
echo "Repository: $PWD"
echo "Action: $ACTION"

if [[ "$ACTION" == status ]]; then
  python - "$OUT" <<'PY'
import json, sys
from pathlib import Path
out=Path(sys.argv[1]);folder=out/'reference_screen'
files=sorted(folder.glob('bridge_t[0-9][0-9].json'))
passed=0
for p in files:
    try:
        data=json.loads(p.read_text(encoding='utf-8'))
        if data.get('lean_statement_elaborates') and data.get('verification',{}).get('success'):
            passed+=1
        else:
            print('FAILED:', p.stem, data.get('verification'))
    except Exception as e:
        print('UNREADABLE:', p.name, type(e).__name__, str(e)[:200])
print(f'Test references: {passed}/{len(files)} verified; target 24/24')
print('Frozen plan:', (out/'plan.json').exists())
report=out/'reports'/'test'/'REPORT.md'
print('Test report:', report if report.exists() else 'not yet available')
PY
  if [[ -f study2_v7_bridge_test.log ]]; then
    printf '\n=== Last lines of test log ===\n'
    tail -n 12 study2_v7_bridge_test.log
  fi
  exit 0
fi

python "$SCRIPT" --mode self-test

if [[ "$ACTION" == screen ]]; then
  echo 'Running test-reference screening only; NO model inference.'
  python "$SCRIPT" \
    --mode screen-test \
    --benchmark bridge \
    --lean-profile bridge-minimal \
    --out "$OUT" \
    2>&1 | tee study2_v7_test_screen.log
  if ! grep -Fq '[Study2] REFERENCE-SCREEN PASS: 24 test proofs' study2_v7_test_screen.log; then
    echo 'Reference-screen success line not found. Do NOT start study.' >&2
    exit 2
  fi
  echo 'REFERENCE SCREEN PASSED: you may now explicitly run: bash study2_v7_launcher.sh study'
  exit 0
fi

# Test inference must be separately initiated by the user, and is BLOCKED
# unless 24/24 reference checkpoints have been verified by V7. V7 repeats
# full fingerprint validation during its own study preflight.
python - "$OUT" <<'PY'
import json,sys
from pathlib import Path
folder=Path(sys.argv[1])/'reference_screen'
for n in range(1,25):
    id=f'bridge_t{n:02d}'
    p=folder/(id+'.json')
    if not p.exists():
        raise SystemExit(f'BLOCKED: missing verified reference {id}; run screen first.')
    record=json.loads(p.read_text(encoding='utf-8'))
    if record.get('id')!=id or not record.get('lean_statement_elaborates') or record.get('verification',{}).get('success') is not True:
        raise SystemExit(f'BLOCKED: unverified reference {id}; run screen first.')
print('24/24 V7 reference checkpoints pass initial inspection; full fingerprint validation follows.')
PY

if [[ ! -f study2_outputs/bridge_v5_base/reports/development/REPORT.md ]]; then
  echo 'BLOCKED: V5 development report missing; unable to reuse calibration evidence.' >&2
  exit 2
fi

echo 'Starting V7 test inference with V5 development evidence (hash-validated by V7).'
echo 'No modifications to V5/V6 directories or publication/.'
python "$SCRIPT" \
  --mode study \
  --benchmark bridge \
  --lean-profile bridge-minimal \
  --models base \
  --download-models \
  --reuse-dev-from study2_outputs/bridge_v5_base \
  --out "$OUT" \
  2>&1 | tee study2_v7_bridge_test.log

echo 'Study command completed. Inspect study2_outputs/bridge_v7_base/reports/test/REPORT.md and terminal-case completeness.'
