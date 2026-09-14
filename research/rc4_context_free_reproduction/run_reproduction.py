from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path


def canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate-dir", required=True)
    parser.add_argument("--cases", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    candidate = Path(args.candidate_dir)
    sys.path.insert(0, str(candidate / "src"))

    from proposition_authoring.coverage_backend import CoverageBackend  # noqa: PLC0415
    from proposition_authoring.engine import AuthoringEngine  # noqa: PLC0415
    from proposition_authoring.model import (  # noqa: PLC0415
        AuthoringRequest,
        SourceRepresentation,
    )

    engine = AuthoringEngine(CoverageBackend("pooled", vendor_dir=candidate / "vendor" / "frozen"))
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)

    with Path(args.cases).open(encoding="utf-8") as src, output.open("w", encoding="utf-8", newline="\n") as dst:
        for line in src:
            if not line.strip():
                continue
            row = json.loads(line)
            req = row["request"]
            sources = tuple(
                SourceRepresentation(
                    source_id=item["source_id"],
                    media_type=item["media_type"],
                    content=item["content"],
                )
                for item in req.get("sources", [])
            )
            request = AuthoringRequest(
                handoff_id=req["handoff_id"],
                producer_id=req["producer_id"],
                producer_version=req["producer_version"],
                work_id=req["work_id"],
                root_id=req["root_id"],
                root_text=req["root_text"],
                sources=sources,
                context_source_id=req.get("context_source_id"),
            )
            result = engine.author(request)
            children: list[str] = []
            if result.contract_a is not None and result.state == "DECLARED":
                children = [item["text"] for item in result.contract_a["decomposition"]["children"]]
            out = {
                "case_id": row["case_id"],
                "state": result.state,
                "reason": result.reason,
                "children": children,
                "contract_a": result.contract_a,
                "receipt": result.receipt,
                "receipt_sha256": hashlib.sha256(canonical(result.receipt).encode("utf-8")).hexdigest(),
            }
            dst.write(canonical(out) + "\n")


if __name__ == "__main__":
    main()
