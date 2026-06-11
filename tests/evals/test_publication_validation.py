import unittest

from services.evals.publication_validation import (
    LEAD_HYPOTHESIS_ID,
    build_validation_queue,
    render_final_paper_roadmap,
    render_validation_checklist,
)


class PublicationValidationTest(unittest.TestCase):
    def test_validation_queue_prioritizes_lead_hypothesis_claims(self) -> None:
        queue = build_validation_queue()

        self.assertEqual(queue["summary"]["lead_hypothesis_id"], LEAD_HYPOTHESIS_ID)
        self.assertGreaterEqual(queue["summary"]["critical"], 3)
        self.assertGreaterEqual(queue["summary"]["high"], 1)
        critical_claims = [item["claim_id"] for item in queue["items"] if item["priority"] == "critical"]
        self.assertIn("real:C107_01", critical_claims)
        self.assertIn("real:C107_02", critical_claims)
        self.assertIn("real:C099_01", critical_claims)

    def test_validation_outputs_contain_publication_gate_language(self) -> None:
        queue = build_validation_queue()
        checklist = render_validation_checklist(queue)
        roadmap = render_final_paper_roadmap(queue)

        self.assertIn("source PDFs", checklist)
        self.assertIn("Allowed in manuscript", checklist)
        self.assertIn("only validated items", queue["summary"]["manuscript_gate"])
        self.assertIn("real:H003", roadmap)
        self.assertIn("hard gate", roadmap)


if __name__ == "__main__":
    unittest.main()
