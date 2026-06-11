from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List


ROOT = Path(__file__).resolve().parents[2]
REAL_CORPUS_PATH = ROOT / "data" / "real_evidence_corpus.json"
REAL_HYPOTHESES_PATH = ROOT / "data" / "real_hypotheses.json"
REAL_AUDITS_PATH = ROOT / "data" / "real_hypothesis_audits.json"
VALIDATION_QUEUE_PATH = ROOT / "data" / "validation_queue.json"
VALIDATION_CHECKLIST_PATH = ROOT / "reports" / "validation_checklist.md"
FINAL_PAPER_ROADMAP_PATH = ROOT / "reports" / "final_paper_roadmap.md"


LEAD_HYPOTHESIS_ID = "real:H003"


@dataclass(frozen=True)
class LinkedClaim:
    claim_id: str
    hypothesis_id: str
    role: str


def load_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)
        handle.write("\n")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def clean(value: Any) -> str:
    text = str(value or "")
    replacements = {
        "g⁻¹": "g^-1",
        "cm⁻²": "cm^-2",
        "Li⁺": "Li+",
        "⁻¹": "^-1",
        "⁻²": "^-2",
        "⁻": "-",
        "⁺": "+",
        "π": "pi",
        "°C": "C",
        "gâ»Â¹": "g^-1",
        "cmâ»Â²": "cm^-2",
        "Liâº": "Li+",
        "â»Â¹": "^-1",
        "â»Â²": "^-2",
        "Ã¢ÂÂ»": "-",
        "Ã¢ÂÂº": "+",
        "â»": "-",
        "âº": "+",
        "Ã‚Â²": "^2",
        "Ã‚Â¹": "^-1",
        "Â²": "^2",
        "Â¹": "^-1",
        "Ã‚Â°C": "C",
        "Ãâ‚¬": "pi",
        "Ï€": "pi",
        "ÃŽÂ¼": "u",
        "Âµ": "u",
        "Â°C": "C",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return " ".join(text.split())


def by_id(items: Iterable[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    return {item["id"]: item for item in items}


def audit_by_hypothesis(audits: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    return {audit["hypothesis_id"]: audit for audit in audits.get("audits", [])}


def linked_claims_for_hypotheses(hypotheses: Dict[str, Any]) -> List[LinkedClaim]:
    linked: List[LinkedClaim] = []
    for hypothesis in hypotheses.get("hypotheses", []):
        hypothesis_id = hypothesis["id"]
        for claim_id in hypothesis.get("supporting_claim_ids", []):
            linked.append(LinkedClaim(claim_id=claim_id, hypothesis_id=hypothesis_id, role="supporting"))
        for claim_id in hypothesis.get("contradicting_claim_ids", []):
            linked.append(LinkedClaim(claim_id=claim_id, hypothesis_id=hypothesis_id, role="contradicting"))
    return linked


def priority_for(link: LinkedClaim, claim: Dict[str, Any], paper: Dict[str, Any]) -> str:
    if link.hypothesis_id == LEAD_HYPOTHESIS_ID:
        return "critical" if link.role == "supporting" else "high"
    if link.role == "contradicting":
        return "high"
    if claim.get("needs_human_review") or paper.get("needs_human_review"):
        return "medium"
    return "low"


def validation_questions(link: LinkedClaim, claim: Dict[str, Any], paper: Dict[str, Any]) -> List[str]:
    questions = [
        "Does the source PDF support the exact claim text without overstatement?",
        "Do the metric, value, condition, and page/section match the source PDF?",
        "Is the citation text a faithful excerpt or close paraphrase of the paper?",
    ]
    if "review" in str(claim.get("evidence_type", "")).lower():
        questions.append("If this is review-derived evidence, can the primary source be identified before manuscript use?")
    if claim.get("source_section_or_page"):
        questions.append(f"Check the cited location: {clean(claim.get('source_section_or_page'))}.")
    if link.role == "contradicting":
        questions.append("Should this limitation change the hypothesis wording, experiment plan, or risk controls?")
    if any(item.get("needs_manual_digitization") for item in paper.get("figure_or_table_evidence", [])):
        questions.append("Does any chart-derived value need manual digitization before it is quoted numerically?")
    return questions


def claim_role_summary(hypotheses: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    summary: Dict[str, Dict[str, Any]] = {}
    for link in linked_claims_for_hypotheses(hypotheses):
        record = summary.setdefault(link.claim_id, {"hypothesis_ids": [], "roles": []})
        record["hypothesis_ids"].append(link.hypothesis_id)
        record["roles"].append(link.role)
    for record in summary.values():
        record["hypothesis_ids"] = sorted(set(record["hypothesis_ids"]))
        record["roles"] = sorted(set(record["roles"]))
    return summary


def build_validation_queue(
    corpus: Dict[str, Any] | None = None,
    hypotheses: Dict[str, Any] | None = None,
    audits: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    corpus = corpus or load_json(REAL_CORPUS_PATH)
    hypotheses = hypotheses or load_json(REAL_HYPOTHESES_PATH)
    audits = audits or load_json(REAL_AUDITS_PATH)
    claims = by_id(corpus.get("claims", []))
    papers = by_id(corpus.get("papers", []))
    audits_lookup = audit_by_hypothesis(audits)
    role_summary = claim_role_summary(hypotheses)

    deduped: Dict[str, Dict[str, Any]] = {}
    for link in linked_claims_for_hypotheses(hypotheses):
        if link.claim_id not in claims:
            continue
        claim = claims[link.claim_id]
        paper = papers.get(claim.get("source_paper_id"), {})
        summary = role_summary[link.claim_id]
        queue_item = {
            "validation_id": "",
            "priority": priority_for(link, claim, paper),
            "claim_id": claim["id"],
            "source_paper_id": claim.get("source_paper_id"),
            "source_paper_title": clean(paper.get("title")),
            "source_extraction_file": claim.get("source_extraction_file") or paper.get("source_extraction_file"),
            "hypothesis_ids": summary["hypothesis_ids"],
            "roles": summary["roles"],
            "lead_hypothesis_relevance": LEAD_HYPOTHESIS_ID in summary["hypothesis_ids"],
            "claim_text": clean(claim.get("claim_text")),
            "metric": clean(claim.get("metric")),
            "value": clean(claim.get("value")),
            "experimental_condition": clean(claim.get("experimental_condition")),
            "evidence_type": clean(claim.get("evidence_type")),
            "limitation": clean(claim.get("limitation")),
            "citation_text": clean(claim.get("citation_text")),
            "source_section_or_page": clean(claim.get("source_section_or_page")),
            "human_review_reason": clean(claim.get("human_review_reason") or paper.get("human_review_reason")),
            "audit_context": {
                hypothesis_id: {
                    "recommendation": audits_lookup.get(hypothesis_id, {}).get("recommendation"),
                    "claim_grounding": audits_lookup.get(hypothesis_id, {}).get("claim_grounding"),
                    "hallucination_risk": audits_lookup.get(hypothesis_id, {}).get("hallucination_risk"),
                }
                for hypothesis_id in summary["hypothesis_ids"]
            },
            "validation_status": "pending",
            "validation_questions": validation_questions(link, claim, paper),
            "correction_fields": {
                "corrected_claim_text": "",
                "corrected_metric": "",
                "corrected_value": "",
                "corrected_condition": "",
                "corrected_citation_text": "",
                "notes": "",
            },
            "allowed_in_manuscript": False,
        }
        deduped[link.claim_id] = queue_item

    priority_rank = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    items = sorted(
        deduped.values(),
        key=lambda item: (
            priority_rank.get(item["priority"], 9),
            not item["lead_hypothesis_relevance"],
            item["claim_id"],
        ),
    )
    for index, item in enumerate(items, start=1):
        item["validation_id"] = f"val:{index:03d}"

    summary = {
        "items": len(items),
        "critical": sum(1 for item in items if item["priority"] == "critical"),
        "high": sum(1 for item in items if item["priority"] == "high"),
        "medium": sum(1 for item in items if item["priority"] == "medium"),
        "low": sum(1 for item in items if item["priority"] == "low"),
        "lead_hypothesis_id": LEAD_HYPOTHESIS_ID,
        "manuscript_gate": "only validated items with allowed_in_manuscript=true should be used in manuscript drafting",
    }
    return {
        "description": "Human validation queue for moving CellForge AI evidence from proposal package toward manuscript-ready evidence.",
        "source_files": [
            str(REAL_CORPUS_PATH.relative_to(ROOT)),
            str(REAL_HYPOTHESES_PATH.relative_to(ROOT)),
            str(REAL_AUDITS_PATH.relative_to(ROOT)),
        ],
        "summary": summary,
        "items": items,
    }


def markdown_status_box(item: Dict[str, Any]) -> str:
    checks = [
        "[ ] PDF text supports claim",
        "[ ] Metric/value/condition verified",
        "[ ] Page or section verified",
        "[ ] Citation text corrected if needed",
        "[ ] Contradiction/risk reflected in hypothesis wording",
        "[ ] Allowed in manuscript",
    ]
    return "\n".join(f"- {check}" for check in checks)


def render_validation_checklist(queue: Dict[str, Any]) -> str:
    lines = [
        "# CellForge AI Human Validation Checklist",
        "",
        "This checklist is the gate between an evidence-backed research proposal package and a manuscript draft. Do not treat extracted claims as publication-ready until a human validates them against the source PDFs.",
        "",
        "## Summary",
        "",
    ]
    for key, value in queue["summary"].items():
        lines.append(f"- **{key}:** `{value}`")
    lines.extend(
        [
            "",
            "## Priority Queue",
            "",
        ]
    )
    for item in queue["items"]:
        lines.extend(
            [
                f"### {item['validation_id']} | {item['priority'].upper()} | {item['claim_id']}",
                "",
                f"- **Source paper:** `{item['source_paper_id']}` {item['source_paper_title']}",
                f"- **Extraction file:** `{item['source_extraction_file']}`",
                f"- **Hypotheses:** `{', '.join(item['hypothesis_ids'])}`",
                f"- **Roles:** `{', '.join(item['roles'])}`",
                f"- **Location:** {item['source_section_or_page'] or 'not provided'}",
                f"- **Metric:** {item['metric']} = `{item['value']}`",
                f"- **Condition:** {item['experimental_condition']}",
                f"- **Claim:** {item['claim_text']}",
                f"- **Citation text:** {item['citation_text']}",
                f"- **Limitation/risk:** {item['limitation']}",
                f"- **Review reason:** {item['human_review_reason']}",
                "",
                "**Validation questions:**",
            ]
        )
        lines.extend(f"- {question}" for question in item["validation_questions"])
        lines.extend(["", "**Checklist:**", markdown_status_box(item), ""])
    return "\n".join(lines).rstrip() + "\n"


def render_final_paper_roadmap(queue: Dict[str, Any]) -> str:
    lead_items = [item for item in queue["items"] if item["lead_hypothesis_relevance"]]
    lines = [
        "# CellForge AI Final Paper Roadmap",
        "",
        "Goal: turn the current Gemini research proposal package into a human-validated manuscript draft without claiming unsupported results.",
        "",
        "## Readiness Gates",
        "",
        "1. **Evidence validation:** complete `reports/validation_checklist.md` for all critical/high claims.",
        "2. **Reference validation:** add authors, venue, year, and DOI only after checking source PDFs or publisher pages.",
        "3. **Manuscript drafting:** generate a draft using only queue items marked `allowed_in_manuscript=true`.",
        "4. **Figure validation:** keep generated schematic figures as conceptual diagrams; use paper figures only with rights/permissions and verified captions.",
        "5. **Experimental boundary:** label all untested mechanisms as proposed hypotheses, not results.",
        "",
        "## Lead Manuscript Story",
        "",
        "- Lead hypothesis: `real:H003` circular natural-graphite anodes with bio-based conductive surface repair.",
        "- Evidence spine: non-thermal plasma purification, regenerated graphite capacity recovery, tannic-acid carbon coating stability, and PHBV/chloroform as a processing-risk counterexample.",
        f"- Critical/high validation items tied to lead: `{len(lead_items)}`.",
        "",
        "## Manuscript Structure",
        "",
        "1. Title",
        "2. Abstract",
        "3. Introduction: green electrode-material bottleneck",
        "4. Methods: CellForge evidence extraction, retrieval benchmark, hypothesis audit, and human validation gate",
        "5. Evidence synthesis: circular graphite anode route",
        "6. Research gap and hypothesis",
        "7. Proposed experiment matrix",
        "8. Sustainability and risk controls",
        "9. Limitations",
        "10. Conclusion",
        "11. References",
        "",
        "## Next Command After Manual Validation",
        "",
        "```powershell",
        "python scripts\\generate_manuscript_draft.py --validated-only",
        "```",
        "",
        "The command is implemented with a hard gate: it writes a readiness report instead of a draft until at least one evidence item is marked `validation_status=validated` or `corrected` and `allowed_in_manuscript=true`.",
    ]
    return "\n".join(lines) + "\n"


def run_publication_validation() -> Dict[str, Any]:
    queue = build_validation_queue()
    write_json(VALIDATION_QUEUE_PATH, queue)
    write_text(VALIDATION_CHECKLIST_PATH, render_validation_checklist(queue))
    write_text(FINAL_PAPER_ROADMAP_PATH, render_final_paper_roadmap(queue))
    return queue


def main() -> None:
    parser = argparse.ArgumentParser(description="Build CellForge AI human validation queue for manuscript readiness.")
    parser.parse_args()
    queue = run_publication_validation()
    print(json.dumps(queue["summary"], indent=2, ensure_ascii=False))
    print(f"Wrote {VALIDATION_QUEUE_PATH.relative_to(ROOT)}")
    print(f"Wrote {VALIDATION_CHECKLIST_PATH.relative_to(ROOT)}")
    print(f"Wrote {FINAL_PAPER_ROADMAP_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
