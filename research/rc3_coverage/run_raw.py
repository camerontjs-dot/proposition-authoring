from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from proposition_authoring.coverage_backend import CoverageBackend
from proposition_authoring.engine import AuthoringEngine
from proposition_authoring.model import AuthoringRequest

ARMS = ("baseline", "p4", "p5", "pooled")


def canon(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def make_request(row: dict[str, Any]) -> AuthoringRequest:
    item = row["request"]
    return AuthoringRequest(
        handoff_id=item["handoff_id"],
        producer_id=item["producer_id"],
        producer_version=item["producer_version"],
        work_id=item["work_id"],
        root_id=item["root_id"],
        root_text=item["root_text"],
    )


def project(result) -> dict[str, Any]:
    children: list[str] = []
    if result.contract_a is not None and result.state == "DECLARED":
        children = [child["text"] for child in result.contract_a["decomposition"]["children"]]
    return {
        "state": result.state,
        "reason": result.reason,
        "children": children,
        "contract_a": result.contract_a,
    }


def first_proposal_control(root: dict[str, Any], backend: CoverageBackend) -> dict[str, Any]:
    proposals = backend.proposals(root)
    for proposer in sorted(proposals):
        for candidate in sorted(proposals[proposer], key=lambda item: item["case_id"]):
            return {
                "state": "DECLARED",
                "proposer": proposer,
                "children": [child["text"] for child in candidate["children"]],
            }
    return {"state": "ABSTAINED", "proposer": None, "children": []}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cases", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    rows = [json.loads(line) for line in Path(args.cases).read_text(encoding="utf-8").splitlines() if line.strip()]
    backends = {arm: CoverageBackend(arm) for arm in ARMS}
    engines = {arm: AuthoringEngine(backends[arm]) for arm in ARMS}
    output: list[dict[str, Any]] = []
    for row in rows:
        req = make_request(row)
        root = {"root_id": req.root_id, "root_text": req.root_text, "context_text": "", "family": "rc3-fresh"}
        arms = {arm: project(engines[arm].author(req)) for arm in ARMS}
        output.append({
            "case_id": row["case_id"],
            "arms": arms,
            "weak_controls": {"first_pooled_proposal": first_proposal_control(root, backends["pooled"])},
        })
    raw = "".join(canon(row) + "\n" for row in output)
    Path(args.output).write_text(raw, encoding="utf-8")
    print(hashlib.sha256(raw.encode("utf-8")).hexdigest())


if __name__ == "__main__":
    main()
