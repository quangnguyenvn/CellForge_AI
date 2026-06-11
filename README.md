# 🔋 CellForge AI

**🧪 Self-auditing research agent for green lithium-ion battery materials**

CellForge AI turns EV battery literature into evidence-backed research hypotheses, helping R&D teams discover safer, faster, and more durable battery improvement strategies.

Unlike a normal paper-search assistant, CellForge AI audits every generated hypothesis with traces, citations, evidence scores, contradiction checks, and a human-validation gate before drafting a research proposal package.

## 🏆 Hackathon Fit

**Google Cloud Rapid Agent Hackathon**  
**Partner track:** Arize  
**Core model path:** Gemini / Google Cloud for document understanding and research brief generation  
**Observability path:** Arize AX / Phoenix-style OpenInference traces

This project targets a real research workflow: materials researchers need to scan papers, extract experimental claims, find gaps, and propose new directions without losing citation grounding. That matters because the future of energy depends on better materials, and green battery manufacturing is one of the most important material-science challenges for industry and humanity.

## 🤖 What The Agent Does

1. 📄 Ingests real battery papers and Gemini extraction JSON.
2. 🔎 Builds a structured evidence corpus of papers and experimental claims.
3. 📊 Benchmarks retrieval against expected paper/claim hits.
4. 💡 Generates deterministic candidate hypotheses for green electrode materials.
5. 🧪 Audits each hypothesis for citation coverage, grounding, contradictions, feasibility, novelty, and hallucination risk.
6. 📡 Sends trace spans to Arize AX when configured, with local trace mirrors for reproducibility.
7. ✅ Applies a human-validation gate before manuscript drafting.
8. 🧾 Exports a research proposal package, manuscript draft, audit report, and visual evidence.

CellForge AI does **not** claim to automatically write a publishable final paper. It creates a validated proposal/manuscript draft that a human researcher can verify, edit, and extend.

## 🌱 Demo Research Direction

The current demo narrows the scope to:

> Green and sustainable electrode materials/fabrication for lithium-ion batteries.

The top audited hypothesis is:

> **Circular natural-graphite anodes with bio-based conductive surface repair**

Evidence spine:

- ⚡ Non-thermal plasma purification of natural graphite.
- ♻️ Regenerated graphite capacity recovery.
- 🧬 Tannic-acid-derived carbon coating for cycling stability.
- ⚠️ PHBV/chloroform evidence as a contradiction/risk-control example.

## 🧱 Architecture

```text
real PDFs / Gemini Document Understanding JSON
        |
        v
real evidence corpus
        |
        v
retrieval benchmark + claim lookup
        |
        v
hypothesis generator
        |
        v
evidence auditor
        |
        v
Arize AX / Phoenix-compatible tracing
        |
        v
human validation gate
        |
        v
Gemini/local research brief + manuscript draft
```

## 📁 Key Outputs

```text
data/real_evidence_corpus.json
data/real_hypotheses.json
data/real_hypothesis_audits.json
data/validation_queue.json

reports/real_retrieval_benchmark_report.md
reports/real_audit_report.md
reports/human_validation_report.md
reports/gemini_research_brief.md
reports/manuscript_draft.md
reports/figures/molecular_interface_schematic.svg
reports/traces/phoenix_connection_report.md
```

## ▶️ Quick Start

```powershell
python -m unittest discover -s tests
python scripts\run_real_retrieval_benchmark.py
python scripts\generate_real_hypotheses.py
python scripts\run_real_hypothesis_audit.py
python scripts\run_traced_real_pipeline.py
python scripts\build_validation_queue.py
python scripts\apply_demo_validation.py
python scripts\generate_manuscript_draft.py --validated-only
```

Generate the research brief locally:

```powershell
python scripts\generate_gemini_research_brief.py --provider local
```

Generate with Gemini on Google Cloud after ADC is configured:

```powershell
gcloud auth application-default login
gcloud config set project cellforge-ai-demo
python scripts\generate_gemini_research_brief.py --provider gemini
```

## ⚙️ Environment

Copy `.env.example` to `.env`.

```env
CELLFORGE_TRACE_PROVIDER=arize_ax
ARIZE_SPACE_ID=...
ARIZE_API_KEY=...
ARIZE_PROJECT_NAME=cellforge-ai

GOOGLE_CLOUD_PROJECT=cellforge-ai-demo
GOOGLE_CLOUD_LOCATION=global
GOOGLE_GENAI_USE_ENTERPRISE=True
GEMINI_MODEL=gemini-3.1-pro-preview
CELLFORGE_BRIEF_PROVIDER=gemini
```

The app still runs without external keys by using local mock adapters and checked-in demo artifacts.

## 📡 Arize Track Differentiation

CellForge AI uses observability as part of the agent's reasoning loop:

- 🔬 Every major stage is logged as a trace span.
- 🧪 Hypothesis audit outputs become inspectable spans.
- 🧭 The self-introspection stage chooses the best hypothesis from audit scores.
- 📦 Local JSONL trace mirrors keep the demo reproducible even without cloud access.
- 📡 Arize AX traces prove this is an agent workflow, not a single prompt response.

## 🎬 Two-Minute Demo Flow

1. 🔋 Show the problem: green battery materials research is high-impact but evidence-heavy.
2. ▶️ Run `python scripts\run_traced_real_pipeline.py`.
3. 📡 Show Arize AX traces for retrieval, hypothesis generation, evaluator spans, and self-introspection.
4. 🧪 Open `reports/real_audit_report.md` and show H003 selected because of grounding/risk scores.
5. ✅ Open `reports/human_validation_report.md` and explain the validation gate.
6. 🧬 Open `reports/manuscript_draft.md` and `reports/figures/molecular_interface_schematic.svg`.
7. 🌱 Close with: CellForge AI helps researchers move from papers to validated research directions, under human oversight.

## ✅ Test Status

```text
python -m unittest discover -s tests
11 tests passing
```

## 🌍 Broader Vision

The same approach can support other local researcher workflows beyond batteries: solar materials, carbon capture, catalysts, biomedical materials, polymers, semiconductors, and agriculture. The key pattern is general:

> 🔎 retrieve evidence -> 🧬 extract claims -> 💡 generate hypotheses -> 🧪 audit grounding -> ✅ validate -> 🧾 draft a research package.

Battery materials are the first demo because cleaner batteries are central to the future of transportation, renewable energy storage, and sustainable industry.

## 🧑‍⚖️ Final Demo Outputs

For quick judging, the main outputs are checked into the repository:

- 🧾 **Final Gemini Pro preview research report:** [reports/gemini_research_brief.md](reports/gemini_research_brief.md)
- ☁️ **Gemini provider proof:** [reports/gemini_research_brief.json](reports/gemini_research_brief.json)
- ✅ **Human validation report:** [reports/human_validation_report.md](reports/human_validation_report.md)
- 📄 **Manuscript draft after validation gate:** [reports/manuscript_draft.md](reports/manuscript_draft.md)
- 🧪 **Evidence audit report:** [reports/real_audit_report.md](reports/real_audit_report.md)
- 📡 **Arize trace report:** [reports/traces/phoenix_connection_report.md](reports/traces/phoenix_connection_report.md)
- 🧬 **Molecular/interface schematic:** [reports/figures/molecular_interface_schematic.svg](reports/figures/molecular_interface_schematic.svg)
- 🎬 **Subtitled 180-second demo video:** [reports/video_demo/cellforge_ai_demo_subtitled_180s.mp4](reports/video_demo/cellforge_ai_demo_subtitled_180s.mp4)
- 🎙️ **Silent 180-second demo video for Clipchamp voice-over:** [reports/video_demo/cellforge_ai_demo_silent.mp4](reports/video_demo/cellforge_ai_demo_silent.mp4)

The most important file for reviewers to read is:

> [reports/gemini_research_brief.md](reports/gemini_research_brief.md)

That report is generated from audited evidence and should be read together with the validation and audit reports above.
