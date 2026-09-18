from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

from proposition_authoring.engine import AuthoringEngine
from proposition_authoring.model import AuthoringRequest

ROOT = Path(__file__).resolve().parents[1]
GOLD = ROOT / "research" / "claimgate_atomic_comparative_v0" / "gold_cases.json"
OUT = ROOT / "artifacts" / "claimgate-atomic-comparative-v0"


def _request(case: dict[str, Any]) -> AuthoringRequest:
    return AuthoringRequest(
        handoff_id=f"atomic-comparative::{case['case_id']}",
        producer_id="claimgate-atomic-comparative-gold-v0",
        producer_version="v0",
        work_id=case["case_id"],
        root_id=case["case_id"],
        root_text=case["claim"],
        sources=(),
    )


def main() -> None:
    gold = json.loads(GOLD.read_text(encoding="utf-8"))
    OUT.mkdir(parents=True, exist_ok=True)
    engine = AuthoringEngine()
    counts: Counter[str] = Counter()
    rows: list[dict[str, Any]] = []

    for case in gold["cases"]:
        result = engine.author(_request(case))
        state_agrees = result.state == case["expected_state"]
        reason_expected = case.get("expected_reason")
        reason_agrees = reason_expected is None or result.reason == reason_expected
        status = "AGREE" if state_agrees and reason_agrees else "DISAGREE"
        counts[f"{case['class']}:{status}"] += 1
        rows.append(
            {
                "case_id": case["case_id"],
                "class": case["class"],
                "claim": case["claim"],
                "expected_state": case["expected_state"],
                "expected_reason": reason_expected,
                "observed_state": result.state,
                "observed_reason": result.reason,
                "state_agrees": state_agrees,
                "reason_agrees": reason_agrees,
                "status": status,
                "falsifier": case.get("falsifier"),
                "receipt_sha256": result.receipt.get("receipt_sha256"),
                "contract_a_emitted": result.contract_a is not None,
            }
        )

    positive_rows = [row for row in rows if row["class"] == "positive"]
    negative_rows = [row for row in rows if row["class"] == "hard_negative"]
    positive_agree = sum(row["status"] == "AGREE" for row in positive_rows)
    negative_agree = sum(row["status"] == "AGREE" for row in negative_rows)

    if positive_agree == len(positive_rows) and negative_agree == len(negative_rows):
        disposition = "BOUNDED_ATOMIC_COMPARATIVE_GOLD_SATISFIED"
    elif negative_agree < len(negative_rows):
        disposition = "UNSAFE_COMPARATIVE_WIDENING_OR_EXISTING_NEGATIVE_FAILURE"
    else:
        disposition = "ATOMIC_COMPARATIVE_COVERAGE_INCOMPLETE"

    report = {
        "schema": "claimgate-atomic-comparative-evaluation-v0",
        "gold_schema": gold["schema"],
        "case_count": len(rows),
        "counts": dict(sorted(counts.items())),
        "positive_agreement": f"{positive_agree}/{len(positive_rows)}",
        "hard_negative_agreement": f"{negative_agree}/{len(negative_rows)}",
        "disposition": disposition,
        "nonclaims": [
            "workflow success means the evaluator executed, not that comparative coverage passed",
            "gold states do not establish general comparative semantics",
            "no Claim Profile classification is used as authoring authority",
        ],
        "cases": rows,
    }
    (OUT / "REPORT.json").write_text(
        json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False))


if __name__ == "__main__":
    main()
