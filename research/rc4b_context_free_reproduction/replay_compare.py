from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw-a", required=True)
    parser.add_argument("--raw-b", required=True)
    parser.add_argument("--provision-a", required=True)
    parser.add_argument("--provision-b", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    raw_a = Path(args.raw_a)
    raw_b = Path(args.raw_b)
    provision_a = Path(args.provision_a)
    provision_b = Path(args.provision_b)

    raw_identical = raw_a.read_bytes() == raw_b.read_bytes()
    provision_identical = provision_a.read_bytes() == provision_b.read_bytes()
    a = json.loads(provision_a.read_text(encoding="utf-8"))
    b = json.loads(provision_b.read_text(encoding="utf-8"))
    tree_match = a["candidate_tree_sha256"] == b["candidate_tree_sha256"]

    report = {
        "schema": "rc4b-replay-receipt-1",
        "raw_byte_identical": raw_identical,
        "provision_receipts_byte_identical": provision_identical,
        "candidate_tree_match": tree_match,
        "raw_a_sha256": digest(raw_a),
        "raw_b_sha256": digest(raw_b),
        "provision_a_sha256": digest(provision_a),
        "provision_b_sha256": digest(provision_b),
        "candidate_tree_sha256": a["candidate_tree_sha256"],
    }
    Path(args.output).write_text(
        json.dumps(report, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    if not (raw_identical and provision_identical and tree_match):
        raise SystemExit("REPRODUCTION_MISMATCH")


if __name__ == "__main__":
    main()
