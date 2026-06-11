import unittest

from services.evals.local_eval import run_auditor_eval


class EvidenceAuditorEvalTest(unittest.TestCase):
    def test_evidence_auditor_eval_set_has_passing_baseline(self) -> None:
        report = run_auditor_eval()
        summary = report["summary"]

        self.assertGreaterEqual(summary["cases"], 200)
        self.assertGreaterEqual(summary["pass_rate"], 0.70)


if __name__ == "__main__":
    unittest.main()
