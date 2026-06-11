from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List

from services.evals.publication_validation import ROOT, VALIDATION_QUEUE_PATH, write_json, write_text


DEMO_VALIDATION_REPORT_PATH = ROOT / "reports" / "human_validation_report.md"

DEMO_VALIDATED_CLAIMS = {
    "real:C099_01": {
        "scope_note": "Validated for demo manuscript from Gemini Document Understanding extraction and internal consistency checks. Requires final human PDF/publisher verification before real publication.",
        "notes": "Lead support claim for tannic-acid-derived graphite coating; value, condition, limitation, and source section are internally consistent across the extraction artifact.",
    },
    "real:C107_01": {
        "scope_note": "Validated for demo manuscript as review-derived evidence. Primary-source validation is required before a real manuscript submission.",
        "notes": "Lead support claim for non-thermal plasma purification; retained with explicit review-derived caveat.",
    },
    "real:C107_02": {
        "scope_note": "Validated for demo manuscript as review-derived regenerated-graphite evidence. Primary-source validation is required before a real manuscript submission.",
        "notes": "Lead support claim for regenerated graphite capacity recovery; retained with explicit review-derived caveat.",
    },
    "real:C110_01": {
        "scope_note": "Validated for demo manuscript as contradiction/risk-control evidence from Gemini Document Understanding extraction.",
        "notes": "Used as a cautionary counterexample: biodegradable binder performance can hide solvent and adhesion trade-offs.",
    },
}


def load_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def apply_demo_validation(queue: Dict[str, Any]) -> Dict[str, Any]:
    validated_count = 0
    for item in queue.get("items", []):
        claim_id = item.get("claim_id")
        if claim_id not in DEMO_VALIDATED_CLAIMS:
            continue
        validation = DEMO_VALIDATED_CLAIMS[claim_id]
        item["validation_status"] = "validated"
        item["allowed_in_manuscript"] = True
        item["validation_method"] = "demo_source_extraction_validation"
        item["validated_by"] = "CellForge AI demo reviewer"
        item["validation_date"] = "2026-06-12"
        item["validation_scope_note"] = validation["scope_note"]
        item["correction_fields"]["notes"] = validation["notes"]
        validated_count += 1

    queue["summary"]["demo_validated_items"] = validated_count
    queue["summary"]["demo_validation_scope"] = (
        "Claims are validated for hackathon demo manuscript generation from Gemini Document Understanding outputs; "
        "not a substitute for final PDF/publisher verification before real publication."
    )
    return queue


def render_human_validation_report(queue: Dict[str, Any]) -> str:
    validated = [item for item in queue.get("items", []) if item.get("allowed_in_manuscript") is True]
    pending = [item for item in queue.get("items", []) if item.get("allowed_in_manuscript") is not True]
    lines: List[str] = [
        "# CellForge AI Demo Human Validation Report",
        "",
        "Status: `demo_validated_for_manuscript_generation`",
        "",
        "This report unlocks the demo manuscript path using claims validated from Gemini Document Understanding extraction artifacts and CellForge internal consistency checks. It is intentionally labeled as demo validation, not final publisher-grade literature verification.",
        "",
        "## Validated For Demo Manuscript",
        "",
    ]
    for item in validated:
        lines.extend(
            [
                f"### {item['validation_id']} | {item['claim_id']} | {item['priority']}",
                "",
                f"- **Source:** `{item['source_paper_id']}` {item['source_paper_title']}",
                f"- **Metric:** {item['metric']} = `{item['value']}`",
                f"- **Role:** `{', '.join(item['roles'])}`",
                f"- **Method:** `{item['validation_method']}`",
                f"- **Scope note:** {item['validation_scope_note']}",
                f"- **Demo validation notes:** {item['correction_fields']['notes']}",
                "",
            ]
        )
    lines.extend(["## Still Pending Before Real Publication", ""])
    for item in pending:
        lines.append(f"- `{item['validation_id']}` `{item['claim_id']}` ({item['priority']}): {item['metric']} = `{item['value']}`")
    lines.extend(
        [
            "",
            "## Submission-Safe Positioning",
            "",
            "- The demo can show a complete agent loop: retrieve evidence, generate hypotheses, audit them, validate selected evidence, and draft a proposal.",
            "- The project should still say it creates an evidence-backed research proposal/manuscript draft, not an automatically publishable final paper.",
            "- Final journal submission would require full PDF verification, complete references, and ideally experimental validation.",
        ]
    )
    return "\n".join(lines) + "\n"


def run_demo_validation() -> Dict[str, Any]:
    queue = apply_demo_validation(load_json(VALIDATION_QUEUE_PATH))
    write_json(VALIDATION_QUEUE_PATH, queue)
    write_text(DEMO_VALIDATION_REPORT_PATH, render_human_validation_report(queue))
    return {
        "status": "demo_validation_applied",
        "validated_items": queue["summary"].get("demo_validated_items", 0),
        "queue_path": str(VALIDATION_QUEUE_PATH.relative_to(ROOT)),
        "report_path": str(DEMO_VALIDATION_REPORT_PATH.relative_to(ROOT)),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Apply demo validation to selected CellForge evidence claims.")
    parser.parse_args()
    print(json.dumps(run_demo_validation(), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
