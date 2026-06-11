import unittest

from services.evals.real_hypothesis_generator import generate_real_hypotheses


class RealHypothesisGeneratorTest(unittest.TestCase):
    def test_generates_grounded_candidate_hypotheses(self) -> None:
        payload = generate_real_hypotheses()
        hypotheses = payload["hypotheses"]

        self.assertEqual(len(hypotheses), 5)
        for hypothesis in hypotheses:
            self.assertTrue(hypothesis["id"].startswith("real:H"))
            self.assertGreaterEqual(len(hypothesis["supporting_claim_ids"]), 2)
            self.assertEqual(hypothesis["status"], "candidate_requires_evidence_audit")
            self.assertIn("evidence_strength", hypothesis["scores"])
            self.assertIn("novelty_gap", hypothesis["scores"])
            self.assertIn("feasibility", hypothesis["scores"])
            self.assertIn("human_validation_need", hypothesis["scores"])


if __name__ == "__main__":
    unittest.main()
