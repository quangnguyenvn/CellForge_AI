import unittest

from services.evals.manuscript_draft import generate_manuscript_draft, MANUSCRIPT_DRAFT_PATH, MANUSCRIPT_READINESS_PATH


class ManuscriptDraftTest(unittest.TestCase):
    def test_validated_only_has_explicit_gate_behavior(self) -> None:
        payload = generate_manuscript_draft(validated_only=True)

        if payload["status"] == "blocked_pending_human_validation":
            self.assertFalse(payload["draft_written"])
            self.assertEqual(payload["validated_items"], 0)
            self.assertTrue(MANUSCRIPT_READINESS_PATH.exists())
            text = MANUSCRIPT_READINESS_PATH.read_text(encoding="utf-8")
            self.assertIn("blocked_pending_human_validation", text)
            self.assertIn("validation_queue.json", text)
        else:
            self.assertEqual(payload["status"], "draft_generated")
            self.assertTrue(payload["draft_written"])
            self.assertGreater(payload["validated_items"], 0)
            self.assertTrue(MANUSCRIPT_DRAFT_PATH.exists())
            text = MANUSCRIPT_DRAFT_PATH.read_text(encoding="utf-8")
            self.assertIn("human-validated CellForge evidence", text)


if __name__ == "__main__":
    unittest.main()
