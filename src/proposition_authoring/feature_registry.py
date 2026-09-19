from __future__ import annotations

from typing import Any

from .canonical import bound_object_hash

_AUTHORITY_LADDER = [
    "IMPLEMENTED_SHADOW",
    "QUALIFIED_DESCRIPTIVE",
    "QUALIFIED_HINT",
    "QUALIFIED_CAUSAL",
]


def _entry(
    field_id: str,
    producer: str,
    *,
    basis_types: tuple[str, ...],
    allowed_consumers: tuple[str, ...] = ("paired_preflight",),
    prohibited_effects: tuple[str, ...] = (
        "claim_authoring",
        "eb_query_construction",
        "eb_source_routing",
        "eb_ranking",
        "eb_admission",
        "cal_semantics",
        "decision_policy",
        "authorization",
    ),
    known_limits: tuple[str, ...] = (),
) -> dict[str, Any]:
    return {
        "field_id": field_id,
        "producer": producer,
        "implementation_status": "IMPLEMENTED_SHADOW",
        "authority_status": "IMPLEMENTED_SHADOW",
        "basis_types": list(basis_types),
        "allowed_consumers": list(allowed_consumers),
        "prohibited_effects": list(prohibited_effects),
        "qualification_records": [],
        "known_limits": list(known_limits),
    }


def build_feature_registry(implementation_identity: str = "runtime") -> dict[str, Any]:
    entries = [
        _entry("claim.claim_families", "ClaimGate", basis_types=("mechanical_text_pattern",)),
        _entry("claim.claim_structure_shape", "ClaimGate", basis_types=("mechanical_surface_shape",)),
        _entry("claim.entities", "ClaimGate", basis_types=("bounded_relation_parse",)),
        _entry("claim.relation_targets", "ClaimGate", basis_types=("bounded_relation_parse",)),
        _entry("claim.domain", "ClaimGate", basis_types=("task_declaration",)),
        _entry("claim.verification_world", "ClaimGate", basis_types=("task_declaration",)),
        _entry(
            "claim.temporal_scope",
            "ClaimGate",
            basis_types=("task_declaration", "mechanical_text_pattern"),
        ),
        _entry("claim.jurisdiction", "ClaimGate", basis_types=("task_declaration",)),
        _entry("claim.expected_evidence_forms", "ClaimGate", basis_types=("claim_family_mapping",)),
        _entry("claim.context_dependence", "ClaimGate", basis_types=("request_structure",)),
        _entry("claim.scope_ambiguity", "ClaimGate", basis_types=("mechanical_surface_shape",)),
        _entry("claim.negation", "ClaimGate", basis_types=("mechanical_text_pattern",)),
        _entry("claim.modality", "ClaimGate", basis_types=("mechanical_text_pattern",)),
        _entry("claim.attribution", "ClaimGate", basis_types=("mechanical_text_pattern",)),
        _entry("evidence.source_identity", "EvidenceGate", basis_types=("supplied_source",)),
        _entry("evidence.content_identity", "EvidenceGate", basis_types=("content_hash",)),
        _entry("evidence.provenance", "EvidenceGate", basis_types=("source_metadata",)),
        _entry("evidence.issuer", "EvidenceGate", basis_types=("source_metadata",)),
        _entry("evidence.source_role", "EvidenceGate", basis_types=("source_metadata",)),
        _entry("evidence.authority_basis", "EvidenceGate", basis_types=("source_metadata",)),
        _entry(
            "evidence.document_type",
            "EvidenceGate",
            basis_types=("source_metadata", "media_type_mapping"),
        ),
        _entry(
            "evidence.evidence_form",
            "EvidenceGate",
            basis_types=("source_metadata", "media_type_mapping"),
        ),
        _entry("evidence.temporal_coverage", "EvidenceGate", basis_types=("source_metadata",)),
        _entry("evidence.jurisdictional_coverage", "EvidenceGate", basis_types=("source_metadata",)),
        _entry("evidence.version", "EvidenceGate", basis_types=("source_metadata",)),
        _entry("evidence.currency_state", "EvidenceGate", basis_types=("source_metadata",)),
        _entry("evidence.duplicate_source_groups", "EvidenceGate", basis_types=("content_hash",)),
        _entry("evidence.conflict_observations", "EvidenceGate", basis_types=("source_metadata",)),
        _entry("evidence.supersession_observations", "EvidenceGate", basis_types=("source_metadata",)),
        _entry("evidence.verification_world", "EvidenceGate", basis_types=("task_declaration",)),
        _entry("evidence.corpus_scope", "EvidenceGate", basis_types=("task_declaration",)),
        _entry("evidence.completeness_state", "EvidenceGate", basis_types=("task_declaration",)),
        _entry("evidence.known_gaps", "EvidenceGate", basis_types=("task_declaration",)),
        _entry("preflight.evidence_forms", "Preflight", basis_types=("profile_comparison",)),
        _entry("preflight.temporal_scope", "Preflight", basis_types=("profile_comparison",)),
        _entry("preflight.jurisdiction", "Preflight", basis_types=("profile_comparison",)),
        _entry("preflight.verification_world", "Preflight", basis_types=("profile_comparison",)),
        _entry("preflight.corpus_aperture", "Preflight", basis_types=("profile_observation",)),
        _entry("preflight.corpus_completeness", "Preflight", basis_types=("profile_observation",)),
        _entry("preflight.known_gaps", "Preflight", basis_types=("profile_observation",)),
        _entry(
            "preflight.missing_expected_evidence_forms",
            "Preflight",
            basis_types=("profile_comparison",),
        ),
    ]
    registry: dict[str, Any] = {
        "schema": "paired-gates-feature-registry-v0",
        "implementation_identity": implementation_identity,
        "authority_ladder": _AUTHORITY_LADDER,
        "default_authority": "IMPLEMENTED_SHADOW",
        "entries": entries,
        "cross_stage_rule": (
            "descriptive fields remain non-causal unless separately qualified and explicitly authorized"
        ),
    }
    registry["registry_sha256"] = bound_object_hash(registry, "registry_sha256")
    return registry


def assert_no_causal_authority(registry: dict[str, Any]) -> None:
    unauthorized = [
        row["field_id"]
        for row in registry.get("entries", [])
        if row.get("authority_status") in {"QUALIFIED_HINT", "QUALIFIED_CAUSAL"}
    ]
    if unauthorized:
        raise ValueError(f"capability-complete V0 forbids causal authority: {unauthorized}")


def qualified_hint_fields(registry: dict[str, Any]) -> tuple[str, ...]:
    return tuple(
        sorted(
            row["field_id"]
            for row in registry.get("entries", [])
            if row.get("authority_status") == "QUALIFIED_HINT"
        )
    )


def require_authority(
    registry: dict[str, Any], field_id: str, required_status: str
) -> dict[str, Any]:
    levels = {name: index for index, name in enumerate(_AUTHORITY_LADDER)}
    if required_status not in levels:
        raise ValueError(f"unsupported required authority status: {required_status}")
    matches = [row for row in registry.get("entries", []) if row.get("field_id") == field_id]
    if len(matches) != 1:
        raise ValueError(f"unknown or duplicate field id: {field_id}")
    row = matches[0]
    current = row.get("authority_status")
    if current not in levels or levels[current] < levels[required_status]:
        raise PermissionError(
            f"field {field_id} has {current!r}; requires {required_status!r}"
        )
    return row


def project_eb_hint(
    registry: dict[str, Any], values: dict[str, Any], requested_fields: tuple[str, ...]
) -> dict[str, Any]:
    projected: dict[str, Any] = {}
    for field_id in requested_fields:
        require_authority(registry, field_id, "QUALIFIED_HINT")
        if field_id not in values:
            raise ValueError(f"authorized field missing from projection values: {field_id}")
        projected[field_id] = values[field_id]
    return {
        "schema": "paired-gates-eb-hint-v0",
        "fields": projected,
        "nonclaims": [
            "does not prescribe source ids, domains, queries, passages, rank weights, or admission",
            "does not judge support or refutation",
        ],
    }
