from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from proposition_authoring.model import AuthoringRequest, SourceRepresentation
from proposition_authoring.preflight import PairedPreflightResult, run_paired_preflight
from proposition_authoring.shadow_models import SourceMetadata, TaskMetadata

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "integration" / "claimgate_v1_candidate" / "fixtures"
OUT = ROOT / "artifacts" / "paired-gates-shadow-batch"


def _request_from_raw(raw: dict[str, Any]) -> AuthoringRequest:
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


def _load_fixture(name: str) -> AuthoringRequest:
    raw = json.loads((FIXTURES / name).read_text(encoding="utf-8"))
    return _request_from_raw(raw)


def _serialize_result(result: PairedPreflightResult) -> dict[str, Any]:
    return {
        "authoring": {
            "state": result.authoring.state,
            "reason": result.authoring.reason,
            "receipt": result.authoring.receipt,
            "contract_a": result.authoring.contract_a,
        },
        "claim_profile": result.claim_profile,
        "claim_profile_receipt": result.claim_profile_receipt,
        "evidence_world_profile": result.evidence_world_profile,
        "evidence_world_receipt": result.evidence_world_receipt,
        "compatibility": result.compatibility,
        "compatibility_receipt": result.compatibility_receipt,
    }


def _summary(case_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    observations = {
        row["field"]: row["state"] for row in payload["compatibility"]["observations"]
    }
    return {
        "case_id": case_id,
        "authoring_state": payload["authoring"]["state"],
        "authoring_reason": payload["authoring"]["reason"],
        "claim_families": payload["claim_profile"]["claim_families"],
        "expected_evidence_forms": payload["claim_profile"]["expected_evidence_forms"],
        "available_evidence_forms": payload["evidence_world_profile"]["evidence_forms"],
        "compatibility": observations,
        "claim_profile_sha256": payload["claim_profile"]["profile_sha256"],
        "evidence_world_profile_sha256": payload["evidence_world_profile"]["profile_sha256"],
        "compatibility_sha256": payload["compatibility"]["compatibility_sha256"],
    }


def _real_a1a_claim_only() -> tuple[AuthoringRequest, TaskMetadata, TaskMetadata, tuple[SourceMetadata, ...]]:
    # This is the exact A1A-C1 claim from the local pipeline run. The original
    # 12 source bytes are not present in GitHub, so this case deliberately does
    # not fabricate them. EvidenceGate therefore sees an unavailable evidence
    # world and must preserve that as unknown.
    request = AuthoringRequest(
        handoff_id="paired-gates-shadow-a1a-observed",
        producer_id="paired-gates-shadow-research",
        producer_version="v0",
        work_id="A1A-observed-shadow",
        root_id="A1A-C1",
        root_text="Women had a higher rate than Men.",
        sources=(),
    )
    evidence_task = TaskMetadata(
        corpus_scope="original A1a 12-source world unavailable to this shadow runner",
        completeness_state="unavailable",
        known_gaps=("exact frozen A1a S01-S12 source bytes unavailable",),
    )
    return request, TaskMetadata(), evidence_task, ()


def _a1a_matched_control() -> tuple[AuthoringRequest, TaskMetadata, TaskMetadata, tuple[SourceMetadata, ...]]:
    request = AuthoringRequest(
        handoff_id="paired-gates-shadow-a1a-matched-control",
        producer_id="paired-gates-shadow-research",
        producer_version="v0",
        work_id="A1A-matched-control",
        root_id="A1A-C1-SYNTH-MATCH",
        root_text="Women had a higher rate than Men.",
        sources=(
            SourceRepresentation(
                source_id="MATCH-MEASUREMENT",
                media_type="text/plain; charset=utf-8",
                content="Synthetic control measurement table: Women rate 12.0%; Men rate 10.0%.",
            ),
            SourceRepresentation(
                source_id="MATCH-DOCUMENT",
                media_type="text/plain; charset=utf-8",
                content="Synthetic control narrative record describing the comparative rate measurement.",
            ),
        ),
    )
    metadata = (
        SourceMetadata(
            source_id="MATCH-MEASUREMENT",
            provenance="synthetic research control",
            source_role="measurement_control",
            evidence_form="measurement",
        ),
        SourceMetadata(
            source_id="MATCH-DOCUMENT",
            provenance="synthetic research control",
            source_role="document_control",
            evidence_form="document_text",
        ),
    )
    return request, TaskMetadata(), TaskMetadata(corpus_scope="synthetic matched control"), metadata


def _a1a_mismatched_control() -> tuple[AuthoringRequest, TaskMetadata, TaskMetadata, tuple[SourceMetadata, ...]]:
    request = AuthoringRequest(
        handoff_id="paired-gates-shadow-a1a-mismatched-control",
        producer_id="paired-gates-shadow-research",
        producer_version="v0",
        work_id="A1A-mismatched-control",
        root_id="A1A-C1-SYNTH-MISMATCH",
        root_text="Women had a higher rate than Men.",
        sources=(
            SourceRepresentation(
                source_id="MISMATCH-REGISTRY",
                media_type="application/json",
                content='{"synthetic":"registry-only control; no comparative measurement"}',
            ),
        ),
    )
    metadata = (
        SourceMetadata(
            source_id="MISMATCH-REGISTRY",
            provenance="synthetic research control",
            source_role="registry_control",
            evidence_form="registry_entry",
        ),
    )
    return request, TaskMetadata(), TaskMetadata(corpus_scope="synthetic mismatched control"), metadata


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)

    cases: list[
        tuple[str, AuthoringRequest, TaskMetadata, TaskMetadata, tuple[SourceMetadata, ...]]
    ] = []

    request, claim_task, evidence_task, metadata = _real_a1a_claim_only()
    cases.append(("a1a-observed-claim-only", request, claim_task, evidence_task, metadata))

    request, claim_task, evidence_task, metadata = _a1a_matched_control()
    cases.append(("a1a-synthetic-matched", request, claim_task, evidence_task, metadata))

    request, claim_task, evidence_task, metadata = _a1a_mismatched_control()
    cases.append(("a1a-synthetic-mismatched", request, claim_task, evidence_task, metadata))

    for case_id, fixture_name in (
        ("frozen-declared", "declared.json"),
        ("frozen-not-needed", "not_needed.json"),
        ("frozen-abstained", "abstained.json"),
    ):
        cases.append((case_id, _load_fixture(fixture_name), TaskMetadata(), TaskMetadata(), ()))

    summaries: list[dict[str, Any]] = []
    for case_id, request, claim_task, evidence_task, metadata in cases:
        result = run_paired_preflight(
            request,
            claim_task=claim_task,
            evidence_task=evidence_task,
            source_metadata=metadata,
        )
        payload = _serialize_result(result)
        (OUT / f"{case_id}.json").write_text(
            json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        summaries.append(_summary(case_id, payload))

    manifest = {
        "schema": "paired-gates-shadow-naturalistic-batch-v0",
        "prototype_subject": "cd026605fffa1f4aee2444e689b732522e57eded",
        "real_subject": {
            "root_id": "A1A-C1",
            "root_text": "Women had a higher rate than Men.",
            "original_request_sha256": "850799d128efb3f3dadd76d79294b37856e1f7f33539445c88d4c240e7f36e71",
            "evidence_world_status": "exact 12 source bytes unavailable; not reconstructed",
        },
        "controls": {
            "a1a-synthetic-matched": "synthetic positive compatibility control; not original A1a evidence",
            "a1a-synthetic-mismatched": "synthetic negative compatibility control; not original A1a evidence",
            "frozen-*": "existing ClaimGate integration fixtures",
        },
        "summaries": summaries,
    }
    (OUT / "BATCH-SUMMARY.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=False))


if __name__ == "__main__":
    main()
