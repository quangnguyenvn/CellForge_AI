import unittest

from services.evals.cloud_extraction_normalizer import build_real_corpus


class CloudExtractionNormalizerTest(unittest.TestCase):
    def test_builds_real_corpus_from_cloud_extractions(self) -> None:
        corpus = build_real_corpus()

        self.assertGreaterEqual(len(corpus["papers"]), 8)
        self.assertGreaterEqual(len(corpus["claims"]), 8)
        self.assertTrue(any(issue["issue"] == "empty_file" for issue in corpus["issues"]))
        self.assertTrue(all(claim["source_paper_id"].startswith("real:P") for claim in corpus["claims"]))
        self.assertTrue(all(claim["needs_human_review"] for claim in corpus["claims"]))
        self.assertEqual(
            corpus["quality_summary"]["publication_readiness"],
            "not_publication_ready_without_human_validation",
        )
        self.assertEqual(len(corpus["manifest"]), len(corpus["papers"]) + len(corpus["issues"]))


if __name__ == "__main__":
    unittest.main()
