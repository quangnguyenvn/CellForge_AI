# Real Hypothesis Evidence Audit

This report audits deterministic hypotheses against Gemini-extracted real-paper claims. It does not certify publication readiness.

## Summary

- Hypotheses audited: `5`
- Advance with human review: `1`
- Revise experiment design: `3`
- Revise before brief: `1`
- Average hallucination risk: `0.45`
- Average claim grounding: `0.65`

## Audit Matrix

| Hypothesis | Citation | Grounding | Contradiction | Evidence | Novelty | Feasibility | Risk | Recommendation |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| real:H001 | 1.000 | 0.626 | 0.500 | 0.950 | 0.880 | 0.455 | 0.447 | revise_experiment_design |
| real:H002 | 0.667 | 0.507 | 0.500 | 0.870 | 0.840 | 0.665 | 0.529 | revise_before_brief |
| real:H003 | 1.000 | 0.725 | 0.500 | 0.900 | 0.920 | 0.595 | 0.413 | advance_with_human_review |
| real:H004 | 1.000 | 0.726 | 0.500 | 0.950 | 0.920 | 0.490 | 0.420 | revise_experiment_design |
| real:H005 | 1.000 | 0.664 | 0.500 | 0.950 | 0.880 | 0.420 | 0.443 | revise_experiment_design |

## Notes

### real:H001

Unsupported or caution flags:
- All cited real-paper claims are extraction artifacts requiring human validation.
- Hypothesis uses directional performance language that must remain proposal-level until experimentally validated.

Contradiction/limitation notes:
- real:C123_01 (real:P123): Low discharge capacity (125 mAh/g) and contamination from electrode sputtering

### real:H002

Unsupported or caution flags:
- All cited real-paper claims are extraction artifacts requiring human validation.

Contradiction/limitation notes:
- real:C081_01 (real:P081): The efficacy is heavily dependent on the biopolymer precursor chemistry, as starch-derived carbons did not exhibit comparable kinetic improvements.

### real:H003

Unsupported or caution flags:
- All cited real-paper claims are extraction artifacts requiring human validation.
- Hypothesis uses directional performance language that must remain proposal-level until experimentally validated.

Contradiction/limitation notes:
- real:C110_01 (real:P110): The processing required chloroform (CHCl3) solvent, and the polymer has lower adhesion to copper than PVDF.

### real:H004

Unsupported or caution flags:
- All cited real-paper claims are extraction artifacts requiring human validation.
- Hypothesis uses directional performance language that must remain proposal-level until experimentally validated.

Contradiction/limitation notes:
- real:C044_01 (real:P044): The processing current was limited to 3-4 mA, and the setup operates under vacuum conditions.

### real:H005

Unsupported or caution flags:
- All cited real-paper claims are extraction artifacts requiring human validation.
- Hypothesis uses directional performance language that must remain proposal-level until experimentally validated.

Contradiction/limitation notes:
- real:C075_01 (real:P075): High tortuosity still limits performance at high discharge rates.
