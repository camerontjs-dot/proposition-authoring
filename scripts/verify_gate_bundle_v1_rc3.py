from __future__ import annotations

import argparse
import json
from pathlib import Path

from proposition_authoring.gate_v1_rc3 import verify_standardized_gate_bundle_v1_rc3


def _load(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser(prog="verify-gate-v1-rc3-bundle")
    parser.add_argument("--claim-gate", required=True)
    parser.add_argument("--evidence-gate", required=True)
    parser.add_argument("--receipt", required=True)
    parser.add_argument("--contract-a")
    args = parser.parse_args()

    result = verify_standardized_gate_bundle_v1_rc3(
        _load(args.claim_gate),
        _load(args.evidence_gate),
        _load(args.receipt),
        contract_a=_load(args.contract_a) if args.contract_a else None,
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
