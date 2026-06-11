from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Sequence


ROOT = Path(__file__).resolve().parents[2]
MOCK_CORPUS_PATH = ROOT / "data" / "mock_papers.json"
RETRIEVAL_BENCHMARK_PATH = ROOT / "data" / "evals" / "retrieval_benchmark.jsonl"
AUDITOR_EVAL_PATH = ROOT / "data" / "evals" / "evidence_auditor_eval_set.jsonl"
SUPPORTED_ADAPTERS = {"local_mock"}


def ensure_supported_adapter(adapter: str) -> None:
    if adapter in SUPPORTED_ADAPTERS:
        return
    if adapter == "pipeline":
        raise RuntimeError(
            "The 'pipeline' adapter is reserved for the full CellForge pipeline. "
            "Connect retrieval and auditor service functions before using it."
        )
    raise RuntimeError(f"Unsupported eval adapter: {adapter}")


def load_jsonl(path: Path) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            stripped = line.strip()
            if stripped:
                rows.append(json.loads(stripped))
    return rows


def load_mock_corpus(path: Path = MOCK_CORPUS_PATH) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def tokens(text: str) -> Counter[str]:
    normalized = "".join(ch.lower() if ch.isalnum() else " " for ch in text)
    stop_words = {
        "and",
        "the",
        "for",
        "with",
        "under",
        "during",
        "will",
        "can",
        "cell",
        "cells",
        "battery",
        "batteries",
    }
    return Counter(token for token in normalized.split() if len(token) > 2 and token not in stop_words)


def overlap_score(query: str, text: str) -> float:
    query_tokens = tokens(query)
    doc_tokens = tokens(text)
    if not query_tokens:
        return 0.0
    overlap = sum(min(count, doc_tokens[token]) for token, count in query_tokens.items())
    return overlap / max(sum(query_tokens.values()), 1)


def hybrid_search_papers(query: str, corpus: Dict[str, Any], limit: int = 5) -> List[Dict[str, Any]]:
    papers = corpus["papers"]
    ranked = sorted(
        papers,
        key=lambda paper: overlap_score(query, " ".join([paper["title"], paper["abstract"], " ".join(paper.get("topics", []))])),
        reverse=True,
    )
    return ranked[:limit]


def search_claims(query: str, corpus: Dict[str, Any], paper_ids: Sequence[str], limit: int = 10) -> List[Dict[str, Any]]:
    paper_id_set = set(paper_ids)
    candidates = [claim for claim in corpus["claims"] if claim["source_paper_id"] in paper_id_set]
    ranked = sorted(
        candidates,
        key=lambda claim: overlap_score(
            query,
            " ".join(
                [
                    claim["claim_text"],
                    claim["battery_chemistry"],
                    claim["approach_type"],
                    claim["metric"],
                    claim["value"],
                    claim["experimental_condition"],
                    claim["limitation"],
                ]
            ),
        ),
        reverse=True,
    )
    return ranked[:limit]


def recall_at_k(expected_ids: Sequence[str], retrieved_ids: Sequence[str], k: int) -> float:
    if not expected_ids:
        return 1.0
    expected = set(expected_ids)
    retrieved = set(retrieved_ids[:k])
    return len(expected & retrieved) / len(expected)


def reciprocal_rank(expected_ids: Sequence[str], retrieved_ids: Sequence[str]) -> float:
    expected = set(expected_ids)
    for index, item_id in enumerate(retrieved_ids, start=1):
        if item_id in expected:
            return 1.0 / index
    return 0.0


def hard_negative_rate(hard_negative_ids: Sequence[str], retrieved_ids: Sequence[str], k: int) -> float:
    if k <= 0:
        return 0.0
    hard_negatives = set(hard_negative_ids)
    return len(hard_negatives & set(retrieved_ids[:k])) / k


def run_retrieval_benchmark(k_papers: int = 5, k_claims: int = 10, adapter: str = "local_mock") -> Dict[str, Any]:
    ensure_supported_adapter(adapter)
    corpus = load_mock_corpus()
    cases = load_jsonl(RETRIEVAL_BENCHMARK_PATH)
    results: List[Dict[str, Any]] = []

    for case in cases:
        retrieved_papers = hybrid_search_papers(case["query"], corpus, limit=k_papers)
        paper_ids = [paper["id"] for paper in retrieved_papers]
        retrieved_claims = search_claims(case["query"], corpus, paper_ids, limit=k_claims)
        claim_ids = [claim["id"] for claim in retrieved_claims]
        result = {
            "case_id": case["case_id"],
            "paper_recall_at_k": recall_at_k(case["expected_paper_ids"], paper_ids, k_papers),
            "claim_recall_at_k": recall_at_k(case["expected_claim_ids"], claim_ids, k_claims),
            "paper_mrr": reciprocal_rank(case["expected_paper_ids"], paper_ids),
            "claim_mrr": reciprocal_rank(case["expected_claim_ids"], claim_ids),
            "hard_negative_rate_at_k": hard_negative_rate(case.get("hard_negative_paper_ids", []), paper_ids, k_papers),
            "retrieved_paper_ids": paper_ids,
            "retrieved_claim_ids": claim_ids,
        }
        results.append(result)

    summary = {
        "adapter": adapter,
        "cases": len(results),
        "paper_recall_at_5": round(sum(item["paper_recall_at_k"] for item in results) / len(results), 3),
        "claim_recall_at_10": round(sum(item["claim_recall_at_k"] for item in results) / len(results), 3),
        "paper_mrr": round(sum(item["paper_mrr"] for item in results) / len(results), 3),
        "claim_mrr": round(sum(item["claim_mrr"] for item in results) / len(results), 3),
        "hard_negative_rate_at_5": round(sum(item["hard_negative_rate_at_k"] for item in results) / len(results), 3),
    }
    return {"summary": summary, "results": results}


def audit_hypothesis(hypothesis: Dict[str, Any], claims: List[Dict[str, Any]]) -> Dict[str, Any]:
    claim_by_id = {claim["id"]: claim for claim in claims}
    support = [claim_by_id[claim_id] for claim_id in hypothesis.get("supporting_claim_ids", []) if claim_id in claim_by_id]
    contradictions = [claim_by_id[claim_id] for claim_id in hypothesis.get("contradicting_claim_ids", []) if claim_id in claim_by_id]
    text = " ".join([hypothesis.get("title", ""), hypothesis.get("hypothesis", ""), " ".join(hypothesis.get("metric_terms", []))])
    chemistry = hypothesis.get("battery_chemistry", "").lower()

    citation_coverage = min(len(support) / 3, 1.0)
    support_text = " ".join(
        " ".join(
            [
                claim["claim_text"],
                claim["battery_chemistry"],
                claim["approach_type"],
                claim["metric"],
                claim["experimental_condition"],
            ]
        )
        for claim in support
    )
    lexical_grounding = overlap_score(text, support_text) if support else 0.0
    chemistry_match = 0.0
    if support:
        matches = [1 for claim in support if chemistry and any(part in claim["battery_chemistry"].lower() for part in chemistry.split())]
        chemistry_match = len(matches) / len(support)
    claim_grounding = min((lexical_grounding * 0.65) + (chemistry_match * 0.35), 1.0)
    contradiction_coverage = min(len(contradictions) / 2, 1.0)

    risk = 1.0 - ((citation_coverage * 0.45) + (claim_grounding * 0.35) + (contradiction_coverage * 0.20))
    unsupported_claims: List[str] = []
    if len(support) < 2:
        unsupported_claims.append("Fewer than two supporting claims are cited.")
    if support and chemistry_match < 0.5:
        unsupported_claims.append("Supporting claims appear to come from a different chemistry or format.")

    hypothesis_lower = hypothesis.get("hypothesis", "").lower()
    risky_phrases = ["proves", "ready to solve", "eliminate", "no charge-time penalty", "identical"]
    if any(phrase in hypothesis_lower for phrase in risky_phrases):
        risk = min(1.0, risk + 0.3)
        unsupported_claims.append("Hypothesis uses over-strong causal or deployment language.")

    contradiction_notes = [f"{claim['citation_text']}: {claim['limitation']}" for claim in contradictions]
    if contradiction_coverage == 0 and any("not " in claim["limitation"].lower() or "mixed" in claim["value"].lower() for claim in support):
        risk = min(1.0, risk + 0.15)
        unsupported_claims.append("Potential contradiction or limitation is present in support but not cited as contradiction.")

    recommendation = "advance" if citation_coverage >= 0.75 and claim_grounding >= 0.60 and risk <= 0.40 else "revise"
    return {
        "citation_coverage": round(citation_coverage, 3),
        "claim_grounding": round(claim_grounding, 3),
        "contradiction_coverage": round(contradiction_coverage, 3),
        "hallucination_risk": round(risk, 3),
        "unsupported_claims": unsupported_claims,
        "contradiction_notes": contradiction_notes,
        "recommendation": recommendation,
    }


def run_auditor_eval(adapter: str = "local_mock") -> Dict[str, Any]:
    ensure_supported_adapter(adapter)
    corpus = load_mock_corpus()
    cases = load_jsonl(AUDITOR_EVAL_PATH)
    results: List[Dict[str, Any]] = []

    for case in cases:
        audit = audit_hypothesis(case["hypothesis"], corpus["claims"])
        expected = case["expected"]
        checks = {
            "citation_coverage": audit["citation_coverage"] >= expected["citation_coverage_min"],
            "claim_grounding": audit["claim_grounding"] >= expected["claim_grounding_min"],
            "contradiction_coverage": audit["contradiction_coverage"] >= expected["contradiction_coverage_min"],
            "hallucination_risk": audit["hallucination_risk"] <= expected["hallucination_risk_max"],
            "recommendation": audit["recommendation"] == expected["recommendation"],
        }
        results.append(
            {
                "case_id": case["case_id"],
                "passed": all(checks.values()),
                "checks": checks,
                "audit": audit,
                "expected": expected,
            }
        )

    passed = sum(1 for item in results if item["passed"])
    summary = {
        "adapter": adapter,
        "cases": len(results),
        "passed": passed,
        "failed": len(results) - passed,
        "pass_rate": round(passed / len(results), 3),
    }
    return {"summary": summary, "results": results}


def print_report(report: Dict[str, Any]) -> None:
    print(json.dumps(report["summary"], indent=2))
    for item in report["results"]:
        status = "PASS" if item.get("passed", True) else "FAIL"
        print(f"{status} {item['case_id']}")
        if not item.get("passed", True):
            print(json.dumps(item, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(description="Run local CellForge AI evaluation packs.")
    parser.add_argument("target", choices=["retrieval", "auditor", "all"], help="Evaluation target to run.")
    parser.add_argument(
        "--adapter",
        default="local_mock",
        choices=["local_mock", "pipeline"],
        help="Eval adapter to use. 'pipeline' is a reserved integration point.",
    )
    args = parser.parse_args()

    if args.target in {"retrieval", "all"}:
        print("Retrieval benchmark")
        print_report(run_retrieval_benchmark(adapter=args.adapter))

    if args.target in {"auditor", "all"}:
        print("Evidence auditor eval")
        print_report(run_auditor_eval(adapter=args.adapter))


if __name__ == "__main__":
    main()
