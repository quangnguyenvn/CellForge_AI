# Devpost Submission Copy

## Project Name

CellForge AI

## Tagline

Self-auditing Gemini agent that turns green EV battery literature into evidence-backed research hypotheses.

## What It Does

CellForge AI helps battery and materials researchers move from scattered scientific papers to a validated research proposal package. The agent ingests Gemini-extracted paper evidence, retrieves relevant experimental claims, generates candidate hypotheses, audits each hypothesis for grounding and hallucination risk, sends trace spans to Arize AX, applies a human-validation gate, and exports a research brief/manuscript draft.

It does not claim to automatically produce a publishable final paper. It produces an evidence-backed proposal package that a human researcher can validate and develop.

## Why It Matters

Cleaner batteries are central to the future of transportation, renewable energy storage, and sustainable industry. Battery manufacturing can be chemically and energetically harmful, so green electrode materials and low-impact processing are high-value research directions. CellForge AI demonstrates how local researchers could use agentic AI to search, audit, and develop new materials hypotheses across battery research and, later, other scientific domains.

## How It Uses Gemini / Google Cloud

- Gemini Document Understanding was used to extract structured evidence from priority battery PDFs.
- Gemini Pro preview generates the final research brief from audited evidence.
- The pipeline can run locally with mock adapters, then switch to Google Cloud/Gemini when credentials are available.

## How It Uses Arize

- CellForge AI sends OpenInference-style trace spans to Arize AX.
- The trace view shows retrieval, hypothesis generation, evidence evaluation, and self-introspection stages.
- Arize makes the agent inspectable and debuggable, proving this is more than a single RAG prompt.

## Demo Flow

1. Run the traced pipeline.
2. Show Arize AX spans.
3. Show the audit report selecting hypothesis `real:H003`.
4. Show the human-validation report.
5. Show the Gemini research brief and molecular/interface schematic.
6. Show the manuscript draft generated only after the validation gate.

## Commands

```powershell
python -m unittest discover -s tests
python scripts\run_traced_real_pipeline.py
python scripts\apply_demo_validation.py
python scripts\generate_manuscript_draft.py --validated-only
python scripts\generate_gemini_research_brief.py --provider gemini
```

## Track

Arize
