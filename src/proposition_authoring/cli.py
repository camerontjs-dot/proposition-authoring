from __future__ import annotations

import argparse
import json
from pathlib import Path

from .engine import AuthoringEngine
from .model import AuthoringRequest, SourceRepresentation


def load_request(path: Path) -> AuthoringRequest:
    raw = json.loads(path.read_text(encoding="utf-8"))
    return AuthoringRequest(
        handoff_id=raw["handoff_id"],
        producer_id=raw["producer_id"],
        producer_version=raw["producer_version"],
        work_id=raw["work_id"],
        root_id=raw["root_id"],
        root_text=raw["root_text"],
        sources=tuple(SourceRepresentation(**row) for row in raw.get("sources", [])),
        context_source_id=raw.get("context_source_id"),
    )


def main() -> None:
    parser = argparse.ArgumentParser(prog="proposition-authoring")
    sub = parser.add_subparsers(dest="command", required=True)
    author = sub.add_parser("author")
    author.add_argument("request")
    author.add_argument("--receipt", required=True)
    author.add_argument("--contract-a")
    args = parser.parse_args()

    request = load_request(Path(args.request))
    result = AuthoringEngine().author(request)
    Path(args.receipt).write_text(
        json.dumps(result.receipt, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    if args.contract_a and result.contract_a is not None:
        Path(args.contract_a).write_text(
            json.dumps(result.contract_a, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    print(result.state)
    print(result.reason)


if __name__ == "__main__":
    main()
