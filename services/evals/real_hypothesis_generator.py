from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List


ROOT = Path(__file__).resolve().parents[2]
REAL_CORPUS_PATH = ROOT / "data" / "real_evidence_corpus.json"
REAL_HYPOTHESES_PATH = ROOT / "data" / "real_hypotheses.json"
REAL_HYPOTHESES_REPORT_PATH = ROOT / "reports" / "real_hypotheses_report.md"


def load_real_corpus(path: Path = REAL_CORPUS_PATH) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def claims_by_id(corpus: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    return {claim["id"]: claim for claim in corpus["claims"]}


def papers_by_id(corpus: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    return {paper["id"]: paper for paper in corpus["papers"]}


def select_claims(corpus: Dict[str, Any], claim_ids: Iterable[str]) -> List[Dict[str, Any]]:
    lookup = claims_by_id(corpus)
    return [lookup[claim_id] for claim_id in claim_ids if claim_id in lookup]


def evidence_strength(claims: List[Dict[str, Any]]) -> float:
    if not claims:
        return 0.0
    experimental = sum(1 for claim in claims if "experimental" in str(claim.get("evidence_type", "")).lower())
    review_penalty = sum(1 for claim in claims if "review" in str(claim.get("evidence_type", "")).lower())
    score = 0.45 + (0.14 * len(claims)) + (0.06 * experimental) - (0.07 * review_penalty)
    return round(max(0.0, min(score, 0.95)), 2)


def feasibility_score(claims: List[Dict[str, Any]], penalty_terms: Iterable[str] = ()) -> float:
    text = " ".join(" ".join([claim.get("limitation", ""), claim.get("experimental_condition", "")]) for claim in claims).lower()
    score = 0.78
    for term in penalty_terms:
        if term in text:
            score -= 0.08
    if any("vacuum" in claim.get("limitation", "").lower() for claim in claims):
        score -= 0.06
    return round(max(0.35, min(score, 0.9)), 2)


def novelty_score(claim_count: int, cross_domain: bool = True) -> float:
    base = 0.72 + (0.04 * max(claim_count - 1, 0))
    if cross_domain:
        base += 0.08
    return round(max(0.0, min(base, 0.95)), 2)


def hypothesis_record(
    *,
    hypothesis_id: str,
    title: str,
    hypothesis: str,
    mechanism: str,
    novelty_rationale: str,
    supporting_claim_ids: List[str],
    contradicting_claim_ids: List[str],
    proposed_experiment: str,
    expected_contribution: str,
    metric_terms: List[str],
    battery_chemistry: str = "lithium-ion",
    corpus: Dict[str, Any],
    feasibility_penalty_terms: Iterable[str] = (),
) -> Dict[str, Any]:
    supporting_claims = select_claims(corpus, supporting_claim_ids)
    contradicting_claims = select_claims(corpus, contradicting_claim_ids)
    all_claims = supporting_claims + contradicting_claims
    scores = {
        "evidence_strength": evidence_strength(supporting_claims),
        "novelty_gap": novelty_score(len(supporting_claims), cross_domain=len({claim.get("approach_type") for claim in supporting_claims}) > 1),
        "feasibility": feasibility_score(all_claims, penalty_terms=feasibility_penalty_terms),
        "human_validation_need": round(sum(1 for claim in all_claims if claim.get("needs_human_review", True)) / max(len(all_claims), 1), 2),
    }
    return {
        "id": hypothesis_id,
        "title": title,
        "hypothesis": hypothesis,
        "battery_chemistry": battery_chemistry,
        "mechanism": mechanism,
        "novelty_rationale": novelty_rationale,
        "supporting_claim_ids": supporting_claim_ids,
        "contradicting_claim_ids": contradicting_claim_ids,
        "proposed_experiment": proposed_experiment,
        "expected_contribution": expected_contribution,
        "metric_terms": metric_terms,
        "scores": scores,
        "generation_mode": "deterministic_template_from_real_claims",
        "status": "candidate_requires_evidence_audit",
    }


def generate_real_hypotheses(corpus: Dict[str, Any] | None = None) -> Dict[str, Any]:
    corpus = corpus or load_real_corpus()
    hypotheses = [
        hypothesis_record(
            hypothesis_id="real:H001",
            title="Atmospheric plasma-assisted dry cathode interfaces for lower-impact manufacturing",
            hypothesis=(
                "Combining dry cathode processing with short-duration plasma surface activation will improve current-collector adhesion "
                "and cycling stability while reducing NMP solvent use and drying energy."
            ),
            mechanism=(
                "Plasma introduces polar surface groups that improve PTFE/current-collector adhesion, while optimized dry-processing "
                "additives reduce calendering damage and maintain conductive networks."
            ),
            novelty_rationale=(
                "The corpus contains separate evidence for plasma-enhanced dry-electrode adhesion and carbon-black-enabled dry cathode "
                "cycling stability, but not a unified roll-compatible interface strategy."
            ),
            supporting_claim_ids=["real:C044_01", "real:C086_01", "real:C075_01"],
            contradicting_claim_ids=["real:C123_01"],
            proposed_experiment=(
                "Fabricate NMC811 dry cathodes with PTFE binder and two carbon-black grades, apply 10-60 s atmospheric or low-vacuum Ar/O2 "
                "plasma before lamination, then compare adhesion, sheet resistance, tortuosity, particle cracking, rate capability, and "
                "capacity retention against untreated dry electrodes."
            ),
            expected_contribution=(
                "A practical route for solvent-free cathode manufacturing that explicitly links interface activation, calendering damage, "
                "and electrochemical durability."
            ),
            metric_terms=["adhesion strength", "capacity retention", "tortuosity", "calendering damage", "NMP elimination"],
            corpus=corpus,
            feasibility_penalty_terms=["vacuum", "tortuosity"],
        ),
        hypothesis_record(
            hypothesis_id="real:H002",
            title="Water-compatible bio-derived binder systems for graphite anodes",
            hypothesis=(
                "A water-compatible hybrid of chitosan-derived self-healing chemistry and PHBV-like biodegradable binder design can retain "
                "graphite cycling stability while avoiding both PVDF/NMP and chlorinated-solvent processing."
            ),
            mechanism=(
                "Dynamic imine or hydrogen-bonding networks can maintain particle adhesion and tolerate volume changes, while biodegradable "
                "polymer segments provide mechanical integrity without fluorinated binder chemistry."
            ),
            novelty_rationale=(
                "Existing evidence supports chitosan self-healing binders and PHBV biodegradable binders separately; the gap is a binder "
                "platform that combines bio-derived durability with genuinely greener solvent processing."
            ),
            supporting_claim_ids=["real:C096_01", "real:C110_01"],
            contradicting_claim_ids=["real:C081_01"],
            proposed_experiment=(
                "Prepare graphite anodes using aqueous chitosan/vanillin derivatives blended with PHBV-inspired biodegradable segments or "
                "waterborne PHBV dispersions. Benchmark against PVDF, pristine chitosan, and PHBV controls for adhesion, swelling, impedance, "
                "rate capability, capacity retention, and binder dissolution."
            ),
            expected_contribution=(
                "A validated path toward non-fluorinated, bio-derived graphite anode binders that does not move the environmental burden "
                "from binder chemistry to hazardous solvent use."
            ),
            metric_terms=["capacity retention", "adhesion", "swelling", "ionic conductivity", "solvent toxicity"],
            corpus=corpus,
            feasibility_penalty_terms=["chloroform", "ionic"],
        ),
        hypothesis_record(
            hypothesis_id="real:H003",
            title="Circular natural-graphite anodes with bio-based conductive surface repair",
            hypothesis=(
                "Green-purified or regenerated natural graphite can recover high anode performance when paired with thin bio-derived carbon "
                "or conductive polymer coatings that stabilize SEI formation and electronic pathways."
            ),
            mechanism=(
                "Chemical-free purification reduces impurity-driven degradation, while thin carbon/polymer coatings repair surface defects, "
                "improve charge transfer, and reduce long-cycle capacity loss."
            ),
            novelty_rationale=(
                "The corpus links natural graphite purification, recycled graphite regeneration, and bio-based graphite coating, suggesting "
                "a circular anode route that has not yet been jointly optimized."
            ),
            supporting_claim_ids=["real:C107_01", "real:C107_02", "real:C099_01"],
            contradicting_claim_ids=["real:C110_01"],
            proposed_experiment=(
                "Compare natural graphite, regenerated spent graphite, and synthetic graphite baselines after non-thermal plasma purification "
                "and tannic-acid-derived carbon coating. Measure purity, ICE, SEI impedance, reversible capacity, 2C cycling retention, and "
                "process energy/chemical burden."
            ),
            expected_contribution=(
                "A circular-economy anode strategy that treats sustainability and electrochemical stability as coupled design targets."
            ),
            metric_terms=["carbon purity", "reversible capacity", "capacity retention", "initial Coulombic efficiency", "process chemicals"],
            corpus=corpus,
            feasibility_penalty_terms=["scale", "equipment", "formaldehyde"],
        ),
        hypothesis_record(
            hypothesis_id="real:H004",
            title="Biomass-derived carbon additives for dry-processed cathode transport control",
            hypothesis=(
                "Functionalized biomass-derived carbons can serve as sustainable conductive/process additives in dry cathodes, improving "
                "ion-transport kinetics without increasing tortuosity as much as very high-surface-area carbon blacks."
            ),
            mechanism=(
                "Sulfonyl or metal-coordination sites from modified lignin carbons may improve interfacial ion transport, while carbon "
                "morphology can be tuned to cushion calendering stress and preserve conductive pathways."
            ),
            novelty_rationale=(
                "The evidence base currently separates lignin-derived carbon ion-transport benefits from carbon-black process-aid behavior "
                "in dry cathodes; testing biomass carbons as dry-processing additives is an underexplored bridge."
            ),
            supporting_claim_ids=["real:C081_01", "real:C086_01", "real:C075_01"],
            contradicting_claim_ids=["real:C044_01"],
            proposed_experiment=(
                "Synthesize lignin-derived carbon additives with controlled surface chemistry, blend them into PTFE-based dry NMC cathodes, "
                "and compare calenderability, electrode tortuosity, charge-transfer resistance, particle cracking, and long-cycle retention "
                "against commercial carbon blacks."
            ),
            expected_contribution=(
                "A lower-impact conductive additive design space for dry cathode manufacturing that explicitly balances mechanical processability "
                "and ion transport."
            ),
            metric_terms=["activation energy", "charge-transfer resistance", "capacity retention", "tortuosity", "calendering"],
            corpus=corpus,
            feasibility_penalty_terms=["900", "tortuosity"],
        ),
        hypothesis_record(
            hypothesis_id="real:H005",
            title="Quality-controlled low-energy plasma synthesis for NMC cathode precursors",
            hypothesis=(
                "Stabilizing atmospheric microplasma synthesis with contamination-resistant reactor materials and downstream dry-electrode "
                "process controls can improve the viability of calcination-free NMC cathode fabrication."
            ),
            mechanism=(
                "Stable plasma discharge should increase precursor conversion and crystal quality, while dry-electrode process optimization "
                "can isolate whether capacity losses originate from synthesis defects or electrode manufacturing artifacts."
            ),
            novelty_rationale=(
                "Sub-second NMC synthesis is promising but limited by low yield, contamination, and low initial capacity; coupling it with "
                "dry-electrode diagnostics offers a concrete path to separate material synthesis gaps from electrode-processing gaps."
            ),
            supporting_claim_ids=["real:C123_01", "real:C086_01", "real:C044_01"],
            contradicting_claim_ids=["real:C075_01"],
            proposed_experiment=(
                "Run a design-of-experiments study varying plasma waveform, electrode material, gas mixture, and precursor feed rate, then "
                "fabricate standardized dry cathodes to compare phase purity, Fe contamination, particle size, initial capacity, impedance, "
                "and 100-cycle retention."
            ),
            expected_contribution=(
                "A grounded assessment of whether calcination-free cathode synthesis can become a credible sustainable manufacturing path, "
                "rather than only a low-energy proof of concept."
            ),
            metric_terms=["synthesis time", "initial capacity", "contamination", "particle size", "capacity retention"],
            corpus=corpus,
            feasibility_penalty_terms=["contamination", "yield", "tortuosity"],
        ),
    ]

    return {
        "description": (
            "Deterministic CellForge hypotheses generated from Gemini-extracted real-paper claims. "
            "These are research proposal candidates, not validated conclusions."
        ),
        "source_corpus": str(REAL_CORPUS_PATH.relative_to(ROOT)),
        "generation_mode": "deterministic_template_from_real_claims",
        "hypotheses": hypotheses,
    }


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)
        handle.write("\n")


def write_report(payload: Dict[str, Any], path: Path = REAL_HYPOTHESES_REPORT_PATH) -> None:
    lines = [
        "# Deterministic Real Hypotheses",
        "",
        "These hypotheses are generated from the real-paper evidence corpus using deterministic templates. They are proposal candidates for audit, not validated research conclusions.",
        "",
        f"- Source corpus: `{payload['source_corpus']}`",
        f"- Hypotheses: `{len(payload['hypotheses'])}`",
        "",
        "## Candidates",
        "",
    ]
    for hypothesis in payload["hypotheses"]:
        scores = hypothesis["scores"]
        lines.extend(
            [
                f"### {hypothesis['id']}: {hypothesis['title']}",
                "",
                hypothesis["hypothesis"],
                "",
                f"- Supporting claims: `{', '.join(hypothesis['supporting_claim_ids'])}`",
                f"- Contradicting/limitation claims: `{', '.join(hypothesis['contradicting_claim_ids'])}`",
                f"- Evidence strength: `{scores['evidence_strength']}`",
                f"- Novelty gap: `{scores['novelty_gap']}`",
                f"- Feasibility: `{scores['feasibility']}`",
                f"- Human validation need: `{scores['human_validation_need']}`",
                "",
                "**Proposed experiment:**",
                "",
                hypothesis["proposed_experiment"],
                "",
            ]
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8", newline="\n")


def generate_and_write_real_hypotheses() -> Dict[str, Any]:
    payload = generate_real_hypotheses()
    write_json(REAL_HYPOTHESES_PATH, payload)
    write_report(payload)
    return {
        "hypotheses": len(payload["hypotheses"]),
        "real_hypotheses_path": str(REAL_HYPOTHESES_PATH),
        "report_path": str(REAL_HYPOTHESES_REPORT_PATH),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate deterministic real-paper hypotheses.")
    parser.add_argument("--write", action="store_true", help="Write data/real_hypotheses.json and report markdown.")
    args = parser.parse_args()

    result = generate_and_write_real_hypotheses() if args.write else generate_real_hypotheses()
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
