import Lean
open Lean

def parseOne (env : Environment) (source : String) : Except String Json := do
  let stx ← Parser.runParserCategory env `command source
  let some thm := stx.find? (·.isOfKind ``Parser.Command.theorem) | throw "one theorem required"
  let some value := thm.getArgs.find? (·.isOfKind ``Parser.Command.declValSimple) | throw "simple theorem assignment required"
  let some start := value[0].getPos? | throw "missing assignment position"
  let some stop := value[0].getTailPos? | throw "missing assignment end"
  pure <| Json.mkObj [("assignment_start",toJson start.byteIdx),("assignment_end",toJson stop.byteIdx)]

/-- Reuse an immutable parser environment; supplied source is never elaborated. -/
unsafe def main : IO UInt32 := do
  initSearchPath (← findSysroot)
  enableInitializersExecution
  let env ← importModules #[{module := `Mathlib}] {} (loadExts := true)
  let input ← IO.getStdin
  let output ← IO.getStdout
  repeat
    let line ← input.getLine
    if line.isEmpty then break
    let result : Except String Json := do
      let request ← Json.parse line
      let source ← request.getObjValAs? String "source"
      let id ← request.getObjValAs? Nat "request_id"
      let answer := match parseOne env source with
        | .ok value => value
        | .error message => Json.mkObj [("error",toJson message)]
      pure <| Json.mkObj [("request_id",toJson id),("result",answer)]
    let response := match result with
      | .ok value => value
      | .error message => Json.mkObj [("fatal_error",toJson message)]
    output.putStrLn response.compress
    output.flush
  return 0
