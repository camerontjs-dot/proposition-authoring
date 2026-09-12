from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from proposition_authoring.backend import FrozenPredecessorBackend
from proposition_authoring.engine import AuthoringEngine
from proposition_authoring.model import AuthoringRequest, SourceRepresentation

from controls import CONTROLS


def canon(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )


def request_from_row(row: dict[str, Any]) -> AuthoringRequest:
    raw = row["request"]
    return AuthoringRequest(
        handoff_id=raw["handoff_id"],
        producer_id=raw["producer_id"],
        producer_version=raw["producer_version"],
        work_id=raw["work_id"],
        root_id=raw["root_id"],
        root_text=raw["root_text"],
        sources=tuple(SourceRepresentation(**source) for source in raw.get("sources", [])),
        context_source_id=raw.get("context_source_id"),
    )


def declared_children(contract_a: dict[str, Any] | None) -> list[str]:
    if contract_a is None:
        return []
    decomposition = contract_a.get("decomposition", {})
    if decomposition.get("state") != "declared":
        return []
    return [child["text"] for child in decomposition["children"]]


def run_case(
    row: dict[str, Any],
    engine: AuthoringEngine,
    backend: FrozenPredecessorBackend,
) -> dict[str, Any]:
    request = request_from_row(row)
    target = engine.author(request)
    controls = {
        name: fn(request, backend)
        for name, fn in CONTROLS.items()
    }
    return {
        "case_id": row["case_id"],
        "target": {
            "state": target.state,
            "reason": target.reason,
            "children": declared_children(target.contract_a),
            "contract_a": target.contract_a,
            "receipt": target.receipt,
        },
        "controls": controls,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cases", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    rows = [
        json.loads(line)
        for line in Path(args.cases).read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    backend = FrozenPredecessorBackend()
    engine = AuthoringEngine(backend)
    output_rows = [run_case(row, engine, backend) for row in rows]
    raw = "".join(canon(row) + "\n" for row in output_rows)
    Path(args.output).write_text(raw, encoding="utf-8")
    print(hashlib.sha256(raw.encode("utf-8")).hexdigest())


if __name__ == "__main__":
    main()
