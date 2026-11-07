"""Read-only, public-aggregate consistency audit for the fixed-theorem Lean pilot.

Usage: python -B scripts/audit_study1_public.py
Does not run inference, Lean, private-byte replay, or amend any experimental record.
"""
import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "publication"

def read_json(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

def require(condition, message):
    if not condition:
        raise AssertionError(message)

def audit():
    cases = read_json("results/cases.json")
    require(len(cases) == 60 and len({c["problem_id"] for c in cases}) == 60, "60 unique cases")
    outcomes = {}
    for arm, successes, observed in (("A", 0, 60), ("B", 1, 60), ("C", 1, 58)):
        present = [c for c in cases if c["outcomes"][arm] is not None]
        require(len(present) == observed, arm + " observed denominator")
        require(sum(c["outcomes"][arm] is True for c in present) == successes, arm + " successes")
        outcomes[arm] = {"successes": successes, "observed": observed}
    missing = sorted(c["problem_id"] for c in cases if c["outcomes"]["C"] is None)
    require(missing == ["lib_a_trig_unit", "lib_i_bernoulli"], "missing C IDs")
    paired = [c for c in cases if c["outcomes"]["C"] is not None]
    require(sum(c["outcomes"]["B"] != c["outcomes"]["C"] for c in paired) == 0, "B/C discordance")
    require([c["problem_id"] for c in paired if c["outcomes"]["B"] and c["outcomes"]["C"]] == ["lib_a_exp_add"], "only joint success")
    summary = read_json("results/results.redacted.json")
    require(summary["actual_unique_generation_calls"] == 410, "physical call count")
    require(summary["actual_unique_prompt_tokens"] == 362035, "input token total")
    require(summary["actual_unique_completion_tokens"] == 130401, "output token total")
    # Historical C aggregate uses the *sensitivity* 60-case denominator, not observed 58.
    require(summary["conditions"]["C"]["denominator"] == 60 and summary["conditions"]["C"]["incomplete"] == 2, "C sensitivity coding")
    resources = read_json("results/review_v2/paired_resources.json")
    means = {}
    for arm, expected in (("B", 1980.8793103448277), ("C", 4353.517241379311)):
        part = resources["conditions"][arm]
        require(part["cases"] == 58 and part["completed_calls"] == 230, arm + " paired counts")
        rows = part["per_problem"]
        require(len(rows) == 58, arm + " per-problem resources")
        mean = sum(r["prompt_tokens"] for r in rows) / 58
        require(abs(mean - expected) < 1e-8, arm + " input-token mean")
        means[arm] = round(mean, 1)
    hoc = read_json("post_hoc/outputs/post_hoc/post_hoc_task1.json")
    require(hoc["post_hoc"] is True and hoc["heldout_model_calls"] == 0, "post-hoc provenance")
    with (ROOT / "post_hoc/outputs/post_hoc/post_hoc_repair_metrics.csv").open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    require(len(rows) == 350, "350 completed repair rows")
    transitions = {}
    repetitions = {}
    for arm, n, repeats, stages in (
        ("B", 178, 90, (11, 161, 4, 1, 1)),
        ("C", 172, 70, (14, 146, 7, 1, 4)),
    ):
        part = [r for r in rows if r["condition"] == arm]
        require(len(part) == n, arm + " repair rows")
        require(sum(int(r["identical"]) for r in part) == repeats, arm + " identical repeats")
        require(hoc["per_condition"][arm]["identical"]["sum"] == repeats, arm + " repetition summary")
        stage = Counter(r["transition_direction"] for r in part)
        got = tuple(stage[x] for x in ("advanced", "same_category", "regressed", "verified", "unranked"))
        require(got == stages, arm + " compiler stage transitions")
        transitions[arm] = dict(zip(("advanced", "same_category", "regressed", "verified", "unranked"), got))
        repetitions[arm] = {"repeats": repeats, "repairs": n}
    calibrated = read_json("post_hoc/outputs/post_hoc/reproduced_run1/post_hoc_calibrated_null.json")
    ca = next(c for c in calibrated["contrasts"] if c["contrast"] == "C_minus_A")
    upper = 100 * ca["family_cluster_primary"]["interval"][1]
    require(abs(upper - 5.555555555555555) < 1e-8, "C-A reconstructed 5.56pp bound")
    bc = next(c for c in calibrated["contrasts"] if c["contrast"] == "C_minus_B")
    require(bc["discordant_pairs"] == 0 and bc["family_cluster_primary"]["interval"] == [0, 0], "C-B zero discordance")
    old = read_json("results/results.redacted.json")
    require(old["conditions"]["C"]["incomplete"] == 2, "missing C retained")
    recon = read_json("post_hoc/outputs/post_hoc/reproduced_run1/reconciliation_summary.json")
    require(recon["checks"] == 38 and recon["mismatches"] == [], "archived reconciliation claim")
    return {
        "status": "PASS", "scope": "public aggregate consistency; not private-byte reproduction",
        "outcomes": outcomes, "missing_C": missing, "paired_BC_discordant": 0,
        "paired_input_tokens_mean": means, "repetition": repetitions,
        "compiler_transitions": transitions,
        "C_minus_A_cluster_upper_post_hoc_pp": round(upper, 2),
        "other_historical_C_minus_A_upper_pp": 5.66,
        "reconciliation_report": "archived 38 checks, 0 mismatches (not rerun)"
    }

if __name__ == "__main__":
    print(json.dumps(audit(), indent=2, sort_keys=True))
