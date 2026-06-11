# CellForge AI English Video Shot List

Target length: 2-3 minutes.

## Main Report To Demo

Use this as the main research report:

```text
reports/gemini_research_brief.md
```

This is the Gemini Pro preview generated research proposal package. The proof that Gemini Pro preview was used is:

```text
reports/gemini_research_brief.json
```

Look for:

```json
"provider": "gemini"
"model": "gemini-3.1-pro-preview"
"project": "cellforge-ai-demo"
```

Secondary outputs to show:

```text
reports/real_audit_report.md
reports/human_validation_report.md
reports/manuscript_draft.md
reports/figures/molecular_interface_schematic.svg
```

## Scene Plan

### 0:00-0:15 - Project Pitch

Show `README.md`.

Highlight:

- Self-auditing research agent.
- Arize partner track.
- Gemini / Google Cloud path.

### 0:15-0:35 - Run The Agent Pipeline

Show terminal:

```powershell
python scripts\run_traced_real_pipeline.py --run-id cellforge-submit-arize-final-4
```

Highlight:

- `ArizeAXAdapter`
- retrieval metrics
- selected hypothesis `real:H003`

### 0:35-0:58 - Arize AX Observability

Open the Arize URL:

```text
https://app.arize.com/organizations/QWNjb3VudE9yZ2FuaXphdGlvbjo0NDExMTowS2sr/spaces/U3BhY2U6NDY2MDc6Uklrbg==/projects/TW9kZWw6ODMwNDY1Nzc2OTpZZThj?traceViewId=__arize_default&queryFilterA=&timeZoneA=Asia%2FBangkok&selectedTab=llmTracing&startA=1780506000000&endA=1781114399999&envA=tracing&timeRangeKeyA=custom&modelType=generative_llm
```

Show spans for:

- retrieval
- hypothesis generation
- evidence auditor
- self-introspection

### 0:58-1:20 - Evidence Audit

Open:

```text
reports/real_audit_report.md
```

Show:

- `real:H003`
- claim grounding
- hallucination risk
- recommendation: `advance_with_human_review`

### 1:20-1:42 - Human Validation Gate

Open:

```text
reports/human_validation_report.md
```

Show:

- `demo_validated_for_manuscript_generation`
- four validated claims
- warning that this is not final publisher-grade verification

### 1:42-2:05 - Gemini Pro Preview Proof

Open:

```text
reports/gemini_research_brief.json
```

Show:

- provider: `gemini`
- model: `gemini-3.1-pro-preview`
- total token count

Then open:

```text
reports/gemini_research_brief.md
```

### 2:05-2:35 - Final Research Outputs

Open:

```text
reports/figures/molecular_interface_schematic.svg
reports/manuscript_draft.md
```

Say:

"The output is an evidence-backed proposal package, not an automatically publishable final paper."

## Clipchamp Import

- Voice-over script: `docs/video_demo_voiceover_en.txt`
- Subtitles: `docs/video_demo_subtitles_en.srt`
- Voice: English male, medium speed
