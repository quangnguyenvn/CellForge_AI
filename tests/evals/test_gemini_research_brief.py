import os
import unittest

from services.evals.gemini_research_brief import (
    BRIEF_JSON_PATH,
    BRIEF_MD_PATH,
    FIGURES_DIR,
    generate_research_brief,
)


class GeminiResearchBriefTest(unittest.TestCase):
    def test_local_brief_generation_writes_expected_artifacts(self) -> None:
        previous_trace_provider = os.environ.get("CELLFORGE_TRACE_PROVIDER")
        os.environ["CELLFORGE_TRACE_PROVIDER"] = "mock"
        payload = generate_research_brief(provider="local", run_id="cellforge-test-brief")
        if previous_trace_provider is None:
            os.environ.pop("CELLFORGE_TRACE_PROVIDER", None)
        else:
            os.environ["CELLFORGE_TRACE_PROVIDER"] = previous_trace_provider

        self.assertEqual(payload["summary"]["hypotheses"], 5)
        self.assertEqual(payload["summary"]["publication_positioning"], "research_proposal_package_not_final_paper")
        self.assertTrue(BRIEF_MD_PATH.exists())
        self.assertTrue(BRIEF_JSON_PATH.exists())
        text = BRIEF_MD_PATH.read_text(encoding="utf-8")
        self.assertIn("not a publishable final paper", text)
        self.assertIn("real:H003", text)
        self.assertIn("audit_scores.svg", text)
        self.assertIn("molecular_interface_schematic.svg", text)
        self.assertTrue((FIGURES_DIR / "audit_scores.svg").exists())
        self.assertTrue((FIGURES_DIR / "evidence_matrix.svg").exists())
        self.assertTrue((FIGURES_DIR / "risk_grounding_scatter.svg").exists())
        self.assertTrue((FIGURES_DIR / "molecular_interface_schematic.svg").exists())


if __name__ == "__main__":
    unittest.main()
