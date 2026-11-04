"""New AI-only gate: never writes or satisfies the historical human gate."""
from ai_common import HERE,ROOT,read,sha,ensure,digest,subject_hash
from resource_gate import authorize

def source_check():
    protocol=read(HERE/'ai_protocol_v1.json')
    ensure(protocol['source_lock_sha256']==sha(HERE/'source_lock.json'),'NO_GO_FREEZE: source lock differs')
    for rel,expected in read(HERE/'source_lock.json')['files'].items():ensure(sha(ROOT/rel)==expected,'NO_GO_FREEZE: frozen implementation changed')
    return protocol

def check(phase):
    try:spec,auth=authorize(phase)
    except (ValueError,FileNotFoundError,KeyError) as error:return dict(status='NO_GO_RESOURCES',reason=str(error))
    try:
        protocol=source_check()
        ensure(phase in ('development','test'),'Wrong experiment phase')
        if phase=='test':
            ensure((HERE/'confirmatory_freeze.json').exists(),'NO_GO_FREEZE: no post-development test freeze')
            ensure(not protocol['pilot_development_only'],'NO_GO_DATA: pilot candidates cannot become confirmatory subjects')
        freeze=read(HERE/'runs/dataset_freeze.json')
        ensure(freeze['protocol_sha256']==sha(HERE/'ai_protocol_v1.json'),'NO_GO_FREEZE: protocol changed after dataset selection')
        manifest=read(HERE/'runs/dataset_manifest.json')
        ensure(sha(HERE/'runs/dataset_manifest.json')==freeze['manifest_sha256'],'NO_GO_FREEZE: manifest changed')
        ensure(manifest[phase]['count']>0,'NO_GO_DATA: no AI-screened subjects')
        if phase=='development':records=read(HERE/'runs/development.json')
        else:
            from test_vault import load_test
            records=load_test('test')
        ensure(digest(records)==manifest[phase]['content_sha256'],'NO_GO_FREEZE: selected records changed')
        decisions=read(HERE/'runs/reviews/accepted_candidates.json');accepted={r['id']:r for r in decisions}
        formal={r['id']:r for r in __import__('ai_common').lines(HERE/'runs/formal_verification/formal_verification.jsonl')}
        reviewers=[{r['id']:r for r in __import__('ai_common').lines(HERE/'runs/reviews'/f'reviewer_{i}.jsonl')} for i in (1,2)]
        for row in records:
            ensure(row['id'] in accepted and row['status']=='AI_SCREENED_FORMALLY_VERIFIED','NO_GO_VALIDATION: no accepted AI-screened subject')
            ensure(subject_hash(row)==subject_hash(accepted[row['id']])==formal[row['id']]['subject_sha256'],'NO_GO_VALIDATION: subject binding mismatch')
            ensure(formal[row['id']]['result']['success'] is True,'NO_GO_VALIDATION: reference failed')
            evidence=[r[row['id']] for r in reviewers]
            ensure(evidence[0]['family']!=evidence[1]['family'],'NO_GO_VALIDATION: reviewers share a family')
            for r in evidence:
                ensure(r['subject_sha256']==subject_hash(row) and r['decision']=='ACCEPT' and not r['review']['problems'] and not r['review']['unresolved_critical'],'NO_GO_VALIDATION: unresolved review concern')
                ensure(r['response_sha256']==__import__('ai_common').text_hash(r['record']['content']),'NO_GO_VALIDATION: reviewer response changed')
        ensure(len(records)*3*4<=spec['max_calls'],'NO_GO_RESOURCES: cohort exceeds actual experimental call authorization')
        return dict(status='READY_FOR_DEVELOPMENT' if phase=='development' else 'READY_FOR_CONFIRMATORY_TEST',records=records,resource_limits=spec,authorization_sha256=auth,protocol=protocol)
    except (ValueError,KeyError,TypeError,FileNotFoundError) as error:
        message=str(error);status=next((s for s in ['NO_GO_DATA','NO_GO_VALIDATION','NO_GO_RESOURCES','NO_GO_FREEZE'] if s in message),'NO_GO_DATA')
        return dict(status=status,reason=message)

def require_ready(phase):
    result=check(phase);ensure(result['status'].startswith('READY_'),result.get('reason',result['status']));return result
