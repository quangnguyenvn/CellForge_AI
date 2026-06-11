import unittest

from services.evals.real_retrieval_eval import run_real_retrieval_benchmark


class RealRetrievalBenchmarkTest(unittest.TestCase):
    def test_real_retrieval_benchmark_has_usable_baseline_quality(self) -> None:
        report = run_real_retrieval_benchmark()
        summary = report["summary"]

        self.assertGreaterEqual(summary["cases"], 10)
        self.assertGreaterEqual(summary["paper_recall_at_5"], 0.80)
        self.assertGreaterEqual(summary["claim_recall_at_5"], 0.75)
        self.assertLessEqual(summary["hard_negative_rate_at_5"], 0.30)


if __name__ == "__main__":
    unittest.main()
