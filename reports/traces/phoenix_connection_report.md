# CellForge AI Arize Trace Report

This report records the latest traced real-paper pipeline run. It is safe to commit because it does not include API keys.

## Run

- Run ID: `cellforge-submit-arize-final-4`
- Adapter: `ArizeAXAdapter`
- Project: `cellforge-ai`
- Cloud export enabled: `True`
- Cloud export status: `attempted_unconfirmed`
- Endpoint inferred from Space ID: `False`
- Endpoint defaulted: `True`
- Space ID present: `True`
- Local trace mirror: `reports/traces/cellforge_phoenix_mock_traces.jsonl`

## Pipeline Quality Signals

- Retrieval paper recall@5: `1.0`
- Retrieval claim recall@5: `1.0`
- Audited hypotheses: `5`
- Average claim grounding: `0.65`
- Average hallucination risk: `0.45`
- Self-improvement selected hypothesis: `real:H003`

## Notes

- Arize/Phoenix traces are mirrored locally so the demo remains reproducible without external services.
- `attempted_unconfirmed` means the exporter initialized and emitted spans without a local exception, but final receipt must be checked in the Arize/Phoenix UI.
- For Arize AX, set `ARIZE_COLLECTOR_ENDPOINT` only if the UI/docs give a workspace-specific OTLP endpoint; otherwise the adapter uses the default Phoenix/Arize OTLP endpoint.
- If cloud traces do not appear, verify `PHOENIX_COLLECTOR_ENDPOINT` in `.env`. For Phoenix Cloud it should usually look like `https://app.phoenix.arize.com/s/<space-name>` or a full `/v1/traces` endpoint.
- Keep `ARIZE_API_KEY` and `PHOENIX_API_KEY` out of chat, screenshots, git history, and reports.
