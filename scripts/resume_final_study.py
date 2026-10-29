"""Resume an interrupted frozen study without replaying generation; then finalize."""
from pathlib import Path
import datetime
import json
import os
import subprocess
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from final_study import BASE, read, sha, validate_protocol


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def main():
    protocol = ROOT / 'configs/repair_experiment_local_v0.4.2.json'
    config = validate_protocol(protocol)
    runroot = ROOT / config['output_root'] / 'heldout' / '2027'
    history = BASE / 'resume_history'
    history.mkdir(exist_ok=True)
    ordinal = len(list(history.glob('resume_*.json'))) + 1
    record_path = history / f'resume_{ordinal}.json'
    artifacts = []
    terminal = []
    interrupted = []
    for manifest in sorted(runroot.glob('*/manifest.json')):
        m = read(manifest)
        if m['status'] in ['completed', 'incomplete']:
            terminal.append(m['problem_id'])
            artifacts.append(manifest)
        else:
            interrupted.append({'problem_id': m['problem_id'], 'prior_status': m['status'],
                'unfinished_generation_intents': [str(p.relative_to(ROOT)) for p in manifest.parent.glob('*/intent.json') if not (p.parent / 'completion.json').exists()]})
    for pattern in ['*/*/intent.json', '*/*/completion.json', '*/*/verification.json', '*/streams/*.jsonl']:
        artifacts.extend(runroot.glob(pattern))
    preserved = {str(p.relative_to(ROOT)): sha(p) for p in sorted(set(artifacts))}
    old_environment = runroot.parent.parent / 'heldout_environment.json'
    if old_environment.exists():
        (history / f'prior_environment_{ordinal}.json').write_bytes(old_environment.read_bytes())
    event = {
        'resumed_at': now(), 'protocol_sha256': sha(protocol),
        'worker_pid': os.getpid(), 'prior_terminal_cases': terminal,
        'interrupted_cases': interrupted, 'preserved_artifact_sha256': preserved,
        'observed_reason': 'Prior experiment and finalization workers absent on read-only process inspection; exact termination cause not established.',
        'recovery_policy': 'Use the frozen runner. Completed generations are reused. An incomplete durable generation intent consumes its call and is never replayed.',
        'timing_caution': 'Recorded trajectory wall elapsed time for the interrupted case includes the inactive interval before recovery; it is not uninterrupted compute time.',
    }
    record_path.write_text(json.dumps(event, indent=2) + '\n')
    log = history / f'heldout_resume_{ordinal}.log'
    print('Resuming frozen held-out checkpoints:', now(), flush=True)
    with log.open('x') as stream:
        result = subprocess.run([sys.executable, '-u', str(ROOT / 'scripts/run_final_study.py'), '--protocol', str(protocol), '--phase', 'heldout'], cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT)
    changed = [name for name, digest in preserved.items() if sha(ROOT / name) != digest]
    event.update(heldout_returncode=result.returncode, prior_artifacts_unchanged=not changed,
                 changed_prior_artifacts=changed, heldout_finished_at=now(), log=str(log.relative_to(ROOT)))
    record_path.write_text(json.dumps(event, indent=2) + '\n')
    if result.returncode or changed:
        raise RuntimeError('Frozen resume failed or altered prior durable evidence; see preserved resume log.')
    print('All trajectories terminal; original durable evidence preserved. Analyzing:', now(), flush=True)
    with (history / f'analysis_resume_{ordinal}.log').open('x') as stream:
        subprocess.run([sys.executable, str(ROOT / 'eval/final_study_analysis.py'), '--protocol', str(protocol), '--output', str(BASE / 'analysis')], cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT, check=True)
    print('Starting actual reporting, tests, Lean build and PDF:', now(), flush=True)
    with (BASE / 'automatic_finalization.log').open('a') as stream:
        subprocess.run([sys.executable, '-u', str(ROOT / 'scripts/finalize_completed_study.py')], cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT, check=True)
    event.update(finalization_finished_at=now(), technical_finalization_complete=True)
    record_path.write_text(json.dumps(event, indent=2) + '\n')
    print('Technical finalization complete; artifact review and Git delivery remain.', flush=True)


if __name__ == '__main__':
    main()
