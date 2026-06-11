# CellForge AI Evaluation Report

Generated at: `2026-06-09T17:06:17.473761+00:00`

This report summarizes the local reliability benchmark for CellForge AI. It is designed to show whether the system retrieves the right battery evidence and whether generated hypotheses are grounded, contradiction-aware, and low-risk enough to recommend for human review.

## Executive Summary

- Mode: `local_mock_eval`
- Adapter: `local_mock`
- Overall status: `pass`
- Retrieval cases: `200`
- Evidence auditor cases: `200`
- Retrieval failed cases: `0`
- Auditor failed cases: `0`

## Retrieval Benchmark

| Metric | Value |
| --- | ---: |
| Paper recall@5 | 100.0% |
| Claim recall@10 | 100.0% |
| Paper MRR | 0.919 |
| Claim MRR | 1.000 |
| Hard negative rate@5 | 12.5% |

## Evidence Auditor Eval

| Metric | Value |
| --- | ---: |
| Cases | 200 |
| Passed | 200 |
| Failed | 0 |
| Pass rate | 100.0% |

## Failure Analysis

No failed cases in the current local benchmark.

If a future retrieval adapter, embedding model, Phoenix evaluator, or auditor agent regresses, failed cases will appear here with expected and actual values.

## Baseline Comparison

- Baseline path: `reports\eval_baseline.json`
- Baseline generated at: `2026-06-09T17:05:39.508429+00:00`

### Retrieval Delta

| Metric | Current | Baseline | Delta |
| --- | ---: | ---: | ---: |
| paper_recall_at_5 | 1.0 | 1.0 | 0.0 |
| claim_recall_at_10 | 1.0 | 1.0 | 0.0 |
| paper_mrr | 0.919 | 0.919 | 0.0 |
| claim_mrr | 1.0 | 1.0 | 0.0 |
| hard_negative_rate_at_5 | 0.125 | 0.125 | 0.0 |

### Auditor Delta

| Metric | Current | Baseline | Delta |
| --- | ---: | ---: | ---: |
| pass_rate | 1.0 | 1.0 | 0.0 |
| failed | 0 | 0 | 0 |

## Demo Interpretation

CellForge AI is not just generating research hypotheses. This benchmark checks whether retrieval finds the right evidence, whether hard negatives are controlled, and whether hypotheses are audited for citation coverage, claim grounding, contradiction coverage, and hallucination risk.

## Commands

```powershell
python scripts\generate_eval_report.py
python scripts\generate_eval_report.py --baseline reports\eval_baseline.json
python scripts\update_eval_baseline.py
python -m services.evals.local_eval all
python -m services.evals.local_eval all --adapter local_mock
python -m unittest discover -s tests
```
