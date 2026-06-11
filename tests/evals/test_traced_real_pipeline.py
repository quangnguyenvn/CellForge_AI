import os
import unittest

from services.evals.traced_real_pipeline import run_traced_real_pipeline


class TracedRealPipelineTest(unittest.TestCase):
    def test_traced_pipeline_logs_observability_and_self_introspection(self) -> None:
        previous_provider = os.environ.get("CELLFORGE_TRACE_PROVIDER")
        os.environ["CELLFORGE_TRACE_PROVIDER"] = "mock"
        summary = run_traced_real_pipeline(run_id="cellforge-test-trace")
        if previous_provider is None:
            os.environ.pop("CELLFORGE_TRACE_PROVIDER", None)
        else:
            os.environ["CELLFORGE_TRACE_PROVIDER"] = previous_provider

        self.assertEqual(summary["adapter"], "MockPhoenixAdapter")
        self.assertEqual(summary["retrieval"]["cases"], 12)
        self.assertEqual(summary["audit"]["hypotheses"], 5)
        self.assertEqual(summary["self_improvement"]["selected_hypothesis_id"], "real:H003")
        stages = summary["compare_runs"]["runs"]["cellforge-test-trace"]["stages"]
        self.assertIn("literature_retrieval_agent.real_benchmark", stages)
        self.assertIn("hypothesis_generator_agent.deterministic", stages)
        self.assertIn("evidence_auditor_agent.real_hypotheses", stages)
        self.assertIn("self_introspection_agent.trace_based_improvement_plan", stages)


if __name__ == "__main__":
    unittest.main()
