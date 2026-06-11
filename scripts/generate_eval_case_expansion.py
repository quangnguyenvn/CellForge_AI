from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, List


ROOT = Path(__file__).resolve().parents[1]
RETRIEVAL_PATH = ROOT / "data" / "evals" / "retrieval_benchmark.jsonl"
AUDITOR_PATH = ROOT / "data" / "evals" / "evidence_auditor_eval_set.jsonl"
TARGET_CASES = 200
SEED_CASES = 30


RETRIEVAL_VARIANTS = [
    "{query}",
    "battery research evidence: {query}",
    "EV cell experiment {query}",
    "{query} limitation evidence",
    "{query} experimental condition",
    "{query} metric value",
    "find paper about {query}",
    "claim extraction target {query}",
    "{query} citation grounding",
    "{query} contradiction or tradeoff",
]


AUDITOR_GOAL_VARIANTS = [
    "{goal}",
    "{goal} with explicit citation grounding",
    "{goal} while checking contradiction coverage",
    "{goal} for local evidence-auditor regression testing",
    "{goal} with hallucination-risk review",
    "{goal} and experimental-condition validation",
    "{goal} while avoiding chemistry-transfer overclaims",
    "{goal} using CellForge audit rubric",
    "{goal} with paper-ready proposal caution",
    "{goal} with limitation-aware scoring",
]


def load_jsonl(path: Path) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            stripped = line.strip()
            if stripped:
                rows.append(json.loads(stripped))
    return rows


def write_jsonl(path: Path, rows: List[Dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, separators=(",", ":"), ensure_ascii=False))
            handle.write("\n")


def expand_retrieval_cases(seed_cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    expanded: List[Dict[str, Any]] = []
    for index in range(TARGET_CASES):
        seed = deepcopy(seed_cases[index % len(seed_cases)])
        variant = RETRIEVAL_VARIANTS[index // len(seed_cases) % len(RETRIEVAL_VARIANTS)]
        seed["case_id"] = f"ret_{index + 1:03d}"
        seed["query"] = variant.format(query=seed["query"])
        seed["notes"] = f"{seed.get('notes', '')} Generated expansion variant {index // len(seed_cases) + 1}."
        expanded.append(seed)
    return expanded


def expand_auditor_cases(seed_cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    expanded: List[Dict[str, Any]] = []
    for index in range(TARGET_CASES):
        seed = deepcopy(seed_cases[index % len(seed_cases)])
        variant = AUDITOR_GOAL_VARIANTS[index // len(seed_cases) % len(AUDITOR_GOAL_VARIANTS)]
        seed["case_id"] = f"audit_{index + 1:03d}"
        seed["goal"] = variant.format(goal=seed["goal"])
        seed["hypothesis"]["id"] = f"hyp:eval{index + 1:03d}"
        seed["notes"] = f"{seed.get('notes', '')} Generated expansion variant {index // len(seed_cases) + 1}."
        expanded.append(seed)
    return expanded


def main() -> None:
    retrieval_seed = load_jsonl(RETRIEVAL_PATH)[:SEED_CASES]
    auditor_seed = load_jsonl(AUDITOR_PATH)[:SEED_CASES]

    if len(retrieval_seed) < SEED_CASES:
        raise RuntimeError(f"Expected at least {SEED_CASES} retrieval seed cases.")
    if len(auditor_seed) < SEED_CASES:
        raise RuntimeError(f"Expected at least {SEED_CASES} auditor seed cases.")

    retrieval_cases = expand_retrieval_cases(retrieval_seed)
    auditor_cases = expand_auditor_cases(auditor_seed)
    write_jsonl(RETRIEVAL_PATH, retrieval_cases)
    write_jsonl(AUDITOR_PATH, auditor_cases)
    print(f"Wrote {len(retrieval_cases)} retrieval cases to {RETRIEVAL_PATH}")
    print(f"Wrote {len(auditor_cases)} auditor cases to {AUDITOR_PATH}")


if __name__ == "__main__":
    main()

