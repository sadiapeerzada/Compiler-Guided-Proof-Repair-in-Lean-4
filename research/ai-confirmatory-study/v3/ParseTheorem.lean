import Lean

open Lean

/-- Parse syntax only. Never elaborate or execute the supplied command. -/
unsafe def main (args : List String) : IO UInt32 := do
  let [input, output] := args | throw <| IO.userError "expected input and output files"
  initSearchPath (← findSysroot)
  enableInitializersExecution
  let env ← importModules #[{module := `Mathlib}] {} (loadExts := true)
  let source ← IO.FS.readFile input
  let result : Except String Json := do
    let stx ← Parser.runParserCategory env `command source
    let some thm := stx.find? (·.isOfKind ``Parser.Command.theorem)
      | throw "expected one theorem declaration"
    -- Access the theorem's own value, not a nested let assignment or comment.
    let some simple := thm.getArgs.find? (·.isOfKind ``Parser.Command.declValSimple)
      | throw "only a simple := proof value is supported"
    let some beginPos := simple[0].getPos? | throw "assignment position unavailable"
    let some endPos := simple[0].getTailPos? | throw "assignment end unavailable"
    pure <| Json.mkObj [("assignment_start", toJson beginPos.byteIdx),
      ("assignment_end", toJson endPos.byteIdx)]
  match result with
  | .ok value => IO.FS.writeFile output value.compress; return 0
  | .error message =>
    IO.FS.writeFile output (Json.mkObj [("error", toJson message)]).compress
    return 1
