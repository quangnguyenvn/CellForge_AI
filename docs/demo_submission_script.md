# CellForge AI Demo Script

Target length: about 2 minutes.

## 0:00-0:15 - Problem

"Battery materials research is moving fast, but researchers still spend huge time reading papers, extracting experimental claims, and checking whether a new research idea is actually grounded. CellForge AI is a self-auditing research agent for green lithium-ion battery materials."

## 0:15-0:35 - Agent Workflow

Show terminal:

```powershell
python scripts\run_traced_real_pipeline.py
```

"This is not a chatbot. The agent loads a real evidence corpus, retrieves relevant claims, generates candidate hypotheses, audits them, and creates a self-introspection recommendation."

## 0:35-0:55 - Arize AX

Show Arize AX tracing project.

"For the Arize track, every agent stage is traceable: retrieval, hypothesis generation, evaluator spans, and the self-introspection span that chooses the safest hypothesis. This makes the agent inspectable and improvable."

## 0:55-1:15 - Audit Result

Open:

```text
reports/real_audit_report.md
```

"The best hypothesis is H003: circular natural-graphite anodes with bio-based conductive surface repair. It wins because it has strong citation coverage, better grounding, and lower hallucination risk than the alternatives."

## 1:15-1:35 - Human Validation Gate

Open:

```text
reports/human_validation_report.md
```

"Before drafting, CellForge applies a validation gate. For the demo, four claims are validated from Gemini Document Understanding artifacts and internal consistency checks. For a real paper, this gate would require final PDF and publisher verification."

## 1:35-1:55 - Output

Open:

```text
reports/manuscript_draft.md
reports/figures/molecular_interface_schematic.svg
```

"The output is not an automatically publishable final paper. It is an evidence-backed research proposal package and manuscript draft that a human researcher can validate and develop."

## 1:55-2:05 - Close

"The same pattern can support many research domains: retrieve evidence, extract claims, generate hypotheses, audit grounding, validate, and draft. We start with green battery materials because cleaner batteries are foundational to the future of energy and industry."

## Commands If Re-Recording

```powershell
python -m unittest discover -s tests
python scripts\run_traced_real_pipeline.py
python scripts\apply_demo_validation.py
python scripts\generate_manuscript_draft.py --validated-only
python scripts\generate_gemini_research_brief.py --provider local
```

Use Gemini Pro instead of local only when you want to spend Google Cloud credit:

```powershell
python scripts\generate_gemini_research_brief.py --provider gemini
```
