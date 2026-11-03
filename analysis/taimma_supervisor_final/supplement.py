"""Read-only additions to PR #20. No model, tokenizer or Lean execution.

Run with .venv/bin/python analysis/taimma_supervisor_final/supplement.py
V7 raw trajectories are optional local evidence; their absence is reported.
"""
from __future__ import annotations

import csv
import hashlib
import importlib.util
import io
import json
import re
import statistics
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).parent
PR20 = ROOT / 'analysis/taimma_20261104'
ARMS = ['B_neutral', 'C_real', 'D_shuffled', 'E_token_matched', 'R_resample']
SOURCES = {}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def clean(text):
    """Publication-view redaction only; original evidence remains untouched."""
    text = re.sub(r'/Users/[^/\s"\\]+', '<HOME>', text)
    text = re.sub(r'/home/[^/\s"\\]+', '<HOME>', text)
    return text.replace('/REDACTED_HOME', '<HOME>')


def read(path):
    raw = (ROOT / path).read_bytes()
    SOURCES[path] = {'path': path, 'sha256': sha(raw), 'provenance': 'repository file or explicitly identified local snapshot'}
    return raw


def js(path):
    return json.loads(read(path))


def rows(raw):
    return list(csv.DictReader(io.StringIO(raw.decode('utf-8-sig'))))


def write_json(name, value):
    (OUT / name).write_text(clean(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False)) + '\n')


def md(name, text):
    (OUT / name).write_text(clean(text.rstrip()) + '\n')


def table(name, values):
    if not values:
        return 'No eligible records.\n'
    cols = list(values[0])
    with (OUT / (name + '.csv')).open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=cols, lineterminator='\n')
        writer.writeheader()
        writer.writerows(values)
    def cell(x):
        return str(x).replace('|', '\\|').replace('\n', '<br>')
    return '\n'.join(['| ' + ' | '.join(cols) + ' |', '| ' + ' | '.join('---' for _ in cols) + ' |'] +
                     ['| ' + ' | '.join(cell(v[c]) for c in cols) + ' |' for v in values]) + '\n'


def load_archive():
    base = 'research/study2-raw-v8-v9/'
    index = js(base + 'ARCHIVE_INDEX.json')
    archive = {}
    for part in index['archives']:
        raw = read(base + part['filename'])
        require(sha(raw) == part['sha256'], 'ZIP checksum mismatch')
        with zipfile.ZipFile(io.BytesIO(raw)) as z:
            require(len(z.namelist()) == len(set(z.namelist())), 'Duplicate ZIP path')
            archive.update({n: z.read(n) for n in z.namelist()})
    for item in index['entries']:
        raw = archive[item['path']]
        require(sha(raw) == item['sha256'], 'Archive member checksum mismatch: ' + item['path'])
    require(set(archive) == {e['path'] for e in index['entries']}, 'Unindexed ZIP member')
    return archive


def archived(archive, path):
    raw = archive[path]
    source = 'research/study2-raw-v8-v9/evidence-part-001.zip::' + path
    SOURCES[source] = {'path': source, 'sha256': sha(raw), 'provenance': 'indexed archived member; checksum verified'}
    return raw


def load_studies(archive):
    data = {}
    for label in ('V7', 'V8'):
        if label == 'V7':
            base = 'research/study2-v7/test/'
            get = lambda n: read(base + n)
            viewpath = 'analysis/taimma_supervisor_final/sources/v7_trajectory_views.json'
            if (ROOT/viewpath).exists():
                views=js(viewpath)
                trajectories=[(v['original_path'],v['trajectory']) for v in views]
                for v in views:
                    original=ROOT/v['original_path']
                    if original.exists(): require(sha(original.read_bytes())==v['original_sha256'],'Local V7 source changed since capture')
                    SOURCES[v['original_path']]={'path':v['original_path'],'sha256':v['original_sha256'],'provenance':'original local digest captured in committed sanitized view; not independently archived historical evidence'}
            else:
                paths = sorted((ROOT / 'study2_outputs/bridge_v7_base/trajectories').glob('*/20*/test/*.json'))
                trajectories = [(str(p.relative_to(ROOT)), json.loads(read(str(p.relative_to(ROOT))))) for p in paths]
        else:
            base = next(n.rsplit('/', 1)[0] + '/' for n in archive if n.endswith('coder_exploratory/reports/test/outcomes.csv'))
            get = lambda n: archived(archive, base + n)
            paths = sorted(n for n in archive if 'coder_exploratory/trajectories/' in n and '/test/' in n and n.endswith('.json'))
            trajectories = [('research/study2-raw-v8-v9/evidence-part-001.zip::' + n, json.loads(archived(archive, n))) for n in paths]
        outcomes, calls, transitions = [rows(get(n + '.csv')) for n in ('outcomes', 'calls', 'transitions')]
        require(len(outcomes) == 72, 'Unexpected evaluation denominator')
        keys = [(r['model'], r['seed'], r['id']) for r in outcomes]
        require(len(set(keys)) == 72, 'Duplicate outcome key')
        require({(r['seed'], r['id']) for r in outcomes} == {(str(s), f'bridge_t{i:02}') for s in (2027, 2028, 2029) for i in range(1, 25)}, 'Incomplete grid')
        tkeys = [(t['model'], str(t['seed']), t['id']) for _, t in trajectories]
        require(len(set(tkeys)) == len(tkeys), 'Duplicate raw trajectory')
        require(not trajectories or set(tkeys) == set(keys), 'Partial raw cohort: refuse silently selective raw analysis')
        if label=='V7': dev=rows(read('research/study2-v7/development/outcomes.csv'))
        else: dev=rows(archived(archive,base.replace('/test/','/development/')+'outcomes.csv'))
        data[label] = dict(outcomes=outcomes, calls=calls, transitions=transitions, trajectories=trajectories, development=dev)
    return data


def numeric_summary(records, field):
    vals = [float(r[field]) for r in records if r.get(field) not in (None, '')]
    return dict(observed=len(vals), missing=len(records)-len(vals), total=sum(vals) if vals else None,
                median=statistics.median(vals) if vals else None, maximum=max(vals) if vals else None)


def resource_analysis(data):
    results = []
    for label, d in data.items():
        previous = rows(read(f'analysis/taimma_20261104/results/{label}_costs.csv'))
        for arm in ['A'] + ARMS:
            calls = [r for r in d['calls'] if r['arm'] == arm]
            old = next(r for r in previous if r['arm'] == arm)
            inp = numeric_summary(calls, 'prompt_tokens'); output = numeric_summary(calls, 'completion_tokens')
            require(inp['total'] == int(old['input_tokens']) and output['total'] == int(old['output_tokens']), 'PR20 token total mismatch')
            generation = numeric_summary(calls, 'seconds'); compiler = numeric_summary(calls, 'compiler_seconds'); memory = numeric_summary(calls, 'memory_gb')
            results.append(dict(study=label, model=d['outcomes'][0]['model'], arm=arm, cohort_evaluations=72,
                                completed_calls=len(calls), input_tokens=inp['total'], output_tokens=output['total'],
                                input_tokens_per_cohort_evaluation=inp['total']/72 if inp['total'] is not None else None,
                                output_tokens_per_cohort_evaluation=output['total']/72 if output['total'] is not None else None,
                                generation_elapsed_seconds=generation['total'], generation_missing=generation['missing'],
                                compiler_elapsed_seconds=compiler['total'], compiler_missing=compiler['missing'],
                                max_recorded_peak_memory_gb=memory['maximum'], memory_observed=memory['observed'], memory_missing=memory['missing'],
                                input_per_new_verified_repair=old['repair_input_per_new_verified_evaluation'] or 'undefined'))
    body = table('resources', results)
    md('RESOURCE_ANALYSIS.md', '# Recorded computational resources\n\nExploratory extension of PR #20; no new experiment. Token totals are cross-checked against its existing cost tables, not presented as a new finding. Added quantities are per-cohort-evaluation normalization, recorded elapsed generation/compiler durations and maximum observed memory.\n\n' + body + '''
A is shared initial generation, charged once across all policies. Other rows are repair-only. Per-evaluation values divide by all 72 theorem–seed evaluations, including those requiring no repair. The PR20 marginal input-token ratio divides repair input tokens by NEW verified evaluations beyond initial successes; zero new repairs makes it undefined. No currency conversion or unlogged compute is estimated.

`seconds` is the runner's monotonic elapsed interval around streaming generation and token-journal writes. It includes streaming and journal I/O overhead; it is not pure accelerator kernel time. `compiler_seconds` is the verifier's recorded elapsed time per call, including its subprocess/setup work. Their sum is not experiment wall time: orchestration, loading, reference screening, development, idle periods and interrupted/unrecorded work are excluded. No total wall time is inferred by summing them.

`memory_gb` copies MLX's last streamed `peak_memory` field under the runner's `peak_memory_gb` label. We report its maximum, never a sum or an estimate. It may be a process-cumulative high-water mark and is not incremental per-arm allocation or OS total RAM. The backend's units and scope are not independently calibrated here. Missing counts remain explicit. V7 and V8 share this reporting implementation; they are separate model snapshots/runs and elapsed times are not controlled hardware-speed comparisons.

Success at cumulative repair budgets and newly verified repair token ratios already appear in `../taimma_20261104/results/{V7,V8}_budgets.csv` and `{V7,V8}_costs.csv`; those frozen derived tables are reused unchanged. In particular, V8 B/C/D/E has zero newly verified repairs; none receives a finite marginal token-per-new-success claim.
''')


def observations(data):
    obs = []
    for label, d in data.items():
        trans = {(r['model'], r['seed'], r['id'], r['arm'], int(r['index'])): r for r in d['transitions']}
        calls = {(r['model'], r['seed'], r['id'], r['arm'], int(r['index'])): r for r in d['calls']}
        for source, t in d['trajectories']:
            for arm in ARMS:
                prev = t['initial']
                for i, step in enumerate(t['arms'][arm]['steps'], 1):
                    k = (t['model'], str(t['seed']), t['id'], arm, i)
                    tr = trans[k]; call = calls[k]; details = step.get('details', {})
                    require(sha(step['candidate'].encode()) == step['candidate_sha256'], 'Raw candidate hash mismatch')
                    require(step['verification']['success'] == (tr['verified'] == 'True'), 'Raw/processed verification mismatch')
                    require(step['metadata']['prompt_tokens'] == int(call['prompt_tokens']), 'Raw/processed prompt tokens mismatch')
                    prevtext = prev.get('verification', {}).get('diagnostic_text', '')
                    newtext = step.get('verification', {}).get('diagnostic_text', '')
                    from difflib import SequenceMatcher
                    distance = 0.0 if prev['candidate']==step['candidate'] else 1-SequenceMatcher(None, prev['candidate'], step['candidate'], autojunk=False).ratio()
                    obs.append(dict(study=label, model=t['model'], seed=t['seed'], theorem=t['id'], family=t['family'], arm=arm, step=i,
                                    prompt_tokens=int(call['prompt_tokens']), output_tokens=int(call['completion_tokens']),
                                    predecessor_diagnostic_characters=len(prevtext), candidate_characters=len(step['candidate']),
                                    original_payload_tokens=details.get('original_feedback_tokens'), used_payload_tokens=details.get('used_feedback_tokens'),
                                    payload_truncated=details.get('truncated'), payload_reason=details.get('reason', ''),
                                    previous_error=tr['previous_error'], new_error=tr['new_error'], verified=tr['verified']=='True',
                                    repeated=prev['candidate']==step['candidate'], candidate_change_sequence_match_distance=distance,
                                    diagnostic_text_changed=prevtext!=newtext, final_arm_outcome=t['arms'][arm]['outcome'], source=source))
                    prev = step
    table('repair_observations', obs)
    return obs


def context_analysis(data, obs):
    missing=js('publication/results/review_v2/missingness_recovery.json')
    require({r['problem_id'] for r in missing['missing_outcomes']}=={'lib_a_trig_unit','lib_i_bernoulli'},'Unexpected Study1 missing cases')
    prompt = []
    for label, d in data.items():
        for arm in ['A'] + ARMS:
            calls = [r for r in d['calls'] if r['arm']==arm]
            summary = numeric_summary(calls, 'prompt_tokens')
            prompt.append(dict(study=label,arm=arm,calls=len(calls),mean_prompt_tokens=summary['total']/summary['observed'] if summary['observed'] else None,median_prompt_tokens=summary['median'],max_prompt_tokens=summary['maximum'],missing_prompt_tokens=summary['missing'],context_statuses=json.dumps(dict(Counter(r[arm+'_status'] for r in d['outcomes'])),sort_keys=True) if arm!='A' else 'initial'))
    bins = []
    for label in data:
        for arm in ('C_real','D_shuffled'):
            for low,high in [(0,128),(128,256),(256,384),(384,float('inf'))]:
                selected = [r for r in obs if r['study']==label and r['arm']==arm and r['original_payload_tokens'] is not None and low<r['original_payload_tokens']<=high]
                bins.append(dict(study=label,arm=arm,original_payload_token_bin=f'({low},{high}]',completed_repairs=len(selected),distinct_theorems=len({r['theorem'] for r in selected}),verified=sum(r['verified'] for r in selected),repeated=sum(r['repeated'] for r in selected),truncated=sum(r['payload_truncated'] is True for r in selected),first_repairs=sum(r['step']==1 for r in selected),first_repair_verified=sum(r['step']==1 and r['verified'] for r in selected)))
    md('CONTEXT_WINDOW_ANALYSIS.md', '# Observational context-window analysis\n\nObserved test records contain no flagged C/D payload truncation and no context-limit terminal status. Maximum recorded prompt lengths are 513 tokens in V7 and 1489 in V8, below the declared 8192-token context cap even after the 1200-token output allowance. This cohort therefore cannot identify a truncation effect or behavior near the context boundary.\n\n' + table('prompt_lengths',prompt) + '\n' + table('diagnostic_length_bins',bins) + '''
Lengths: prompt/output tokens are historical model-tokenizer counts recorded by the MLX runner, not newly retokenized estimates. `original_feedback_tokens` counts the already extracted diagnostic payload (at most the first three structured compiler errors, with message character limits), before the 384-token prefix cap. It is NOT the entire compiler output. `used_feedback_tokens` is the model-token count of the actual capped payload; for shuffled D it describes its donor's feedback, not the target's compiler output. B has no diagnostic payload; E neutral padding is not a compiler diagnostic. Missing payload fields are unavailable, not zero. `predecessor_diagnostic_characters` measures Unicode characters in stored diagnostic text, not tokens. No tokenizer was loaded.

Binning is fixed post-hoc at 128/256/384 tokens. Rows count completed repair calls, not independent problems. All attempts of a theorem/seed and repeated seeds remain dependent; no p-values or causal length effects are claimed. First-repair columns restrict to identical-predecessor budget one; later rows are selected by prior failure and divergent histories. Repetition is exact candidate-byte equality; changing errors is not proof progress. Inspect `repair_observations.csv` for all measured lengths, truncation flags and verification outcomes. These descriptive relationships may be driven by theorem difficulty, arm, stopping after success, or previous failure.

Context statuses are copied without turning unknown outcomes into failures. The plans declare an 8192-token context and 1200-token output allowance; compare actual prompt maxima to those declared limits, not advertised model limits. Recorded truncation reflects the frozen prefix policy, not a randomized truncation experiment. No absence-of-failure claim extends beyond recorded test trajectories. V7 local raw traces have weaker portable provenance than the indexed V8 archive. Committed sanitized V7 trajectory views permit deterministic reanalysis on a clean checkout; original local digests remain separately recorded and do not authenticate history externally.

For Study 1, the existing missingness recovery identifies `lib_a_trig_unit/C1` as a context-preflight rejection: 9653 recorded rendered input tokens plus a 2000-token output allowance exceed the 8192 cap. `lib_i_bernoulli/C1` instead has 2205 input tokens and a 2000 output allowance, with only a stream header surviving; it is an interrupted generation without a response, not a demonstrated context overflow. Both C outcomes remain unknown. This is reuse of documented recovery evidence, not a new prompt reconstruction or retry. Existing `publication/post_hoc/outputs/post_hoc/post_hoc_task1.json` and `post_hoc_prompt_length_bins.csv` already analyze prompt length descriptively; `publication/results/review_v2/missingness_recovery.json` documents unavailable C trajectories. Those analyses are cited, not rerun here. Missing Study 1 outcomes remain unknown.

A prospective truncation study would require a new independently reviewed held-out benchmark, fixed initial failures, randomized no-feedback / full / 128 / 256 / 384-token prefix conditions, identical call and output caps, padding to match prompt-token budgets, frozen seeds and theorem-clustered verification endpoints. Predeclare incomplete handling, token accounting and stopping limits using a development-only precision study. Do not reuse these inspected test examples for a new confirmatory truncation test. This proposal is not executed and requires separate authorization.
''')


def failure_analysis(obs):
    groups = defaultdict(list)
    for r in obs:
        groups[r['study'],r['arm'],r['step']].append(r)
    values=[]
    for (label,arm,step), records in sorted(groups.items()):
        values.append(dict(study=label,arm=arm,step=step,completed_repairs=len(records),same_error_category=sum(r['previous_error']==r['new_error'] for r in records),changed_error_category=sum(r['previous_error']!=r['new_error'] for r in records),changed_category_but_unverified=sum(r['previous_error']!=r['new_error'] and not r['verified'] for r in records),changed_diagnostic_text_but_unverified=sum(r['diagnostic_text_changed'] and not r['verified'] for r in records),repeated_candidates=sum(r['repeated'] for r in records),large_change_unverified=sum(r['candidate_change_sequence_match_distance']>=.5 and not r['verified'] for r in records),verified=sum(r['verified'] for r in records)))
    md('FAILURE_ANALYSIS.md', '# Failure persistence and non-verifying changes\n\nAcross completed guided repairs, V7 repeats the exact predecessor in 111/197 calls; V8 repeats it in 178/183. Shuffled feedback repeats in 116/200 and 180/183, respectively. V7 guided repair changes error category without verification in 16 calls; shuffled repair does so in 11. V8 B/C/D/E retain the same error category throughout recorded repair attempts and add no verified successes. These are descriptive process counts, not independent trials or evidence of repair improvement.\n\n' + table('failure_persistence',values) + '''
These are post-hoc completed-attempt denominators, conditional on reaching the step. A category change, a different diagnostic or a large edit is not verified mathematical progress. `large_change` is a predeclared-for-this-analysis threshold of at least 0.5 on one minus Python SequenceMatcher ratio with autojunk disabled; it is not Levenshtein distance and not a semantic similarity score. No synthetic candidate is introduced. Selected authentic excerpts appear in CASE_STUDIES.md.

Initial-error category success and newly verified repair counts are already in PR20 `results/V7_errors.csv`, `V8_errors.csv` and theorem tables; no duplicate category efficacy calculation is introduced. The inherited classification is the frozen runner's `failure_class` function, which maps a multi-error compiler response to ONE priority label using diagnostic strings/failure status. Thus mixed syntax/identifier/unsolved-goal failures may receive only one label; it is not independent expert annotation. Precedence is missing verification, verified success, a recorded non-compiler failure kind, then syntax/parser strings, unknown-name strings, type/elaboration strings, tactic/unsolved-goal strings, and finally other compiler error. A mixed parser/unknown-identifier response is therefore syntax, even if both errors occur. Stored error messages remain available in case excerpts and raw sources. Unknown or other labels are not retrospectively renamed. See `study2_supervisor_suite_v7.py::failure_class` for the exact precedence.

This analysis uses actual previous/new fields in `transitions.csv`, cross-checked against trajectory verification flags; it does not infer repair transitions from initial-error labels. V8 B/C/D/E has zero newly verified repairs, even if errors or candidates change. Histories diverge after step one, selection by previous failure is strong, and no treatment mechanism is identified by these descriptive persistence counts. V7 raw observations depend on locally available untracked snapshots, explicitly listed in SOURCE_HASHES.json; committed sanitized trajectory views make this addition portable while the original CSV transitions remain frozen and authoritative.
''')


def check_candidate(step):
    candidate = step['candidate']
    require(sha(candidate.encode())==step['candidate_sha256'], 'Case candidate hash mismatch')
    v = step.get('verification') or {}
    if v.get('candidate_sha256'):
        require(v['candidate_sha256']==step['candidate_sha256'], 'Verification/candidate binding mismatch')
    return dict(candidate=candidate,candidate_sha256=step['candidate_sha256'],diagnostic=v.get('diagnostic_text', '\n'.join(v.get('errors',[]))),verified=v.get('success'),failure_kind=v.get('failure_kind'),exit_code=v.get('exit_code'),axiom_dependencies=v.get('axiom_dependencies'))


def case_studies(data):
    cases=[]
    family_rows=js('publication/results/review_v2/analysis_verified/case_outcomes.json')
    for tid, interpretation in [('lib_a_exp_add','Both blind B and correct-diagnostic C retrieve the direct Real.exp_add rewrite and verify. This authentic repair does not establish diagnostic specificity.'),('div_008','Compiler feedback is followed by candidate edits, but the strict verifier still rejects the repairs. Edits and error changes are not theorem verification.')]:
        base=f'publication/evidence/redacted_runs/heldout/2027/{tid}/'
        manifest=js(base+'manifest.json')
        initial=check_candidate(manifest['initial'])
        family=next(r['family'] for r in family_rows if r['problem_id']==tid)
        initial_completion=js(base+'initial/completion.json')
        require(initial['candidate'] in initial_completion['raw_response'],'Initial candidate not in recorded response')
        initial_view=js(base+'initial/candidate.lean.json')
        require(initial_view['candidate_view']==initial['candidate'],'Initial view mismatch')
        initial_verification=js(base+'initial/verification.json')
        require(initial_verification['success']==initial['verified'],'Initial verification mismatch')
        require(initial_verification.get('diagnostic_text')==initial['diagnostic'],'Initial diagnostic excerpt mismatch')
        meta=initial_completion['metadata']
        steps=[]
        for arm in ('B','C'):
            for step in manifest['conditions'][arm]['attempts']:
                entry=check_candidate(step);key=step['key']
                verification=js(base+key+'/verification.json')
                require(verification['success']==entry['verified'],'Public verification mismatch')
                require(verification.get('diagnostic_text')==entry['diagnostic'],'Repair diagnostic excerpt mismatch')
                candidate_view=js(base+key+'/candidate.lean.json')
                require(candidate_view['candidate_view']==entry['candidate'],'Publication candidate view mismatch')
                source=base+key+'/completion.json'
                completion=js(source)
                require(entry['candidate'] in completion['raw_response'],'Repair candidate not in recorded response')
                steps.append(dict(arm=arm,key=key,source=source,verification_source=base+key+'/verification.json',**entry))
        cases.append(dict(id=tid,family=family,experiment='Study 1 frozen heldout pilot; protocol '+manifest['protocol_sha256'],model=meta['model'],model_revision=meta.get('snapshot_revision'),seed=2027,source=base+'manifest.json',initial=initial,steps=steps,interpretation=interpretation,caveat='Publication-redacted views: recorded original hashes and current view-file hashes differ by design. Full generated candidates are shown, not reconstructed responses. Shuffled arm was not part of Study 1.'))
    matches=[(p,t) for p,t in data['V7']['trajectories'] if t['id']=='bridge_t16' and t['seed']==2027]
    if matches:
        path,t=matches[0]
        steps=[dict(arm=a,key=s['key'],source=path,**check_candidate(s)) for a in ('B_neutral','C_real','D_shuffled') for s in t['arms'][a]['steps']]
        cases.append(dict(id=t['id'],family=t['family'],experiment='Study 2 V7 test; 2026-11-03-study2-v7-t08-application-syntax',model=t['model'],model_revision='c26a38f6a37d0a51b4e9a1eb3026530fa35d9fed',seed=t['seed'],source=path,initial=check_candidate(t['initial']),steps=steps,interpretation='C fixes the Lean 3 begin/end shell to Lean 4 := by ring and verifies at step 1; blind B and shuffled D exhaust their budgets without verification. This selected discordance illustrates a possible mechanism, not an average causal benefit.',caveat='V7 raw trajectory is a local untracked snapshot, not in the public V8/V9 archive; its minimal sanitized view is committed in sources/v7_trajectory_views.json for portable reanalysis. Candidate hashes bind text internally; final arm outcomes are checked against frozen V7 outcomes.csv. Newly hashed excerpts do not retroactively authenticate raw history.'))
        r=next(r for r in data['V7']['outcomes'] if r['id']==t['id'] and r['seed']==str(t['seed']))
        for a in ('B_neutral','C_real','D_shuffled'):require(t['arms'][a]['outcome']==(r[a]=='True'),'Selected-case final mismatch')
    write_json('case_excerpts.json',cases)
    text='# Three authentic proof-repair case studies\n\nSelected post-hoc for contrasting behavior, not representative sampling. All text below is extracted from recorded candidates and diagnostics, never fabricated. Source-file hashes are in SOURCE_HASHES.json. Candidate SHA-256 refers to original UTF-8 candidate bytes; display-only personal home paths are redacted. The extracted Lean candidate may omit response code fences; no proof is reconstructed. Strict outcomes are historical verifier records, not a new Lean replay.\n'
    for case in cases:
        text+=f"\n## {case['id']}\n\nFamily: `{case['family']}`. {case['experiment']}; model `{case['model']}`; revision `{case.get('model_revision')}`; seed {case['seed']}.\n\nSource: `{case['source']}`.\n\n{case['caveat']}\n\n{case['interpretation']}\n"
        for title,step in [('Initial',case['initial'])]+[(s['key'],s) for s in case['steps']]:
            text+=f"\n### {title}\n\nCandidate SHA-256: `{step['candidate_sha256']}`. Verified: **{step['verified']}**; exit {step['exit_code']}; failure kind `{step['failure_kind']}`; recorded axioms `{step['axiom_dependencies']}`.\n\n```lean\n{step['candidate']}\n```\n\nActual diagnostic:\n\n```text\n{step['diagnostic'] or '[No error diagnostic recorded for this verified step]'}\n```\n"
            if step.get('source'):text+=f"\nCompletion/trajectory source: `{step['source']}`; verification: `{step.get('verification_source',case['source'])}`.\n"
    if len(cases)<3:text+='\nThird case unavailable: local V7 raw trajectories are absent. No missing output is reconstructed. Consult the committed excerpt snapshot for the original audit environment.\n'
    md('CASE_STUDIES.md',text)
    return cases


def benchmark_packet(data, archive):
    # Pure benchmark constructor: no model or Lean function is called.
    spec=importlib.util.spec_from_file_location('frozen_v7',ROOT/'study2_supervisor_suite_v7.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    read('study2_supervisor_suite_v7.py')
    refs={r['id']:r for split in ('development','test') for r in module.bridge_rows(split)}
    old=js('analysis/taimma_20261104/results/benchmark_review.json')
    pairs=[('bridge_d06','bridge_t11','Binomial square with multiplication notation; exact/rewritten identity needs expert confirmation.'),('bridge_d06','bridge_t12','Nat binomial square after binder renaming.'),('bridge_t11','bridge_t12','Square versus repeated multiplication syntax.'),('bridge_d07','bridge_t13','Possible z=1 distributivity specialization.'),('bridge_t07','bridge_t08','Successor/addition identities related through commutativity, not assumed definitionally equal.')]
    text='# Independent benchmark review worksheet\n\nUNAPPROVED: AI-assisted preparation for a mathematician/Lean expert. No signed independent adjudication is asserted. Exact source statements/reference proofs below come from the frozen V7 constructor; recorded outcomes come from frozen test CSVs. Reference checking establishes formal acceptance only. PR20 retains all 36 provisional review rows and all overlap-exclusion counts unchanged.\n'
    for left,right,relation in pairs:
        text+=f'\n## {left} / {right}\n\nRelationship to examine: {relation}\n\nPotential development/test leakage: {"cross-split pair" if "_d" in left else "within-test dependence"}.\n'
        for tid in (left,right):
            r=refs[tid];text+=f"\n`{tid}`; family `{r['study_eligibility']['family']}`.\n\nExact statement:\n```lean\n{r['expected_lean_statement']}\n```\nAvailable reference proof:\n```lean\n{r['reference_lean_proof']}\n```\n"
            for label,d in data.items():
                relevant=[x for x in d['outcomes'] if x['id']==tid]
                if relevant:
                    counts={a:sum(x[a]=='True' for x in relevant) for a in ['initial_success']+ARMS}
                    text+=f'\n{label} test successes across 3 seeds: `{json.dumps(counts,sort_keys=True)}`.\n'
                else:
                    dev=[x for x in d['development'] if x['id']==tid]
                    counts={a:sum(x[a]=='True' for x in dev) for a in ['initial_success']+ARMS}
                    text+=f'\n{label} development-source successes ({len(dev)} recorded evaluations): `{json.dumps(counts,sort_keys=True)}`. The base-model development source is the archived V5 lineage; V8 development is separately recorded. No development success is counted as held-out.\n'
        for tid in (left,right):
            screens=[n for n in archive if '/reference_screen/' in n and n.endswith('/'+tid+'.json')]
            for screen in sorted(screens):
                evidence=json.loads(archived(archive,screen))
                text+=f"\nRecorded reference-screen source: `research/study2-raw-v8-v9/evidence-part-001.zip::{screen}`; recorded strict reference flag `{evidence.get('constructed_reference_proof_kernel_verified')}`. This is an archived check, not independent adjudication.\n"
        proposed=[r for r in old if {r.get('left'),r.get('right')}=={left,right}]
        text+='\nExisting proposals: '+json.dumps([{k:r.get(k) for k in ('source','decision','recommendation','mathematical_justification','justification')} for r in proposed],ensure_ascii=False)+'.\n'
        text+='\nReviewer questions: Are the propositions identical under binder renaming, definitional equality, a proved rewrite, or only related by a specialization? Does development exposure supply the same proof template? Should inference cluster these items together? Are reference proofs valid in the pinned environment, and does the English accurately express the statement? Do not approve independence solely because each reference compiles.\n\nReviewer name/affiliation: ____; independence/conflicts: ____; signed date: ____; exact reasoning and disposition: ____.\n'
    text+='\nReference-screen attestations and their source hashes are indexed in PR20 `results/reference_evidence.json` and this supplement SOURCE_HASHES.json. No new Lean equivalence checks were executed, and no frozen entries were deleted, regrouped or relabeled.\n'
    md('INDEPENDENT_BENCHMARK_REVIEW_PACKET.md',text)


def integrity(data, archive, cases, obs):
    previous=js('analysis/taimma_20261104/results/results.json')
    v7=read('research/study2-v7/test/outcomes.csv')
    require(sha(v7)=='e766a98ae53830e748da273aaace3ff958e15d53dd72cd92387f25928a3cc72a','Frozen V7 mismatch')
    for label,d in data.items():
        for comparison in previous[label]['paired']:
            baseline=comparison['contrast'].split(' minus ')[1]
            cells=Counter((r['C_real']=='True',r[baseline]=='True') for r in d['outcomes'])
            require((cells[True,False],cells[False,True])==(comparison['C_only'],comparison['baseline_only']),'PR20 discordance mismatch')
        require(len({r['id'] for r in d['outcomes']})==24 and len({r['family'] for r in d['outcomes']})==8,'Cluster counts changed')
    for a in ARMS[:4]:require(not any(r[a]=='True' and r['initial_success']=='False' for r in data['V8']['outcomes']),'Unexpected new V8 repair')
    study1=js('publication/results/review_v2/analysis_verified/case_outcomes.json')
    require(len(study1)==60 and sum(r['outcomes']['C'] is None for r in study1)==2,'Study1 missingness mismatch')
    for item in previous['provenance']['lock_checks']:
        path=item['path']
        if path in archive:raw=archived(archive,path)
        elif path.startswith('study2_outputs/bridge_v7_base/'):
            tail=path.split('bridge_v7_base/')[1].replace('reports/','')
            raw=read('research/study2-v7/'+('test/plan.json' if tail=='plan.json' else tail))
        else:raw=read(path)
        require(sha(raw)==item['expected'],'Frozen lock mismatch')
    warnings=js('research/study2-raw-v8-v9/PRIVACY_SCAN_WARNINGS.json')
    require(warnings['public_release_requires_manual_review'] is True,'Review privacy status explicitly')
    for name in ('research/study2-final/FINAL_RESEARCH_HANDOFF.md','research/study2-final/V8_EVIDENCE_REPORT.md','research/study2-final/BENCHMARK_ADJUDICATION_NOTES.md','analysis/taimma_20261104/FINDINGS.md'):
        read(name)
    audit=dict(base_main='af5534217c25d966bf15c44280942113891e2523',v7_sha256=sha(v7),archive_members_verified=len(archive),lock_entries_verified=len(previous['provenance']['lock_checks']),study1_missing_C=2,v8_new_repairs_B_C_D_E=0,case_count=len(cases),raw_trajectory_counts={k:len(d['trajectories']) for k,d in data.items()},repair_observation_count=len(obs),privacy_manual_review_required=True)
    write_json('integrity_checks.json',audit)
    md('FINAL_SCIENTIFIC_AUDIT.md', '''# Final scientific integrity audit

Audit base: latest fetched main `af5534217c25d966bf15c44280942113891e2523`, merging PR20 on top of PR19. The supplement branch does not edit their outputs or manuscript. All new summaries are exploratory post-hoc. No inference, held-out rerun, tokenizer execution or Lean replay was run.

''' + '\n'.join(f'- {k}: `{v}`' for k,v in audit.items()) + '''

PR20 results are reused, not regenerated. Verification assertions compare frozen outcome discordances and call-token totals with its tables. The 24 theorem types reuse three dependent seeds, with eight recorded families; nominal theorem independence remains questionable because of known overlap. No 72-independent-problem inference is justified. All V8 B/C/D/E verified outcomes are already initial successes. Study 1 keeps two missing C trajectories unknown, with 58 observed C endpoints and 58 complete B/C pairs. Its shared B/C success is not new diagnostic benefit.

## Numerical and documentation discrepancies

The old handoff reports pooled family C−B interval [−1.67,+15.39] and C−D [−2.78,+6.41] percentage points, while PR20's pooled family bootstrap gives [−1.52,+15.38] and [−3.03,+6.67]. A pooled recipe/source draw stream for the handoff numbers is not recorded in the handoff. Sampling variation is a possible explanation, NOT an established attribution. PR20 explicitly uses all seeds, family clusters, row-weighted ratio, 10,000 draws and seed 20261104; its theorem-cluster C−B interval is [−1.39,+18.06]. Historical per-seed family intervals instead use seed 20271102 and each seed's 24 rows. Different units/cohorts/streams must not be silently substituted. Original intervals remain untouched; all cross zero and none establishes equivalence.

The handoff's earlier statement that V8 raw trajectories were not public is stale relative to PR19's indexed ZIP release; provenance is now inspectable, without implying independent experiment replication. Its base-C 10/72 versus Coder-C 11/72 comparison must not be called improved repair: the Coder numerator is entirely initial success. V7 blind/C/shuffled solve 3/4/7 theorem types, so ordering by successful evaluations differs from theorem coverage. Existing overlap exclusions retain all successes while removing failed cases; improved percentages are denominator changes only.

APRIL's v1 and v2 primary HTML list Yiran Wang, whereas the official arXiv abstract metadata labels the first author Evan Wang; the exact version/metadata discrepancy is linked in RELATED_WORK_COMPARISON.md and requires author reconciliation before submission. No bibliography file was edited. The paper's empirical task is fixed-statement proof repair; placeholder English in Study 2 does not establish NL-to-Lean semantic correctness.

## Provenance and privacy

ZIP and every indexed member hash are verified, as are the 40 prior frozen-lock entries. V9 is development-only; archival consistency is not a fresh held-out test. Model weights, caches, hardware and original toolchain are not independently recreated. Source hashes authenticate consistency with committed manifests, not the truth of an experiment or independent human review.

V7 raw trajectory snapshots are local and untracked, with hashes recorded on this audit; PR20 only supplies processed V7 records. Cases and raw length observations can be inspected from the committed sanitized excerpt/CSV views, and a fresh checkout can reproduce the analyses from committed sanitized trajectory views, which retain candidate text and recorded verification fields. Their original-file digests are recorded separately; these new views are derivatives, not newly recovered historical archives. No response is filled from aggregate counts. V8 raw inputs are indexed archival members. Study 1 publication views are redacted derivatives, whose current file hashes need not equal original hashes embedded in manifests. Candidate text is checked against recorded candidate SHA and public candidate views. SOURCE_HASHES.json records exact bytes of every source used by this script.

PR19 privacy warnings explicitly require manual review and contain local-path warnings. No credential-regex matches is not general privacy approval. New display excerpts redact personal home-directory prefixes while retaining original source hashes; originals and archives are untouched. This supplement's scan does not certify the existing archive for privacy, licensing or human consent.

## What remains unresolved

Independent mathematical/split/NL-semantic adjudication, training-contamination uncertainty, adequate precision, and a fresh diagnostic-content experiment remain open. Later repair histories diverge, and error/candidate changes are not proof verification. No new inferential p-values or independent-row significance claims are introduced. Manuscript integration and venue checks remain with the author. See SUPERVISOR_29_POINT_STATUS.md, RELATED_WORK_COMPARISON.md and the signed-review blanks in the benchmark packet.
''')


def main():
    SOURCES.clear()
    archive=load_archive()
    data=load_studies(archive)
    resource_analysis(data)
    obs=observations(data)
    context_analysis(data,obs)
    failure_analysis(obs)
    cases=case_studies(data)
    benchmark_packet(data,archive)
    integrity(data,archive,cases,obs)
    write_json('SOURCE_HASHES.json',list(sorted(SOURCES.values(),key=lambda r:r['path'])))
    print('Verified archive and generated supplement; cases:',len(cases),'repair observations:',len(obs))

if __name__=='__main__':
    main()
