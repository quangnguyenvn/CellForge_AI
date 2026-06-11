from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from services.evals.local_eval import ROOT, run_auditor_eval, run_retrieval_benchmark


REPORTS_DIR = ROOT / "reports"
REPORT_JSON_PATH = REPORTS_DIR / "eval_report.json"
REPORT_MD_PATH = REPORTS_DIR / "eval_report.md"
BASELINE_JSON_PATH = REPORTS_DIR / "eval_baseline.json"


RETRIEVAL_METRICS = [
    "paper_recall_at_5",
    "claim_recall_at_10",
    "paper_mrr",
    "claim_mrr",
    "hard_negative_rate_at_5",
]
AUDITOR_METRICS = ["pass_rate", "failed"]


def failed_cases(report: Dict[str, Any]) -> List[Dict[str, Any]]:
    return [item for item in report["results"] if not item.get("passed", True)]


def load_baseline(path: Optional[Path]) -> Optional[Dict[str, Any]]:
    if path is None or not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def metric_delta(current: Dict[str, Any], baseline: Dict[str, Any], section: str, metric: str) -> Dict[str, Any]:
    current_value = current[section]["summary"].get(metric)
    baseline_value = baseline[section]["summary"].get(metric)
    if isinstance(current_value, (int, float)) and isinstance(baseline_value, (int, float)):
        delta = round(current_value - baseline_value, 4)
    else:
        delta = None
    return {"metric": metric, "current": current_value, "baseline": baseline_value, "delta": delta}


def build_comparison(current: Dict[str, Any], baseline: Optional[Dict[str, Any]], baseline_path: Optional[Path]) -> Dict[str, Any]:
    if baseline is None:
        return {"enabled": False, "baseline_path": str(baseline_path) if baseline_path else None, "retrieval": [], "auditor": []}

    retrieval = [metric_delta(current, baseline, "retrieval", metric) for metric in RETRIEVAL_METRICS]
    auditor = [metric_delta(current, baseline, "auditor", metric) for metric in AUDITOR_METRICS]
    return {
        "enabled": True,
        "baseline_path": str(baseline_path) if baseline_path else None,
        "baseline_generated_at": baseline.get("generated_at"),
        "retrieval": retrieval,
        "auditor": auditor,
    }


def build_eval_report(adapter: str = "local_mock", baseline_path: Optional[Path] = None) -> Dict[str, Any]:
    retrieval = run_retrieval_benchmark(adapter=adapter)
    auditor = run_auditor_eval(adapter=adapter)
    retrieval_failures = failed_cases(retrieval)
    auditor_failures = failed_cases(auditor)
    generated_at = datetime.now(timezone.utc).isoformat()

    report = {
        "generated_at": generated_at,
        "mode": f"{adapter}_eval",
        "adapter": adapter,
        "summary": {
            "retrieval_cases": retrieval["summary"]["cases"],
            "auditor_cases": auditor["summary"]["cases"],
            "retrieval_failed_cases": len(retrieval_failures),
            "auditor_failed_cases": len(auditor_failures),
            "overall_status": "pass" if not retrieval_failures and not auditor_failures else "review",
        },
        "retrieval": retrieval,
        "auditor": auditor,
        "failure_analysis": {
            "retrieval": retrieval_failures,
            "auditor": auditor_failures,
        },
    }
    report["comparison"] = build_comparison(report, load_baseline(baseline_path), baseline_path)
    return report


def pct(value: float) -> str:
    return f"{value * 100:.1f}%"


def render_markdown_report(report: Dict[str, Any]) -> str:
    retrieval_summary = report["retrieval"]["summary"]
    auditor_summary = report["auditor"]["summary"]
    retrieval_failures = report["failure_analysis"]["retrieval"]
    auditor_failures = report["failure_analysis"]["auditor"]

    lines = [
        "# CellForge AI Evaluation Report",
        "",
        f"Generated at: `{report['generated_at']}`",
        "",
        "This report summarizes the local reliability benchmark for CellForge AI. It is designed to show whether the system retrieves the right battery evidence and whether generated hypotheses are grounded, contradiction-aware, and low-risk enough to recommend for human review.",
        "",
        "## Executive Summary",
        "",
        f"- Mode: `{report['mode']}`",
        f"- Adapter: `{report['adapter']}`",
        f"- Overall status: `{report['summary']['overall_status']}`",
        f"- Retrieval cases: `{report['summary']['retrieval_cases']}`",
        f"- Evidence auditor cases: `{report['summary']['auditor_cases']}`",
        f"- Retrieval failed cases: `{report['summary']['retrieval_failed_cases']}`",
        f"- Auditor failed cases: `{report['summary']['auditor_failed_cases']}`",
        "",
        "## Retrieval Benchmark",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
        f"| Paper recall@5 | {pct(retrieval_summary['paper_recall_at_5'])} |",
        f"| Claim recall@10 | {pct(retrieval_summary['claim_recall_at_10'])} |",
        f"| Paper MRR | {retrieval_summary['paper_mrr']:.3f} |",
        f"| Claim MRR | {retrieval_summary['claim_mrr']:.3f} |",
        f"| Hard negative rate@5 | {pct(retrieval_summary['hard_negative_rate_at_5'])} |",
        "",
        "## Evidence Auditor Eval",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
        f"| Cases | {auditor_summary['cases']} |",
        f"| Passed | {auditor_summary['passed']} |",
        f"| Failed | {auditor_summary['failed']} |",
        f"| Pass rate | {pct(auditor_summary['pass_rate'])} |",
        "",
        "## Failure Analysis",
        "",
    ]

    if not retrieval_failures and not auditor_failures:
        lines.extend(
            [
                "No failed cases in the current local benchmark.",
                "",
                "If a future retrieval adapter, embedding model, Phoenix evaluator, or auditor agent regresses, failed cases will appear here with expected and actual values.",
                "",
            ]
        )
    else:
        if retrieval_failures:
            lines.extend(["### Retrieval Failures", ""])
            for item in retrieval_failures[:20]:
                lines.extend(
                    [
                        f"- `{item['case_id']}`",
                        f"  - retrieved papers: `{item.get('retrieved_paper_ids', [])}`",
                        f"  - retrieved claims: `{item.get('retrieved_claim_ids', [])}`",
                    ]
                )
            lines.append("")
        if auditor_failures:
            lines.extend(["### Auditor Failures", ""])
            for item in auditor_failures[:20]:
                failed_checks = [name for name, passed in item.get("checks", {}).items() if not passed]
                lines.extend(
                    [
                        f"- `{item['case_id']}`",
                        f"  - failed checks: `{failed_checks}`",
                        f"  - expected: `{item.get('expected', {})}`",
                        f"  - actual audit: `{item.get('audit', {})}`",
                    ]
                )
            lines.append("")

    comparison = report.get("comparison", {})
    lines.extend(["## Baseline Comparison", ""])
    if not comparison.get("enabled"):
        lines.extend(
            [
                "No baseline comparison was provided for this report.",
                "",
                "Create or refresh a baseline with:",
                "",
                "```powershell",
                "python scripts\\update_eval_baseline.py",
                "python scripts\\generate_eval_report.py --baseline reports\\eval_baseline.json",
                "```",
                "",
            ]
        )
    else:
        lines.extend(
            [
                f"- Baseline path: `{comparison.get('baseline_path')}`",
                f"- Baseline generated at: `{comparison.get('baseline_generated_at')}`",
                "",
                "### Retrieval Delta",
                "",
                "| Metric | Current | Baseline | Delta |",
                "| --- | ---: | ---: | ---: |",
            ]
        )
        for item in comparison["retrieval"]:
            lines.append(f"| {item['metric']} | {item['current']} | {item['baseline']} | {item['delta']} |")
        lines.extend(["", "### Auditor Delta", "", "| Metric | Current | Baseline | Delta |", "| --- | ---: | ---: | ---: |"])
        for item in comparison["auditor"]:
            lines.append(f"| {item['metric']} | {item['current']} | {item['baseline']} | {item['delta']} |")
        lines.append("")

    lines.extend(
        [
            "## Demo Interpretation",
            "",
            "CellForge AI is not just generating research hypotheses. This benchmark checks whether retrieval finds the right evidence, whether hard negatives are controlled, and whether hypotheses are audited for citation coverage, claim grounding, contradiction coverage, and hallucination risk.",
            "",
            "## Commands",
            "",
            "```powershell",
            "python scripts\\generate_eval_report.py",
            "python scripts\\generate_eval_report.py --baseline reports\\eval_baseline.json",
            "python scripts\\update_eval_baseline.py",
            "python -m services.evals.local_eval all",
            "python -m services.evals.local_eval all --adapter local_mock",
            "python -m unittest discover -s tests",
            "```",
            "",
        ]
    )
    return "\n".join(lines)


def write_eval_report(
    adapter: str = "local_mock",
    baseline_path: Optional[Path] = None,
    report_json_path: Path = REPORT_JSON_PATH,
    report_md_path: Path = REPORT_MD_PATH,
) -> Dict[str, Path]:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    report = build_eval_report(adapter=adapter, baseline_path=baseline_path)
    report_json_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    report_md_path.write_text(render_markdown_report(report), encoding="utf-8")
    return {"json": report_json_path, "markdown": report_md_path}


def update_baseline(source_path: Path = REPORT_JSON_PATH, baseline_path: Path = BASELINE_JSON_PATH) -> Path:
    if not source_path.exists():
        write_eval_report(report_json_path=source_path, report_md_path=REPORT_MD_PATH)
    baseline_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source_path, baseline_path)
    return baseline_path


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Generate CellForge AI evaluation report artifacts.")
    parser.add_argument("--adapter", default="local_mock", choices=["local_mock", "pipeline"], help="Eval adapter to use.")
    parser.add_argument("--baseline", type=Path, default=None, help="Optional baseline JSON report to compare against.")
    args = parser.parse_args()

    paths = write_eval_report(adapter=args.adapter, baseline_path=args.baseline)
    print(f"Wrote JSON report: {paths['json']}")
    print(f"Wrote Markdown report: {paths['markdown']}")


if __name__ == "__main__":
    main()
