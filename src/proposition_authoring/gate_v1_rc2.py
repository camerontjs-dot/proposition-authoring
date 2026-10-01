from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from typing import Any

from .canonical import bound_object_hash, canonical_json, sha256_bytes, sha256_text
from .engine import AuthoringEngine
from .gate_v1 import (
    UNKNOWN,
    EvidenceTaskV1,
    GateV1Error,
    SourceMetadataV1,
    build_claim_gate_output_v1,
    build_evidence_gate_output_v1,
    classify_claim_v1,
)
from .model import AuthoringRequest, AuthoringResult

GATE_V1_RC2_VERSION = "1.0.0-rc.2"
CLAIM_GATE_SCHEMA = "claim-gate-output-v1"
EVIDENCE_GATE_SCHEMA = "evidence-gate-output-v1"
STANDARDIZATION_RECEIPT_SCHEMA = "paired-gates-standardization-receipt-v1"

_IDENTIFIER_SPAN_RE = re.compile(
    r"""\b(?:DIN|NDC|NPN|LOT(?:\s+(?:NO\.?|NUMBER))?|SERIAL(?:\s+(?:NO\.?|NUMBER))?|DOCUMENT(?:\s+(?:NO\.?|NUMBER))?|DOC(?:\s+(?:NO\.?|NUMBER))?|ID|IDENTIFIER|LICEN[CS]E(?:\s+(?:NO\.?|NUMBER))?|APPLICATION(?:\s+(?:NO\.?|NUMBER))?|REGISTRATION(?:\s+(?:NO\.?|NUMBER))?)\s*[:#]?\s*[A-Z0-9][A-Z0-9._/-]*\b""",
    re.IGNORECASE,
)
_QUANTITATIVE_RE = re.compile(
    r"(?:\b(?!19\d{2}\b|20\d{2}\b)\d+(?:\.\d+)?\b|%|\b(rate|count|mean|median|average|variance|standard deviation|percentage|percent)\b)",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class SourceMetadataV1RC2:
    source_id: str
    origin_type: str = UNKNOWN
    source_uri: str = UNKNOWN
    issuer: str = UNKNOWN
    source_role: str = UNKNOWN
    authority_basis: str = UNKNOWN
    document_type: str = UNKNOWN
    evidence_form: str = UNKNOWN
    temporal_coverage: str = UNKNOWN
    jurisdictional_coverage: str = UNKNOWN
    version: str = UNKNOWN
    currency_state: str = UNKNOWN


@dataclass(frozen=True)
class PairedGateV1RC2Result:
    authoring: AuthoringResult
    claim_gate: dict[str, Any]
    evidence_gate: dict[str, Any]
    receipt: dict[str, Any]


def _basis(kind: str, detail: str, source_ref: str | None = None) -> dict[str, str]:
    row = {"kind": kind, "detail": detail}
    if source_ref is not None:
        row["source_ref"] = source_ref
    return row


def _observed(value: str, *, detail: str, source_ref: str) -> dict[str, Any]:
    if value == UNKNOWN:
        return {
            "state": "unknown",
            "value": None,
            "basis": _basis("no_basis", detail, source_ref),
        }
    return {
        "state": "known",
        "value": value,
        "basis": _basis("source_metadata", detail, source_ref),
    }


def classify_claim_v1_rc2(text: str) -> tuple[str, ...]:
    categories = set(classify_claim_v1(text))
    if "quantitative" in categories:
        quantitative_surface = _IDENTIFIER_SPAN_RE.sub(" ", text)
        if _QUANTITATIVE_RE.search(quantitative_surface) is None:
            categories.remove("quantitative")
    if not categories:
        return ("other",)
    return tuple(sorted(categories))


def build_claim_gate_output_v1_rc2(
    request: AuthoringRequest,
    result: AuthoringResult,
    *,
    implementation_identity: str = "runtime",
) -> dict[str, Any]:
    out = build_claim_gate_output_v1(
        request,
        result,
        implementation_identity=implementation_identity,
    )
    out["version"] = GATE_V1_RC2_VERSION
    out["claim"]["categories"] = {
        "state": "known",
        "values": list(classify_claim_v1_rc2(request.root_text)),
        "basis": _basis(
            "bounded_classifier_v1_rc2",
            "finite lexical category standardizer with identifier masking; descriptive only",
        ),
    }
    out["output_sha256"] = bound_object_hash(out, "output_sha256")
    return out


def _base_metadata(rows: tuple[SourceMetadataV1RC2, ...]) -> tuple[SourceMetadataV1, ...]:
    return tuple(
        SourceMetadataV1(
            source_id=row.source_id,
            provenance=row.origin_type,
            issuer=row.issuer,
            source_role=row.source_role,
            authority_basis=row.authority_basis,
            document_type=row.document_type,
            evidence_form=row.evidence_form,
            temporal_coverage=row.temporal_coverage,
            jurisdictional_coverage=row.jurisdictional_coverage,
            version=row.version,
            currency_state=row.currency_state,
        )
        for row in rows
    )


def _metadata_index(
    rows: tuple[SourceMetadataV1RC2, ...],
) -> dict[str, SourceMetadataV1RC2]:
    index: dict[str, SourceMetadataV1RC2] = {}
    for row in rows:
        if row.source_id in index:
            raise GateV1Error(f"duplicate metadata row for source: {row.source_id}")
        index[row.source_id] = row
    return index


def _evidence_world_id_from_sources(sources: list[dict[str, Any]]) -> str:
    projection = [
        {"source_id": row["source_id"], "content_sha256": row["content_sha256"]}
        for row in sources
    ]
    return "sha256:" + sha256_bytes(
        canonical_json({"sources": projection}).encode("utf-8")
    )[7:]


def build_evidence_gate_output_v1_rc2(
    request: AuthoringRequest,
    *,
    task: EvidenceTaskV1 | None = None,
    source_metadata: tuple[SourceMetadataV1RC2, ...] = (),
    implementation_identity: str = "runtime",
) -> dict[str, Any]:
    metadata_by_id = _metadata_index(source_metadata)
    supplied_ids = {source.source_id for source in request.sources}
    unknown_metadata = sorted(set(metadata_by_id) - supplied_ids)
    if unknown_metadata:
        raise GateV1Error(
            f"metadata references unsupplied source: {unknown_metadata[0]}"
        )

    out = build_evidence_gate_output_v1(
        request,
        task=task,
        source_metadata=_base_metadata(source_metadata),
        implementation_identity=implementation_identity,
    )
    out["version"] = GATE_V1_RC2_VERSION
    out.pop("root_id", None)

    for source in out["sources"]:
        meta = metadata_by_id.get(
            source["source_id"],
            SourceMetadataV1RC2(source_id=source["source_id"]),
        )
        old = source["provenance"]
        source["provenance"] = {
            "origin": {
                "origin_type": old["origin"],
                "source_uri": _observed(
                    meta.source_uri,
                    detail=(
                        "source-origin URI unavailable"
                        if meta.source_uri == UNKNOWN
                        else "declared source-origin URI"
                    ),
                    source_ref=source["source_id"],
                ),
            },
            "issuer": old["issuer"],
            "source_role": old["source_role"],
            "authority_basis": old["authority_basis"],
        }

    out["evidence_world_id"] = _evidence_world_id_from_sources(out["sources"])
    out["output_sha256"] = bound_object_hash(out, "output_sha256")
    return out


def build_provenance_inputs_v1_rc2(
    request: AuthoringRequest,
    *,
    evidence_task: EvidenceTaskV1 | None = None,
    source_metadata: tuple[SourceMetadataV1RC2, ...] = (),
) -> tuple[dict[str, Any], dict[str, Any]]:
    evidence_task = evidence_task or EvidenceTaskV1()
    request_sources = [
        {
            "source_id": source.source_id,
            "media_type": source.media_type,
            "content": source.content,
        }
        for source in request.sources
    ]
    claim_input = {
        "schema": "claim-gate-reconstruction-input-v1-rc2",
        "request": {
            "handoff_id": request.handoff_id,
            "producer_id": request.producer_id,
            "producer_version": request.producer_version,
            "work_id": request.work_id,
            "root_id": request.root_id,
            "root_text": request.root_text,
            "sources": request_sources,
            "context_source_id": request.context_source_id,
        },
    }
    evidence_input = {
        "schema": "evidence-gate-reconstruction-input-v1-rc2",
        "sources": request_sources,
        "source_metadata": [
            asdict(row) for row in sorted(source_metadata, key=lambda row: row.source_id)
        ],
        "evidence_task": asdict(evidence_task),
    }
    return claim_input, evidence_input


def _exact_keys(value: Any, expected: set[str], label: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != expected:
        actual = sorted(value) if isinstance(value, dict) else type(value).__name__
        raise GateV1Error(f"{label} key mismatch: {actual}")
    return value


def validate_claim_gate_output_v1_rc2(value: Any) -> dict[str, Any]:
    row = _exact_keys(
        value,
        {
            "schema",
            "version",
            "implementation_identity",
            "authoring",
            "claim",
            "lineage",
            "contract_a_binding",
            "authority",
            "output_sha256",
        },
        "claim_gate",
    )
    if row["schema"] != CLAIM_GATE_SCHEMA or row["version"] != GATE_V1_RC2_VERSION:
        raise GateV1Error("ClaimGate V1 RC2 schema/version mismatch")
    if row["output_sha256"] != bound_object_hash(row, "output_sha256"):
        raise GateV1Error("ClaimGate V1 RC2 output hash mismatch")
    claim = _exact_keys(
        row["claim"],
        {"proposition_id", "text", "text_sha256", "categories"},
        "claim_gate.claim",
    )
    if claim["text_sha256"] != sha256_text(claim["text"]):
        raise GateV1Error("ClaimGate V1 RC2 claim text hash mismatch")
    if claim["categories"]["values"] != list(classify_claim_v1_rc2(claim["text"])):
        raise GateV1Error("ClaimGate V1 RC2 category classification mismatch")
    return row


def validate_evidence_gate_output_v1_rc2(value: Any) -> dict[str, Any]:
    row = _exact_keys(
        value,
        {
            "schema",
            "version",
            "implementation_identity",
            "evidence_world_id",
            "source_count",
            "sources",
            "corpus",
            "authority",
            "output_sha256",
        },
        "evidence_gate",
    )
    if row["schema"] != EVIDENCE_GATE_SCHEMA or row["version"] != GATE_V1_RC2_VERSION:
        raise GateV1Error("EvidenceGate V1 RC2 schema/version mismatch")
    if row["output_sha256"] != bound_object_hash(row, "output_sha256"):
        raise GateV1Error("EvidenceGate V1 RC2 output hash mismatch")
    if row["source_count"] != len(row["sources"]):
        raise GateV1Error("EvidenceGate V1 RC2 source_count mismatch")

    source_ids: list[str] = []
    for index, source in enumerate(row["sources"]):
        source = _exact_keys(
            source,
            {
                "source_id",
                "media_type",
                "content_sha256",
                "provenance",
                "classification",
                "coverage",
            },
            f"evidence_gate.sources[{index}]",
        )
        source_ids.append(source["source_id"])
        provenance = _exact_keys(
            source["provenance"],
            {"origin", "issuer", "source_role", "authority_basis"},
            f"evidence_gate.sources[{index}].provenance",
        )
        _exact_keys(
            provenance["origin"],
            {"origin_type", "source_uri"},
            f"evidence_gate.sources[{index}].provenance.origin",
        )

    if source_ids != sorted(source_ids) or len(source_ids) != len(set(source_ids)):
        raise GateV1Error("EvidenceGate V1 RC2 sources must be unique and source_id sorted")
    if row["evidence_world_id"] != _evidence_world_id_from_sources(row["sources"]):
        raise GateV1Error("EvidenceGate V1 RC2 evidence_world_id mismatch")
    return row


def standardize_gates_v1_rc2(
    request: AuthoringRequest,
    *,
    evidence_task: EvidenceTaskV1 | None = None,
    source_metadata: tuple[SourceMetadataV1RC2, ...] = (),
    engine: AuthoringEngine | None = None,
    implementation_identity: str = "runtime",
) -> PairedGateV1RC2Result:
    authoring = (engine or AuthoringEngine()).author(request)
    claim_gate = build_claim_gate_output_v1_rc2(
        request,
        authoring,
        implementation_identity=implementation_identity,
    )
    evidence_gate = build_evidence_gate_output_v1_rc2(
        request,
        task=evidence_task,
        source_metadata=source_metadata,
        implementation_identity=implementation_identity,
    )
    validate_claim_gate_output_v1_rc2(claim_gate)
    validate_evidence_gate_output_v1_rc2(evidence_gate)

    receipt: dict[str, Any] = {
        "schema": STANDARDIZATION_RECEIPT_SCHEMA,
        "version": GATE_V1_RC2_VERSION,
        "root_id": request.root_id,
        "evidence_world_id": evidence_gate["evidence_world_id"],
        "claim_gate_output_sha256": claim_gate["output_sha256"],
        "evidence_gate_output_sha256": evidence_gate["output_sha256"],
        "contract_a_state": claim_gate["contract_a_binding"]["state"],
        "contract_a_handoff_sha256": claim_gate["contract_a_binding"]["handoff_sha256"],
        "downstream_authority": {
            "evidence_bundler_may_consume_contract_a": authoring.contract_a is not None,
            "gate_metadata_is_retrieval_instruction": False,
            "gate_metadata_is_cal_verdict": False,
        },
    }
    receipt["receipt_sha256"] = bound_object_hash(receipt, "receipt_sha256")
    return PairedGateV1RC2Result(
        authoring=authoring,
        claim_gate=claim_gate,
        evidence_gate=evidence_gate,
        receipt=receipt,
    )
