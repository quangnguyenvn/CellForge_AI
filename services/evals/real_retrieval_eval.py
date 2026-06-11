from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

from services.evals.local_eval import (
    hard_negative_rate,
    load_jsonl,
    overlap_score,
    recall_at_k,
    reciprocal_rank,
)


ROOT = Path(__file__).resolve().parents[2]
REAL_CORPUS_PATH = ROOT / "data" / "real_evidence_corpus.json"
REAL_RETRIEVAL_BENCHMARK_PATH = ROOT / "data" / "evals" / "real_retrieval_benchmark.jsonl"
REAL_RETRIEVAL_REPORT_JSON = ROOT / "reports" / "real_retrieval_benchmark_report.json"
REAL_RETRIEVAL_REPORT_MD = ROOT / "reports" / "real_retrieval_benchmark_report.md"


def load_real_corpus(path: Path = REAL_CORPUS_PATH) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def flatten_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, (int, float, bool)):
        return str(value)
    if isinstance(value, list):
        return " ".join(flatten_text(item) for item in value)
    if isinstance(value, dict):
        return " ".join(flatten_text(item) for item in value.values())
    return str(value)


def paper_document_text(paper: Dict[str, Any]) -> str:
    fields = [
        paper.get("title", ""),
        paper.get("abstract", ""),
        paper.get("paper_type", ""),
        paper.get("battery_chemistry", ""),
        paper.get("electrode_component", ""),
        paper.get("green_strategy", ""),
        paper.get("fabrication_method", ""),
        paper.get("performance_metrics", []),
        paper.get("limitations", []),
        paper.get("figure_or_table_evidence", []),
    ]
    return flatten_text(fields)


def claim_document_text(claim: Dict[str, Any], paper: Dict[str, Any] | None = None) -> str:
    fields = [
        claim.get("claim_text", ""),
        claim.get("battery_chemistry", ""),
        claim.get("approach_type", ""),
        claim.get("metric", ""),
        claim.get("value", ""),
        claim.get("experimental_condition", ""),
        claim.get("evidence_type", ""),
        claim.get("limitation", ""),
        claim.get("citation_text", ""),
        claim.get("source_section_or_page", ""),
    ]
    if paper is not None:
        fields.extend([paper.get("title", ""), paper.get("green_strategy", ""), paper.get("electrode_component", "")])
    return flatten_text(fields)


def rank_items(query: str, items: Sequence[Dict[str, Any]], text_builder: Any) -> List[Tuple[float, Dict[str, Any]]]:
    scored = [(overlap_score(query, text_builder(item)), item) for item in items]
    return sorted(scored, key=lambda pair: (pair[0], pair[1].get("id", "")), reverse=True)


def hybrid_search_real_papers(query: str, corpus: Dict[str, Any], limit: int = 5) -> List[Dict[str, Any]]:
    ranked = rank_items(query, corpus["papers"], paper_document_text)
    return [item for score, item in ranked if score > 0][:limit]


def search_real_claims(
    query: str,
    corpus: Dict[str, Any],
    retrieved_paper_ids: Sequence[str],
    limit: int = 5,
) -> List[Dict[str, Any]]:
    paper_by_id = {paper["id"]: paper for paper in corpus["papers"]}
    paper_rank_boost = {paper_id: max(0.0, 0.15 - (index * 0.025)) for index, paper_id in enumerate(retrieved_paper_ids)}
    scored: List[Tuple[float, Dict[str, Any]]] = []

    for claim in corpus["claims"]:
        paper = paper_by_id.get(claim.get("source_paper_id"))
        score = overlap_score(query, claim_document_text(claim, paper))
        score += paper_rank_boost.get(claim.get("source_paper_id", ""), 0.0)
        scored.append((score, claim))

    ranked = sorted(scored, key=lambda pair: (pair[0], pair[1].get("id", "")), reverse=True)
    return [item for score, item in ranked if score > 0][:limit]


def run_real_retrieval_benchmark(k_papers: int = 5, k_claims: int = 5) -> Dict[str, Any]:
    corpus = load_real_corpus()
    cases = load_jsonl(REAL_RETRIEVAL_BENCHMARK_PATH)
    results: List[Dict[str, Any]] = []

    for case in cases:
        retrieved_papers = hybrid_search_real_papers(case["query"], corpus, limit=k_papers)
        paper_ids = [paper["id"] for paper in retrieved_papers]
        retrieved_claims = search_real_claims(case["query"], corpus, paper_ids, limit=k_claims)
        claim_ids = [claim["id"] for claim in retrieved_claims]
        results.append(
            {
                "case_id": case["case_id"],
                "query": case["query"],
                "paper_recall_at_k": recall_at_k(case["expected_paper_ids"], paper_ids, k_papers),
                "claim_recall_at_k": recall_at_k(case["expected_claim_ids"], claim_ids, k_claims),
                "paper_mrr": reciprocal_rank(case["expected_paper_ids"], paper_ids),
                "claim_mrr": reciprocal_rank(case["expected_claim_ids"], claim_ids),
                "hard_negative_rate_at_k": hard_negative_rate(case.get("hard_negative_paper_ids", []), paper_ids, k_papers),
                "expected_paper_ids": case["expected_paper_ids"],
                "expected_claim_ids": case["expected_claim_ids"],
                "retrieved_paper_ids": paper_ids,
                "retrieved_claim_ids": claim_ids,
            }
        )

    summary = {
        "adapter": "local_real_corpus",
        "corpus": str(REAL_CORPUS_PATH.relative_to(ROOT)),
        "cases": len(results),
        "paper_recall_at_5": round(sum(item["paper_recall_at_k"] for item in results) / len(results), 3),
        "claim_recall_at_5": round(sum(item["claim_recall_at_k"] for item in results) / len(results), 3),
        "paper_mrr": round(sum(item["paper_mrr"] for item in results) / len(results), 3),
        "claim_mrr": round(sum(item["claim_mrr"] for item in results) / len(results), 3),
        "hard_negative_rate_at_5": round(sum(item["hard_negative_rate_at_k"] for item in results) / len(results), 3),
    }
    return {"summary": summary, "results": results}


def write_real_retrieval_report(report: Dict[str, Any]) -> None:
    REAL_RETRIEVAL_REPORT_JSON.parent.mkdir(parents=True, exist_ok=True)
    with REAL_RETRIEVAL_REPORT_JSON.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(report, handle, indent=2, ensure_ascii=False)
        handle.write("\n")

    summary = report["summary"]
    lines = [
        "# Real Retrieval Benchmark Report",
        "",
        "This benchmark validates retrieval over Gemini-extracted real-paper evidence, not the mock corpus.",
        "",
        "## Summary",
        "",
        f"- Cases: `{summary['cases']}`",
        f"- Paper recall@5: `{summary['paper_recall_at_5']}`",
        f"- Claim recall@5: `{summary['claim_recall_at_5']}`",
        f"- Paper MRR: `{summary['paper_mrr']}`",
        f"- Claim MRR: `{summary['claim_mrr']}`",
        f"- Hard negative rate@5: `{summary['hard_negative_rate_at_5']}`",
        "",
        "## Cases",
        "",
        "| Case | Paper recall | Claim recall | Paper MRR | Claim MRR | Retrieved papers | Retrieved claims |",
        "| --- | ---: | ---: | ---: | ---: | --- | --- |",
    ]
    for item in report["results"]:
        lines.append(
            "| {case_id} | {paper_recall:.3f} | {claim_recall:.3f} | {paper_mrr:.3f} | {claim_mrr:.3f} | {papers} | {claims} |".format(
                case_id=item["case_id"],
                paper_recall=item["paper_recall_at_k"],
                claim_recall=item["claim_recall_at_k"],
                paper_mrr=item["paper_mrr"],
                claim_mrr=item["claim_mrr"],
                papers=", ".join(item["retrieved_paper_ids"]),
                claims=", ".join(item["retrieved_claim_ids"]),
            )
        )

    REAL_RETRIEVAL_REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def print_report(report: Dict[str, Any]) -> None:
    print(json.dumps(report["summary"], indent=2))
    for item in report["results"]:
        passed = item["paper_recall_at_k"] > 0 and item["claim_recall_at_k"] > 0
        print(f"{'PASS' if passed else 'FAIL'} {item['case_id']}")
        if not passed:
            print(json.dumps(item, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(description="Run real-paper retrieval benchmark.")
    parser.add_argument("--write-report", action="store_true", help="Write JSON and Markdown reports under reports/.")
    args = parser.parse_args()

    report = run_real_retrieval_benchmark()
    print_report(report)
    if args.write_report:
        write_real_retrieval_report(report)


if __name__ == "__main__":
    main()
