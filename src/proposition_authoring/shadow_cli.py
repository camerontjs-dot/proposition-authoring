from __future__ import annotations

import argparse
import json
from pathlib import Path

from .capability_service import PairedGatesCapabilityService
from .cli import load_request
from .shadow_models import SourceMetadata, TaskMetadata


def _task(raw: dict | None) -> TaskMetadata:
    raw = raw or {}
    return TaskMetadata(
        domain=raw.get("domain", "unknown"),
        verification_world=raw.get("verification_world", "unknown"),
        temporal_scope=raw.get("temporal_scope", "unknown"),
        jurisdiction=raw.get("jurisdiction", "unknown"),
        corpus_scope=raw.get("corpus_scope", "unknown"),
        completeness_state=raw.get("completeness_state", "unknown"),
        known_gaps=tuple(raw.get("known_gaps", [])),
    )


def _source_metadata(raw: list[dict] | None) -> tuple[SourceMetadata, ...]:
    rows: list[SourceMetadata] = []
    for source in raw or []:
        normalized = dict(source)
        normalized["supersedes"] = tuple(normalized.get("supersedes", []))
        normalized["conflicts_with"] = tuple(normalized.get("conflicts_with", []))
        rows.append(SourceMetadata(**normalized))
    return tuple(rows)


def _write(path: Path, value: dict) -> None:
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser(prog="paired-gates-shadow")
    parser.add_argument("request")
    parser.add_argument("--out", required=True)
    parser.add_argument("--implementation-identity", default="runtime")
    args = parser.parse_args()

    request_path = Path(args.request)
    raw = json.loads(request_path.read_text(encoding="utf-8"))
    shadow = raw.get("shadow", {})
    request = load_request(request_path)
    service = PairedGatesCapabilityService(args.implementation_identity)
    result = service.run(
        request,
        claim_task=_task(shadow.get("claim")),
        evidence_task=_task(shadow.get("evidence_world")),
        source_metadata=_source_metadata(shadow.get("sources")),
    )

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    _write(out / "CLAIMGATE-RECEIPT.json", result.authoring.receipt)
    if result.authoring.contract_a is not None:
        _write(out / "CONTRACT-A.json", result.authoring.contract_a)
    _write(out / "CLAIM-PROFILE.json", result.claim_profile)
    _write(out / "CLAIM-PROFILE-RECEIPT.json", result.claim_profile_receipt)
    _write(out / "EVIDENCE-WORLD-PROFILE.json", result.evidence_world_profile)
    _write(out / "EVIDENCE-WORLD-RECEIPT.json", result.evidence_world_receipt)
    _write(out / "PREFLIGHT-COMPATIBILITY.json", result.compatibility)
    _write(out / "PREFLIGHT-COMPATIBILITY-RECEIPT.json", result.compatibility_receipt)
    _write(out / "FEATURE-REGISTRY.json", result.feature_registry)

    print(result.authoring.state)
    print(result.authoring.reason)


if __name__ == "__main__":
    main()
