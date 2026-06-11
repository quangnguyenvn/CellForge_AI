from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Tuple


ROOT = Path(__file__).resolve().parents[2]
CLOUD_EXTRACTIONS_DIR = ROOT / "data" / "cloud_extractions"
REAL_PAPERS_PATH = ROOT / "data" / "real_papers.json"
REAL_CLAIMS_PATH = ROOT / "data" / "real_claims.json"
REAL_EVIDENCE_CORPUS_PATH = ROOT / "data" / "real_evidence_corpus.json"
REAL_EVIDENCE_MANIFEST_PATH = ROOT / "data" / "real_evidence_manifest.json"
CLOUD_EXTRACTION_REPORT_PATH = ROOT / "reports" / "cloud_extraction_report.md"


@dataclass(frozen=True)
class ExtractionIssue:
    filename: str
    issue: str


def load_extraction_files(directory: Path = CLOUD_EXTRACTIONS_DIR) -> Tuple[List[Dict[str, Any]], List[ExtractionIssue]]:
    extractions: List[Dict[str, Any]] = []
    issues: List[ExtractionIssue] = []

    for path in sorted(directory.glob("*.json")):
        if path.stat().st_size == 0:
            issues.append(ExtractionIssue(path.name, "empty_file"))
            continue

        try:
            with path.open("r", encoding="utf-8-sig") as handle:
                payload = json.load(handle)
        except json.JSONDecodeError as exc:
            issues.append(ExtractionIssue(path.name, f"invalid_json: {exc}"))
            continue

        if not isinstance(payload, dict):
            issues.append(ExtractionIssue(path.name, "top_level_json_is_not_object"))
            continue

        payload["_source_extraction_file"] = path.name
        extractions.append(payload)

    return extractions, issues


def infer_numeric_prefix(filename: str) -> str:
    digits = []
    for char in filename:
        if char.isdigit():
            digits.append(char)
        elif digits:
            break
    return "".join(digits).zfill(3) if digits else "000"


def normalize_paper(extraction: Dict[str, Any]) -> Dict[str, Any]:
    filename = extraction["_source_extraction_file"]
    paper_num = infer_numeric_prefix(filename)
    title = clean_text(str(extraction.get("title") or filename))
    needs_review, review_reason = review_status(extraction)
    return {
        "id": f"real:P{paper_num}",
        "title": title,
        "authors": [],
        "year": None,
        "venue": None,
        "abstract": clean_text(extraction.get("abstract_summary", "")),
        "paper_type": clean_text(extraction.get("paper_type", "")),
        "battery_chemistry": clean_text(extraction.get("battery_chemistry", "")),
        "electrode_component": clean_text(extraction.get("electrode_component", "")),
        "green_strategy": clean_text(extraction.get("green_strategy", "")),
        "fabrication_method": clean_text(extraction.get("fabrication_method", "")),
        "performance_metrics": clean_value(extraction.get("performance_metrics", [])),
        "limitations": clean_value(extraction.get("limitations", [])),
        "figure_or_table_evidence": clean_value(extraction.get("figure_or_table_evidence", [])),
        "confidence": extraction.get("confidence"),
        "needs_human_review": needs_review,
        "human_review_reason": review_reason,
        "source_extraction_file": filename,
        "source_type": "google_cloud_gemini_document_understanding",
        "status": "extracted_needs_human_validation",
    }


def normalize_claims(extraction: Dict[str, Any], paper_id: str) -> List[Dict[str, Any]]:
    filename = extraction["_source_extraction_file"]
    paper_num = infer_numeric_prefix(filename)
    claims = extraction.get("candidate_research_claims", [])
    needs_review, review_reason = review_status(extraction)
    normalized: List[Dict[str, Any]] = []

    if not isinstance(claims, list):
        return normalized

    for index, claim in enumerate(claims, start=1):
        if not isinstance(claim, dict):
            continue

        claim_text = str(claim.get("claim_text") or "").strip()
        if not claim_text:
            continue

        normalized.append(
            {
                "id": f"real:C{paper_num}_{index:02d}",
                "claim_text": clean_text(claim_text),
                "battery_chemistry": clean_text(claim.get("battery_chemistry", extraction.get("battery_chemistry", ""))),
                "approach_type": clean_text(claim.get("approach_type", "")),
                "metric": clean_text(claim.get("metric", "")),
                "value": clean_text(claim.get("value", "")),
                "experimental_condition": clean_text(claim.get("experimental_condition", "")),
                "evidence_type": clean_text(claim.get("evidence_type", "")),
                "limitation": clean_text(claim.get("limitation", "")),
                "source_paper_id": paper_id,
                "citation_text": clean_text(claim.get("citation_text", "")),
                "source_section_or_page": clean_text(claim.get("source_section_or_page", "")),
                "needs_human_review": needs_review,
                "human_review_reason": review_reason,
                "source_extraction_file": filename,
            }
        )

    return normalized


def clean_text(value: Any) -> str:
    text = str(value or "")
    replacements = {
        "Ï€": "pi",
        "â€“": "-",
        "â€”": "-",
        "Â°C": "C",
        "Â°": " degrees",
        "Âµ": "micro",
    }
    for source, target in replacements.items():
        text = text.replace(source, target)
    return text


def clean_value(value: Any) -> Any:
    if isinstance(value, str):
        return clean_text(value)
    if isinstance(value, list):
        return [clean_value(item) for item in value]
    if isinstance(value, dict):
        return {key: clean_value(item) for key, item in value.items()}
    return value


def review_status(extraction: Dict[str, Any]) -> Tuple[bool, str]:
    reasons: List[str] = []
    if extraction.get("needs_human_review", True):
        reason = str(extraction.get("human_review_reason", "")).strip()
        reasons.append(reason or "Gemini extraction marked this paper as needing human review.")

    figures = extraction.get("figure_or_table_evidence", [])
    if isinstance(figures, list) and any(
        isinstance(item, dict) and item.get("needs_manual_digitization") for item in figures
    ):
        reasons.append("At least one figure/table requires manual digitization or visual verification.")

    metrics = extraction.get("performance_metrics", [])
    claims = extraction.get("candidate_research_claims", [])
    if isinstance(metrics, list) and isinstance(claims, list) and metrics and claims:
        reasons.append("High-value performance metrics and claims should be verified before use in a research brief.")

    unique_reasons = []
    for reason in reasons:
        if reason and reason not in unique_reasons:
            unique_reasons.append(reason)

    return bool(unique_reasons), " ".join(unique_reasons)


def build_real_corpus() -> Dict[str, Any]:
    extractions, issues = load_extraction_files()
    papers = [normalize_paper(extraction) for extraction in extractions]
    claims: List[Dict[str, Any]] = []

    for extraction, paper in zip(extractions, papers):
        claims.extend(normalize_claims(extraction, paper["id"]))

    manifest = build_manifest(papers, claims, issues)
    quality_summary = build_quality_summary(papers, claims, issues)

    return {
        "description": (
            "Real-paper evidence corpus generated from Google Cloud/Gemini document understanding outputs. "
            "Claims are extraction artifacts and require human validation before publication use."
        ),
        "source_directory": str(CLOUD_EXTRACTIONS_DIR.relative_to(ROOT)),
        "scope": "green and sustainable electrode materials/fabrication for lithium-ion batteries",
        "papers": papers,
        "claims": claims,
        "issues": [{"filename": issue.filename, "issue": issue.issue} for issue in issues],
        "manifest": manifest,
        "quality_summary": quality_summary,
    }


def build_manifest(
    papers: List[Dict[str, Any]], claims: List[Dict[str, Any]], issues: List[ExtractionIssue]
) -> List[Dict[str, Any]]:
    claim_counts: Dict[str, int] = {}
    for claim in claims:
        paper_id = str(claim.get("source_paper_id", ""))
        claim_counts[paper_id] = claim_counts.get(paper_id, 0) + 1

    rows = [
        {
            "source_extraction_file": paper["source_extraction_file"],
            "status": "extracted_needs_human_validation",
            "paper_id": paper["id"],
            "claim_count": claim_counts.get(paper["id"], 0),
            "needs_human_review": paper.get("needs_human_review", True),
            "title": paper.get("title", ""),
        }
        for paper in papers
    ]
    rows.extend(
        {
            "source_extraction_file": issue.filename,
            "status": issue.issue,
            "paper_id": None,
            "claim_count": 0,
            "needs_human_review": True,
            "title": "",
        }
        for issue in issues
    )
    return sorted(rows, key=lambda row: str(row["source_extraction_file"]))


def build_quality_summary(
    papers: List[Dict[str, Any]], claims: List[Dict[str, Any]], issues: List[ExtractionIssue]
) -> Dict[str, Any]:
    paper_ids_with_claims = {claim["source_paper_id"] for claim in claims}
    claimless_papers = [paper["id"] for paper in papers if paper["id"] not in paper_ids_with_claims]
    approach_counts: Dict[str, int] = {}
    component_counts: Dict[str, int] = {}
    review_claims = 0

    for claim in claims:
        approach = str(claim.get("approach_type") or "unspecified")
        approach_counts[approach] = approach_counts.get(approach, 0) + 1
        if claim.get("needs_human_review", True):
            review_claims += 1

    for paper in papers:
        component = str(paper.get("electrode_component") or "unspecified")
        component_counts[component] = component_counts.get(component, 0) + 1

    return {
        "extracted_paper_count": len(papers),
        "extracted_claim_count": len(claims),
        "skipped_or_invalid_file_count": len(issues),
        "human_review_claim_count": review_claims,
        "claimless_paper_ids": claimless_papers,
        "approach_type_counts": dict(sorted(approach_counts.items())),
        "electrode_component_counts": dict(sorted(component_counts.items())),
        "quality_gate": "usable_for_demo_retrieval_and_hypothesis_generation",
        "publication_readiness": "not_publication_ready_without_human_validation",
    }


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)
        handle.write("\n")


def write_report(path: Path, corpus: Dict[str, Any]) -> None:
    papers = corpus["papers"]
    claims = corpus["claims"]
    issues = corpus["issues"]
    summary = corpus["quality_summary"]
    review_count = sum(1 for paper in papers if paper.get("needs_human_review"))

    lines = [
        "# Cloud Extraction Normalization Report",
        "",
        "This report summarizes the Google Cloud/Gemini document-understanding outputs normalized for CellForge AI.",
        "",
        "## Summary",
        "",
        f"- Extracted papers: `{len(papers)}`",
        f"- Extracted claims: `{len(claims)}`",
        f"- Papers needing human review: `{review_count}`",
        f"- Skipped/invalid files: `{len(issues)}`",
        f"- Quality gate: `{summary['quality_gate']}`",
        f"- Publication readiness: `{summary['publication_readiness']}`",
        "",
        "## Corpus Scope",
        "",
        str(corpus["scope"]),
        "",
        "## Papers",
        "",
        "| Paper ID | Review | Title | Source file |",
        "| --- | --- | --- | --- |",
    ]

    for paper in papers:
        review = "yes" if paper.get("needs_human_review") else "no"
        title = str(paper.get("title", "")).replace("|", "\\|")
        source = str(paper.get("source_extraction_file", "")).replace("|", "\\|")
        lines.append(f"| {paper['id']} | {review} | {title} | {source} |")

    lines.extend(["", "## Claims", "", "| Claim ID | Paper ID | Approach | Metric | Value | Human review |", "| --- | --- | --- | --- | --- | --- |"])
    for claim in claims:
        approach = str(claim.get("approach_type", "")).replace("|", "\\|")
        metric = str(claim.get("metric", "")).replace("|", "\\|")
        value = str(claim.get("value", "")).replace("|", "\\|")
        review = "yes" if claim.get("needs_human_review") else "no"
        lines.append(f"| {claim['id']} | {claim['source_paper_id']} | {approach} | {metric} | {value} | {review} |")

    if issues:
        lines.extend(["", "## Skipped Or Invalid Files", "", "| File | Issue |", "| --- | --- |"])
        for issue in issues:
            lines.append(f"| {issue['filename']} | {issue['issue']} |")

    lines.extend(
        [
            "",
            "## Quality Summary",
            "",
            "```json",
            json.dumps(summary, indent=2, ensure_ascii=False),
            "```",
        ]
    )

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def normalize_cloud_extractions() -> Dict[str, Any]:
    corpus = build_real_corpus()
    write_json(
        REAL_PAPERS_PATH,
        {key: corpus[key] for key in ("description", "source_directory", "scope", "papers", "issues", "quality_summary")},
    )
    write_json(
        REAL_CLAIMS_PATH,
        {key: corpus[key] for key in ("description", "source_directory", "scope", "claims", "issues", "quality_summary")},
    )
    write_json(
        REAL_EVIDENCE_CORPUS_PATH,
        {key: corpus[key] for key in ("description", "source_directory", "scope", "papers", "claims", "issues", "quality_summary")},
    )
    write_json(
        REAL_EVIDENCE_MANIFEST_PATH,
        {key: corpus[key] for key in ("description", "source_directory", "scope", "manifest", "quality_summary")},
    )
    write_report(CLOUD_EXTRACTION_REPORT_PATH, corpus)
    return {
        "papers": len(corpus["papers"]),
        "claims": len(corpus["claims"]),
        "issues": len(corpus["issues"]),
        "real_papers_path": str(REAL_PAPERS_PATH),
        "real_claims_path": str(REAL_CLAIMS_PATH),
        "real_evidence_corpus_path": str(REAL_EVIDENCE_CORPUS_PATH),
        "real_evidence_manifest_path": str(REAL_EVIDENCE_MANIFEST_PATH),
        "report_path": str(CLOUD_EXTRACTION_REPORT_PATH),
    }


if __name__ == "__main__":
    print(json.dumps(normalize_cloud_extractions(), indent=2))
