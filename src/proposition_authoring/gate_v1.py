from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Literal

from .canonical import bound_object_hash, canonical_json, sha256_bytes, sha256_text
from .engine import AuthoringEngine
from .model import AuthoringRequest, AuthoringResult

UNKNOWN = "unknown"
CLAIM_GATE_SCHEMA = "claim-gate-output-v1"
EVIDENCE_GATE_SCHEMA = "evidence-gate-output-v1"
STANDARDIZATION_RECEIPT_SCHEMA = "paired-gates-standardization-receipt-v1"
GATE_VERSION = "1.0.0"

ClaimCategory = Literal[
    "comparative",
    "causal",
    "attribution",
    "quantitative",
    "temporal",
    "definitional",
    "existence",
    "status",
    "compliance",
    "other",
]
GapDeclarationState = Literal["unknown", "declared_none", "declared_some"]

_MEDIA_TO_FORM = {
    "application/pdf": "document_text",
    "text/plain": "document_text",
    "text/markdown": "document_text",
    "text/html": "document_text",
    "text/csv": "database_record",
    "application/json": "database_record",
    "application/xml": "database_record",
}
_MEDIA_TO_DOCUMENT_TYPE = {
    "application/pdf": "pdf_document",
    "text/plain": "text_document",
    "text/markdown": "markdown_document",
    "text/html": "html_document",
    "text/csv": "tabular_record",
    "application/json": "structured_record",
    "application/xml": "structured_record",
}

_CATEGORY_PATTERNS: tuple[tuple[ClaimCategory, re.Pattern[str]], ...] = (
    (
        "comparative",
        re.compile(
            r"\b(more|less|higher|lower|greater|fewer|than|compared|versus|vs\.?|exceed(?:s|ed)?)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "causal",
        re.compile(
            r"\b(because|caus(?:e|ed|es)|led to|result(?:ed|s)? in|due to)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "attribution",
        re.compile(
            r"\b(reported|stated|claimed|said|asserted|concluded|observed|confirmed|indicated|showed|found)\b|\baccording to\b",
            re.IGNORECASE,
        ),
    ),
    (
        "quantitative",
        re.compile(
            r"(?:\b\d+(?:\.\d+)?\b|%|\b(rate|count|mean|median|average|variance|standard deviation|percentage|percent)\b)",
            re.IGNORECASE,
        ),
    ),
    (
        "temporal",
        re.compile(
            r"\b(?:19|20)\d{2}\b|\b(as of|before|after|during|since|between|from|until|through)\b",
            re.IGNORECASE,
        ),
    ),
    ("definitional", re.compile(r"\b(means|defined as|refers to)\b", re.IGNORECASE)),
    ("existence", re.compile(r"\b(exists?|there (?:is|are)|contains?|includes?)\b", re.IGNORECASE)),
    (
        "status",
        re.compile(
            r"\b(active|inactive|approved|compliant|ready|failed|passed|rejected|revoked|expired|open|closed)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "compliance",
        re.compile(
            r"\b(compliant|compliance|regulation|regulatory|regulated|requirement|requirements)\b",
            re.IGNORECASE,
        ),
    ),
)


class GateV1Error(ValueError):
    pass


@dataclass(frozen=True)
class SourceMetadataV1:
    source_id: str
    provenance: str = UNKNOWN
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
class EvidenceTaskV1:
    verification_world: str = UNKNOWN
    corpus_scope: str = UNKNOWN
    completeness_state: str = UNKNOWN
    known_gaps_state: GapDeclarationState = "unknown"
    known_gaps: tuple[str, ...] = ()


@dataclass(frozen=True)
class PairedGateV1Result:
    authoring: AuthoringResult
    claim_gate: dict[str, Any]
    evidence_gate: dict[str, Any]
    receipt: dict[str, Any]


def _normalized_media_type(media_type: str) -> str:
    return media_type.split(";", 1)[0].strip().lower()


def _basis(kind: str, detail: str, source_ref: str | None = None) -> dict[str, str]:
    row = {"kind": kind, "detail": detail}
    if source_ref is not None:
        row["source_ref"] = source_ref
    return row


def _observed(value: str, *, kind: str, detail: str, source_ref: str | None = None) -> dict[str, Any]:
    if value == UNKNOWN:
        return {
            "state": "unknown",
            "value": None,
            "basis": _basis("no_basis", detail, source_ref),
        }
    return {
        "state": "known",
        "value": value,
        "basis": _basis(kind, detail, source_ref),
    }


def classify_claim_v1(text: str) -> tuple[ClaimCategory, ...]:
    found = {name for name, pattern in _CATEGORY_PATTERNS if pattern.search(text)}
    if not found:
        return ("other",)
    return tuple(sorted(found))


def _claim_decomposition(result: AuthoringResult) -> dict[str, Any]:
    if result.contract_a is None:
        return {
            "state": "unresolved",
            "basis": _basis("authoring_state", f"ClaimGate ended {result.state}: {result.reason}"),
        }
    return dict(result.contract_a["decomposition"])


def build_claim_gate_output_v1(
    request: AuthoringRequest,
    result: AuthoringResult,
    *,
    implementation_identity: str = "runtime",
) -> dict[str, Any]:
    categories = classify_claim_v1(request.root_text)
    contract_a_binding: dict[str, Any]
    if result.contract_a is None:
        contract_a_binding = {"state": "absent", "handoff_sha256": None}
    else:
        expected_root = result.contract_a.get("root_proposition", {})
        if expected_root.get("proposition_id") != request.root_id:
            raise GateV1Error("Contract A root proposition identity disagrees with ClaimGate request")
        if expected_root.get("text_sha256") != sha256_text(request.root_text):
            raise GateV1Error("Contract A root proposition hash disagrees with ClaimGate request")
        contract_a_binding = {
            "state": "present",
            "handoff_sha256": result.contract_a["handoff_sha256"],
        }

    out: dict[str, Any] = {
        "schema": CLAIM_GATE_SCHEMA,
        "version": GATE_VERSION,
        "implementation_identity": implementation_identity,
        "authoring": {"state": result.state, "reason": result.reason},
        "claim": {
            "proposition_id": request.root_id,
            "text": request.root_text,
            "text_sha256": sha256_text(request.root_text),
            "categories": {
                "state": "known",
                "values": list(categories),
                "basis": _basis(
                    "bounded_classifier_v1",
                    "finite lexical category standardizer; descriptive only",
                ),
            },
        },
        "lineage": {
            "handoff_id": request.handoff_id,
            "producer_id": request.producer_id,
            "producer_version": request.producer_version,
            "work_id": request.work_id,
            "decomposition": _claim_decomposition(result),
        },
        "contract_a_binding": contract_a_binding,
        "authority": {
            "standardizes_claim_identity": True,
            "standardizes_claim_category": True,
            "standardizes_decomposition_lineage": True,
            "retrieval_authority": False,
            "evidence_relation_authority": False,
            "decision_authority": False,
            "authorization_authority": False,
        },
    }
    out["output_sha256"] = bound_object_hash(out, "output_sha256")
    return out


def _metadata_index(rows: tuple[SourceMetadataV1, ...], source_ids: set[str]) -> dict[str, SourceMetadataV1]:
    index: dict[str, SourceMetadataV1] = {}
    for row in rows:
        if row.source_id not in source_ids:
            raise GateV1Error(f"metadata references unsupplied source: {row.source_id}")
        if row.source_id in index:
            raise GateV1Error(f"duplicate metadata row for source: {row.source_id}")
        index[row.source_id] = row
    return index


def _effective_document_type(media_type: str, declared: str) -> tuple[str, str, str]:
    if declared != UNKNOWN:
        return declared, "source_metadata", "declared document type"
    value = _MEDIA_TO_DOCUMENT_TYPE.get(_normalized_media_type(media_type), UNKNOWN)
    if value == UNKNOWN:
        return UNKNOWN, "no_basis", "document type unavailable"
    return value, "media_type_mapping", "document type derived from normalized media type"


def _effective_evidence_form(media_type: str, declared: str) -> tuple[str, str, str]:
    if declared != UNKNOWN:
        return declared, "source_metadata", "declared evidence form"
    value = _MEDIA_TO_FORM.get(_normalized_media_type(media_type), UNKNOWN)
    if value == UNKNOWN:
        return UNKNOWN, "no_basis", "evidence form unavailable"
    return value, "media_type_mapping", "evidence form derived from normalized media type"


def _gap_declaration(task: EvidenceTaskV1) -> dict[str, Any]:
    values = sorted(set(task.known_gaps))
    if task.known_gaps_state == "unknown":
        if values:
            raise GateV1Error("known gaps cannot be supplied while known_gaps_state is unknown")
        return {
            "state": "unknown",
            "values": [],
            "basis": _basis("no_basis", "no gap declaration supplied"),
        }
    if task.known_gaps_state == "declared_none":
        if values:
            raise GateV1Error("declared_none known-gaps state cannot contain gap values")
        return {
            "state": "declared_none",
            "values": [],
            "basis": _basis("task_declaration", "task explicitly declares no known gaps"),
        }
    if task.known_gaps_state == "declared_some":
        if not values:
            raise GateV1Error("declared_some known-gaps state requires at least one gap")
        return {
            "state": "declared_some",
            "values": values,
            "basis": _basis("task_declaration", "task explicitly declares known gaps"),
        }
    raise GateV1Error(f"unknown known-gaps state: {task.known_gaps_state}")


def build_evidence_gate_output_v1(
    request: AuthoringRequest,
    *,
    task: EvidenceTaskV1 | None = None,
    source_metadata: tuple[SourceMetadataV1, ...] = (),
    implementation_identity: str = "runtime",
) -> dict[str, Any]:
    task = task or EvidenceTaskV1()
    source_ids = [source.source_id for source in request.sources]
    if len(set(source_ids)) != len(source_ids):
        raise GateV1Error("EvidenceGate V1 requires unique supplied source_id values")
    by_id = _metadata_index(source_metadata, set(source_ids))

    sources: list[dict[str, Any]] = []
    identity_projection: list[dict[str, str]] = []
    for source in sorted(request.sources, key=lambda row: row.source_id):
        meta = by_id.get(source.source_id, SourceMetadataV1(source_id=source.source_id))
        document_type, document_kind, document_detail = _effective_document_type(
            source.media_type, meta.document_type
        )
        evidence_form, form_kind, form_detail = _effective_evidence_form(
            source.media_type, meta.evidence_form
        )
        content_sha256 = sha256_text(source.content)
        identity_projection.append(
            {"source_id": source.source_id, "content_sha256": content_sha256}
        )
        sources.append(
            {
                "source_id": source.source_id,
                "media_type": source.media_type,
                "content_sha256": content_sha256,
                "provenance": {
                    "origin": _observed(
                        meta.provenance,
                        kind="source_metadata",
                        detail="source provenance/origin declaration unavailable" if meta.provenance == UNKNOWN else "declared source provenance/origin",
                        source_ref=source.source_id,
                    ),
                    "issuer": _observed(
                        meta.issuer,
                        kind="source_metadata",
                        detail="issuer declaration unavailable" if meta.issuer == UNKNOWN else "declared issuer",
                        source_ref=source.source_id,
                    ),
                    "source_role": _observed(
                        meta.source_role,
                        kind="source_metadata",
                        detail="source-role declaration unavailable" if meta.source_role == UNKNOWN else "declared source role",
                        source_ref=source.source_id,
                    ),
                    "authority_basis": _observed(
                        meta.authority_basis,
                        kind="source_metadata",
                        detail="authority-basis declaration unavailable" if meta.authority_basis == UNKNOWN else "declared authority basis",
                        source_ref=source.source_id,
                    ),
                },
                "classification": {
                    "document_type": _observed(
                        document_type,
                        kind=document_kind,
                        detail=document_detail,
                        source_ref=source.source_id,
                    ),
                    "evidence_form": _observed(
                        evidence_form,
                        kind=form_kind,
                        detail=form_detail,
                        source_ref=source.source_id,
                    ),
                },
                "coverage": {
                    "temporal": _observed(
                        meta.temporal_coverage,
                        kind="source_metadata",
                        detail="temporal coverage unavailable" if meta.temporal_coverage == UNKNOWN else "declared temporal coverage",
                        source_ref=source.source_id,
                    ),
                    "jurisdiction": _observed(
                        meta.jurisdictional_coverage,
                        kind="source_metadata",
                        detail="jurisdictional coverage unavailable" if meta.jurisdictional_coverage == UNKNOWN else "declared jurisdictional coverage",
                        source_ref=source.source_id,
                    ),
                    "version": _observed(
                        meta.version,
                        kind="source_metadata",
                        detail="version unavailable" if meta.version == UNKNOWN else "declared source version",
                        source_ref=source.source_id,
                    ),
                    "currency": _observed(
                        meta.currency_state,
                        kind="source_metadata",
                        detail="currency state unavailable" if meta.currency_state == UNKNOWN else "declared currency state",
                        source_ref=source.source_id,
                    ),
                },
            }
        )

    evidence_world_id = "sha256:" + sha256_bytes(
        canonical_json(
            {"root_id": request.root_id, "sources": identity_projection}
        ).encode("utf-8")
    )[7:]
    out: dict[str, Any] = {
        "schema": EVIDENCE_GATE_SCHEMA,
        "version": GATE_VERSION,
        "implementation_identity": implementation_identity,
        "root_id": request.root_id,
        "evidence_world_id": evidence_world_id,
        "source_count": len(sources),
        "sources": sources,
        "corpus": {
            "verification_world": _observed(
                task.verification_world,
                kind="task_declaration",
                detail="verification world unavailable" if task.verification_world == UNKNOWN else "declared verification world",
            ),
            "scope": _observed(
                task.corpus_scope,
                kind="task_declaration",
                detail="corpus scope unavailable" if task.corpus_scope == UNKNOWN else "declared corpus scope",
            ),
            "completeness": _observed(
                task.completeness_state,
                kind="task_declaration",
                detail="completeness unavailable" if task.completeness_state == UNKNOWN else "declared completeness state",
            ),
            "known_gaps": _gap_declaration(task),
        },
        "authority": {
            "standardizes_evidence_identity": True,
            "standardizes_source_provenance": True,
            "standardizes_evidence_classification": True,
            "retrieval_authority": False,
            "evidence_relation_authority": False,
            "decision_authority": False,
            "authorization_authority": False,
        },
    }
    out["output_sha256"] = bound_object_hash(out, "output_sha256")
    return out


def _exact_keys(value: Any, expected: set[str], label: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != expected:
        actual = sorted(value) if isinstance(value, dict) else type(value).__name__
        raise GateV1Error(f"{label} key mismatch: {actual}")
    return value


def validate_claim_gate_output_v1(value: Any) -> dict[str, Any]:
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
    if row["schema"] != CLAIM_GATE_SCHEMA or row["version"] != GATE_VERSION:
        raise GateV1Error("ClaimGate V1 schema/version mismatch")
    if row["output_sha256"] != bound_object_hash(row, "output_sha256"):
        raise GateV1Error("ClaimGate V1 output hash mismatch")
    _exact_keys(row["authoring"], {"state", "reason"}, "claim_gate.authoring")
    claim = _exact_keys(
        row["claim"], {"proposition_id", "text", "text_sha256", "categories"}, "claim_gate.claim"
    )
    if claim["text_sha256"] != sha256_text(claim["text"]):
        raise GateV1Error("ClaimGate V1 claim text hash mismatch")
    categories = _exact_keys(claim["categories"], {"state", "values", "basis"}, "claim_gate.claim.categories")
    if categories["state"] != "known" or not isinstance(categories["values"], list) or not categories["values"]:
        raise GateV1Error("ClaimGate V1 categories must be a non-empty known list")
    allowed = {name for name, _ in _CATEGORY_PATTERNS} | {"other"}
    if any(value not in allowed for value in categories["values"]):
        raise GateV1Error("ClaimGate V1 contains unknown category")
    return row


def validate_evidence_gate_output_v1(value: Any) -> dict[str, Any]:
    row = _exact_keys(
        value,
        {
            "schema",
            "version",
            "implementation_identity",
            "root_id",
            "evidence_world_id",
            "source_count",
            "sources",
            "corpus",
            "authority",
            "output_sha256",
        },
        "evidence_gate",
    )
    if row["schema"] != EVIDENCE_GATE_SCHEMA or row["version"] != GATE_VERSION:
        raise GateV1Error("EvidenceGate V1 schema/version mismatch")
    if row["output_sha256"] != bound_object_hash(row, "output_sha256"):
        raise GateV1Error("EvidenceGate V1 output hash mismatch")
    if not isinstance(row["sources"], list) or row["source_count"] != len(row["sources"]):
        raise GateV1Error("EvidenceGate V1 source_count mismatch")
    source_ids: list[str] = []
    identity_projection: list[dict[str, str]] = []
    for index, source in enumerate(row["sources"]):
        source = _exact_keys(
            source,
            {"source_id", "media_type", "content_sha256", "provenance", "classification", "coverage"},
            f"evidence_gate.sources[{index}]",
        )
        source_ids.append(source["source_id"])
        identity_projection.append(
            {"source_id": source["source_id"], "content_sha256": source["content_sha256"]}
        )
    if source_ids != sorted(source_ids) or len(set(source_ids)) != len(source_ids):
        raise GateV1Error("EvidenceGate V1 sources must be unique and source_id sorted")
    expected_world = "sha256:" + sha256_bytes(
        canonical_json({"root_id": row["root_id"], "sources": identity_projection}).encode("utf-8")
    )[7:]
    if row["evidence_world_id"] != expected_world:
        raise GateV1Error("EvidenceGate V1 evidence_world_id mismatch")
    return row


def standardize_gates_v1(
    request: AuthoringRequest,
    *,
    evidence_task: EvidenceTaskV1 | None = None,
    source_metadata: tuple[SourceMetadataV1, ...] = (),
    engine: AuthoringEngine | None = None,
    implementation_identity: str = "runtime",
) -> PairedGateV1Result:
    authoring = (engine or AuthoringEngine()).author(request)
    claim_gate = build_claim_gate_output_v1(
        request,
        authoring,
        implementation_identity=implementation_identity,
    )
    evidence_gate = build_evidence_gate_output_v1(
        request,
        task=evidence_task,
        source_metadata=source_metadata,
        implementation_identity=implementation_identity,
    )
    validate_claim_gate_output_v1(claim_gate)
    validate_evidence_gate_output_v1(evidence_gate)
    receipt: dict[str, Any] = {
        "schema": STANDARDIZATION_RECEIPT_SCHEMA,
        "version": GATE_VERSION,
        "root_id": request.root_id,
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
    return PairedGateV1Result(
        authoring=authoring,
        claim_gate=claim_gate,
        evidence_gate=evidence_gate,
        receipt=receipt,
    )
