from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError as JsonSchemaValidationError

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

_ORIGIN_TYPES = {
    "official_database",
    "official_document",
    "official_website",
    "publisher_document",
    "organization_record",
    "repository",
    "user_supplied",
    "local_artifact",
    "other",
}
_LOCATOR_KINDS = {
    "web_uri",
    "doi",
    "registry_identifier",
    "repository_reference",
    "file_reference",
    "other",
}
_AUTHORITY_BASIS_KINDS = {
    "official_issuer",
    "first_party_record",
    "publisher_record",
    "repository_record",
    "user_declaration",
    "other",
}

_QUANT_SIGNAL_RE = re.compile(
    r"(?:%|\b(?:rate|count|mean|median|average|variance|standard deviation|percentage|percent)\b)",
    re.IGNORECASE,
)
_CARDINALITY_RE = re.compile(
    r"\b\d+(?:\.\d+)?(?:\s+[A-Za-z][A-Za-z-]*){0,3}\s+(?:records?|cases?|items?|patients?|events?|failures?|errors?|samples?|documents?|units?|occurrences?|incidents?|observations?|responses?|participants?)\b",
    re.IGNORECASE,
)
_MEASUREMENT_RE = re.compile(
    r"\b\d+(?:\.\d+)?\s*(?:mg|g|kg|mcg|µg|ml|l|mm|cm|m|km|ms|s|sec|seconds?|min|minutes?|h|hours?|hz|khz|mhz|ghz|°c|°f|celsius|fahrenheit|pa|kpa|mpa|psi|v|mv|a|ma|w|kw|mw)\b",
    re.IGNORECASE,
)
_CURRENCY_RE = re.compile(
    r"(?:[$€£]\s*\d+(?:\.\d+)?|\b\d+(?:\.\d+)?\s*(?:usd|cad|eur|gbp)\b)",
    re.IGNORECASE,
)
_NUMERIC_COMPARISON_RE = re.compile(
    r"\b\d+(?:\.\d+)?\b.{0,60}\b(?:greater|less|higher|lower|more|fewer|exceed(?:s|ed)?)\b.{0,60}\b\d+(?:\.\d+)?\b",
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
    source_authority_basis_kind: str = UNKNOWN
    source_authority_basis_detail: str = UNKNOWN
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


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _schema(name: str) -> dict[str, Any]:
    path = _repo_root() / "schema" / "gates" / GATE_V1_RC3_VERSION / name
    if not path.is_file():
        raise GateV1Error(f"Gate V1 RC3 schema unavailable: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _validate_schema(value: Any, schema_name: str, label: str) -> None:
    try:
        Draft202012Validator(_schema(schema_name)).validate(value)
    except (JsonSchemaValidationError, json.JSONDecodeError) as exc:
        raise GateV1Error(f"{label} schema validation failed: {exc}") from exc


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


def _normalized_media_type(media_type: str) -> str:
    value = media_type.split(";", 1)[0].strip().lower()
    if not value:
        raise GateV1Error("source media_type must be nonblank")
    return value


def _has_quantitative_semantics(text: str) -> bool:
    return any(
        pattern.search(text) is not None
        for pattern in (
            _QUANT_SIGNAL_RE,
            _CARDINALITY_RE,
            _MEASUREMENT_RE,
            _CURRENCY_RE,
            _NUMERIC_COMPARISON_RE,
        )
    )


def classify_claim_v1_rc3(text: str) -> tuple[str, ...]:
    categories = set(classify_claim_v1(text))
    categories.discard("quantitative")
    if _has_quantitative_semantics(text):
        categories.add("quantitative")
    if not categories:
        return ("other",)
    return tuple(sorted(categories))


def _representation_id(source_id: str, media_type: str, content_sha256: str) -> str:
    payload = {
        "source_id": source_id,
        "media_type": _normalized_media_type(media_type),
        "content_sha256": content_sha256,
    }
    return sha256_bytes(canonical_json(payload).encode("utf-8"))


def _evidence_world_id_from_sources(sources: list[dict[str, Any]]) -> str:
    identities = sorted(source["representation_id"] for source in sources)
    return sha256_bytes(canonical_json({"representation_ids": identities}).encode("utf-8"))


def _metadata_index(rows: tuple[SourceMetadataV1RC3, ...]) -> dict[str, SourceMetadataV1RC3]:
    index: dict[str, SourceMetadataV1RC3] = {}
    for row in rows:
        if row.source_id in index:
            raise GateV1Error(f"duplicate metadata row for source: {row.source_id}")
        index[row.source_id] = row
    return index


def _validate_web_uri(value: str) -> None:
    parsed = urlsplit(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise GateV1Error("web_uri source locator must be an absolute http/https URI")


def _source_origin(meta: SourceMetadataV1RC3, source_id: str) -> dict[str, Any]:
    if meta.origin_type == UNKNOWN:
        if meta.locator_kind != UNKNOWN or meta.locator_value != UNKNOWN:
            raise GateV1Error("source locator cannot be known while origin_type is unknown")
        return {
            "state": "unknown",
            "origin_type": None,
            "locator": {"state": "unknown", "kind": None, "value": None},
            "basis": _basis("no_basis", "source origin unavailable", source_id),
        }

    if meta.origin_type not in _ORIGIN_TYPES:
        raise GateV1Error(f"unsupported origin_type: {meta.origin_type}")

    if (meta.locator_kind == UNKNOWN) != (meta.locator_value == UNKNOWN):
        raise GateV1Error("source locator kind/value must be known or unknown together")

    if meta.locator_kind == UNKNOWN:
        locator = {"state": "unknown", "kind": None, "value": None}
    else:
        if meta.locator_kind not in _LOCATOR_KINDS:
            raise GateV1Error(f"unsupported locator_kind: {meta.locator_kind}")
        if not meta.locator_value.strip():
            raise GateV1Error("known source locator value must be nonblank")
        if meta.locator_kind == "web_uri":
            _validate_web_uri(meta.locator_value)
        locator = {
            "state": "known",
            "kind": meta.locator_kind,
            "value": meta.locator_value,
        }

    return {
        "state": "known",
        "origin_type": meta.origin_type,
        "locator": locator,
        "basis": _basis("source_metadata", "declared source origin", source_id),
    }


def _source_authority_basis(meta: SourceMetadataV1RC3, source_id: str) -> dict[str, Any]:
    if meta.source_authority_basis_kind == UNKNOWN:
        if meta.source_authority_basis_detail != UNKNOWN:
            raise GateV1Error("source authority detail cannot be known while basis kind is unknown")
        return {
            "state": "unknown",
            "kind": None,
            "detail": None,
            "basis": _basis("no_basis", "source authority basis unavailable", source_id),
        }
    if meta.source_authority_basis_kind not in _AUTHORITY_BASIS_KINDS:
        raise GateV1Error(
            f"unsupported source_authority_basis_kind: {meta.source_authority_basis_kind}"
        )
    detail = None
    if meta.source_authority_basis_detail != UNKNOWN:
        if not meta.source_authority_basis_detail.strip():
            raise GateV1Error("known source authority basis detail must be nonblank")
        detail = meta.source_authority_basis_detail
    return {
        "state": "known",
        "kind": meta.source_authority_basis_kind,
        "detail": detail,
        "basis": _basis(
            "source_metadata",
            "proposition-independent source authority characterization",
            source_id,
        ),
    }


def _base_metadata(rows: tuple[SourceMetadataV1RC3, ...]) -> tuple[SourceMetadataV1, ...]:
    return tuple(
        SourceMetadataV1(
            source_id=row.source_id,
            provenance=row.origin_type,
            issuer=row.issuer,
            source_role=row.source_role,
            authority_basis=UNKNOWN,
            document_type=row.document_type,
            evidence_form=row.evidence_form,
            temporal_coverage=row.temporal_coverage,
            jurisdictional_coverage=row.jurisdictional_coverage,
            version=row.version,
            currency_state=row.currency_state,
        )
        for row in rows
    )


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


def build_evidence_gate_output_v1_rc3(
    request: AuthoringRequest,
    *,
    task: EvidenceTaskV1 | None = None,
    source_metadata: tuple[SourceMetadataV1RC3, ...] = (),
    implementation_identity: str = "runtime",
) -> dict[str, Any]:
    metadata_by_id = _metadata_index(source_metadata)
    supplied_ids = {source.source_id for source in request.sources}
    unknown_metadata = sorted(set(metadata_by_id) - supplied_ids)
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
        source["media_type"] = _normalized_media_type(source["media_type"])
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
            "source_origin": _source_origin(meta, source["source_id"]),
            "issuer": old["issuer"],
            "source_role": old["source_role"],
            "source_authority_basis": _source_authority_basis(meta, source["source_id"]),
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
    _validate_schema(value, "claim-gate-output.schema.json", "ClaimGate V1 RC3")
    row = value
    if row["output_sha256"] != bound_object_hash(row, "output_sha256"):
        raise GateV1Error("ClaimGate V1 RC3 output hash mismatch")
    claim = row["claim"]
    if claim["text_sha256"] != sha256_text(claim["text"]):
        raise GateV1Error("ClaimGate V1 RC3 claim text hash mismatch")
    expected = list(classify_claim_v1_rc3(claim["text"]))
    if claim["categories"]["values"] != expected:
        raise GateV1Error("ClaimGate V1 RC3 category classification mismatch")
    return row


def validate_evidence_gate_output_v1_rc3(value: Any) -> dict[str, Any]:
    _validate_schema(value, "evidence-gate-output.schema.json", "EvidenceGate V1 RC3")
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
    _validate_schema(
        value,
        "standardization-receipt.schema.json",
        "Paired Gates V1 RC3 receipt",
    )
    if value["receipt_sha256"] != bound_object_hash(value, "receipt_sha256"):
        raise GateV1Error("Paired Gates V1 RC3 receipt hash mismatch")
    return value


def _validate_contract_a(contract_a: dict[str, Any]) -> None:
    if contract_a.get("handoff_sha256") != bound_object_hash(contract_a, "handoff_sha256"):
        raise GateV1Error("Contract A handoff hash mismatch")
    root = contract_a.get("root_proposition")
    if not isinstance(root, dict) or root.get("text_sha256") != sha256_text(root.get("text", "")):
        raise GateV1Error("Contract A root proposition hash mismatch")
    for source in contract_a.get("sources", []):
        if source.get("content_sha256") != sha256_text(source.get("content", "")):
            raise GateV1Error("Contract A source content hash mismatch")
    decomposition = contract_a.get("decomposition", {})
    if decomposition.get("state") == "declared":
        for child in decomposition.get("children", []):
            if child.get("text_sha256") != sha256_text(child.get("text", "")):
                raise GateV1Error("Contract A child proposition hash mismatch")


def verify_standardized_gate_bundle_v1_rc3(
    claim_gate: Any,
    evidence_gate: Any,
    contract_a: Any,
    receipt: Any,
) -> dict[str, Any]:
    claim = validate_claim_gate_output_v1_rc3(claim_gate)
    evidence = validate_evidence_gate_output_v1_rc3(evidence_gate)
    bound = validate_standardization_receipt_v1_rc3(receipt)

    if bound["root_id"] != claim["claim"]["proposition_id"]:
        raise GateV1Error("receipt root_id disagrees with ClaimGate")
    if bound["claim_gate_output_sha256"] != claim["output_sha256"]:
        raise GateV1Error("receipt ClaimGate hash disagreement")
    if bound["evidence_gate_output_sha256"] != evidence["output_sha256"]:
        raise GateV1Error("receipt EvidenceGate hash disagreement")
    if bound["evidence_world_id"] != evidence["evidence_world_id"]:
        raise GateV1Error("receipt evidence_world_id disagreement")

    binding = claim["contract_a_binding"]
    if binding["state"] == "present":
        if not isinstance(contract_a, dict):
            raise GateV1Error("Contract A required by ClaimGate binding")
        _validate_contract_a(contract_a)
        handoff_hash = contract_a["handoff_sha256"]
        if binding["handoff_sha256"] != handoff_hash:
            raise GateV1Error("ClaimGate Contract A binding disagreement")
        if bound["contract_a_state"] != "present":
            raise GateV1Error("receipt Contract A state disagreement")
        if bound["contract_a_handoff_sha256"] != handoff_hash:
            raise GateV1Error("receipt Contract A hash disagreement")
        root = contract_a["root_proposition"]
        if root["proposition_id"] != claim["claim"]["proposition_id"]:
            raise GateV1Error("Contract A root proposition identity disagreement")
        if root["text_sha256"] != claim["claim"]["text_sha256"]:
            raise GateV1Error("Contract A root proposition content disagreement")
    else:
        if contract_a is not None:
            raise GateV1Error("Contract A presented while ClaimGate binding is absent")
        if bound["contract_a_state"] != "absent":
            raise GateV1Error("receipt Contract A state disagreement")
        if bound["contract_a_handoff_sha256"] is not None:
            raise GateV1Error("receipt Contract A hash must be null when absent")

    return {
        "state": "VERIFIED",
        "root_id": claim["claim"]["proposition_id"],
        "evidence_world_id": evidence["evidence_world_id"],
        "claim_gate_output_sha256": claim["output_sha256"],
        "evidence_gate_output_sha256": evidence["output_sha256"],
        "receipt_sha256": bound["receipt_sha256"],
        "contract_a_handoff_sha256": bound["contract_a_handoff_sha256"],
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
        authoring.contract_a,
        receipt,
    )

    return PairedGateV1RC3Result(
        authoring=authoring,
        claim_gate=claim_gate,
        evidence_gate=evidence_gate,
        receipt=receipt,
    )
