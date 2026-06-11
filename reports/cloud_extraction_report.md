# Cloud Extraction Normalization Report

This report summarizes the Google Cloud/Gemini document-understanding outputs normalized for CellForge AI.

## Summary

- Extracted papers: `9`
- Extracted claims: `10`
- Papers needing human review: `9`
- Skipped/invalid files: `1`
- Quality gate: `usable_for_demo_retrieval_and_hypothesis_generation`
- Publication readiness: `not_publication_ready_without_human_validation`

## Corpus Scope

green and sustainable electrode materials/fabrication for lithium-ion batteries

## Papers

| Paper ID | Review | Title | Source file |
| --- | --- | --- | --- |
| real:P044 | yes | Solvent-free processing of lithium-ion batteries via plasma treatment of electrodes for adhesive interfaces | 044_solvent_free_plasma_processing.json |
| real:P075 | yes | High-energy density ultra-thick drying-free Ni-rich cathode electrodes for application in Lithium-ion batteries | 075_drying_free_ni_rich_cathode.json |
| real:P081 | yes | Comparative thermo-electrochemical study of lignin- and starch-derived carbon electrodes modified with Zn(TFSI)2 and ionic liquids for lithium-ion battery applications | 081_lignin_starch_thermo_electrochemical.json.json |
| real:P086 | yes | Effect of carbon black properties on dry electrode processing of cathodes for lithium-ion batteries | 086_carbon_black_dry_electrode_processing.json |
| real:P096 | yes | Self-healable chitosan-based polymer binder for anode in lithium-ion batteries | 096_chitosan_binder_anode.json |
| real:P099 | yes | A green route based on π-π interactions to coat graphite for high-rate and long-life anodes in lithium-ion batteries | 099_green_graphite_coating.json |
| real:P107 | yes | Natural graphite in making ecofriendly lithium-ion batteries: Challenges, current status, and future outlooks | 107_natural_graphite_ecofriendly.json |
| real:P110 | yes | Poly(hydroxybutyrate-co-hydroxyvalerate) as a biodegradable binder in a negative electrode material for lithium-ion batteries | 110_biodegradable_phbv_binder.json |
| real:P123 | yes | One-step atmospheric microplasma synthesis of an NMC-type lithium-ion battery cathode | 123_ One-step atmospheric microplasma synthesis of an NMC-type lithium-ion.json |

## Claims

| Claim ID | Paper ID | Approach | Metric | Value | Human review |
| --- | --- | --- | --- | --- | --- |
| real:C044_01 | real:P044 | solvent-free processing | adhesion strength | ~2.8 N/cm | yes |
| real:C075_01 | real:P075 | solvent-assisted dry processing | capacity retention | 77.7 % | yes |
| real:C081_01 | real:P081 | biomass-derived carbon modification | activation energy | 15.3 kJ mol^-1 | yes |
| real:C086_01 | real:P086 | solvent-free processing | capacity retention | 94 % | yes |
| real:C096_01 | real:P096 | bio-based self-healing polymer binder | capacity retention | 81 % | yes |
| real:C099_01 | real:P099 | bio-based carbon coating | capacity retention | 89% | yes |
| real:C107_01 | real:P107 | green purification of natural graphite | carbon purity | exceeding 99.99% | yes |
| real:C107_02 | real:P107 | recycled graphite anode material | reversible capacity | 353 mAh/g | yes |
| real:C110_01 | real:P110 | biodegradable biopolymer binder | capacity retention | 99.1 % | yes |
| real:C123_01 | real:P123 | calcination-free/low-energy synthesis | synthesis time | < 1 s | yes |

## Skipped Or Invalid Files

| File | Issue |
| --- | --- |
| 036_electrode_calendering_review.json.json | empty_file |

## Quality Summary

```json
{
  "extracted_paper_count": 9,
  "extracted_claim_count": 10,
  "skipped_or_invalid_file_count": 1,
  "human_review_claim_count": 10,
  "claimless_paper_ids": [],
  "approach_type_counts": {
    "bio-based carbon coating": 1,
    "bio-based self-healing polymer binder": 1,
    "biodegradable biopolymer binder": 1,
    "biomass-derived carbon modification": 1,
    "calcination-free/low-energy synthesis": 1,
    "green purification of natural graphite": 1,
    "recycled graphite anode material": 1,
    "solvent-assisted dry processing": 1,
    "solvent-free processing": 2
  },
  "electrode_component_counts": {
    "anode": 4,
    "cathode": 4,
    "negative electrode (anode)": 1
  },
  "quality_gate": "usable_for_demo_retrieval_and_hypothesis_generation",
  "publication_readiness": "not_publication_ready_without_human_validation"
}
```
