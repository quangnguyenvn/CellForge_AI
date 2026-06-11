from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List

from services.evals.publication_validation import (
    LEAD_HYPOTHESIS_ID,
    REAL_HYPOTHESES_PATH,
    ROOT,
    VALIDATION_QUEUE_PATH,
    write_text,
)


MANUSCRIPT_DRAFT_PATH = ROOT / "reports" / "manuscript_draft.md"
MANUSCRIPT_READINESS_PATH = ROOT / "reports" / "manuscript_readiness_report.md"


def load_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def selected_validation_items(queue: Dict[str, Any], validated_only: bool = True) -> List[Dict[str, Any]]:
    items = queue.get("items", [])
    if not validated_only:
        return items
    return [
        item
        for item in items
        if item.get("allowed_in_manuscript") is True
        and item.get("validation_status") in {"validated", "corrected"}
    ]


def lead_hypothesis(hypotheses: Dict[str, Any]) -> Dict[str, Any]:
    for hypothesis in hypotheses.get("hypotheses", []):
        if hypothesis.get("id") == LEAD_HYPOTHESIS_ID:
            return hypothesis
    raise ValueError(f"Lead hypothesis {LEAD_HYPOTHESIS_ID} was not found.")


def render_blocked_report(queue: Dict[str, Any]) -> str:
    critical_pending = [
        item
        for item in queue.get("items", [])
        if item.get("priority") in {"critical", "high"} and not item.get("allowed_in_manuscript")
    ]
    lines = [
        "# CellForge AI Manuscript Readiness Report",
        "",
        "Status: `blocked_pending_human_validation`",
        "",
        "The manuscript draft was not generated because no validated evidence items are currently allowed for manuscript use. This is intentional: CellForge AI should not convert extraction artifacts into paper claims until a human verifies them against the PDFs.",
        "",
        "## Blocking Items",
        "",
    ]
    for item in critical_pending:
        lines.append(
            f"- `{item['validation_id']}` `{item['claim_id']}` ({item['priority']}): "
            f"{item['metric']} = `{item['value']}` from `{item['source_paper_id']}`"
        )
    lines.extend(
        [
            "",
            "## How To Unblock",
            "",
            "1. Open `reports/validation_checklist.md`.",
            "2. Verify each critical/high claim against the source PDF.",
            "3. Update `data/validation_queue.json`: set `validation_status` to `validated` or `corrected`, and `allowed_in_manuscript` to `true` only for claims that passed.",
            "4. Re-run `python scripts\\generate_manuscript_draft.py --validated-only`.",
        ]
    )
    return "\n".join(lines) + "\n"


def render_manuscript_draft(hypothesis: Dict[str, Any], items: List[Dict[str, Any]]) -> str:
    support = [item for item in items if "supporting" in item.get("roles", [])]
    contradiction = [item for item in items if "contradicting" in item.get("roles", [])]
    lines = [
        "# Draft Manuscript: Circular Natural-Graphite Anodes with Bio-Based Conductive Surface Repair",
        "",
        "> Draft generated only from human-validated CellForge evidence items. This remains a researcher-editable manuscript draft, not an automatically publishable paper.",
        "",
        "## Abstract",
        "",
        f"We propose and evaluate a research direction based on `{hypothesis['id']}`: {hypothesis['hypothesis']} The draft uses only validation-approved evidence items from the CellForge evidence queue.",
        "",
        "## Introduction",
        "",
        "Sustainable lithium-ion battery manufacturing requires electrode materials and processes that reduce hazardous chemistry while preserving electrochemical performance. The validated evidence in this draft focuses on a circular graphite-anode route.",
        "",
        "## Evidence Synthesis",
        "",
    ]
    for item in support:
        lines.append(
            f"- `{item['claim_id']}`: {item['claim_text']} "
            f"Metric: {item['metric']} = `{item['value']}` under {item['experimental_condition']}."
        )
    lines.extend(["", "## Contradictions and Risk Controls", ""])
    for item in contradiction:
        lines.append(f"- `{item['claim_id']}` risk: {item['limitation']}")
    lines.extend(
        [
            "",
            "## Proposed Experiment Plan",
            "",
            hypothesis["proposed_experiment"],
            "",
            "## Limitations",
            "",
            "- This is a draft built from validated evidence items, but the proposed mechanism still requires experimental confirmation.",
            "- Conceptual figures should be labeled as schematics unless they are replaced by real microscopy, spectroscopy, or simulation outputs.",
            "",
            "## References To Complete",
            "",
        ]
    )
    for source_id in sorted({item["source_paper_id"] for item in items}):
        title = next(item["source_paper_title"] for item in items if item["source_paper_id"] == source_id)
        lines.append(f"- `{source_id}` {title}")
    return "\n".join(lines) + "\n"


def generate_manuscript_draft(validated_only: bool = True) -> Dict[str, Any]:
    queue = load_json(VALIDATION_QUEUE_PATH)
    hypotheses = load_json(REAL_HYPOTHESES_PATH)
    items = selected_validation_items(queue, validated_only=validated_only)
    if not items:
        write_text(MANUSCRIPT_READINESS_PATH, render_blocked_report(queue))
        return {
            "status": "blocked_pending_human_validation",
            "readiness_report": str(MANUSCRIPT_READINESS_PATH.relative_to(ROOT)),
            "validated_items": 0,
            "draft_written": False,
        }

    hypothesis = lead_hypothesis(hypotheses)
    write_text(MANUSCRIPT_DRAFT_PATH, render_manuscript_draft(hypothesis, items))
    return {
        "status": "draft_generated",
        "draft_path": str(MANUSCRIPT_DRAFT_PATH.relative_to(ROOT)),
        "validated_items": len(items),
        "draft_written": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a manuscript draft only from human-validated evidence.")
    parser.add_argument("--validated-only", action="store_true", default=False)
    args = parser.parse_args()
    print(json.dumps(generate_manuscript_draft(validated_only=args.validated_only), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
