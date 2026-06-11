import unittest

from services.evals.local_eval import run_retrieval_benchmark


class RetrievalBenchmarkTest(unittest.TestCase):
    def test_retrieval_benchmark_has_usable_baseline_quality(self) -> None:
        report = run_retrieval_benchmark()
        summary = report["summary"]

        self.assertGreaterEqual(summary["cases"], 200)
        self.assertGreaterEqual(summary["paper_recall_at_5"], 0.70)
        self.assertGreaterEqual(summary["claim_recall_at_10"], 0.60)
        self.assertLessEqual(summary["hard_negative_rate_at_5"], 0.25)


if __name__ == "__main__":
    unittest.main()
