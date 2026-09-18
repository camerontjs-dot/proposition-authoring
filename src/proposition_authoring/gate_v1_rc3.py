from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError

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

GATE_V1_RC3_VERSION = "1.0.0-rc.3"
CLAIM_GATE_SCHEMA = "claim-gate-output-v1"
EVIDENCE_GATE_SCHEMA = "evidence-gate-output-v1"
STANDARDIZATION_RECEIPT_SCHEMA = "paired-gates-standardization-receipt-v1"

ORIGIN_TYPES = {
    "official_database",
    "official_document",
    "official_website",
    "publisher_document",
    "organization_record",
    "repository",
    "user_supplied",
    "local_artifact",
    "other",
    UNKNOWN,
}
LOCATOR_KINDS = {
    "web_uri",
    "doi",
    "registry_identifier",
    "repository_reference",
    "file_reference",
    "other",
    UNKNOWN,
}

_QUANTITATIVE_KEYWORD_RE = re.compile(
    r"\b(rate|count|mean|median|average|variance|standard deviation|percentage|percent|"
    r"frequency|ratio|proportion|total|number of)\b|%",
    re.IGNORECASE,
)
_EXPLICIT_COUNT_RE = re.compile(
    r"\b\d+(?:\.\d+)?\s+(?:\w+\s+){0,2}"
    r"(?:records?|patients?|subjects?|cases?|events?|items?|samples?|failures?|errors?|"
    r"defects?|documents?|devices?|units?|observations?|occurrences?|incidents?)\b",
    re.IGNORECASE,
)
_MEASUREMENT_RE = re.compile(
    r"\b\d+(?:\.\d+)?\s*(?:mg|g|kg|µg|ug|ml|l|mm|cm|m|km|°c|celsius|"
    r"seconds?|minutes?|hours?|days?|weeks?|months?)\b",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class SourceMetadataV1RC3:
    source_id: str
    origin_type: str = UNKNOWN
    locator_kind: str = UNKNOWN
    locator_value: str = UNKNOWN
    issuer: str = UNKNOWN
    source_role: str = UNKNOWN
    source_authority_basis: str = UNKNOWN
    document_type: str = UNKNOWN
    evidence_form: str = UNKNOWN
    temporal_coverage: str = UNKNOWN
    jurisdictional_coverage: str = UNKNOWN
    version: str = UNKNOWN
    currency_state: str = UNKNOWN


@dataclass(frozen=True)
class PairedGateV1RC3Result:
    authoring: AuthoringResult
    claim_gate: dict[str, Any]
    evidence_gate: dict[str, Any]
    receipt: dict[str, Any]


def _schema_path(name: str) -> Path:
    root = Path(__file__).resolve().parents[2]
    path = root / "schema" / "gates" / GATE_V1_RC3_VERSION / name
    if not path.exists():
        raise GateV1Error(f"Gate V1 RC3 schema unavailable: {path}")
    return path


def _validate_schema(name: str, value: Any) -> None:
    schema = json.loads(_schema_path(name).read_text(encoding="utf-8"))
    try:
        Draft202012Validator(schema).validate(value)
    except ValidationError as exc:
        location = ".".join(str(part) for part in exc.absolute_path)
        raise GateV1Error(
            f"{name} schema validation failed at {location or '<root>'}: {exc.message}"
        ) from exc


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


def _normalize_media_type(media_type: str) -> str:
    return media_type.split(";", 1)[0].strip().lower()


def _is_quantitative(text: str) -> bool:
    return bool(
        _QUANTITATIVE_KEYWORD_RE.search(text)
        or _EXPLICIT_COUNT_RE.search(text)
        or _MEASUREMENT_RE.search(text)
    )


def classify_claim_v1_rc3(text: str) -> tuple[str, ...]:
    categories = set(classify_claim_v1(text))
    categories.discard("quantitative")
    if _is_quantitative(text):
        categories.add("quantitative")
    if not categories:
        return ("other",)
    return tuple(sorted(categories))


def _validate_locator(kind: str, value: str) -> None:
    if kind not in LOCATOR_KINDS:
        raise GateV1Error(f"unsupported source-origin locator kind: {kind}")
    if kind == UNKNOWN:
        if value != UNKNOWN:
            raise GateV1Error("unknown locator kind requires unknown locator value")
        return
    if value == UNKNOWN or not value.strip():
        raise GateV1Error(f"known locator kind {kind} requires a value")
    if kind == "web_uri":
        parsed = urlparse(value)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise GateV1Error("web_uri locator must be an absolute HTTP/HTTPS URI")


def _validate_metadata(rows: tuple[SourceMetadataV1RC3, ...]) -> None:
    for row in rows:
        if row.origin_type not in ORIGIN_TYPES:
            raise GateV1Error(f"unsupported origin_type: {row.origin_type}")
        _validate_locator(row.locator_kind, row.locator_value)


def build_claim_gate_output_v1_rc3(
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
    out["version"] = GATE_V1_RC3_VERSION
    out["claim"]["categories"] = {
        "state": "known",
        "values": list(classify_claim_v1_rc3(request.root_text)),
        "basis": _basis(
            "bounded_classifier_v1_rc3",
            "finite descriptive classifier; quantitative requires positive quantitative semantics",
        ),
    }
    out["output_sha256"] = bound_object_hash(out, "output_sha256")
    return out


def _base_metadata(rows: tuple[SourceMetadataV1RC3, ...]) -> tuple[SourceMetadataV1, ...]:
    return tuple(
        SourceMetadataV1(
            source_id=row.source_id,
            provenance=row.origin_type,
            issuer=row.issuer,
            source_role=row.source_role,
            authority_basis=row.source_authority_basis,
            document_type=row.document_type,
            evidence_form=row.evidence_form,
            temporal_coverage=row.temporal_coverage,
            jurisdictional_coverage=row.jurisdictional_coverage,
            version=row.version,
            currency_state=row.currency_state,
        )
        for row in rows
    )


def _metadata_index(rows: tuple[SourceMetadataV1RC3, ...]) -> dict[str, SourceMetadataV1RC3]:
    index: dict[str, SourceMetadataV1RC3] = {}
    for row in rows:
        if row.source_id in index:
            raise GateV1Error(f"duplicate metadata row for source: {row.source_id}")
        index[row.source_id] = row
    return index


def _representation_id(source_id: str, media_type: str, content_sha256: str) -> str:
    payload = {
        "source_id": source_id,
        "media_type": _normalize_media_type(media_type),
        "content_sha256": content_sha256,
    }
    return sha256_bytes(canonical_json(payload).encode("utf-8"))


def _evidence_world_id_from_sources(sources: list[dict[str, Any]]) -> str:
    representation_ids = sorted(row["representation_id"] for row in sources)
    return sha256_bytes(
        canonical_json({"representation_ids": representation_ids}).encode("utf-8")
    )


def _origin(meta: SourceMetadataV1RC3, source_ref: str) -> dict[str, Any]:
    if meta.origin_type == UNKNOWN:
        return {
            "state": "unknown",
            "origin_type": None,
            "locator": None,
            "basis": _basis("no_basis", "source origin unavailable", source_ref),
        }
    locator = None
    if meta.locator_kind != UNKNOWN:
        locator = {"kind": meta.locator_kind, "value": meta.locator_value}
    return {
        "state": "known",
        "origin_type": meta.origin_type,
        "locator": locator,
        "basis": _basis("source_metadata", "declared source origin", source_ref),
    }


def build_evidence_gate_output_v1_rc3(
    request: AuthoringRequest,
    *,
    task: EvidenceTaskV1 | None = None,
    source_metadata: tuple[SourceMetadataV1RC3, ...] = (),
    implementation_identity: str = "runtime",
) -> dict[str, Any]:
    _validate_metadata(source_metadata)
    metadata_by_id = _metadata_index(source_metadata)
    supplied_ids = [source.source_id for source in request.sources]
    if len(supplied_ids) != len(set(supplied_ids)):
        raise GateV1Error("duplicate supplied source_id")
    unknown_metadata = sorted(set(metadata_by_id) - set(supplied_ids))
    if unknown_metadata:
        raise GateV1Error(f"metadata references unsupplied source: {unknown_metadata[0]}")

    out = build_evidence_gate_output_v1(
        request,
        task=task,
        source_metadata=_base_metadata(source_metadata),
        implementation_identity=implementation_identity,
    )
    out["version"] = GATE_V1_RC3_VERSION
    out.pop("root_id", None)

    for source in out["sources"]:
        source["media_type"] = _normalize_media_type(source["media_type"])
        source["representation_id"] = _representation_id(
            source["source_id"],
            source["media_type"],
            source["content_sha256"],
        )
        meta = metadata_by_id.get(
            source["source_id"],
            SourceMetadataV1RC3(source_id=source["source_id"]),
        )
        old = source["provenance"]
        source["provenance"] = {
            "source_origin": _origin(meta, source["source_id"]),
            "issuer": old["issuer"],
            "source_role": old["source_role"],
            "source_authority_basis": old["authority_basis"],
        }

    out["evidence_world_id"] = _evidence_world_id_from_sources(out["sources"])
    out["output_sha256"] = bound_object_hash(out, "output_sha256")
    return out


def build_provenance_inputs_v1_rc3(
    request: AuthoringRequest,
    *,
    evidence_task: EvidenceTaskV1 | None = None,
    source_metadata: tuple[SourceMetadataV1RC3, ...] = (),
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
        "schema": "claim-gate-reconstruction-input-v1-rc3",
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
        "schema": "evidence-gate-reconstruction-input-v1-rc3",
        "sources": request_sources,
        "source_metadata": [
            asdict(row) for row in sorted(source_metadata, key=lambda row: row.source_id)
        ],
        "evidence_task": asdict(evidence_task),
    }
    return claim_input, evidence_input


def validate_claim_gate_output_v1_rc3(value: Any) -> dict[str, Any]:
    _validate_schema("claim-gate-output.schema.json", value)
    row = value
    if row["output_sha256"] != bound_object_hash(row, "output_sha256"):
        raise GateV1Error("ClaimGate V1 RC3 output hash mismatch")
    claim = row["claim"]
    if claim["text_sha256"] != sha256_text(claim["text"]):
        raise GateV1Error("ClaimGate V1 RC3 claim text hash mismatch")
    if claim["categories"]["values"] != list(classify_claim_v1_rc3(claim["text"])):
        raise GateV1Error("ClaimGate V1 RC3 category classification mismatch")
    return row


def validate_evidence_gate_output_v1_rc3(value: Any) -> dict[str, Any]:
    _validate_schema("evidence-gate-output.schema.json", value)
    row = value
    if row["output_sha256"] != bound_object_hash(row, "output_sha256"):
        raise GateV1Error("EvidenceGate V1 RC3 output hash mismatch")
    if row["source_count"] != len(row["sources"]):
        raise GateV1Error("EvidenceGate V1 RC3 source_count mismatch")
    source_ids: list[str] = []
    for source in row["sources"]:
        source_ids.append(source["source_id"])
        expected_representation = _representation_id(
            source["source_id"],
            source["media_type"],
            source["content_sha256"],
        )
        if source["representation_id"] != expected_representation:
            raise GateV1Error("EvidenceGate V1 RC3 representation_id mismatch")
    if source_ids != sorted(source_ids) or len(source_ids) != len(set(source_ids)):
        raise GateV1Error("EvidenceGate V1 RC3 sources must be unique and source_id sorted")
    if row["evidence_world_id"] != _evidence_world_id_from_sources(row["sources"]):
        raise GateV1Error("EvidenceGate V1 RC3 evidence_world_id mismatch")
    return row


def validate_standardization_receipt_v1_rc3(value: Any) -> dict[str, Any]:
    _validate_schema("standardization-receipt.schema.json", value)
    if value["receipt_sha256"] != bound_object_hash(value, "receipt_sha256"):
        raise GateV1Error("Gate V1 RC3 receipt hash mismatch")
    return value


def _verify_contract_a(contract_a: dict[str, Any]) -> None:
    required = {
        "schema",
        "handoff_id",
        "producer",
        "work",
        "root_proposition",
        "sources",
        "decomposition",
        "handoff_sha256",
    }
    if set(contract_a) != required:
        raise GateV1Error("Contract A key mismatch")
    if contract_a["schema"] != "contract-a-wire-candidate-rc2":
        raise GateV1Error("unsupported Contract A schema")
    if contract_a["handoff_sha256"] != bound_object_hash(contract_a, "handoff_sha256"):
        raise GateV1Error("Contract A handoff hash mismatch")
    root = contract_a["root_proposition"]
    if root["text_sha256"] != sha256_text(root["text"]):
        raise GateV1Error("Contract A root text hash mismatch")
    for source in contract_a["sources"]:
        if source["content_sha256"] != sha256_text(source["content"]):
            raise GateV1Error("Contract A source content hash mismatch")


def verify_standardized_gate_bundle_v1_rc3(
    claim_gate: dict[str, Any],
    evidence_gate: dict[str, Any],
    receipt: dict[str, Any],
    *,
    contract_a: dict[str, Any] | None,
) -> dict[str, Any]:
    validate_claim_gate_output_v1_rc3(claim_gate)
    validate_evidence_gate_output_v1_rc3(evidence_gate)
    validate_standardization_receipt_v1_rc3(receipt)

    if receipt["root_id"] != claim_gate["claim"]["proposition_id"]:
        raise GateV1Error("receipt root_id disagrees with ClaimGate")
    if receipt["claim_gate_output_sha256"] != claim_gate["output_sha256"]:
        raise GateV1Error("receipt ClaimGate identity mismatch")
    if receipt["evidence_gate_output_sha256"] != evidence_gate["output_sha256"]:
        raise GateV1Error("receipt EvidenceGate identity mismatch")
    if receipt["evidence_world_id"] != evidence_gate["evidence_world_id"]:
        raise GateV1Error("receipt evidence_world_id mismatch")

    binding = claim_gate["contract_a_binding"]
    if binding["state"] == "present":
        if contract_a is None:
            raise GateV1Error("receipt requires presented Contract A")
        _verify_contract_a(contract_a)
        handoff = contract_a["handoff_sha256"]
        if binding["handoff_sha256"] != handoff:
            raise GateV1Error("ClaimGate Contract A binding mismatch")
        if receipt["contract_a_state"] != "present":
            raise GateV1Error("receipt Contract A state mismatch")
        if receipt["contract_a_handoff_sha256"] != handoff:
            raise GateV1Error("receipt Contract A handoff mismatch")
        root = contract_a["root_proposition"]
        if root["proposition_id"] != claim_gate["claim"]["proposition_id"]:
            raise GateV1Error("Contract A root identity disagrees with ClaimGate")
        if root["text_sha256"] != claim_gate["claim"]["text_sha256"]:
            raise GateV1Error("Contract A root hash disagrees with ClaimGate")
    else:
        if contract_a is not None:
            raise GateV1Error("Contract A presented while ClaimGate binding is absent")
        if receipt["contract_a_state"] != "absent":
            raise GateV1Error("receipt Contract A state mismatch")
        if receipt["contract_a_handoff_sha256"] is not None:
            raise GateV1Error("absent Contract A requires null receipt handoff")

    return {
        "state": "VERIFIED",
        "root_id": receipt["root_id"],
        "evidence_world_id": receipt["evidence_world_id"],
        "claim_gate_output_sha256": claim_gate["output_sha256"],
        "evidence_gate_output_sha256": evidence_gate["output_sha256"],
        "contract_a_handoff_sha256": receipt["contract_a_handoff_sha256"],
    }


def standardize_gates_v1_rc3(
    request: AuthoringRequest,
    *,
    evidence_task: EvidenceTaskV1 | None = None,
    source_metadata: tuple[SourceMetadataV1RC3, ...] = (),
    engine: AuthoringEngine | None = None,
    implementation_identity: str = "runtime",
) -> PairedGateV1RC3Result:
    authoring = (engine or AuthoringEngine()).author(request)
    claim_gate = build_claim_gate_output_v1_rc3(
        request,
        authoring,
        implementation_identity=implementation_identity,
    )
    evidence_gate = build_evidence_gate_output_v1_rc3(
        request,
        task=evidence_task,
        source_metadata=source_metadata,
        implementation_identity=implementation_identity,
    )
    validate_claim_gate_output_v1_rc3(claim_gate)
    validate_evidence_gate_output_v1_rc3(evidence_gate)

    receipt: dict[str, Any] = {
        "schema": STANDARDIZATION_RECEIPT_SCHEMA,
        "version": GATE_V1_RC3_VERSION,
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
    validate_standardization_receipt_v1_rc3(receipt)
    verify_standardized_gate_bundle_v1_rc3(
        claim_gate,
        evidence_gate,
        receipt,
        contract_a=authoring.contract_a,
    )
    return PairedGateV1RC3Result(
        authoring=authoring,
        claim_gate=claim_gate,
        evidence_gate=evidence_gate,
        receipt=receipt,
    )
