from __future__ import annotations

import argparse
import json
import math
import os
import re
import sys
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

from services.evals.phoenix_adapter import add_local_dependency_path, create_phoenix_adapter, load_env_file


ROOT = Path(__file__).resolve().parents[2]
REPORTS_DIR = ROOT / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"
REAL_CORPUS_PATH = ROOT / "data" / "real_evidence_corpus.json"
REAL_HYPOTHESES_PATH = ROOT / "data" / "real_hypotheses.json"
REAL_AUDITS_PATH = ROOT / "data" / "real_hypothesis_audits.json"
RETRIEVAL_REPORT_PATH = ROOT / "reports" / "real_retrieval_benchmark_report.json"
BRIEF_MD_PATH = ROOT / "reports" / "gemini_research_brief.md"
BRIEF_JSON_PATH = ROOT / "reports" / "gemini_research_brief.json"


SCORE_FIELDS = [
    "citation_coverage",
    "claim_grounding",
    "contradiction_coverage",
    "evidence_strength",
    "novelty_gap",
    "feasibility",
    "hallucination_risk",
]


def load_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)
        handle.write("\n")


TEXT_REPLACEMENTS = {
        "â»": "-",
        "âº": "+",
        "Â²": "^2",
        "Â¹": "^-1",
        "Â°C": "C",
        "Â®": "",
        "Â±": "+/-",
        "Ï€": "pi",
        "Î¼": "u",
        "µ": "u",
        "â€”": "-",
        "â€“": "-",
        "â€": '"',
        "â€œ": '"',
        "â€": '"',
        "â€™": "'",
        "â€˜": "'",
        "â€¦": "...",
}


TEXT_REPLACEMENTS.update(
    {
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
        "â»": "-",
        "âº": "+",
        "Â²": "^2",
        "Â¹": "^-1",
        "Â°C": "C",
        "Ï€": "pi",
    }
)


def replace_mojibake(text: str) -> str:
    for old, new in TEXT_REPLACEMENTS.items():
        text = text.replace(old, new)
    return text


def clean_text(value: Any) -> str:
    text = replace_mojibake(str(value or ""))
    return re.sub(r"\s+", " ", text).strip()


def clean_markdown(text: str) -> str:
    cleaned = replace_mojibake(text)
    cleaned = cleaned.replace("(reports/figures/", "(figures/")
    cleaned = cleaned.replace("] (figures/", "](figures/")
    return cleaned


def ensure_visual_markdown(text: str, figure_paths: List[str]) -> str:
    if all(f"figures/{Path(path).name}" in text for path in figure_paths) and "![" in text:
        return text
    figure_lines = ["", "### Generated Figure Embeds", ""]
    for path in figure_paths:
        figure_lines.append(f"![{Path(path).stem}](figures/{Path(path).name})")
    return text.rstrip() + "\n" + "\n".join(figure_lines) + "\n"


def claim_lookup(corpus: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    return {claim["id"]: claim for claim in corpus.get("claims", [])}


def paper_lookup(corpus: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    return {paper["id"]: paper for paper in corpus.get("papers", [])}


def audit_lookup(audit_payload: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    return {audit["hypothesis_id"]: audit for audit in audit_payload.get("audits", [])}


def build_brief_context() -> Dict[str, Any]:
    corpus = load_json(REAL_CORPUS_PATH)
    hypotheses = load_json(REAL_HYPOTHESES_PATH)
    audits = load_json(REAL_AUDITS_PATH)
    retrieval = load_json(RETRIEVAL_REPORT_PATH) if RETRIEVAL_REPORT_PATH.exists() else {"summary": {}}
    papers_by_id = paper_lookup(corpus)
    claims_by_id = claim_lookup(corpus)
    audits_by_id = audit_lookup(audits)

    enriched_hypotheses: List[Dict[str, Any]] = []
    for hypothesis in hypotheses.get("hypotheses", []):
        audit = audits_by_id.get(hypothesis["id"], {})
        supporting_claims = [claims_by_id[claim_id] for claim_id in hypothesis.get("supporting_claim_ids", []) if claim_id in claims_by_id]
        contradicting_claims = [claims_by_id[claim_id] for claim_id in hypothesis.get("contradicting_claim_ids", []) if claim_id in claims_by_id]
        enriched_hypotheses.append(
            {
                **hypothesis,
                "audit": audit,
                "supporting_claims": [
                    {
                        "id": claim["id"],
                        "claim_text": clean_text(claim.get("claim_text")),
                        "metric": clean_text(claim.get("metric")),
                        "value": clean_text(claim.get("value")),
                        "condition": clean_text(claim.get("experimental_condition")),
                        "limitation": clean_text(claim.get("limitation")),
                        "source_paper_id": claim.get("source_paper_id"),
                        "source_paper_title": clean_text(papers_by_id.get(claim.get("source_paper_id"), {}).get("title")),
                        "citation_text": clean_text(claim.get("citation_text")),
                    }
                    for claim in supporting_claims
                ],
                "contradicting_claims": [
                    {
                        "id": claim["id"],
                        "claim_text": clean_text(claim.get("claim_text")),
                        "limitation": clean_text(claim.get("limitation")),
                        "source_paper_id": claim.get("source_paper_id"),
                        "source_paper_title": clean_text(papers_by_id.get(claim.get("source_paper_id"), {}).get("title")),
                    }
                    for claim in contradicting_claims
                ],
            }
        )

    return {
        "research_goal": "Develop green or sustainable electrode material and electrode-fabrication research directions for lithium-ion batteries while preserving battery performance.",
        "scope": corpus.get("scope"),
        "quality_summary": corpus.get("quality_summary", {}),
        "retrieval_summary": retrieval.get("summary", retrieval),
        "hypotheses": enriched_hypotheses,
        "papers": [
            {
                "id": paper["id"],
                "title": clean_text(paper.get("title")),
                "green_strategy": clean_text(paper.get("green_strategy")),
                "fabrication_method": clean_text(paper.get("fabrication_method")),
                "limitations": [clean_text(item) for item in paper.get("limitations", [])[:4]],
            }
            for paper in corpus.get("papers", [])
        ],
        "claims": [
            {
                "id": claim["id"],
                "source_paper_id": claim.get("source_paper_id"),
                "approach_type": clean_text(claim.get("approach_type")),
                "metric": clean_text(claim.get("metric")),
                "value": clean_text(claim.get("value")),
                "claim_text": clean_text(claim.get("claim_text")),
                "limitation": clean_text(claim.get("limitation")),
                "needs_human_review": claim.get("needs_human_review", True),
            }
            for claim in corpus.get("claims", [])
        ],
    }


def svg_escape(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def score_color(score: float, lower_is_better: bool = False) -> str:
    adjusted = 1.0 - score if lower_is_better else score
    if adjusted >= 0.75:
        return "#15803d"
    if adjusted >= 0.55:
        return "#ca8a04"
    return "#dc2626"


def write_audit_score_chart(context: Dict[str, Any]) -> Path:
    rows = []
    for hypothesis in context["hypotheses"]:
        audit = hypothesis["audit"]
        rows.append(
            {
                "id": hypothesis["id"].replace("real:", ""),
                "grounding": float(audit.get("claim_grounding", 0)),
                "risk": float(audit.get("hallucination_risk", 1)),
                "feasibility": float(audit.get("feasibility", 0)),
            }
        )
    width, height = 980, 420
    margin_left, margin_top = 90, 50
    group_w = 160
    bar_w = 34
    scale_h = 260
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        '<text x="40" y="30" font-family="Arial" font-size="20" font-weight="700" fill="#111827">CellForge Hypothesis Audit Scores</text>',
        '<text x="40" y="55" font-family="Arial" font-size="12" fill="#4b5563">Higher grounding/feasibility is better; lower hallucination risk is better.</text>',
    ]
    for tick in range(0, 6):
        y = margin_top + scale_h - tick * scale_h / 5
        svg.append(f'<line x1="{margin_left}" y1="{y:.1f}" x2="{width - 70}" y2="{y:.1f}" stroke="#e5e7eb"/>')
        svg.append(f'<text x="44" y="{y + 4:.1f}" font-family="Arial" font-size="11" fill="#6b7280">{tick / 5:.1f}</text>')
    for i, row in enumerate(rows):
        x0 = margin_left + 35 + i * group_w
        values = [
            ("Grounding", row["grounding"], "#2563eb"),
            ("Low Risk", 1 - row["risk"], "#16a34a"),
            ("Feasible", row["feasibility"], "#9333ea"),
        ]
        for j, (_, value, color) in enumerate(values):
            h = value * scale_h
            x = x0 + j * (bar_w + 8)
            y = margin_top + scale_h - h
            svg.append(f'<rect x="{x}" y="{y:.1f}" width="{bar_w}" height="{h:.1f}" rx="4" fill="{color}"/>')
            svg.append(f'<text x="{x + bar_w / 2}" y="{y - 6:.1f}" text-anchor="middle" font-family="Arial" font-size="11" fill="#111827">{value:.2f}</text>')
        svg.append(f'<text x="{x0 + 58}" y="{margin_top + scale_h + 28}" text-anchor="middle" font-family="Arial" font-size="13" font-weight="700" fill="#111827">{row["id"]}</text>')
    legend_x = 620
    for i, (label, color) in enumerate([("Claim grounding", "#2563eb"), ("1 - hallucination risk", "#16a34a"), ("Feasibility", "#9333ea")]):
        x = legend_x + i * 115
        svg.append(f'<rect x="{x}" y="26" width="12" height="12" fill="{color}"/>')
        svg.append(f'<text x="{x + 18}" y="37" font-family="Arial" font-size="12" fill="#374151">{label}</text>')
    svg.append("</svg>")
    path = FIGURES_DIR / "audit_scores.svg"
    write_text(path, "\n".join(svg))
    return path


def write_evidence_matrix(context: Dict[str, Any]) -> Path:
    claims = context["claims"]
    hypotheses = context["hypotheses"]
    width = 1120
    row_h = 34
    height = 120 + row_h * len(claims)
    left = 250
    col_w = 92
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        '<text x="30" y="32" font-family="Arial" font-size="20" font-weight="700" fill="#111827">Evidence Matrix: Claims by Hypothesis</text>',
        '<text x="30" y="56" font-family="Arial" font-size="12" fill="#4b5563">Blue = supporting claim; amber = contradiction or caution claim.</text>',
    ]
    for i, hypothesis in enumerate(hypotheses):
        x = left + i * col_w
        svg.append(f'<text x="{x + 28}" y="92" transform="rotate(-25 {x + 28},92)" font-family="Arial" font-size="12" fill="#111827">{hypothesis["id"].replace("real:", "")}</text>')
    for r, claim in enumerate(claims):
        y = 110 + r * row_h
        fill = "#f9fafb" if r % 2 == 0 else "#ffffff"
        svg.append(f'<rect x="20" y="{y - 22}" width="{width - 40}" height="{row_h}" fill="{fill}"/>')
        svg.append(f'<text x="30" y="{y}" font-family="Arial" font-size="12" fill="#111827">{svg_escape(claim["id"])} | {svg_escape(claim["source_paper_id"] or "")}</text>')
        for c, hypothesis in enumerate(hypotheses):
            x = left + c * col_w + 24
            support = claim["id"] in hypothesis.get("supporting_claim_ids", [])
            contra = claim["id"] in hypothesis.get("contradicting_claim_ids", [])
            if support or contra:
                color = "#2563eb" if support else "#d97706"
                label = "S" if support else "C"
                svg.append(f'<circle cx="{x}" cy="{y - 4}" r="11" fill="{color}"/>')
                svg.append(f'<text x="{x}" y="{y}" text-anchor="middle" font-family="Arial" font-size="11" font-weight="700" fill="#ffffff">{label}</text>')
    svg.append("</svg>")
    path = FIGURES_DIR / "evidence_matrix.svg"
    write_text(path, "\n".join(svg))
    return path


def write_risk_grounding_scatter(context: Dict[str, Any]) -> Path:
    width, height = 760, 520
    left, top = 80, 55
    plot_w, plot_h = 600, 360
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        '<text x="34" y="30" font-family="Arial" font-size="20" font-weight="700" fill="#111827">Grounding vs. Hallucination Risk</text>',
        f'<line x1="{left}" y1="{top + plot_h}" x2="{left + plot_w}" y2="{top + plot_h}" stroke="#111827"/>',
        f'<line x1="{left}" y1="{top}" x2="{left}" y2="{top + plot_h}" stroke="#111827"/>',
    ]
    for tick in range(0, 6):
        x = left + tick * plot_w / 5
        y = top + plot_h - tick * plot_h / 5
        svg.append(f'<line x1="{x:.1f}" y1="{top}" x2="{x:.1f}" y2="{top + plot_h}" stroke="#e5e7eb"/>')
        svg.append(f'<line x1="{left}" y1="{y:.1f}" x2="{left + plot_w}" y2="{y:.1f}" stroke="#e5e7eb"/>')
        svg.append(f'<text x="{x - 7:.1f}" y="{top + plot_h + 22}" font-family="Arial" font-size="11" fill="#6b7280">{tick / 5:.1f}</text>')
        svg.append(f'<text x="{left - 34}" y="{y + 4:.1f}" font-family="Arial" font-size="11" fill="#6b7280">{tick / 5:.1f}</text>')
    svg.append(f'<text x="{left + plot_w / 2}" y="{height - 35}" text-anchor="middle" font-family="Arial" font-size="13" fill="#111827">Claim grounding</text>')
    svg.append(f'<text x="18" y="{top + plot_h / 2}" transform="rotate(-90 18,{top + plot_h / 2})" text-anchor="middle" font-family="Arial" font-size="13" fill="#111827">Hallucination risk</text>')
    for hypothesis in context["hypotheses"]:
        audit = hypothesis["audit"]
        grounding = float(audit.get("claim_grounding", 0))
        risk = float(audit.get("hallucination_risk", 1))
        x = left + grounding * plot_w
        y = top + plot_h - risk * plot_h
        color = score_color(risk, lower_is_better=True)
        svg.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="15" fill="{color}" opacity="0.9"/>')
        svg.append(f'<text x="{x:.1f}" y="{y + 4:.1f}" text-anchor="middle" font-family="Arial" font-size="10" font-weight="700" fill="#ffffff">{hypothesis["id"].replace("real:H", "H")}</text>')
    svg.append("</svg>")
    path = FIGURES_DIR / "risk_grounding_scatter.svg"
    write_text(path, "\n".join(svg))
    return path


def write_molecular_interface_schematic(context: Dict[str, Any]) -> Path:
    lead = select_lead_hypothesis(context)
    support_ids = set(lead.get("supporting_claim_ids", []))
    lead_claims = [claim for claim in context["claims"] if claim["id"] in support_ids]
    claim_labels = {
        claim["id"]: f"{claim['id']}: {claim['metric']} {claim['value']}".strip()
        for claim in lead_claims
    }
    width, height = 1180, 680
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<defs>',
        '<radialGradient id="graphiteGrad" cx="45%" cy="40%" r="65%">',
        '<stop offset="0%" stop-color="#475569"/>',
        '<stop offset="65%" stop-color="#1f2937"/>',
        '<stop offset="100%" stop-color="#020617"/>',
        '</radialGradient>',
        '<linearGradient id="seiGrad" x1="0%" x2="100%" y1="0%" y2="100%">',
        '<stop offset="0%" stop-color="#a7f3d0" stop-opacity="0.85"/>',
        '<stop offset="100%" stop-color="#67e8f9" stop-opacity="0.7"/>',
        '</linearGradient>',
        '<marker id="arrow" markerWidth="12" markerHeight="12" refX="10" refY="6" orient="auto">',
        '<path d="M2,2 L10,6 L2,10 Z" fill="#2563eb"/>',
        '</marker>',
        '<marker id="electronArrow" markerWidth="12" markerHeight="12" refX="10" refY="6" orient="auto">',
        '<path d="M2,2 L10,6 L2,10 Z" fill="#f59e0b"/>',
        '</marker>',
        '</defs>',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        '<text x="44" y="42" font-family="Arial" font-size="23" font-weight="700" fill="#111827">Conceptual molecular/interface schematic for lead hypothesis H003</text>',
        '<text x="44" y="68" font-family="Arial" font-size="13" fill="#4b5563">Simulated interpretation: regenerated/natural graphite surface repaired by bio-derived carbon coating and stabilized SEI. Not an atomistic simulation result.</text>',
        '<rect x="42" y="96" width="1096" height="510" rx="14" fill="#f8fafc" stroke="#d1d5db"/>',
        '<ellipse cx="420" cy="350" rx="235" ry="160" fill="url(#graphiteGrad)" stroke="#111827" stroke-width="3"/>',
        '<ellipse cx="420" cy="350" rx="257" ry="181" fill="none" stroke="#7c2d12" stroke-width="22" stroke-opacity="0.72"/>',
        '<ellipse cx="420" cy="350" rx="285" ry="207" fill="none" stroke="url(#seiGrad)" stroke-width="28" stroke-opacity="0.86"/>',
        '<text x="311" y="342" font-family="Arial" font-size="19" font-weight="700" fill="#f8fafc">Regenerated / natural</text>',
        '<text x="350" y="368" font-family="Arial" font-size="19" font-weight="700" fill="#f8fafc">graphite core</text>',
        '<text x="206" y="160" font-family="Arial" font-size="13" font-weight="700" fill="#7c2d12">thin bio-derived carbon repair layer</text>',
        '<text x="214" y="545" font-family="Arial" font-size="13" font-weight="700" fill="#0f766e">stable SEI / electrolyte interface</text>',
    ]

    # Graphite basal planes.
    for offset in range(-110, 130, 28):
        y = 350 + offset
        svg.append(f'<path d="M235 {y} C330 {y - 28}, 505 {y - 28}, 600 {y}" fill="none" stroke="#94a3b8" stroke-width="2" opacity="0.45"/>')
        for x in range(270, 575, 48):
            svg.append(f'<circle cx="{x}" cy="{y - 8}" r="3.5" fill="#cbd5e1" opacity="0.7"/>')

    # Tannic-acid-like aromatic clusters in the coating.
    aromatic_centers = [(210, 273), (244, 222), (338, 170), (536, 190), (640, 287), (625, 428), (498, 520), (300, 515), (176, 398)]
    for cx, cy in aromatic_centers:
        points = []
        for k in range(6):
            angle = math.pi / 6 + k * math.pi / 3
            points.append(f"{cx + 13 * math.cos(angle):.1f},{cy + 13 * math.sin(angle):.1f}")
        svg.append(f'<polygon points="{" ".join(points)}" fill="#fed7aa" stroke="#9a3412" stroke-width="1.4"/>')
        svg.append(f'<circle cx="{cx + 19}" cy="{cy - 13}" r="4" fill="#ef4444"/>')
        svg.append(f'<circle cx="{cx - 18}" cy="{cy + 15}" r="4" fill="#ef4444"/>')

    # Lithium-ion and electron transport paths.
    for y in (245, 320, 395):
        svg.append(f'<path d="M865 {y} C760 {y - 30}, 720 {y + 20}, 647 {y}" fill="none" stroke="#2563eb" stroke-width="3" marker-end="url(#arrow)" stroke-dasharray="8 7"/>')
        svg.append(f'<circle cx="890" cy="{y - 4}" r="14" fill="#dbeafe" stroke="#2563eb" stroke-width="2"/>')
        svg.append(f'<text x="890" y="{y + 1}" text-anchor="middle" font-family="Arial" font-size="11" font-weight="700" fill="#1d4ed8">Li+</text>')
    svg.append('<path d="M655 470 C760 525, 835 505, 932 445" fill="none" stroke="#f59e0b" stroke-width="3" marker-end="url(#electronArrow)"/>')
    svg.append('<text x="800" y="535" text-anchor="middle" font-family="Arial" font-size="13" font-weight="700" fill="#92400e">electron pathway through repaired conductive coating</text>')

    # Callouts.
    callouts = [
        (735, 132, "Green purification", claim_labels.get("real:C107_01", "real:C107_01: carbon purity >99.99%"), "#166534"),
        (742, 214, "Regenerated graphite", claim_labels.get("real:C107_02", "real:C107_02: reversible capacity 353 mAh/g"), "#1d4ed8"),
        (742, 296, "Bio-based coating", claim_labels.get("real:C099_01", "real:C099_01: retention 89% after 500 cycles"), "#9a3412"),
        (742, 378, "Risk control", "Avoid solvent/regulatory burden flagged by real:C110_01", "#b91c1c"),
    ]
    for x, y, title, body, color in callouts:
        svg.append(f'<rect x="{x}" y="{y}" width="360" height="58" rx="9" fill="#ffffff" stroke="{color}" stroke-width="1.6"/>')
        svg.append(f'<text x="{x + 14}" y="{y + 21}" font-family="Arial" font-size="13" font-weight="700" fill="{color}">{svg_escape(title)}</text>')
        svg.append(f'<text x="{x + 14}" y="{y + 42}" font-family="Arial" font-size="12" fill="#374151">{svg_escape(body[:72])}</text>')
    svg.append('<line x1="735" y1="162" x2="660" y2="230" stroke="#166534" stroke-width="1.5"/>')
    svg.append('<line x1="742" y1="242" x2="600" y2="330" stroke="#1d4ed8" stroke-width="1.5"/>')
    svg.append('<line x1="742" y1="324" x2="655" y2="294" stroke="#9a3412" stroke-width="1.5"/>')
    svg.append('<line x1="742" y1="406" x2="655" y2="435" stroke="#b91c1c" stroke-width="1.5"/>')

    svg.extend(
        [
            '<rect x="72" y="626" width="18" height="18" fill="#1f2937"/>',
            '<text x="98" y="640" font-family="Arial" font-size="12" fill="#374151">graphite basal-plane network</text>',
            '<rect x="294" y="626" width="18" height="18" fill="#fed7aa" stroke="#9a3412"/>',
            '<text x="320" y="640" font-family="Arial" font-size="12" fill="#374151">tannic-derived carbon/phenolic motif</text>',
            '<rect x="574" y="626" width="18" height="18" fill="#a7f3d0" stroke="#0f766e"/>',
            '<text x="600" y="640" font-family="Arial" font-size="12" fill="#374151">SEI/electrolyte interface</text>',
            '<line x1="790" y1="635" x2="850" y2="635" stroke="#2563eb" stroke-width="3" marker-end="url(#arrow)" stroke-dasharray="8 7"/>',
            '<text x="862" y="640" font-family="Arial" font-size="12" fill="#374151">Li-ion flux</text>',
            "</svg>",
        ]
    )
    path = FIGURES_DIR / "molecular_interface_schematic.svg"
    write_text(path, "\n".join(svg))
    return path


def generate_figures(context: Dict[str, Any]) -> List[str]:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    paths = [
        write_audit_score_chart(context),
        write_evidence_matrix(context),
        write_risk_grounding_scatter(context),
        write_molecular_interface_schematic(context),
    ]
    return [str(path.relative_to(ROOT)) for path in paths]


def compact_context_for_prompt(context: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "research_goal": context["research_goal"],
        "scope": context["scope"],
        "quality_summary": context["quality_summary"],
        "retrieval_summary": context["retrieval_summary"],
        "hypotheses": [
            {
                "id": hypothesis["id"],
                "title": hypothesis["title"],
                "hypothesis": hypothesis["hypothesis"],
                "mechanism": hypothesis["mechanism"],
                "novelty_rationale": hypothesis["novelty_rationale"],
                "proposed_experiment": hypothesis["proposed_experiment"],
                "expected_contribution": hypothesis["expected_contribution"],
                "audit": hypothesis["audit"],
                "supporting_claims": hypothesis["supporting_claims"],
                "contradicting_claims": hypothesis["contradicting_claims"],
            }
            for hypothesis in context["hypotheses"]
        ],
        "claims": context["claims"],
        "references": context["papers"],
    }


def build_prompt(context: Dict[str, Any], figure_paths: List[str]) -> str:
    payload = compact_context_for_prompt(context)
    lead_id = select_lead_hypothesis(context)["id"]
    markdown_figures = "\n".join(f"- ![{Path(path).stem}](figures/{Path(path).name})" for path in figure_paths)
    return (
        "You are CellForge AI's Gemini Pro research brief writer.\n\n"
        "Task: Generate an evidence-backed research proposal package, not a publishable final paper. "
        "The package is for a human battery researcher to validate and turn into a paper.\n\n"
        "Hard rules:\n"
        "- Use only the provided audited evidence, claims, hypotheses, contradictions, and references.\n"
        "- Do not invent DOIs, authors, publication years, metrics, experimental results, or external citations.\n"
        "- Every strong technical claim must cite claim IDs and source paper IDs inline.\n"
        "- Label weak evidence, review-derived claims, and chart-derived values as human-validation needs.\n"
        f"- The recommended lead hypothesis must be {lead_id}, because it is the hypothesis selected by the evidence auditor/self-introspection stage for advancement with human review.\n"
        "- Compare alternatives after the lead hypothesis, but do not make an alternative the recommended lead.\n"
        "- Keep language proposal-oriented: use 'we propose', 'should be tested', and 'requires validation'.\n\n"
        "Required Markdown sections:\n"
        "1. Title Candidates\n"
        "2. Abstract Draft\n"
        "3. Research Goal and Scope\n"
        "4. Why This Is a Gap\n"
        "5. Recommended Lead Hypothesis\n"
        "6. Alternative Hypotheses\n"
        "7. Evidence Matrix Summary\n"
        "8. Visual Evidence\n"
        "9. Contradictions and Risk Controls\n"
        "10. Proposed Experiment Plan\n"
        "11. Expected Contribution\n"
        "12. Limitations and Human Validation Checklist\n"
        "13. References\n\n"
        "Use these exact Markdown image references in the Visual Evidence section:\n"
        f"{markdown_figures}\n\n"
        "Audited evidence package JSON:\n"
        f"{json.dumps(payload, ensure_ascii=False, indent=2)}"
    )


def select_lead_hypothesis(context: Dict[str, Any]) -> Dict[str, Any]:
    return sorted(
        context["hypotheses"],
        key=lambda item: (
            item["audit"].get("recommendation") == "advance_with_human_review",
            -item["audit"].get("hallucination_risk", 1),
            item["audit"].get("claim_grounding", 0),
        ),
        reverse=True,
    )[0]


def local_brief(context: Dict[str, Any], figure_paths: List[str]) -> str:
    lead = select_lead_hypothesis(context)
    ranked = [lead] + [hypothesis for hypothesis in context["hypotheses"] if hypothesis["id"] != lead["id"]]
    lines = [
        "# CellForge AI Research Proposal Package",
        "",
        "> This is an evidence-backed research proposal package generated from audited extraction artifacts. It is not a publishable final paper and requires human validation before publication use.",
        "",
        "## Title Candidates",
        "",
        "- Circular Natural-Graphite Anodes with Bio-Based Conductive Surface Repair for Greener Lithium-Ion Batteries",
        "- Coupling Green Graphite Purification and Bio-Derived Surface Coatings for Durable Lithium-Ion Anodes",
        "- Evidence-Audited Research Directions for Sustainable Electrode Materials in Lithium-Ion Batteries",
        "",
        "## Abstract Draft",
        "",
        f"CellForge AI analyzed {context['quality_summary'].get('extracted_paper_count')} real-paper extraction artifacts and {context['quality_summary'].get('extracted_claim_count')} structured claims in the scope of {context['scope']}. "
        f"The strongest proposal candidate is **{lead['title']}** ({lead['id']}), which combines green natural-graphite purification, regenerated graphite, and bio-derived conductive surface repair. "
        "The proposal is grounded in cited claims but remains a research direction requiring human review and experimental validation.",
        "",
        "## Research Goal and Scope",
        "",
        context["research_goal"],
        "",
        "## Recommended Lead Hypothesis",
        "",
        f"**{lead['id']}: {lead['title']}**",
        "",
        lead["hypothesis"],
        "",
        f"Mechanism: {lead['mechanism']}",
        "",
        f"Novelty rationale: {lead['novelty_rationale']}",
        "",
        "Audit scores:",
        "",
    ]
    for field in SCORE_FIELDS:
        lines.append(f"- {field}: `{lead['audit'].get(field)}`")
    lines.extend(["", "Supporting evidence:"])
    for claim in lead["supporting_claims"]:
        lines.append(f"- `{claim['id']}` from `{claim['source_paper_id']}`: {claim['claim_text']} Metric: {claim['metric']} = {claim['value']}.")
    lines.extend(["", "## Alternative Hypotheses", ""])
    for hypothesis in ranked[1:]:
        audit = hypothesis["audit"]
        lines.append(
            f"- `{hypothesis['id']}` **{hypothesis['title']}**: {hypothesis['hypothesis']} "
            f"Recommendation: `{audit.get('recommendation')}`, grounding `{audit.get('claim_grounding')}`, hallucination risk `{audit.get('hallucination_risk')}`."
        )
    lines.extend(["", "## Visual Evidence", ""])
    for path in figure_paths:
        lines.append(f"![{Path(path).stem}]({path.replace(chr(92), '/')})")
    lines.extend(["", "## Contradictions and Risk Controls", ""])
    for hypothesis in ranked:
        notes = hypothesis["audit"].get("contradiction_notes", [])
        if notes:
            lines.append(f"- `{hypothesis['id']}`: " + "; ".join(clean_text(note) for note in notes))
    lines.extend(
        [
            "",
            "## Proposed Experiment Plan",
            "",
            lead["proposed_experiment"],
            "",
            "Primary measurements should include carbon purity, reversible capacity, initial Coulombic efficiency, SEI impedance, capacity retention, process energy, and chemical burden.",
            "",
            "## Limitations and Human Validation Checklist",
            "",
            "- All cited claims are extraction artifacts and require human validation against the source PDFs.",
            "- Review-derived claims should be checked against their primary sources before manuscript use.",
            "- Chart-derived values should be manually digitized before being treated as precise numerical evidence.",
            "- The output is a proposal package, not a final paper.",
            "",
            "## References",
            "",
        ]
    )
    for paper in context["papers"]:
        lines.append(f"- `{paper['id']}` {paper['title']}")
    return "\n".join(lines) + "\n"


def gemini_brief(prompt: str) -> tuple[str, Dict[str, Any]]:
    load_env_file()
    add_local_dependency_path()
    try:
        from google import genai
        from google.genai import types
    except Exception as exc:  # pragma: no cover - depends on optional SDK
        raise RuntimeError("google-genai is not installed. Run `python -m pip install --target .python-deps google-genai`.") from exc

    project = os.getenv("GOOGLE_CLOUD_PROJECT")
    location = os.getenv("GOOGLE_CLOUD_LOCATION", "global")
    model = os.getenv("GEMINI_MODEL", "gemini-2.5-pro")
    if not project:
        raise RuntimeError("GOOGLE_CLOUD_PROJECT is required for Gemini brief generation.")
    client = genai.Client(vertexai=True, project=project, location=location)
    config = types.GenerateContentConfig(
        temperature=0.2,
        top_p=0.9,
        max_output_tokens=16000,
        system_instruction=(
            "You are an expert battery R&D research strategist. "
            "You write careful proposal packages from provided evidence only."
        ),
    )
    response = client.models.generate_content(model=model, contents=prompt, config=config)
    text = getattr(response, "text", "") or str(response)
    metadata = {
        "provider": "gemini",
        "model": model,
        "project": project,
        "location": location,
    }
    usage = getattr(response, "usage_metadata", None)
    if usage is not None:
        metadata["usage_metadata"] = {
            key: getattr(usage, key)
            for key in ("prompt_token_count", "candidates_token_count", "total_token_count")
            if hasattr(usage, key)
        }
    return text, metadata


def generate_research_brief(provider: Optional[str] = None, run_id: Optional[str] = None) -> Dict[str, Any]:
    load_env_file()
    start = int(time.time() * 1000)
    provider = provider or os.getenv("CELLFORGE_BRIEF_PROVIDER", "local").lower()
    run_id = run_id or f"cellforge-brief-{uuid.uuid4().hex[:8]}"
    context = build_brief_context()
    figure_paths = generate_figures(context)
    prompt = build_prompt(context, figure_paths)
    provider_metadata: Dict[str, Any]
    try:
        if provider == "gemini":
            brief_markdown, provider_metadata = gemini_brief(prompt)
        else:
            brief_markdown = local_brief(context, figure_paths)
            provider_metadata = {"provider": "local_template"}
    except Exception as exc:
        brief_markdown = local_brief(context, figure_paths)
        provider_metadata = {
            "provider": "local_template_fallback",
            "requested_provider": provider,
            "error": f"{exc.__class__.__name__}: {exc}",
        }
    brief_markdown = ensure_visual_markdown(clean_markdown(brief_markdown), figure_paths)
    end = int(time.time() * 1000)
    payload = {
        "run_id": run_id,
        "provider": provider_metadata,
        "source_files": [
            str(REAL_CORPUS_PATH.relative_to(ROOT)),
            str(REAL_HYPOTHESES_PATH.relative_to(ROOT)),
            str(REAL_AUDITS_PATH.relative_to(ROOT)),
        ],
        "figures": figure_paths,
        "summary": {
            "hypotheses": len(context["hypotheses"]),
            "claims": len(context["claims"]),
            "papers": len(context["papers"]),
            "lead_hypothesis_id": select_lead_hypothesis(context)["id"],
            "publication_positioning": "research_proposal_package_not_final_paper",
        },
    }
    write_text(BRIEF_MD_PATH, brief_markdown)
    write_json(BRIEF_JSON_PATH, payload)

    adapter = create_phoenix_adapter()
    adapter.log_agent_trace(
        run_id=run_id,
        stage="paper_draft_agent.gemini_research_brief",
        input={
            "provider": provider,
            "source_files": payload["source_files"],
            "figure_paths": figure_paths,
            "prompt_chars": len(prompt),
        },
        output={
            "brief_path": str(BRIEF_MD_PATH.relative_to(ROOT)),
            "json_path": str(BRIEF_JSON_PATH.relative_to(ROOT)),
            "provider": provider_metadata,
            "summary": payload["summary"],
        },
        metadata={
            "span_kind": "LLM" if provider_metadata.get("provider") == "gemini" else "CHAIN",
            "openinference_span_kind": "LLM" if provider_metadata.get("provider") == "gemini" else "CHAIN",
            "start_time_ms": start,
            "end_time_ms": end,
            "status": "OK",
            "uses_audited_evidence": True,
            "output_positioning": "evidence_backed_research_proposal_package",
        },
    )
    adapter.flush()
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate CellForge AI research proposal package with local or Gemini provider.")
    parser.add_argument("--provider", choices=["local", "gemini"], default=None)
    parser.add_argument("--run-id", default=None)
    args = parser.parse_args()
    print(json.dumps(generate_research_brief(provider=args.provider, run_id=args.run_id), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
