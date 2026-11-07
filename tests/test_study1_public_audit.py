"""Read-only tests: python -m unittest discover -s tests -p 'test_study1_public_audit.py' -v."""
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("public_audit", ROOT / "scripts" / "audit_study1_public.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class PublicEvidenceTests(unittest.TestCase):
    def test_released_aggregates(self):
        summary = module.audit()
        self.assertEqual(summary["status"], "PASS")
        self.assertEqual(summary["outcomes"]["C"]["observed"], 58)
        self.assertEqual(summary["paired_BC_discordant"], 0)
        self.assertEqual(summary["C_minus_A_cluster_upper_post_hoc_pp"], 5.56)

    def test_negative_case_cannot_be_silently_accepted(self):
        with self.assertRaises(AssertionError):
            module.require(False, "synthetic tampering detected")

    def test_missing_cases_not_coded_as_observed_failures(self):
        cases = module.read_json("results/cases.json")
        c_missing = [c for c in cases if c["outcomes"]["C"] is None]
        self.assertEqual(len(c_missing), 2)
        self.assertEqual(sum(c["outcomes"]["C"] is False for c in cases), 57)

    def test_paired_counts_are_not_60(self):
        results = module.read_json("results/results.redacted.json")
        self.assertEqual(results["conditions"]["C"]["denominator"], 60)  # frozen sensitivity coding
        cases = module.read_json("results/cases.json")
        self.assertEqual(sum(c["outcomes"]["C"] is not None for c in cases), 58)


if __name__ == "__main__":
    unittest.main()
