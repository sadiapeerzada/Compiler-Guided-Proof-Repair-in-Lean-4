#!/usr/bin/env python3
"""Read-only, explicitly post-hoc sensitivity audit of the frozen V7 test CSV.

Run from any directory:
    python research/study2-final/study2_sensitivity.py

Does not modify datasets, raw outcomes, frozen plans, or the manuscript.
Not valid for the separate V8 Coder run because its row-level outcomes are
not included in the public V7 snapshot.
"""
from __future__ import annotations

import csv
import hashlib
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SOURCE = REPO / 'research/study2-v7/test/outcomes.csv'
EXPECTED_SHA256 = 'e766a98ae53830e748da273aaace3ff958e15d53dd72cd92387f25928a3cc72a'
SEEDS = {2027, 2028, 2029}
ENDPOINTS = ('initial_success', 'B_neutral', 'C_real', 'D_shuffled',
             'E_token_matched', 'R_resample')
SENSITIVITY = (
    ('Frozen all cases', ()),
    ('Exclude exact cross-split d06/t11-t12', ('bridge_t11', 'bridge_t12')),
    ('Also exclude d07/t13 specialization', ('bridge_t11', 'bridge_t12', 'bridge_t13')),
    ('Also collapse t07/t08 successor relation',
     ('bridge_t11', 'bridge_t12', 'bridge_t13', 'bridge_t08')),
)


def audit(rows: list[dict[str, str]]) -> list[dict]:
    keys = [(r['model'], int(r['seed']), r['id']) for r in rows]
    assert len(rows) == 72 and len(set(keys)) == 72, 'Not 72 unique rows'
    assert {k[1] for k in keys} == SEEDS, 'Unexpected seeds'
    ids = {k[2] for k in keys}
    assert ids == {f'bridge_t{i:02d}' for i in range(1, 25)}
    assert len({k[0] for k in keys}) == 1, 'V7 must be one-model snapshot'
    for r in rows:
        assert all(r[e] in ('True', 'False') for e in ENDPOINTS), 'Missing endpoint'
    results = []
    for name, excluded in SENSITIVITY:
        data = [r for r in rows if r['id'] not in excluded]
        assert len(data) == (24 - len(excluded)) * 3
        n = len(data)
        counts = {e: sum(r[e] == 'True' for r in data) for e in ENDPOINTS}
        c_only = sum(r['C_real'] == 'True' and r['B_neutral'] == 'False'
                     for r in data)
        b_only = sum(r['C_real'] == 'False' and r['B_neutral'] == 'True'
                     for r in data)
        results.append({
            'scope': name, 'excluded_theorem_ids': list(excluded),
            'n_theorem_seed': n, 'n_distinct_theorems': n // 3,
            'counts': counts,
            'C_minus_B_count': counts['C_real'] - counts['B_neutral'],
            'C_minus_D_count': counts['C_real'] - counts['D_shuffled'],
            'C_minus_B_percentage_points': round(100 * (counts['C_real'] - counts['B_neutral']) / n, 4),
            'C_minus_D_percentage_points': round(100 * (counts['C_real'] - counts['D_shuffled']) / n, 4),
            'C_only_vs_B': c_only, 'B_only_vs_C': b_only,
        })
    assert results[0]['counts'] == {
        'initial_success': 4, 'B_neutral': 5, 'C_real': 10,
        'D_shuffled': 9, 'E_token_matched': 5, 'R_resample': 5}, \
        'Frozen V7 results unexpectedly changed'
    return results


def main() -> None:
    assert SOURCE.is_file(), f'Frozen test CSV not found: {SOURCE}'
    raw = SOURCE.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    assert digest == EXPECTED_SHA256, f'Frozen source SHA-256 mismatch: {digest}'
    rows = list(csv.DictReader(raw.decode('utf-8-sig').splitlines()))
    output = {'source': str(SOURCE.relative_to(REPO)), 'source_sha256': digest,
              'study': 'Study 2 V7 (base model only)',
              'analysis': 'post-hoc exploratory; not preregistered',
              'warning': 'Repeated seeds are not independent theorem types; exclusions cannot repair a contaminated benchmark retrospectively.',
              'results': audit(rows)}
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == '__main__':
    try:
        main()
    except (AssertionError, FileNotFoundError) as exc:
        print(f'VALIDATION FAILED: {exc}', file=sys.stderr)
        raise SystemExit(2)