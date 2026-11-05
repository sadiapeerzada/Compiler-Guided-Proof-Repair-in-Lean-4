from study_common import *
from header_parser import NativeHeaderParser
from native_parser import ParseError

def main():
    out=run_root()/'header_parser_fixture_checks_v2';out.mkdir(exist_ok=True);parser=NativeHeaderParser(out/'server');results=[]
    try:
        for i,source in enumerate(['theorem fixture : True := by made_up_tactic','theorem fixture : True := by\n  let n := 2\n  made_up_tactic']):
            folder=out/str(i);folder.mkdir(exist_ok=True);target,proof=parser.split(source,'fixture',folder)
            expected=source[:source.index(' := by')];ensure(target==expected,'Wrong native header boundary');ensure(source.encode()==(target+' := '+proof).encode(),'Mathematical source reconstructed differently');results.append(dict(index=i,target=target,status='PASSED_HEADER_EXTRACTION_ONLY'))
        folder=out/'2';folder.mkdir(exist_ok=True)
        try:parser.split('theorem fixture (h : "x := y" = "x := y") : True := by made_up_tactic','fixture',folder);raise AssertionError('Unsupported assignment-bearing target was accepted')
        except ParseError as error:results.append(dict(index=2,status='CORRECTLY_REJECTED_UNSUPPORTED_TARGET',reason=str(error)))
        folder=out/'3';folder.mkdir(exist_ok=True);source='theorem fixture : True := by\n  let s := "x := y"\n  made_up_tactic';target,proof=parser.split(source,'fixture',folder);ensure(target=='theorem fixture : True','Proof string confused header boundary');results.append(dict(index=3,status='PASSED_PROOF_STRING_BOUNDARY'))
    finally:parser.close()
    dump(out/'results.json',dict(fixtures=results,model_calls=0,not_proof_successes=True));print('Header fixtures:',len(results),'passed; no model calls or proof approvals')

if __name__=='__main__':main()
