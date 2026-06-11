# CellForge AI Video Shot List

Target length: 2-3 minutes.

## Recording Setup

- Use Windows screen recording or Clipchamp screen recorder.
- Browser zoom: 90% or 100%.
- Hide `.env`, API keys, terminal history with tokens.
- Keep Arize tab open at:
  `https://app.arize.com/organizations/QWNjb3VudE9yZ2FuaXphdGlvbjo0NDExMTowS2sr/spaces/U3BhY2U6NDY2MDc6Uklrbg==/projects/TW9kZWw6ODMwNDY1Nzc2OTpZZThj?traceViewId=__arize_default&queryFilterA=&timeZoneA=Asia%2FBangkok&selectedTab=llmTracing&startA=1780506000000&endA=1781114399999&envA=tracing&timeRangeKeyA=custom&modelType=generative_llm`

## Scene Plan

### 0:00-0:15 - README Pitch

Show `README.md`.

Highlight:

- "Self-auditing research agent"
- Partner track: Arize
- Gemini / Google Cloud

### 0:15-0:35 - Terminal Pipeline

Show terminal in repo root.

Command to display or run:

```powershell
python scripts\run_traced_real_pipeline.py --run-id cellforge-submit-arize-final-4
```

Focus on:

- `ArizeAXAdapter`
- retrieval recall
- selected hypothesis `real:H003`

### 0:35-0:58 - Arize AX Traces

Show Arize project page.

Point to spans:

- retrieval
- hypothesis generator
- evaluator spans
- self-introspection

Narration point:

"Arize makes every decision inspectable."

### 0:58-1:20 - Audit Report

Open:

```text
reports/real_audit_report.md
```

Show:

- `real:H003`
- hallucination risk
- claim grounding
- recommendation: `advance_with_human_review`

### 1:20-1:42 - Human Validation Gate

Open:

```text
reports/human_validation_report.md
```

Show:

- `demo_validated_for_manuscript_generation`
- four validated claims
- "not final publisher-grade literature verification"

### 1:42-2:05 - Gemini Pro Preview Evidence

Open:

```text
reports/gemini_research_brief.json
```

Show:

- provider: `gemini`
- model: `gemini-3.1-pro-preview`
- project: `cellforge-ai-demo`
- total token count

Then show:

```text
reports/gemini_research_brief.md
```

### 2:05-2:28 - Visual + Draft Output

Open:

```text
reports/figures/molecular_interface_schematic.svg
reports/manuscript_draft.md
```

Emphasize:

- molecular/interface schematic
- manuscript draft only after validation gate

### 2:28-2:45 - Close

Return to README or Devpost summary.

Closing line:

"CellForge AI helps researchers move from papers to validated research directions, under human oversight."

## Clipchamp Tips

- Add the voice-over from `docs/video_demo_voiceover_vi.txt`.
- Add subtitles from `docs/video_demo_subtitles.srt`.
- Use 1.1x speed only if the final video exceeds 3 minutes.
- Crop terminal/browser to avoid showing personal browser tabs if needed.
