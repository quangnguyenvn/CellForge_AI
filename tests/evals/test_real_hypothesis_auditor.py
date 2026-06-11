import unittest

from services.evals.real_hypothesis_auditor import run_real_hypothesis_audit


class RealHypothesisAuditorTest(unittest.TestCase):
    def test_audits_real_hypotheses_with_self_audit_signals(self) -> None:
        payload = run_real_hypothesis_audit()
        summary = payload["summary"]
        audits = payload["audits"]

        self.assertEqual(summary["hypotheses"], 5)
        self.assertGreaterEqual(summary["advance_with_human_review"], 1)
        self.assertGreaterEqual(summary["revise_experiment_design"] + summary["revise_before_brief"], 1)
        self.assertLessEqual(summary["avg_hallucination_risk"], 0.65)
        self.assertTrue(all(audit["human_review_pressure"] == 1.0 for audit in audits))
        self.assertTrue(all(audit["unsupported_claims"] for audit in audits))


if __name__ == "__main__":
    unittest.main()
