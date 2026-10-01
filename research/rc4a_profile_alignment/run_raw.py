from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

from proposition_authoring.coverage_backend import CoverageBackend
from proposition_authoring.coverage_proposers import (
    proposer_p5,
    proposer_p5_prealignment_control,
)
from proposition_authoring.engine import AuthoringEngine
from proposition_authoring.model import AuthoringRequest


def canon(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )


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
        children = [
            child["text"] for child in result.contract_a["decomposition"]["children"]
        ]
    return {
        "state": result.state,
        "reason": result.reason,
        "children": children,
        "contract_a": result.contract_a,
    }


def proposal_projection(proposals: list[dict[str, Any]]) -> list[list[str]]:
    return [
        [child["text"] for child in candidate["children"]]
        for candidate in proposals
    ]


def authority_probe(root: dict[str, Any], backend: CoverageBackend) -> dict[str, Any]:
    """Measurement-only candidate construction, never fed to the authoring engine."""
    text = " ".join(root["root_text"].strip().rstrip(".").split())
    match = re.fullmatch(
        r"(?P<matrix>.+?\s+reported)\s+that\s+(?P<body>.+)",
        text,
        re.IGNORECASE,
    )
    if not match:
        return {"available": False, "disposition": None, "children": []}
    body = match.group("body")
    if body.lower().count(" and ") != 1:
        return {"available": False, "disposition": None, "children": []}
    left, right = (
        part.strip()
        for part in re.split(r"\s+and\s+", body, maxsplit=1, flags=re.IGNORECASE)
    )
    matrix = match.group("matrix")
    children = [f"{matrix} that {left}.", f"{matrix} that {right}."]
    candidate = {
        "case_id": f"{root['root_id']}::authority-probe",
        "root_id": root["root_id"],
        "root_text": root["root_text"],
        "context_text": root.get("context_text", ""),
        "profile_id": "pc-evaluator-rc1-binding-v1",
        "candidate_state": "DECLARED",
        "operator": "all_of",
        "children": [
            {"child_id": f"{root['root_id']}::probe::c1", "text": children[0]},
            {"child_id": f"{root['root_id']}::probe::c2", "text": children[1]},
        ],
    }
    evaluation = backend.evaluate(candidate)
    return {
        "available": True,
        "disposition": evaluation["disposition"],
        "children": children,
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
    p5_backend = CoverageBackend("p5")
    pooled_backend = CoverageBackend("pooled")
    p5_engine = AuthoringEngine(p5_backend)
    pooled_engine = AuthoringEngine(pooled_backend)

    output: list[dict[str, Any]] = []
    for row in rows:
        req = make_request(row)
        root = {
            "root_id": req.root_id,
            "root_text": req.root_text,
            "context_text": "",
            "family": "rc4a-fresh",
        }
        aligned = proposer_p5(root)
        weak = proposer_p5_prealignment_control(root)
        output.append(
            {
                "case_id": row["case_id"],
                "aligned_p5_proposals": proposal_projection(aligned),
                "weak_prealignment_p5_proposals": proposal_projection(weak),
                "authority_probe": authority_probe(root, p5_backend),
                "p5_result": project(p5_engine.author(req)),
                "pooled_result": project(pooled_engine.author(req)),
            }
        )

    raw = "".join(canon(row) + "\n" for row in output)
    Path(args.output).write_text(raw, encoding="utf-8")
    print(hashlib.sha256(raw.encode("utf-8")).hexdigest())


if __name__ == "__main__":
    main()
