from __future__ import annotations

import argparse
import json
from collections.abc import Sequence
from pathlib import Path

from proposition_authoring.canonical import canonical_json
from proposition_authoring.gate_v1 import EvidenceTaskV1
from proposition_authoring.gate_v1_rc3 import (
    SourceMetadataV1RC3,
    build_provenance_inputs_v1_rc3,
)
from proposition_authoring.model import AuthoringRequest, SourceRepresentation
from proposition_authoring.production_slice import standardize_gate_production_slice_v1


def _request(raw: dict) -> AuthoringRequest:
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


def _write(path: Path, value: dict) -> None:
    path.write_text(canonical_json(value) + "\n", encoding="utf-8")


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="proposition-authoring-v1")
    parser.add_argument("packet")
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--implementation-identity", default="runtime")
    args = parser.parse_args(argv)

    packet = json.loads(Path(args.packet).read_text(encoding="utf-8"))
    request = _request(packet["request"])
    evidence_task_raw = dict(packet.get("evidence_task", {}))
    if "known_gaps" in evidence_task_raw:
        evidence_task_raw["known_gaps"] = tuple(evidence_task_raw["known_gaps"])
    evidence_task = EvidenceTaskV1(**evidence_task_raw)
    source_metadata = tuple(
        SourceMetadataV1RC3(**row) for row in packet.get("source_metadata", [])
    )

    result = standardize_gate_production_slice_v1(
        request,
        evidence_task=evidence_task,
        source_metadata=source_metadata,
        implementation_identity=args.implementation_identity,
    )
    claim_input, evidence_input = build_provenance_inputs_v1_rc3(
        request,
        evidence_task=evidence_task,
        source_metadata=source_metadata,
    )

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=False)
    _write(out_dir / "CLAIM-GATE-INPUT.json", claim_input)
    _write(out_dir / "EVIDENCE-GATE-INPUT.json", evidence_input)
    _write(out_dir / "CLAIM-GATE.json", result.claim_gate)
    _write(out_dir / "EVIDENCE-GATE.json", result.evidence_gate)
    _write(out_dir / "STANDARDIZATION-RECEIPT.json", result.receipt)
    _write(out_dir / "AUTHORING-RECEIPT.json", result.authoring.receipt)
    if result.authoring.contract_a is not None:
        _write(out_dir / "CONTRACT-A.json", result.authoring.contract_a)

    print(result.authoring.state)
    print(result.claim_gate["output_sha256"])
    print(result.evidence_gate["output_sha256"])
    print(result.receipt["receipt_sha256"])


if __name__ == "__main__":
    main()
