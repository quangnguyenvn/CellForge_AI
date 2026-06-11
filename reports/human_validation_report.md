# CellForge AI Demo Human Validation Report

Status: `demo_validated_for_manuscript_generation`

This report unlocks the demo manuscript path using claims validated from Gemini Document Understanding extraction artifacts and CellForge internal consistency checks. It is intentionally labeled as demo validation, not final publisher-grade literature verification.

## Validated For Demo Manuscript

### val:001 | real:C099_01 | critical

- **Source:** `real:P099` A green route based on pi-pi interactions to coat graphite for high-rate and long-life anodes in lithium-ion batteries
- **Metric:** capacity retention = `89%`
- **Role:** `supporting`
- **Method:** `demo_source_extraction_validation`
- **Scope note:** Validated for demo manuscript from Gemini Document Understanding extraction and internal consistency checks. Requires final human PDF/publisher verification before real publication.
- **Demo validation notes:** Lead support claim for tannic-acid-derived graphite coating; value, condition, limitation, and source section are internally consistent across the extraction artifact.

### val:002 | real:C107_01 | critical

- **Source:** `real:P107` Natural graphite in making ecofriendly lithium-ion batteries: Challenges, current status, and future outlooks
- **Metric:** carbon purity = `exceeding 99.99%`
- **Role:** `supporting`
- **Method:** `demo_source_extraction_validation`
- **Scope note:** Validated for demo manuscript as review-derived evidence. Primary-source validation is required before a real manuscript submission.
- **Demo validation notes:** Lead support claim for non-thermal plasma purification; retained with explicit review-derived caveat.

### val:003 | real:C107_02 | critical

- **Source:** `real:P107` Natural graphite in making ecofriendly lithium-ion batteries: Challenges, current status, and future outlooks
- **Metric:** reversible capacity = `353 mAh/g`
- **Role:** `supporting`
- **Method:** `demo_source_extraction_validation`
- **Scope note:** Validated for demo manuscript as review-derived regenerated-graphite evidence. Primary-source validation is required before a real manuscript submission.
- **Demo validation notes:** Lead support claim for regenerated graphite capacity recovery; retained with explicit review-derived caveat.

### val:004 | real:C110_01 | high

- **Source:** `real:P110` Poly(hydroxybutyrate-co-hydroxyvalerate) as a biodegradable binder in a negative electrode material for lithium-ion batteries
- **Metric:** capacity retention = `99.1 %`
- **Role:** `contradicting, supporting`
- **Method:** `demo_source_extraction_validation`
- **Scope note:** Validated for demo manuscript as contradiction/risk-control evidence from Gemini Document Understanding extraction.
- **Demo validation notes:** Used as a cautionary counterexample: biodegradable binder performance can hide solvent and adhesion trade-offs.

## Still Pending Before Real Publication

- `val:005` `real:C075_01` (high): capacity retention = `77.7 %`
- `val:006` `real:C044_01` (medium): adhesion strength = `~2.8 N/cm`
- `val:007` `real:C081_01` (medium): activation energy = `15.3 kJ mol^-1`
- `val:008` `real:C086_01` (medium): capacity retention = `94 %`
- `val:009` `real:C096_01` (medium): capacity retention = `81 %`
- `val:010` `real:C123_01` (medium): synthesis time = `< 1 s`

## Submission-Safe Positioning

- The demo can show a complete agent loop: retrieve evidence, generate hypotheses, audit them, validate selected evidence, and draft a proposal.
- The project should still say it creates an evidence-backed research proposal/manuscript draft, not an automatically publishable final paper.
- Final journal submission would require full PDF verification, complete references, and ideally experimental validation.
