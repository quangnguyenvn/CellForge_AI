from __future__ import annotations

import argparse
import json
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List

from services.evals.phoenix_adapter import create_phoenix_adapter, write_trace_summary
from services.evals.real_hypothesis_auditor import run_and_write_real_hypothesis_audit
from services.evals.real_hypothesis_generator import generate_and_write_real_hypotheses
from services.evals.real_retrieval_eval import run_real_retrieval_benchmark, write_real_retrieval_report


ROOT = Path(__file__).resolve().parents[2]
REAL_CORPUS_PATH = ROOT / "data" / "real_evidence_corpus.json"
REAL_HYPOTHESES_PATH = ROOT / "data" / "real_hypotheses.json"
REAL_AUDITS_PATH = ROOT / "data" / "real_hypothesis_audits.json"
PHOENIX_CONNECTION_REPORT_PATH = ROOT / "reports" / "traces" / "phoenix_connection_report.md"


def load_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def timed_stage(fn: Any) -> tuple[Any, int, int]:
    start = int(time.time() * 1000)
    output = fn()
    end = int(time.time() * 1000)
    return output, start, end


def top_audit(audits: List[Dict[str, Any]]) -> Dict[str, Any]:
    return sorted(
        audits,
        key=lambda audit: (
            audit.get("recommendation") == "advance_with_human_review",
            -audit.get("hallucination_risk", 1.0),
            audit.get("claim_grounding", 0.0),
        ),
        reverse=True,
    )[0]


def build_self_improvement_plan(audit_payload: Dict[str, Any]) -> Dict[str, Any]:
    audits = audit_payload["audits"]
    selected = top_audit(audits)
    revise = [audit for audit in audits if audit["recommendation"] != "advance_with_human_review"]
    recurring_flags: Dict[str, int] = {}
    for audit in audits:
        for note in audit.get("unsupported_claims", []):
            recurring_flags[note] = recurring_flags.get(note, 0) + 1
    return {
        "selected_hypothesis_id": selected["hypothesis_id"],
        "recommendation": selected["recommendation"],
        "why_selected": {
            "hallucination_risk": selected["hallucination_risk"],
            "claim_grounding": selected["claim_grounding"],
            "citation_coverage": selected["citation_coverage"],
            "feasibility": selected["feasibility"],
        },
        "blocked_or_revise_count": len(revise),
        "recurring_caution_flags": recurring_flags,
        "next_actions": [
            "Human-validate cited claims before Gemini Pro brief generation.",
            "Digitize chart-derived metrics where audit flags manual review.",
            "Revise experiment design for candidates with feasibility below 0.55.",
            "Use Phoenix trace comparison after prompt/model changes to verify quality does not regress.",
        ],
    }


def write_phoenix_connection_report(summary: Dict[str, Any]) -> None:
    diagnostics = summary.get("phoenix_diagnostics", {})
    lines = [
        "# CellForge AI Arize Trace Report",
        "",
        "This report records the latest traced real-paper pipeline run. It is safe to commit because it does not include API keys.",
        "",
        "## Run",
        "",
        f"- Run ID: `{summary['run_id']}`",
        f"- Adapter: `{summary['adapter']}`",
        f"- Project: `{diagnostics.get('project_name', 'n/a')}`",
        f"- Cloud export enabled: `{diagnostics.get('cloud_export_enabled', False)}`",
        f"- Cloud export status: `{diagnostics.get('cloud_export_status', 'n/a')}`",
        f"- Endpoint inferred from Space ID: `{diagnostics.get('endpoint_inferred_from_space_id', False)}`",
        f"- Endpoint defaulted: `{diagnostics.get('endpoint_defaulted', False)}`",
        f"- Space ID present: `{diagnostics.get('space_id_present', False)}`",
        f"- Local trace mirror: `{summary['trace_file']}`",
        "",
        "## Pipeline Quality Signals",
        "",
        f"- Retrieval paper recall@5: `{summary['retrieval']['paper_recall_at_5']}`",
        f"- Retrieval claim recall@5: `{summary['retrieval']['claim_recall_at_5']}`",
        f"- Audited hypotheses: `{summary['audit']['hypotheses']}`",
        f"- Average claim grounding: `{summary['audit']['avg_claim_grounding']}`",
        f"- Average hallucination risk: `{summary['audit']['avg_hallucination_risk']}`",
        f"- Self-improvement selected hypothesis: `{summary['self_improvement']['selected_hypothesis_id']}`",
        "",
        "## Notes",
        "",
        "- Arize/Phoenix traces are mirrored locally so the demo remains reproducible without external services.",
        "- `attempted_unconfirmed` means the exporter initialized and emitted spans without a local exception, but final receipt must be checked in the Arize/Phoenix UI.",
        "- For Arize AX, set `ARIZE_COLLECTOR_ENDPOINT` only if the UI/docs give a workspace-specific OTLP endpoint; otherwise the adapter uses the default Phoenix/Arize OTLP endpoint.",
        "- If cloud traces do not appear, verify `PHOENIX_COLLECTOR_ENDPOINT` in `.env`. For Phoenix Cloud it should usually look like `https://app.phoenix.arize.com/s/<space-name>` or a full `/v1/traces` endpoint.",
        "- Keep `ARIZE_API_KEY` and `PHOENIX_API_KEY` out of chat, screenshots, git history, and reports.",
    ]
    error = diagnostics.get("cloud_export_error")
    if error:
        lines.extend(["", "## Export Error", "", f"`{error}`"])
    PHOENIX_CONNECTION_REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    PHOENIX_CONNECTION_REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_traced_real_pipeline(run_id: str | None = None) -> Dict[str, Any]:
    run_id = run_id or f"cellforge-real-{uuid.uuid4().hex[:8]}"
    adapter = create_phoenix_adapter()
    corpus = load_json(REAL_CORPUS_PATH)

    adapter.log_agent_trace(
        run_id=run_id,
        stage="real_evidence_corpus_loaded",
        input={"path": str(REAL_CORPUS_PATH.relative_to(ROOT))},
        output=corpus.get("quality_summary", {}),
        metadata={
            "span_kind": "CHAIN",
            "status": "OK",
            "paper_count": len(corpus.get("papers", [])),
            "claim_count": len(corpus.get("claims", [])),
            "mock_mode_reason": getattr(adapter, "mock_mode_reason", ""),
        },
    )

    retrieval_report, start, end = timed_stage(run_real_retrieval_benchmark)
    write_real_retrieval_report(retrieval_report)
    adapter.log_agent_trace(
        run_id=run_id,
        stage="literature_retrieval_agent.real_benchmark",
        input={"corpus": "data/real_evidence_corpus.json", "benchmark": "data/evals/real_retrieval_benchmark.jsonl"},
        output=retrieval_report["summary"],
        metadata={
            "span_kind": "RETRIEVER",
            "openinference_span_kind": "RETRIEVER",
            "start_time_ms": start,
            "end_time_ms": end,
            "status": "OK",
            "case_count": retrieval_report["summary"]["cases"],
        },
    )

    hypothesis_result, start, end = timed_stage(generate_and_write_real_hypotheses)
    hypotheses_payload = load_json(REAL_HYPOTHESES_PATH)
    adapter.log_agent_trace(
        run_id=run_id,
        stage="hypothesis_generator_agent.deterministic",
        input={"source_corpus": "data/real_evidence_corpus.json"},
        output={
            "summary": hypothesis_result,
            "hypothesis_ids": [hypothesis["id"] for hypothesis in hypotheses_payload["hypotheses"]],
        },
        metadata={
            "span_kind": "CHAIN",
            "start_time_ms": start,
            "end_time_ms": end,
            "status": "OK",
            "generation_mode": hypotheses_payload["generation_mode"],
        },
    )

    audit_result, start, end = timed_stage(run_and_write_real_hypothesis_audit)
    audit_payload = load_json(REAL_AUDITS_PATH)
    adapter.log_agent_trace(
        run_id=run_id,
        stage="evidence_auditor_agent.real_hypotheses",
        input={
            "hypotheses": "data/real_hypotheses.json",
            "claims": "data/real_evidence_corpus.json",
        },
        output=audit_payload["summary"],
        metadata={
            "span_kind": "EVALUATOR",
            "openinference_span_kind": "EVALUATOR",
            "start_time_ms": start,
            "end_time_ms": end,
            "status": "OK",
            "audit_result": audit_result,
        },
    )

    claim_list = corpus["claims"]
    hypothesis_by_id = {hypothesis["id"]: hypothesis for hypothesis in hypotheses_payload["hypotheses"]}
    for audit in audit_payload["audits"]:
        hypothesis = {**hypothesis_by_id[audit["hypothesis_id"]], "audit": audit}
        evals = {
            "citation_coverage": adapter.evaluate_citation_coverage(hypothesis, claim_list),
            "claim_grounding": adapter.evaluate_claim_grounding(hypothesis, claim_list),
            "hallucination_risk": adapter.evaluate_hallucination_risk(hypothesis, claim_list),
        }
        adapter.log_agent_trace(
            run_id=run_id,
            stage=f"evidence_auditor_agent.eval.{audit['hypothesis_id']}",
            input={"hypothesis_id": audit["hypothesis_id"], "supporting_claim_ids": audit["supporting_claim_ids"]},
            output={**evals, "recommendation": audit["recommendation"]},
            metadata={
                "span_kind": "EVALUATOR",
                "openinference_span_kind": "EVALUATOR",
                "status": "OK",
                "hypothesis_id": audit["hypothesis_id"],
            },
        )

    improvement_plan = build_self_improvement_plan(audit_payload)
    adapter.log_agent_trace(
        run_id=run_id,
        stage="self_introspection_agent.trace_based_improvement_plan",
        input={"audit_summary": audit_payload["summary"]},
        output=improvement_plan,
        metadata={
            "span_kind": "CHAIN",
            "status": "OK",
            "uses_observability_data": True,
        },
    )

    compare = adapter.compare_runs([run_id])
    adapter.flush()
    phoenix_diagnostics = {}
    if hasattr(adapter, "diagnostics"):
        phoenix_diagnostics = adapter.diagnostics()
    summary = {
        "run_id": run_id,
        "adapter": adapter.__class__.__name__,
        "mock_mode_reason": getattr(adapter, "mock_mode_reason", ""),
        "phoenix_diagnostics": phoenix_diagnostics,
        "trace_file": "reports/traces/cellforge_phoenix_mock_traces.jsonl",
        "retrieval": retrieval_report["summary"],
        "audit": audit_payload["summary"],
        "self_improvement": improvement_plan,
        "compare_runs": compare,
    }
    write_trace_summary(summary)
    write_phoenix_connection_report(summary)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Run CellForge real-paper pipeline with Phoenix-compatible mock tracing.")
    parser.add_argument("--run-id", default=None, help="Optional stable run id for trace comparison.")
    args = parser.parse_args()
    print(json.dumps(run_traced_real_pipeline(run_id=args.run_id), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
