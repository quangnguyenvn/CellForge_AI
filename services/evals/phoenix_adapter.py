from __future__ import annotations

import json
import os
import sys
import time
import uuid
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Protocol


ROOT = Path(__file__).resolve().parents[2]
TRACE_DIR = ROOT / "reports" / "traces"
TRACE_JSONL_PATH = TRACE_DIR / "cellforge_phoenix_mock_traces.jsonl"
TRACE_SUMMARY_PATH = TRACE_DIR / "cellforge_phoenix_mock_summary.json"
ENV_PATH = ROOT / ".env"
LOCAL_DEPS_PATH = ROOT / ".python-deps"


class PhoenixAdapter(Protocol):
    def log_agent_trace(self, run_id: str, stage: str, input: Any, output: Any, metadata: Dict[str, Any]) -> Dict[str, Any]:
        ...

    def evaluate_citation_coverage(self, hypothesis: Dict[str, Any], claims: List[Dict[str, Any]]) -> Dict[str, Any]:
        ...

    def evaluate_claim_grounding(self, hypothesis: Dict[str, Any], claims: List[Dict[str, Any]]) -> Dict[str, Any]:
        ...

    def evaluate_hallucination_risk(self, hypothesis: Dict[str, Any], claims: List[Dict[str, Any]]) -> Dict[str, Any]:
        ...

    def compare_runs(self, run_ids: Iterable[str]) -> Dict[str, Any]:
        ...

    def flush(self) -> None:
        ...


def now_ms() -> int:
    return int(time.time() * 1000)


def load_env_file(path: Path = ENV_PATH) -> None:
    if not path.exists():
        return
    parsed: Dict[str, str] = {}
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            stripped = line.strip()
            if not stripped or stripped.startswith("#") or "=" not in stripped:
                continue
            key, value = stripped.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key:
                parsed[key] = value
    for key, value in parsed.items():
        if key not in os.environ:
            os.environ[key] = value


def compact(value: Any, max_chars: int = 6000) -> Any:
    text = json.dumps(value, ensure_ascii=False, default=str)
    if len(text) <= max_chars:
        return value
    return {"truncated": True, "preview": text[:max_chars], "original_chars": len(text)}


def add_local_dependency_path() -> None:
    deps = str(LOCAL_DEPS_PATH)
    if LOCAL_DEPS_PATH.exists() and deps not in sys.path:
        sys.path.insert(0, deps)


def json_text(value: Any, max_chars: int = 6000) -> str:
    return json.dumps(compact(value, max_chars=max_chars), ensure_ascii=False, default=str)


def otel_value(value: Any) -> Any:
    if isinstance(value, (str, bool, int, float)) or value is None:
        return value
    if isinstance(value, list) and all(isinstance(item, (str, bool, int, float)) for item in value):
        return value
    return json.dumps(value, ensure_ascii=False, default=str)


def resolve_phoenix_endpoint() -> tuple[Optional[str], bool]:
    configured = os.getenv("PHOENIX_COLLECTOR_ENDPOINT") or os.getenv("PHOENIX_ENDPOINT")
    if configured:
        return configured, False
    space_id = os.getenv("PHOENIX_SPACE_ID")
    if not space_id:
        return "https://app.phoenix.arize.com/v1/traces", True
    return f"https://app.phoenix.arize.com/s/{space_id}/v1/traces", True


def resolve_arize_ax_endpoint() -> tuple[str, bool]:
    configured = os.getenv("ARIZE_COLLECTOR_ENDPOINT") or os.getenv("ARIZE_ENDPOINT")
    if configured:
        return configured, False
    return "https://otlp.arize.com/v1", True


class MockPhoenixAdapter:
    """Local Phoenix-compatible trace adapter used when Phoenix Cloud is not configured."""

    def __init__(self, trace_path: Path = TRACE_JSONL_PATH) -> None:
        self.trace_path = trace_path
        self.trace_path.parent.mkdir(parents=True, exist_ok=True)
        self.mock_mode_reason = "Phoenix credentials/config missing; writing OpenInference-style local JSONL traces."

    def log_agent_trace(self, run_id: str, stage: str, input: Any, output: Any, metadata: Dict[str, Any]) -> Dict[str, Any]:
        span = {
            "trace_id": run_id,
            "span_id": str(uuid.uuid4()),
            "parent_span_id": metadata.get("parent_span_id"),
            "name": stage,
            "span_kind": metadata.get("span_kind", "CHAIN"),
            "start_time_ms": metadata.get("start_time_ms", now_ms()),
            "end_time_ms": metadata.get("end_time_ms", now_ms()),
            "status": metadata.get("status", "OK"),
            "input": compact(input),
            "output": compact(output),
            "attributes": {
                "cellforge.run_id": run_id,
                "cellforge.stage": stage,
                "cellforge.mock_phoenix": True,
                "openinference.span.kind": metadata.get("openinference_span_kind", metadata.get("span_kind", "CHAIN")),
                **{key: value for key, value in metadata.items() if key not in {"parent_span_id", "start_time_ms", "end_time_ms"}},
            },
        }
        with self.trace_path.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(span, ensure_ascii=False) + "\n")
        return span

    def evaluate_citation_coverage(self, hypothesis: Dict[str, Any], claims: List[Dict[str, Any]]) -> Dict[str, Any]:
        cited = [claim_id for claim_id in hypothesis.get("supporting_claim_ids", []) if any(claim["id"] == claim_id for claim in claims)]
        score = min(len(cited) / 3, 1.0)
        return {
            "label": "citation_coverage",
            "score": round(score, 3),
            "explanation": f"{len(cited)} supporting claim citations resolved against the real evidence corpus.",
        }

    def evaluate_claim_grounding(self, hypothesis: Dict[str, Any], claims: List[Dict[str, Any]]) -> Dict[str, Any]:
        audit_scores = hypothesis.get("audit", {})
        score = audit_scores.get("claim_grounding", 0.0)
        return {
            "label": "claim_grounding",
            "score": score,
            "explanation": "Uses local deterministic auditor score derived from lexical, metric, and chemistry overlap.",
        }

    def evaluate_hallucination_risk(self, hypothesis: Dict[str, Any], claims: List[Dict[str, Any]]) -> Dict[str, Any]:
        audit_scores = hypothesis.get("audit", {})
        risk = audit_scores.get("hallucination_risk", 1.0)
        return {
            "label": "hallucination_risk",
            "score": risk,
            "explanation": "Lower is better. Includes citation, grounding, contradiction coverage, feasibility, and human-review pressure.",
        }

    def compare_runs(self, run_ids: Iterable[str]) -> Dict[str, Any]:
        run_id_set = set(run_ids)
        spans = self._read_spans()
        selected = [span for span in spans if span.get("trace_id") in run_id_set]
        by_run: Dict[str, Dict[str, Any]] = {}
        for span in selected:
            run = by_run.setdefault(span["trace_id"], {"span_count": 0, "stages": [], "final_recommendations": []})
            run["span_count"] += 1
            run["stages"].append(span["name"])
            output = span.get("output", {})
            if isinstance(output, dict) and "recommendation" in output:
                run["final_recommendations"].append(output["recommendation"])
        return {"runs": by_run, "compared_run_ids": sorted(run_id_set)}

    def flush(self) -> None:
        return None

    def _read_spans(self) -> List[Dict[str, Any]]:
        if not self.trace_path.exists():
            return []
        spans: List[Dict[str, Any]] = []
        with self.trace_path.open("r", encoding="utf-8") as handle:
            for line in handle:
                stripped = line.strip()
                if stripped:
                    spans.append(json.loads(stripped))
        return spans


class PhoenixCloudPlaceholderAdapter(MockPhoenixAdapter):
    """Placeholder until OpenInference/Phoenix dependencies are installed and configured."""

    def __init__(self, trace_path: Path = TRACE_JSONL_PATH) -> None:
        super().__init__(trace_path=trace_path)
        self.mock_mode_reason = (
            "Phoenix environment variables were detected, but cloud export is not installed in this MVP. "
            "Local traces preserve the same adapter contract."
        )


class CloudTraceAdapter(MockPhoenixAdapter):
    """Shared OpenTelemetry exporter with a local JSONL mirror."""

    trace_backend = "cloud"
    delivery_confirmation = "Check the tracing UI; OTLP exporters do not provide span-query confirmation."

    def _init_cloud_exporter(
        self,
        *,
        endpoint: str,
        project_name: str,
        api_key: Optional[str],
        headers: Optional[Dict[str, str]],
        mock_mode_reason: str,
        init_failure_reason: str,
    ) -> None:
        add_local_dependency_path()
        self.project_name = project_name
        self.endpoint = endpoint
        self.cloud_export_enabled = False
        self.cloud_export_error: Optional[str] = None
        self.mock_mode_reason = mock_mode_reason
        self._tracer_provider: Any = None
        self._tracer: Any = None
        self._span_attributes: Any = None
        try:
            from phoenix.otel import SpanAttributes, register

            self._span_attributes = SpanAttributes
            self._tracer_provider = register(
                endpoint=self.endpoint,
                project_name=self.project_name,
                batch=True,
                set_global_tracer_provider=False,
                protocol="http/protobuf",
                verbose=False,
                auto_instrument=False,
                api_key=api_key,
                headers=headers,
            )
            self._tracer = self._tracer_provider.get_tracer("cellforge-ai.real_pipeline")
            self.cloud_export_enabled = True
        except Exception as exc:  # pragma: no cover - defensive cloud fallback
            self.cloud_export_error = f"{exc.__class__.__name__}: {exc}"
            self.mock_mode_reason = init_failure_reason

    def log_agent_trace(self, run_id: str, stage: str, input: Any, output: Any, metadata: Dict[str, Any]) -> Dict[str, Any]:
        span = super().log_agent_trace(run_id=run_id, stage=stage, input=input, output=output, metadata=metadata)
        if not self.cloud_export_enabled:
            return span
        try:
            self._export_cloud_span(span)
        except Exception as exc:  # pragma: no cover - defensive cloud fallback
            self.cloud_export_error = f"{exc.__class__.__name__}: {exc}"
            self.cloud_export_enabled = False
            self.mock_mode_reason = f"{self.trace_backend} export failed during span write; subsequent spans are mirrored locally only."
        return span

    def _extra_cloud_attributes(self) -> Dict[str, Any]:
        return {}

    def _export_cloud_span(self, span: Dict[str, Any]) -> None:
        attributes = {
            **span.get("attributes", {}),
            "cellforge.project": "CellForge AI",
            "cellforge.trace_backend": self.trace_backend,
            **self._extra_cloud_attributes(),
        }
        with self._tracer.start_as_current_span(span["name"]) as cloud_span:
            cloud_span.set_attribute("openinference.span.kind", span.get("span_kind", "CHAIN"))
            for key, value in attributes.items():
                cloud_span.set_attribute(key, otel_value(value))
            cloud_span.set_attribute(self._span_attributes.INPUT_VALUE, json_text(span.get("input")))
            cloud_span.set_attribute(self._span_attributes.INPUT_MIME_TYPE, "application/json")
            cloud_span.set_attribute(self._span_attributes.OUTPUT_VALUE, json_text(span.get("output")))
            cloud_span.set_attribute(self._span_attributes.OUTPUT_MIME_TYPE, "application/json")
            if span.get("status") and span["status"] != "OK":
                from opentelemetry.trace import Status, StatusCode

                cloud_span.set_status(Status(StatusCode.ERROR, span["status"]))

    def flush(self) -> None:
        if not self.cloud_export_enabled or self._tracer_provider is None:
            return None
        try:
            self._tracer_provider.force_flush(timeout_millis=5000)
        except Exception as exc:  # pragma: no cover - defensive cloud fallback
            self.cloud_export_error = f"{exc.__class__.__name__}: {exc}"

    def diagnostics(self) -> Dict[str, Any]:
        cloud_export_status = "attempted_unconfirmed" if self.cloud_export_enabled else "local_only"
        if self.cloud_export_error:
            cloud_export_status = "local_only_after_export_error"
        return {
            "project_name": self.project_name,
            "endpoint": self.endpoint,
            "cloud_export_enabled": self.cloud_export_enabled,
            "cloud_export_status": cloud_export_status,
            "cloud_delivery_confirmation": self.delivery_confirmation,
            "cloud_export_error": self.cloud_export_error,
            "local_trace_path": str(self.trace_path.relative_to(ROOT)),
        }


class PhoenixCloudAdapter(CloudTraceAdapter):
    """Phoenix Cloud exporter with a local JSONL mirror for reproducible demos."""

    trace_backend = "phoenix_cloud"
    delivery_confirmation = "Check the Phoenix/Arize UI; OTLP exporters do not provide span-query confirmation."

    def __init__(self, trace_path: Path = TRACE_JSONL_PATH) -> None:
        super().__init__(trace_path=trace_path)
        self.endpoint, self.endpoint_inferred_from_space_id = resolve_phoenix_endpoint()
        self._init_cloud_exporter(
            endpoint=self.endpoint or "https://app.phoenix.arize.com/v1/traces",
            project_name=os.getenv("PHOENIX_PROJECT_NAME", "cellforge-ai"),
            api_key=os.getenv("PHOENIX_API_KEY"),
            headers=None,
            mock_mode_reason="Phoenix Cloud export enabled; local JSONL mirror also written.",
            init_failure_reason=(
                "Phoenix Cloud configuration was detected, but exporter initialization failed; "
                "local JSONL traces are still available."
            ),
        )

    def _extra_cloud_attributes(self) -> Dict[str, Any]:
        return {"cellforge.endpoint_inferred_from_space_id": self.endpoint_inferred_from_space_id}

    def diagnostics(self) -> Dict[str, Any]:
        diagnostics = super().diagnostics()
        diagnostics["endpoint_inferred_from_space_id"] = self.endpoint_inferred_from_space_id
        return diagnostics


class ArizeAXAdapter(CloudTraceAdapter):
    """Arize AX trace exporter using OpenTelemetry/Phoenix-compatible OpenInference spans."""

    trace_backend = "arize_ax"
    delivery_confirmation = "Check the Arize AX UI; OTLP exporters do not provide span-query confirmation."

    def __init__(self, trace_path: Path = TRACE_JSONL_PATH) -> None:
        super().__init__(trace_path=trace_path)
        add_local_dependency_path()
        self.project_name = os.getenv("ARIZE_PROJECT_NAME", os.getenv("PHOENIX_PROJECT_NAME", "cellforge-ai"))
        self.space_id = os.getenv("ARIZE_SPACE_ID", "")
        api_key = os.getenv("ARIZE_API_KEY")
        self.endpoint, self.endpoint_defaulted = resolve_arize_ax_endpoint()
        self.cloud_export_enabled = False
        self.cloud_export_error: Optional[str] = None
        self.mock_mode_reason = "Arize AX export enabled; local JSONL mirror also written."
        self._tracer_provider: Any = None
        self._tracer: Any = None
        self._span_attributes: Any = None
        try:
            from arize.otel import Transport, register
            from phoenix.otel import SpanAttributes

            self._span_attributes = SpanAttributes
            self._tracer_provider = register(
                space_id=self.space_id,
                api_key=api_key or "",
                project_name=self.project_name,
                endpoint=self.endpoint,
                transport=Transport.GRPC,
                batch=True,
                set_global_tracer_provider=False,
                verbose=False,
                auto_instrument=False,
            )
            self._tracer = self._tracer_provider.get_tracer("cellforge-ai.real_pipeline")
            self.cloud_export_enabled = True
        except Exception as exc:  # pragma: no cover - defensive cloud fallback
            self.cloud_export_error = f"{exc.__class__.__name__}: {exc}"
            self.mock_mode_reason = (
                "Arize AX configuration was detected, but exporter initialization failed; "
                "local JSONL traces are still available."
            )

    def _extra_cloud_attributes(self) -> Dict[str, Any]:
        return {
            "cellforge.arize_space_id_present": bool(self.space_id),
            "cellforge.endpoint_defaulted": self.endpoint_defaulted,
        }

    def diagnostics(self) -> Dict[str, Any]:
        diagnostics = super().diagnostics()
        diagnostics["endpoint_defaulted"] = self.endpoint_defaulted
        diagnostics["space_id_present"] = bool(self.space_id)
        return diagnostics


def create_phoenix_adapter() -> PhoenixAdapter:
    load_env_file()
    trace_provider = os.getenv("CELLFORGE_TRACE_PROVIDER", "").lower()
    has_arize_ax_config = bool(os.getenv("ARIZE_API_KEY") and os.getenv("ARIZE_SPACE_ID"))
    has_cloud_config = bool(
        os.getenv("PHOENIX_API_KEY")
        and (
            os.getenv("PHOENIX_SPACE_ID")
            or os.getenv("PHOENIX_COLLECTOR_ENDPOINT")
            or os.getenv("PHOENIX_ENDPOINT")
        )
    )
    if trace_provider == "mock":
        return MockPhoenixAdapter()
    if trace_provider == "arize_ax" and has_arize_ax_config:
        return ArizeAXAdapter()
    if has_cloud_config:
        return PhoenixCloudAdapter()
    if has_arize_ax_config:
        return ArizeAXAdapter()
    return MockPhoenixAdapter()


def write_trace_summary(summary: Dict[str, Any], path: Path = TRACE_SUMMARY_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(summary, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
