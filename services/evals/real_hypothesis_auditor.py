from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

from services.evals.local_eval import overlap_score


ROOT = Path(__file__).resolve().parents[2]
REAL_CORPUS_PATH = ROOT / "data" / "real_evidence_corpus.json"
REAL_HYPOTHESES_PATH = ROOT / "data" / "real_hypotheses.json"
REAL_HYPOTHESIS_AUDITS_PATH = ROOT / "data" / "real_hypothesis_audits.json"
REAL_AUDIT_REPORT_PATH = ROOT / "reports" / "real_audit_report.md"


def load_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def claim_text_for_grounding(claim: Dict[str, Any]) -> str:
    return " ".join(
        [
            claim.get("claim_text", ""),
            claim.get("battery_chemistry", ""),
            claim.get("approach_type", ""),
            claim.get("metric", ""),
            claim.get("value", ""),
            claim.get("experimental_condition", ""),
            claim.get("evidence_type", ""),
            claim.get("limitation", ""),
        ]
    )


def hypothesis_text(hypothesis: Dict[str, Any]) -> str:
    return " ".join(
        [
            hypothesis.get("title", ""),
            hypothesis.get("hypothesis", ""),
            hypothesis.get("mechanism", ""),
            hypothesis.get("novelty_rationale", ""),
            hypothesis.get("proposed_experiment", ""),
            " ".join(hypothesis.get("metric_terms", [])),
        ]
    )


def linked_claims(hypothesis: Dict[str, Any], claim_by_id: Dict[str, Dict[str, Any]], key: str) -> List[Dict[str, Any]]:
    return [claim_by_id[claim_id] for claim_id in hypothesis.get(key, []) if claim_id in claim_by_id]


def citation_coverage_score(support: List[Dict[str, Any]]) -> float:
    return round(min(len(support) / 3, 1.0), 3)


def claim_grounding_score(hypothesis: Dict[str, Any], support: List[Dict[str, Any]]) -> float:
    if not support:
        return 0.0
    lexical = overlap_score(hypothesis_text(hypothesis), " ".join(claim_text_for_grounding(claim) for claim in support))
    metric_terms = [term.lower() for term in hypothesis.get("metric_terms", [])]
    support_text = " ".join(claim_text_for_grounding(claim).lower() for claim in support)
    metric_hits = sum(1 for term in metric_terms if term and any(part in support_text for part in term.split()))
    metric_grounding = metric_hits / max(len(metric_terms), 1)
    chemistry = hypothesis.get("battery_chemistry", "").lower()
    chemistry_match = sum(1 for claim in support if chemistry and chemistry in claim.get("battery_chemistry", "").lower()) / len(support)
    return round(min((0.50 * lexical) + (0.30 * metric_grounding) + (0.20 * chemistry_match), 1.0), 3)


def contradiction_coverage_score(contradictions: List[Dict[str, Any]]) -> float:
    return round(min(len(contradictions) / 2, 1.0), 3)


def evidence_strength_score(support: List[Dict[str, Any]], corpus_claims: List[Dict[str, Any]]) -> float:
    if not support:
        return 0.0
    experimental = sum(1 for claim in support if "experimental" in claim.get("evidence_type", "").lower())
    review = sum(1 for claim in support if "review" in claim.get("evidence_type", "").lower())
    source_diversity = len({claim.get("source_paper_id") for claim in support}) / max(len(support), 1)
    corpus_fraction = len(support) / max(len(corpus_claims), 1)
    score = 0.35 + (0.08 * len(support)) + (0.08 * experimental) + (0.18 * source_diversity) + (0.10 * corpus_fraction) - (0.08 * review)
    return round(max(0.0, min(score, 0.95)), 3)


def feasibility_score(hypothesis: Dict[str, Any], support: List[Dict[str, Any]], contradictions: List[Dict[str, Any]]) -> float:
    base = float(hypothesis.get("scores", {}).get("feasibility", 0.65))
    text = " ".join([hypothesis_text(hypothesis)] + [claim_text_for_grounding(claim) for claim in support + contradictions]).lower()
    penalty_terms = [
        "vacuum",
        "contamination",
        "yield",
        "chloroform",
        "formaldehyde",
        "tortuosity",
        "scale",
        "equipment cost",
        "high thermal",
    ]
    penalty = sum(0.035 for term in penalty_terms if term in text)
    return round(max(0.2, min(base - penalty, 0.95)), 3)


def novelty_gap_score(hypothesis: Dict[str, Any], support: List[Dict[str, Any]]) -> float:
    base = float(hypothesis.get("scores", {}).get("novelty_gap", 0.65))
    approach_diversity = len({claim.get("approach_type") for claim in support})
    if approach_diversity >= 3:
        base += 0.04
    elif approach_diversity <= 1:
        base -= 0.05
    return round(max(0.0, min(base, 0.95)), 3)


def human_review_pressure(claims: Iterable[Dict[str, Any]]) -> float:
    claims_list = list(claims)
    if not claims_list:
        return 1.0
    return round(sum(1 for claim in claims_list if claim.get("needs_human_review", True)) / len(claims_list), 3)


def collect_unsupported_claims(
    hypothesis: Dict[str, Any],
    support: List[Dict[str, Any]],
    contradictions: List[Dict[str, Any]],
    grounding: float,
    contradiction_coverage: float,
) -> List[str]:
    notes: List[str] = []
    if len(support) < 2:
        notes.append("Fewer than two supporting claims are cited.")
    if grounding < 0.45:
        notes.append("Hypothesis wording is only weakly grounded in cited claim text.")
    if contradiction_coverage < 0.5:
        notes.append("Contradiction or limitation coverage is thin.")
    if any(claim.get("needs_human_review", True) for claim in support + contradictions):
        notes.append("All cited real-paper claims are extraction artifacts requiring human validation.")
    hypothesis_lower = hypothesis.get("hypothesis", "").lower()
    risky_phrases = ["will improve", "will retain", "can recover", "can serve", "can improve"]
    if any(phrase in hypothesis_lower for phrase in risky_phrases):
        notes.append("Hypothesis uses directional performance language that must remain proposal-level until experimentally validated.")
    return notes


def contradiction_notes(contradictions: List[Dict[str, Any]]) -> List[str]:
    return [
        f"{claim['id']} ({claim['source_paper_id']}): {claim.get('limitation', 'No limitation text available.')}"
        for claim in contradictions
    ]


def hallucination_risk(
    citation_coverage: float,
    claim_grounding: float,
    contradiction_coverage: float,
    evidence_strength: float,
    feasibility: float,
    review_pressure: float,
) -> float:
    risk = 1.0 - (
        (0.22 * citation_coverage)
        + (0.22 * claim_grounding)
        + (0.16 * contradiction_coverage)
        + (0.16 * evidence_strength)
        + (0.14 * feasibility)
    )
    risk += 0.10 * review_pressure
    return round(max(0.0, min(risk, 1.0)), 3)


def recommendation(audit: Dict[str, Any]) -> str:
    if audit["hallucination_risk"] <= 0.45 and audit["citation_coverage"] >= 0.67 and audit["claim_grounding"] >= 0.45:
        if audit["feasibility"] >= 0.55:
            return "advance_with_human_review"
        return "revise_experiment_design"
    return "revise_before_brief"


def audit_real_hypothesis(
    hypothesis: Dict[str, Any],
    claim_by_id: Dict[str, Dict[str, Any]],
    corpus_claims: List[Dict[str, Any]],
) -> Dict[str, Any]:
    support = linked_claims(hypothesis, claim_by_id, "supporting_claim_ids")
    contradictions = linked_claims(hypothesis, claim_by_id, "contradicting_claim_ids")
    citation_coverage = citation_coverage_score(support)
    grounding = claim_grounding_score(hypothesis, support)
    contradiction_coverage = contradiction_coverage_score(contradictions)
    evidence_strength = evidence_strength_score(support, corpus_claims)
    novelty_gap = novelty_gap_score(hypothesis, support)
    feasibility = feasibility_score(hypothesis, support, contradictions)
    review_pressure = human_review_pressure(support + contradictions)
    risk = hallucination_risk(
        citation_coverage,
        grounding,
        contradiction_coverage,
        evidence_strength,
        feasibility,
        review_pressure,
    )
    audit = {
        "hypothesis_id": hypothesis["id"],
        "citation_coverage": citation_coverage,
        "claim_grounding": grounding,
        "contradiction_coverage": contradiction_coverage,
        "evidence_strength": evidence_strength,
        "novelty_gap": novelty_gap,
        "feasibility": feasibility,
        "human_review_pressure": review_pressure,
        "hallucination_risk": risk,
        "unsupported_claims": collect_unsupported_claims(hypothesis, support, contradictions, grounding, contradiction_coverage),
        "contradiction_notes": contradiction_notes(contradictions),
        "supporting_claim_ids": [claim["id"] for claim in support],
        "contradicting_claim_ids": [claim["id"] for claim in contradictions],
    }
    audit["recommendation"] = recommendation(audit)
    return audit


def run_real_hypothesis_audit() -> Dict[str, Any]:
    corpus = load_json(REAL_CORPUS_PATH)
    hypotheses_payload = load_json(REAL_HYPOTHESES_PATH)
    claim_by_id = {claim["id"]: claim for claim in corpus["claims"]}
    audits = [
        audit_real_hypothesis(hypothesis, claim_by_id, corpus["claims"])
        for hypothesis in hypotheses_payload["hypotheses"]
    ]
    summary = {
        "adapter": "local_real_evidence_auditor",
        "hypotheses": len(audits),
        "advance_with_human_review": sum(1 for audit in audits if audit["recommendation"] == "advance_with_human_review"),
        "revise_experiment_design": sum(1 for audit in audits if audit["recommendation"] == "revise_experiment_design"),
        "revise_before_brief": sum(1 for audit in audits if audit["recommendation"] == "revise_before_brief"),
        "avg_hallucination_risk": round(sum(audit["hallucination_risk"] for audit in audits) / max(len(audits), 1), 3),
        "avg_claim_grounding": round(sum(audit["claim_grounding"] for audit in audits) / max(len(audits), 1), 3),
        "source_hypotheses": str(REAL_HYPOTHESES_PATH.relative_to(ROOT)),
        "source_corpus": str(REAL_CORPUS_PATH.relative_to(ROOT)),
    }
    return {
        "description": "Evidence audit for deterministic real-paper CellForge hypotheses.",
        "summary": summary,
        "audits": audits,
    }


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)
        handle.write("\n")


def write_report(payload: Dict[str, Any], path: Path = REAL_AUDIT_REPORT_PATH) -> None:
    summary = payload["summary"]
    lines = [
        "# Real Hypothesis Evidence Audit",
        "",
        "This report audits deterministic hypotheses against Gemini-extracted real-paper claims. It does not certify publication readiness.",
        "",
        "## Summary",
        "",
        f"- Hypotheses audited: `{summary['hypotheses']}`",
        f"- Advance with human review: `{summary['advance_with_human_review']}`",
        f"- Revise experiment design: `{summary['revise_experiment_design']}`",
        f"- Revise before brief: `{summary['revise_before_brief']}`",
        f"- Average hallucination risk: `{summary['avg_hallucination_risk']}`",
        f"- Average claim grounding: `{summary['avg_claim_grounding']}`",
        "",
        "## Audit Matrix",
        "",
        "| Hypothesis | Citation | Grounding | Contradiction | Evidence | Novelty | Feasibility | Risk | Recommendation |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for audit in payload["audits"]:
        lines.append(
            "| {hypothesis_id} | {citation:.3f} | {grounding:.3f} | {contradiction:.3f} | {evidence:.3f} | {novelty:.3f} | {feasibility:.3f} | {risk:.3f} | {recommendation} |".format(
                hypothesis_id=audit["hypothesis_id"],
                citation=audit["citation_coverage"],
                grounding=audit["claim_grounding"],
                contradiction=audit["contradiction_coverage"],
                evidence=audit["evidence_strength"],
                novelty=audit["novelty_gap"],
                feasibility=audit["feasibility"],
                risk=audit["hallucination_risk"],
                recommendation=audit["recommendation"],
            )
        )

    lines.extend(["", "## Notes", ""])
    for audit in payload["audits"]:
        lines.extend([f"### {audit['hypothesis_id']}", ""])
        if audit["unsupported_claims"]:
            lines.append("Unsupported or caution flags:")
            for note in audit["unsupported_claims"]:
                lines.append(f"- {note}")
        if audit["contradiction_notes"]:
            lines.append("")
            lines.append("Contradiction/limitation notes:")
            for note in audit["contradiction_notes"]:
                lines.append(f"- {note}")
        lines.append("")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8", newline="\n")


def run_and_write_real_hypothesis_audit() -> Dict[str, Any]:
    payload = run_real_hypothesis_audit()
    write_json(REAL_HYPOTHESIS_AUDITS_PATH, payload)
    write_report(payload)
    return {
        "hypotheses": payload["summary"]["hypotheses"],
        "advance_with_human_review": payload["summary"]["advance_with_human_review"],
        "avg_hallucination_risk": payload["summary"]["avg_hallucination_risk"],
        "real_hypothesis_audits_path": str(REAL_HYPOTHESIS_AUDITS_PATH),
        "report_path": str(REAL_AUDIT_REPORT_PATH),
    }


def print_report(payload: Dict[str, Any]) -> None:
    print(json.dumps(payload["summary"], indent=2))
    for audit in payload["audits"]:
        print(f"{audit['recommendation'].upper()} {audit['hypothesis_id']} risk={audit['hallucination_risk']}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit deterministic real-paper hypotheses.")
    parser.add_argument("--write", action="store_true", help="Write data/real_hypothesis_audits.json and report markdown.")
    args = parser.parse_args()

    if args.write:
        print(json.dumps(run_and_write_real_hypothesis_audit(), indent=2))
        return
    print_report(run_real_hypothesis_audit())


if __name__ == "__main__":
    main()
