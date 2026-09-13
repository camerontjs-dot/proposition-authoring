from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from controls import CONTROLS
from proposition_authoring.authority import evaluate_candidate
from proposition_authoring.backend import FrozenPredecessorBackend
from proposition_authoring.contract_a import emit_declared
from proposition_authoring.model import AuthoringRequest


def canon(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def contract_projection(candidate: dict[str, Any]) -> dict[str, Any]:
    request = AuthoringRequest(
        handoff_id=f"rc2::{candidate['case_id']}",
        producer_id="proposition-authoring",
        producer_version="rc2-research",
        work_id=f"rc2::{candidate['case_id']}",
        root_id=candidate["root_id"],
        root_text=candidate["root_text"],
    )
    return emit_declared(
        request,
        decomposition_id=f"rc2::{candidate['case_id']}",
        child_texts=[row["text"] for row in candidate["children"]],
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cases", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    rows = [json.loads(line) for line in Path(args.cases).read_text(encoding="utf-8").splitlines() if line.strip()]
    backend = FrozenPredecessorBackend()
    output = []
    for row in rows:
        candidate = row["candidate"]
        target = evaluate_candidate(candidate, backend).as_dict()
        target["contract_a"] = contract_projection(candidate) if target["disposition"] == "ALLOW" else None
        controls = {name: fn(candidate, backend) for name, fn in CONTROLS.items()}
        output.append({"case_id": row["case_id"], "target": target, "controls": controls})
    raw = "".join(canon(row) + "\n" for row in output)
    Path(args.output).write_text(raw, encoding="utf-8")
    print(hashlib.sha256(raw.encode()).hexdigest())


if __name__ == "__main__":
    main()
