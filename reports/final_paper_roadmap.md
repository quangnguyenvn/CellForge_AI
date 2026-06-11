# CellForge AI Final Paper Roadmap

Goal: turn the current Gemini research proposal package into a human-validated manuscript draft without claiming unsupported results.

## Readiness Gates

1. **Evidence validation:** complete `reports/validation_checklist.md` for all critical/high claims.
2. **Reference validation:** add authors, venue, year, and DOI only after checking source PDFs or publisher pages.
3. **Manuscript drafting:** generate a draft using only queue items marked `allowed_in_manuscript=true`.
4. **Figure validation:** keep generated schematic figures as conceptual diagrams; use paper figures only with rights/permissions and verified captions.
5. **Experimental boundary:** label all untested mechanisms as proposed hypotheses, not results.

## Lead Manuscript Story

- Lead hypothesis: `real:H003` circular natural-graphite anodes with bio-based conductive surface repair.
- Evidence spine: non-thermal plasma purification, regenerated graphite capacity recovery, tannic-acid carbon coating stability, and PHBV/chloroform as a processing-risk counterexample.
- Critical/high validation items tied to lead: `4`.

## Manuscript Structure

1. Title
2. Abstract
3. Introduction: green electrode-material bottleneck
4. Methods: CellForge evidence extraction, retrieval benchmark, hypothesis audit, and human validation gate
5. Evidence synthesis: circular graphite anode route
6. Research gap and hypothesis
7. Proposed experiment matrix
8. Sustainability and risk controls
9. Limitations
10. Conclusion
11. References

## Next Command After Manual Validation

```powershell
python scripts\generate_manuscript_draft.py --validated-only
```

The command is implemented with a hard gate: it writes a readiness report instead of a draft until at least one evidence item is marked `validation_status=validated` or `corrected` and `allowed_in_manuscript=true`.
