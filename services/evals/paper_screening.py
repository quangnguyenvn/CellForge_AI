from __future__ import annotations

import json
import re
import subprocess
import sys
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Sequence


ROOT = Path(__file__).resolve().parents[2]
REAL_PAPERS_DIR = ROOT / "data" / "real_papers"
REAL_MANIFEST_PATH = ROOT / "data" / "real_papers_manifest.json"
SELECTED_PAPERS_PATH = ROOT / "data" / "selected_papers.json"
SCREENING_REPORT_PATH = ROOT / "reports" / "paper_screening_report.md"
TMP_SCREENING_DIR = ROOT / ".tmp_screening"
LOCAL_DEPS_DIR = ROOT / ".python-deps"

if LOCAL_DEPS_DIR.exists():
    sys.path.insert(0, str(LOCAL_DEPS_DIR))


BATTERY_TERMS = [
    "lithium-ion",
    "lithium ion",
    "li-ion",
    "lithium battery",
    "lithium-ion battery",
    "lib",
    "battery",
]

ELECTRODE_TERMS = [
    "electrode",
    "anode",
    "cathode",
    "active material",
    "binder",
    "graphite",
    "silicon",
    "lifepo4",
    "lithium iron phosphate",
    "nmc",
    "layered cathode",
    "electrode production",
    "electrode fabrication",
    "dry electrode",
    "thick electrode",
    "calendering",
    "slurry",
    "coating",
]

GREEN_TERMS = [
    "green",
    "sustainable",
    "eco-friendly",
    "ecofriendly",
    "environmental",
    "water-based",
    "aqueous",
    "solvent-free",
    "solvent-free processing",
    "drying-free",
    "dry electrode",
    "dry electrodes",
    "dry electrode processing",
    "dry processing",
    "nmp-free",
    "pvdf-free",
    "biomass",
    "bio-derived",
    "biodegradable",
    "chitosan",
    "lignin",
    "starch",
    "cellulose",
    "poly(hydroxybutyrate",
    "hydroxyvalerate",
    "plasma treatment",
    "microplasma",
    "natural graphite",
    "recycled graphite",
    "reuse of graphite",
    "tailings",
    "low-temperature synthesis",
    "one-step",
    "low energy",
    "fluorine-free",
]

PERFORMANCE_TERMS = [
    "capacity",
    "specific capacity",
    "capacity retention",
    "cycle",
    "cycling",
    "cycle life",
    "rate capability",
    "high-rate",
    "fast charging",
    "impedance",
    "coulombic efficiency",
    "energy density",
    "power density",
    "electrochemical performance",
    "long-cycle",
]

OUT_OF_SCOPE_TERMS = [
    "thermal runaway",
    "cooling",
    "state of health",
    "remaining useful life",
    "desalination",
    "fire extinguishing",
    "soot oxidation",
    "solar pond",
    "briquette",
    "catalyst",
    "electrocatalytic reduction",
]

REVIEW_TERMS = ["review", "perspective", "overview", "advancements", "recent advances", "critical review", "prospects"]
EXPERIMENT_TERMS = ["synthesis", "prepared", "fabrication", "performance", "electrochemical", "characterization", "properties"]


@dataclass
class ExtractedPdf:
    text: str
    pages: int
    extracted_pages: int
    metadata_text: str = ""
    extraction_error: str | None = None


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def console_safe(text: str) -> str:
    return text.encode("ascii", errors="replace").decode("ascii")


def contains_any(text: str, terms: Sequence[str]) -> bool:
    lowered = text.lower()
    return any(term in lowered for term in terms)


def count_terms(text: str, terms: Sequence[str]) -> int:
    lowered = text.lower()
    return sum(lowered.count(term) for term in terms)


def matched_terms(text: str, terms: Sequence[str]) -> List[str]:
    lowered = text.lower()
    return [term for term in terms if term in lowered]


def extract_pdf_text(pdf_path: Path, max_pages: int = 4) -> ExtractedPdf:
    if pdf_path.stat().st_size == 0:
        return ExtractedPdf(text="", pages=0, extracted_pages=0, extraction_error="empty_file")

    try:
        import fitz  # type: ignore

        document = fitz.open(str(pdf_path))
        page_count = document.page_count
        chunks = [document.load_page(index).get_text("text") for index in range(min(page_count, max_pages))]
        metadata = document.metadata or {}
        metadata_text = normalize(
            "\n".join(str(metadata.get(key) or "") for key in ["title", "subject", "keywords"] if metadata.get(key))
        )
        document.close()
        page_text = normalize("\n".join(chunks))
        combined_text = page_text if page_text else metadata_text
        return ExtractedPdf(
            text=combined_text,
            pages=page_count,
            extracted_pages=min(page_count, max_pages),
            metadata_text=metadata_text,
        )
    except ImportError:
        pass
    except Exception as exc:
        return ExtractedPdf(text="", pages=0, extracted_pages=0, extraction_error=f"pymupdf_extract_error: {exc}")

    try:
        from pypdf import PdfReader
    except ImportError as exc:
        return ExtractedPdf(text="", pages=0, extracted_pages=0, extraction_error=f"missing_pypdf: {exc}")

    try:
        reader = PdfReader(str(pdf_path))
        page_count = len(reader.pages)
        chunks: List[str] = []
        for page in reader.pages[:max_pages]:
            chunks.append(page.extract_text() or "")
        metadata = reader.metadata or {}
        metadata_text = normalize(
            "\n".join(str(metadata.get(key) or "") for key in ["/Title", "/Subject", "/Keywords"] if metadata.get(key))
        )
        page_text = normalize("\n".join(chunks))
        combined_text = page_text if page_text else metadata_text
        return ExtractedPdf(text=combined_text, pages=page_count, extracted_pages=min(page_count, max_pages), metadata_text=metadata_text)
    except Exception as exc:  # pragma: no cover - depends on arbitrary PDF structure
        return ExtractedPdf(text="", pages=0, extracted_pages=0, extraction_error=f"pdf_extract_error: {exc}")


def extract_title(text: str) -> str:
    if not text:
        return ""

    lines = [normalize(line) for line in text.splitlines() if normalize(line)]
    if len(lines) <= 1:
        sentences = re.split(r"(?<=[.!?])\s+", text)
        return normalize(sentences[0])[:220] if sentences else ""

    candidates: List[str] = []
    for line in lines[:25]:
        lowered = line.lower()
        if len(line) < 12 or len(line) > 220:
            continue
        if any(skip in lowered for skip in ["abstract", "keywords", "journal", "copyright", "received", "accepted", "available online"]):
            continue
        if re.match(r"^\d+$", line):
            continue
        candidates.append(line)

    if candidates:
        return candidates[0]
    return lines[0][:220]


def extract_abstract(text: str) -> str:
    if not text:
        return ""

    match = re.search(r"\babstract\b[:\s]*(.*?)(?:\bkeywords?\b|\bintroduction\b|\b1\.?\s+introduction\b)", text, re.IGNORECASE | re.DOTALL)
    if match:
        return normalize(match.group(1))[:1600]

    sentences = re.split(r"(?<=[.!?])\s+", text)
    useful = [sentence for sentence in sentences[:12] if 40 <= len(sentence) <= 500]
    return normalize(" ".join(useful[:4]))[:1600]


def classify_paper_type(text: str) -> str:
    lowered = text.lower()
    if contains_any(lowered, REVIEW_TERMS):
        return "review_or_overview"
    if contains_any(lowered, EXPERIMENT_TERMS):
        return "experimental_or_methods"
    return "unknown"


def score_screening(text: str, title: str, abstract: str) -> Dict[str, Any]:
    evidence_text = " ".join([title, abstract, text[:5000]])
    battery_matches = matched_terms(evidence_text, BATTERY_TERMS)
    electrode_matches = matched_terms(evidence_text, ELECTRODE_TERMS)
    green_matches = matched_terms(evidence_text, GREEN_TERMS)
    performance_matches = matched_terms(evidence_text, PERFORMANCE_TERMS)
    out_matches = matched_terms(evidence_text, OUT_OF_SCOPE_TERMS)
    paper_type = classify_paper_type(evidence_text)

    score = 0
    score += min(len(battery_matches), 3) * 2
    score += min(len(electrode_matches), 4) * 2
    score += min(len(green_matches), 4) * 3
    score += min(len(performance_matches), 4) * 2
    if paper_type == "experimental_or_methods":
        score += 2
    elif paper_type == "review_or_overview":
        score += 1
    score -= min(len(out_matches), 4) * 2

    has_battery = bool(battery_matches)
    has_electrode = bool(electrode_matches)
    has_green = bool(green_matches)
    has_performance = bool(performance_matches)

    reasons: List[str] = []
    if has_battery:
        reasons.append("battery/LIB relevance")
    if has_electrode:
        reasons.append("electrode/material fabrication relevance")
    if has_green:
        reasons.append("green/sustainable/process relevance")
    if has_performance:
        reasons.append("performance metrics present")
    if out_matches:
        reasons.append("contains out-of-scope signals")

    if has_battery and has_electrode and has_green and has_performance and score >= 14:
        decision = "KEEP"
    elif has_battery and has_electrode and (has_green or has_performance) and score >= 9:
        decision = "MAYBE"
    elif not text:
        decision = "NEEDS_OCR"
    else:
        decision = "DROP"

    return {
        "decision": decision,
        "relevance_score": score,
        "paper_type": paper_type,
        "reasons": reasons,
        "matches": {
            "battery": battery_matches,
            "electrode": electrode_matches,
            "green": green_matches,
            "performance": performance_matches,
            "out_of_scope": out_matches,
        },
    }


def screen_pdf(pdf_path: Path) -> Dict[str, Any]:
    extracted = extract_pdf_text(pdf_path)
    title = extract_title(extracted.text)
    abstract = extract_abstract(extracted.text)
    scoring = score_screening(extracted.text, title, abstract)

    if extracted.extraction_error == "empty_file":
        scoring["decision"] = "DROP"
        scoring["reasons"] = ["empty or failed download"]
        needs_ocr_or_cloud = False
    elif extracted.extraction_error:
        scoring["decision"] = "NEEDS_OCR"
        scoring["reasons"] = [extracted.extraction_error]
        needs_ocr_or_cloud = True
    elif len(extracted.text) < 800:
        needs_ocr_or_cloud = True
        if scoring["decision"] in {"KEEP", "MAYBE"}:
            scoring["reasons"].append("metadata/title-only screening; needs OCR/cloud for abstract, tables, and figures")
        else:
            scoring["decision"] = "NEEDS_OCR"
            scoring["reasons"].append("low text extraction yield")
    else:
        needs_ocr_or_cloud = False

    return {
        "file_name": pdf_path.name,
        "path": str(pdf_path),
        "file_size_bytes": pdf_path.stat().st_size,
        "title_from_pdf_text": title,
        "abstract_or_summary_from_pdf_text": abstract,
        "pages": extracted.pages,
        "extracted_pages": extracted.extracted_pages,
        "text_chars": len(extracted.text),
        "metadata_text": extracted.metadata_text,
        "needs_ocr_or_cloud": needs_ocr_or_cloud,
        **scoring,
    }


def empty_screening_result(pdf_path: Path, reason: str) -> Dict[str, Any]:
    return {
        "file_name": pdf_path.name,
        "path": str(pdf_path),
        "file_size_bytes": pdf_path.stat().st_size if pdf_path.exists() else 0,
        "title_from_pdf_text": "",
        "abstract_or_summary_from_pdf_text": "",
        "pages": 0,
        "extracted_pages": 0,
        "text_chars": 0,
        "needs_ocr_or_cloud": True,
        "decision": "NEEDS_OCR",
        "relevance_score": 0,
        "paper_type": "unknown",
        "reasons": [reason],
        "matches": {
            "battery": [],
            "electrode": [],
            "green": [],
            "performance": [],
            "out_of_scope": [],
        },
    }


def screen_pdf_with_timeout(pdf_path: Path, timeout_seconds: int = 20) -> Dict[str, Any]:
    TMP_SCREENING_DIR.mkdir(parents=True, exist_ok=True)
    safe_stem = re.sub(r"[^A-Za-z0-9_.-]+", "_", pdf_path.stem)[:80]
    output_path = TMP_SCREENING_DIR / f"{safe_stem}.json"
    if output_path.exists():
        try:
            output_path.unlink()
        except PermissionError:
            output_path = TMP_SCREENING_DIR / f"{safe_stem}_{datetime.now(timezone.utc).timestamp()}.json"

    command = [
        sys.executable,
        "-m",
        "services.evals.paper_screening",
        "--worker-pdf",
        str(pdf_path),
        "--worker-output",
        str(output_path),
    ]
    env = None
    if LOCAL_DEPS_DIR.exists():
        import os

        env = os.environ.copy()
        existing_pythonpath = env.get("PYTHONPATH", "")
        env["PYTHONPATH"] = str(LOCAL_DEPS_DIR) + (f";{existing_pythonpath}" if existing_pythonpath else "")
    try:
        subprocess.run(
            command,
            cwd=str(ROOT),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=timeout_seconds,
            check=False,
            env=env,
        )
    except subprocess.TimeoutExpired:
        return empty_screening_result(pdf_path, f"text_extraction_timeout_after_{timeout_seconds}s")

    if output_path.exists():
        try:
            return json.loads(output_path.read_text(encoding="utf-8"))
        finally:
            try:
                output_path.unlink(missing_ok=True)
            except PermissionError:
                pass

    return empty_screening_result(pdf_path, "text_extraction_subprocess_returned_no_result")


def cluster_tags(item: Dict[str, Any]) -> List[str]:
    matches = item.get("matches", {})
    tags: List[str] = []
    green = set(matches.get("green", []))
    electrode = set(matches.get("electrode", []))
    if {"dry electrode", "solvent-free", "drying-free"} & green:
        tags.append("dry/solvent-free electrode processing")
    if {"water-based", "aqueous", "nmp-free", "pvdf-free"} & green:
        tags.append("aqueous/NMP-free electrode processing")
    if {"biomass", "bio-derived", "chitosan", "lignin", "starch", "cellulose", "biodegradable"} & green:
        tags.append("bio-derived binders/materials")
    if {"natural graphite", "recycled graphite", "reuse of graphite", "tailings"} & green:
        tags.append("recycled/natural feedstock")
    if {"binder"} & electrode:
        tags.append("binder engineering")
    if {"cathode", "lifepo4", "nmc", "layered cathode"} & electrode:
        tags.append("cathode materials")
    if {"anode", "graphite", "silicon"} & electrode:
        tags.append("anode materials")
    if not tags:
        tags.append("general electrode materials")
    return tags


def build_selected_papers(items: List[Dict[str, Any]], limit: int = 20) -> List[Dict[str, Any]]:
    candidates = [item for item in items if item["decision"] in {"KEEP", "MAYBE"}]
    ranked = sorted(candidates, key=lambda item: (item["decision"] == "KEEP", item["relevance_score"], item["text_chars"]), reverse=True)
    selected: List[Dict[str, Any]] = []
    for item in ranked[:limit]:
        selected.append(
            {
                "file_name": item["file_name"],
                "path": item["path"],
                "title_from_pdf_text": item["title_from_pdf_text"],
                "decision": item["decision"],
                "relevance_score": item["relevance_score"],
                "paper_type": item["paper_type"],
                "cluster_tags": cluster_tags(item),
                "why_selected": item["reasons"],
                "abstract_or_summary_from_pdf_text": item["abstract_or_summary_from_pdf_text"],
            }
        )
    return selected


def summarize_counts(items: List[Dict[str, Any]]) -> Dict[str, Any]:
    decisions = Counter(item["decision"] for item in items)
    tags = Counter(tag for item in items if item["decision"] in {"KEEP", "MAYBE"} for tag in cluster_tags(item))
    return {
        "total_pdfs": len(items),
        "decisions": dict(sorted(decisions.items())),
        "top_clusters": dict(tags.most_common(12)),
        "text_readable": sum(1 for item in items if item["text_chars"] >= 800),
        "needs_ocr_or_cloud": sum(1 for item in items if item["needs_ocr_or_cloud"]),
        "empty_or_failed_downloads": sum(1 for item in items if item["file_size_bytes"] == 0),
    }


def render_report(items: List[Dict[str, Any]], selected: List[Dict[str, Any]]) -> str:
    summary = summarize_counts(items)
    lines = [
        "# Real Paper Screening Report",
        "",
        f"Generated at: `{datetime.now(timezone.utc).isoformat()}`",
        "",
        "Scope used for screening: `sustainable/green fabrication of high-performance lithium-ion battery electrode materials`.",
        "",
        "The screening reads title/abstract text extracted from inside each PDF. File names are kept only as identifiers.",
        "",
        "## Summary",
        "",
        f"- Total PDFs scanned: `{summary['total_pdfs']}`",
        f"- Text-readable PDFs: `{summary['text_readable']}`",
        f"- Needs OCR/cloud review: `{summary['needs_ocr_or_cloud']}`",
        f"- Empty or failed downloads: `{summary['empty_or_failed_downloads']}`",
        "",
        "### Decision Counts",
        "",
        "| Decision | Count |",
        "| --- | ---: |",
    ]
    for decision, count in summary["decisions"].items():
        lines.append(f"| {decision} | {count} |")

    lines.extend(["", "### Candidate Topic Clusters", "", "| Cluster | Count |", "| --- | ---: |"])
    for tag, count in summary["top_clusters"].items():
        lines.append(f"| {tag} | {count} |")

    lines.extend(
        [
            "",
            "## Recommended Narrow Scope",
            "",
            "Based on the screened corpus, the strongest demo direction should stay focused on green electrode fabrication routes that preserve electrochemical performance. Prioritize papers involving dry/solvent-free electrode processing, aqueous/NMP-free processing, biodegradable or bio-derived binders, recycled/natural feedstock, and measurable capacity/cycle/rate outcomes.",
            "",
            "Suggested demo research question:",
            "",
            "> What sustainable electrode fabrication strategies can reduce environmental burden while preserving capacity retention, rate capability, and cycle life in lithium-ion batteries?",
            "",
            "## Top Selected Papers For Demo",
            "",
            "| Rank | Decision | Score | Title extracted from PDF text | Clusters | File |",
            "| ---: | --- | ---: | --- | --- | --- |",
        ]
    )
    for index, item in enumerate(selected, start=1):
        title = item["title_from_pdf_text"] or "(title not extracted)"
        tags = ", ".join(item["cluster_tags"])
        lines.append(f"| {index} | {item['decision']} | {item['relevance_score']} | {title} | {tags} | {item['file_name']} |")

    lines.extend(
        [
            "",
            "## OCR / Google Cloud Candidates",
            "",
            "Use Google Cloud Document AI or Gemini document understanding only for these cases first: empty-looking scans, low text extraction yield, or selected papers whose chart/table evidence is important.",
            "",
            "### Priority OCR / Cloud Candidates",
            "",
            "These papers could be highly relevant, but the local text layer is title/metadata-only or too sparse. They should be first in line for OCR or Gemini document understanding.",
            "",
            "| Rank | Score | Title extracted from PDF metadata/text | Reasons | File |",
            "| ---: | ---: | --- | --- | --- |",
        ]
    )
    priority_ocr = sorted(
        [item for item in items if item["needs_ocr_or_cloud"] and item["relevance_score"] > 0],
        key=lambda row: (row["relevance_score"], len(row.get("matches", {}).get("green", [])), len(row.get("matches", {}).get("electrode", []))),
        reverse=True,
    )
    for index, item in enumerate(priority_ocr[:25], start=1):
        title = item["title_from_pdf_text"] or item.get("metadata_text", "") or "(title not extracted)"
        reasons = "; ".join(item["reasons"])
        lines.append(f"| {index} | {item['relevance_score']} | {title} | {reasons} | {item['file_name']} |")

    lines.extend(
        [
            "",
            "| File | Reason | Text chars |",
            "| --- | --- | ---: |",
        ]
    )
    for item in [candidate for candidate in items if candidate["needs_ocr_or_cloud"]][:40]:
        reason = "; ".join(item["reasons"])
        lines.append(f"| {item['file_name']} | {reason} | {item['text_chars']} |")

    lines.extend(
        [
            "",
            "## Full Screening Table",
            "",
            "| Decision | Score | Title extracted from PDF text | Reasons | File |",
            "| --- | ---: | --- | --- | --- |",
        ]
    )
    for item in sorted(items, key=lambda row: (row["decision"], -row["relevance_score"], row["file_name"])):
        title = item["title_from_pdf_text"] or "(title not extracted)"
        reasons = "; ".join(item["reasons"])
        lines.append(f"| {item['decision']} | {item['relevance_score']} | {title} | {reasons} | {item['file_name']} |")

    return "\n".join(lines) + "\n"


def screen_real_papers(timeout_seconds: int = 20) -> Dict[str, Path]:
    pdfs = sorted(REAL_PAPERS_DIR.glob("*.pdf"))
    items: List[Dict[str, Any]] = []
    for index, path in enumerate(pdfs, start=1):
        print(f"[{index}/{len(pdfs)}] screening {console_safe(path.name)}")
        items.append(screen_pdf_with_timeout(path, timeout_seconds=timeout_seconds))
    selected = build_selected_papers(items)
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scope": "sustainable/green fabrication of high-performance lithium-ion battery electrode materials",
        "summary": summarize_counts(items),
        "papers": items,
    }
    REAL_MANIFEST_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    SELECTED_PAPERS_PATH.write_text(json.dumps({"selected": selected}, indent=2, ensure_ascii=False), encoding="utf-8")
    SCREENING_REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    SCREENING_REPORT_PATH.write_text(render_report(items, selected), encoding="utf-8")
    return {
        "manifest": REAL_MANIFEST_PATH,
        "selected": SELECTED_PAPERS_PATH,
        "report": SCREENING_REPORT_PATH,
    }


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Screen real paper PDFs for CellForge AI demo relevance.")
    parser.add_argument("--timeout-seconds", type=int, default=20, help="Per-PDF text extraction timeout.")
    parser.add_argument("--worker-pdf", type=Path, default=None, help=argparse.SUPPRESS)
    parser.add_argument("--worker-output", type=Path, default=None, help=argparse.SUPPRESS)
    args = parser.parse_args()

    if args.worker_pdf and args.worker_output:
        result = screen_pdf(args.worker_pdf)
        args.worker_output.write_text(json.dumps(result, ensure_ascii=False), encoding="utf-8")
        return

    paths = screen_real_papers(timeout_seconds=args.timeout_seconds)
    print(f"Wrote manifest: {paths['manifest']}")
    print(f"Wrote selected papers: {paths['selected']}")
    print(f"Wrote screening report: {paths['report']}")


if __name__ == "__main__":
    main()
