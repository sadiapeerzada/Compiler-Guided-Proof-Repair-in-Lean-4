"""Actual resource authorization, distinct from AI mathematical adjudication."""
import argparse
import time
from ai_common import HERE,read,save,sha,ensure

STAGES=('generation','reviewer_1','reviewer_2','development','test')

def authorize(stage,authorization=None):
    ensure(stage in STAGES,'Unknown resource phase')
    path=authorization or HERE/'resource_authorization.json'
    ensure(path.exists(),'NO_GO_RESOURCES: explicit phase authorization has not been supplied; planning ceilings are not permission')
    record=read(path)
    ensure(record.get('status')=='AUTHORIZED' and record.get('actor_kind')=='researcher_resource_authority','NO_GO_RESOURCES: wrong actor/status; AI approval is not compute permission')
    ensure(record.get('source')=='direct_user_authorization' and record.get('exact_user_instruction'),'NO_GO_RESOURCES: genuine user instruction absent')
    ensure(record.get('unit_test_only') is not True,'Synthetic authorization cannot enable production inference')
    spec=record['phases'].get(stage)
    ensure(spec is not None and type(spec['max_calls']) is int and spec['max_calls']>0,'NO_GO_RESOURCES: phase has no positive call allocation')
    for k,cap in [('max_input_tokens',4096),('max_output_tokens',1200)]:ensure(type(spec[k]) is int and 0<spec[k]<=cap,'NO_GO_RESOURCES: invalid token allocation')
    ensure(0<spec['max_runtime_seconds']<=172800,'NO_GO_RESOURCES: runtime cap absent')
    return spec,sha(path)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('stage',choices=STAGES);a=p.parse_args()
    try:print(authorize(a.stage))
    except (ValueError,FileNotFoundError) as e:print(e)
