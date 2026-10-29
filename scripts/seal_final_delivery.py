"""Seal completed study artifacts after finalization; never generate or alter runs."""
from pathlib import Path
import datetime
import hashlib
import json
import os
import platform
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from final_study import BASE, read, sha, validate_freeze, validate_protocol


def main():
    protocol = ROOT / 'configs/repair_experiment_local_v0.4.2.json'
    validate_protocol(protocol)
    validate_freeze()
    summary = read(BASE / 'final_delivery_summary.json')
    if summary['status'] != 'completed_frozen_single_seed_study':
        raise ValueError('Finalization has not completed')
    validation = read(BASE / 'final_result_validation.json')
    if not validation['valid'] or validation['test_trajectories'] != 60:
        raise ValueError('Actual result validation is missing')
    pdf_validation = read(BASE / 'final_pdf_validation.json')
    if not pdf_validation['valid']:
        raise ValueError('Compiled PDF text check is missing or failed')
    build = read(BASE / 'paper_build_manifest.json')
    if build['exit_code'] or sha(ROOT / build['pdf']) != build['pdf_sha256']:
        raise ValueError('Final compiled paper is missing or changed')
    if read(BASE / 'finalization_steps.json')[-1] != next(
        x for x in read(BASE / 'finalization_steps.json') if x['step'] == 'reports'
    ):
        raise ValueError('Automatic finalization has not reached its final report step')
    packages = subprocess.run(
        [sys.executable, '-m', 'pip', 'list', '--format=json'],
        check=True, capture_output=True, text=True,
    )
    runtime = {
        'python_version': platform.python_version(),
        'platform': platform.platform(),
        'machine': platform.machine(),
        'packages': json.loads(packages.stdout),
    }
    (BASE / 'final_runtime_inventory.json').write_text(json.dumps(runtime, indent=2) + '\n')
    manifest_path = BASE / 'final_artifact_manifest.json'
    files = set(x for x in BASE.rglob('*') if x.is_file() and x != manifest_path)
    files.update(x for x in (ROOT / 'paper/generated').glob('final_*') if x.is_file())
    files.update(ROOT / p for p in [
        'paper/main.tex', 'paper/references.bib', 'paper/compiled_final_manuscript.pdf',
        'paper/README.md', 'paper/claims_to_evidence.md', 'README.md',
        'docs/FINAL_M1_M7_COMPLIANCE_REPORT.md', 'docs/FINAL_EXPERIMENT_RESULTS.md',
        'docs/FINAL_DATASET_COMPLETION.md', 'docs/FINAL_PAPER_READINESS.md',
        'docs/FINAL_EXECUTION_REPRODUCIBILITY.md', 'docs/SEMANTIC_REVIEW_STATUS.md',
        'docs/LOCAL_MODEL_EXECUTION_REPORT.md',
        'docs/REMAINING_HUMAN_ACTIONS.md', 'docs/dataset_card.md', 'docs/reproducibility.md',
        'scripts/render_final_study.py', 'scripts/verify_final_study_artifacts.py',
        'scripts/write_final_delivery_reports.py', 'scripts/finalize_completed_study.py',
        'scripts/seal_final_delivery.py', 'scripts/resume_final_study.py', 'paper/scripts/write_final_manuscript.py',
        'paper/scripts/build_final_manuscript.py', 'paper/scripts/check_final_pdf.py',
    ])
    # Examine credential values without ever printing them or writing them to evidence.
    secret_values = [v.encode() for k, v in os.environ.items()
                     if any(word in k.upper() for word in ['API_KEY', 'ACCESS_TOKEN', 'SECRET_KEY'])
                     and len(v) >= 16]
    oversized = []
    secret_paths = []
    inventory = {}
    for path in sorted(files):
        data = path.read_bytes()
        rel = str(path.relative_to(ROOT))
        if len(data) > 20 * 1024 * 1024:
            oversized.append(rel)
        if any(secret in data for secret in secret_values):
            secret_paths.append(rel)
        inventory[rel] = {'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data)}
    if oversized or secret_paths:
        raise ValueError('Publishable-file audit failed: ' + json.dumps({
            'oversized_paths': oversized, 'credential_match_paths': secret_paths,
        }))
    manifest = {
        'created_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'scope': 'Final-study evidence, reporting source, manuscript and current documentation; manifest excludes itself.',
        'protocol_sha256': sha(protocol),
        'preheldout_source_commit': read(BASE / 'heldout_launch.json')['source_git_commit'],
        'approval_evidence_status': 'student_reported_not_independently_verified',
        'independent_human_reviews': 0,
        'publishable_file_audit': {
            'file_count': len(inventory), 'files_above_20_mib': 0,
            'matches_to_available_environment_credential_values': 0,
            'credential_scan_scope': 'Available API_KEY/ACCESS_TOKEN/SECRET_KEY environment values of length at least 16; no claim of exhaustive secret detection.',
        },
        'files': inventory,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2) + '\n')
    print('Sealed', len(inventory), 'actual evidence/source files; manifest SHA-256', sha(manifest_path))


if __name__ == '__main__':
    main()
