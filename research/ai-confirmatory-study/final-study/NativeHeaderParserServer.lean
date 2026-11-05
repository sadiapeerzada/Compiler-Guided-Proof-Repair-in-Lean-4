import Lean
open Lean Parser

def headerParser : Parser := leading_parser
  "theorem " >> Command.declId >> ppIndent Command.declSig >> " :="

partial def assignmentPositions (source : String) (stx : Syntax) : Array (Nat × Nat) := Id.run do
  let mut result := #[]
  if stx.isAtom then
    if let (some start, some stop) := (stx.getPos?, stx.getTailPos?) then
      if source.toUTF8.extract start.byteIdx stop.byteIdx == ":=".toUTF8 then
        result := result.push (start.byteIdx, stop.byteIdx)
  for child in stx.getArgs do
    result := result ++ assignmentPositions source child
  return result

def parseHeader (env : Environment) (source : String) : Except String Json := do
  let ictx := mkInputContext source "<reference-construction-header>"
  let parser := andthenFn whitespace headerParser.fn
  let state := parser.run ictx {env, options := {}} (getTokenTable env) (mkParserState source)
  if !state.allErrors.isEmpty then throw (state.toErrorMsg ictx)
  let positions := (state.stxStack.extract 0 state.stxStack.size).foldl (fun acc stx => acc ++ assignmentPositions source stx) #[]
  if positions.isEmpty then throw "outer assignment token unavailable"
  -- Only the header was parsed. Its last := atom is the theorem assignment;
  -- inner lets/strings cannot move this boundary into the unparsed proof body.
  let position := positions.foldl (fun best current => if current.1 > best.1 then current else best) positions[0]!
  pure <| Json.mkObj [("assignment_start",toJson position.1),("assignment_end",toJson position.2)]

/-- Parse only the existing header; do not parse, elaborate or repair the body. -/
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
      let answer := match parseHeader env source with
        | .ok value => value
        | .error message => Json.mkObj [("error",toJson message)]
      pure <| Json.mkObj [("request_id",toJson id),("result",answer)]
    output.putStrLn (match result with | .ok value => value | .error message => Json.mkObj [("fatal_error",toJson message)]).compress
    output.flush
  return 0
