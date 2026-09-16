from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from proposition_authoring.coverage_backend import CoverageBackend
from proposition_authoring.engine import AuthoringEngine
from proposition_authoring.model import AuthoringRequest, SourceRepresentation


def canonical(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )


def request_from(row: dict[str, Any]) -> AuthoringRequest:
    req = row["request"]
    return AuthoringRequest(
        handoff_id=req["handoff_id"],
        producer_id=req["producer_id"],
        producer_version=req["producer_version"],
        work_id=req["work_id"],
        root_id=req["root_id"],
        root_text=req["root_text"],
        sources=tuple(SourceRepresentation(**item) for item in req.get("sources", [])),
        context_source_id=req.get("context_source_id"),
    )


def project(result: Any) -> dict[str, Any]:
    children: list[str] = []
    if result.contract_a is not None and result.state == "DECLARED":
        children = [row["text"] for row in result.contract_a["decomposition"]["children"]]
    return {
        "state": result.state,
        "reason": result.reason,
        "children": children,
        "contract_a": result.contract_a,
        "receipt": result.receipt,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cases", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    rows = [
        json.loads(line)
        for line in args.cases.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    default_engine = AuthoringEngine()
    explicit_engine = AuthoringEngine(CoverageBackend("pooled"))
    if not isinstance(default_engine.backend, CoverageBackend) or default_engine.backend.arm != "pooled":
        raise SystemExit("default runtime is not CoverageBackend('pooled')")

    observations: list[dict[str, Any]] = []
    mismatches: list[dict[str, Any]] = []
    for row in rows:
        request = request_from(row)
        default = project(default_engine.author(request))
        explicit = project(explicit_engine.author(request))
        equal = canonical(default) == canonical(explicit)
        observation = {
            "case_id": row["case_id"],
            "equal": equal,
            "state": default["state"],
            "reason": default["reason"],
            "children": default["children"],
        }
        observations.append(observation)
        if not equal:
            mismatches.append(
                {
                    "case_id": row["case_id"],
                    "default": default,
                    "explicit_pooled": explicit,
                }
            )

    result = {
        "schema": "claimgate-default-pooled-equivalence-v1",
        "case_count": len(rows),
        "all_equal": not mismatches,
        "observations": observations,
        "mismatches": mismatches,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"case_count": len(rows), "all_equal": not mismatches}, sort_keys=True))
    if len(rows) != 44:
        raise SystemExit(f"expected exact 44-case RC4b surface, got {len(rows)}")
    if mismatches:
        raise SystemExit("default runtime diverges from explicit pooled RC4b subject")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
