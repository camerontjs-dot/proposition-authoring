from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

CompatibilityState = Literal["match", "mismatch", "partial", "unknown", "not_applicable"]
AuthorityStatus = Literal[
    "IMPLEMENTED_SHADOW",
    "QUALIFIED_DESCRIPTIVE",
    "QUALIFIED_HINT",
    "QUALIFIED_CAUSAL",
    "FALSIFIED",
    "SUPERSEDED",
]
UNKNOWN = "unknown"


@dataclass(frozen=True)
class ObservationBasis:
    kind: str
    detail: str
    source_ref: str = UNKNOWN

    def as_dict(self) -> dict[str, str]:
        return {
            "kind": self.kind,
            "detail": self.detail,
            "source_ref": self.source_ref,
        }


@dataclass(frozen=True)
class TaskMetadata:
    domain: str = UNKNOWN
    verification_world: str = UNKNOWN
    temporal_scope: str = UNKNOWN
    jurisdiction: str = UNKNOWN
    corpus_scope: str = UNKNOWN
    completeness_state: str = UNKNOWN
    known_gaps: tuple[str, ...] = ()


@dataclass(frozen=True)
class SourceMetadata:
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
    supersedes: tuple[str, ...] = ()
    conflicts_with: tuple[str, ...] = ()


@dataclass(frozen=True)
class ClaimProfileV0:
    root_id: str
    claim_families: tuple[str, ...]
    expected_evidence_forms: tuple[str, ...]
    claim_structure_shape: str = UNKNOWN
    entities: tuple[str, ...] = ()
    relation_targets: tuple[str, ...] = ()
    domain: str = UNKNOWN
    verification_world: str = UNKNOWN
    temporal_scope: str = UNKNOWN
    jurisdiction: str = UNKNOWN
    context_dependence: str = UNKNOWN
    scope_ambiguity: str = UNKNOWN
    negation: str = UNKNOWN
    modality: str = UNKNOWN
    attribution: str = UNKNOWN
    field_basis: tuple[tuple[str, tuple[dict[str, str], ...]], ...] = ()
    notes: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, Any]:
        return {
            "schema": "claim-profile-v0",
            "root_id": self.root_id,
            "claim_families": list(self.claim_families),
            "expected_evidence_forms": list(self.expected_evidence_forms),
            "claim_structure_shape": self.claim_structure_shape,
            "entities": list(self.entities),
            "relation_targets": list(self.relation_targets),
            "domain": self.domain,
            "verification_world": self.verification_world,
            "temporal_scope": self.temporal_scope,
            "jurisdiction": self.jurisdiction,
            "context_dependence": self.context_dependence,
            "scope_ambiguity": self.scope_ambiguity,
            "negation": self.negation,
            "modality": self.modality,
            "attribution": self.attribution,
            "field_basis": {key: list(rows) for key, rows in self.field_basis},
            "notes": list(self.notes),
        }


@dataclass(frozen=True)
class EvidenceWorldProfileV0:
    source_inventory: tuple[dict[str, Any], ...]
    evidence_forms: tuple[str, ...]
    source_roles: tuple[str, ...]
    temporal_coverage: tuple[str, ...]
    jurisdictional_coverage: tuple[str, ...]
    issuers: tuple[str, ...] = ()
    document_types: tuple[str, ...] = ()
    currency_states: tuple[str, ...] = ()
    duplicate_source_groups: tuple[tuple[str, ...], ...] = ()
    conflict_observations: tuple[tuple[str, str], ...] = ()
    supersession_observations: tuple[tuple[str, str], ...] = ()
    verification_world: str = UNKNOWN
    corpus_scope: str = UNKNOWN
    completeness_state: str = UNKNOWN
    known_gaps: tuple[str, ...] = ()
    field_basis: tuple[tuple[str, tuple[dict[str, str], ...]], ...] = ()

    def as_dict(self) -> dict[str, Any]:
        return {
            "schema": "evidence-world-profile-v0",
            "source_inventory": list(self.source_inventory),
            "evidence_forms": list(self.evidence_forms),
            "source_roles": list(self.source_roles),
            "temporal_coverage": list(self.temporal_coverage),
            "jurisdictional_coverage": list(self.jurisdictional_coverage),
            "issuers": list(self.issuers),
            "document_types": list(self.document_types),
            "currency_states": list(self.currency_states),
            "duplicate_source_groups": [list(row) for row in self.duplicate_source_groups],
            "conflict_observations": [list(row) for row in self.conflict_observations],
            "supersession_observations": [list(row) for row in self.supersession_observations],
            "verification_world": self.verification_world,
            "corpus_scope": self.corpus_scope,
            "completeness_state": self.completeness_state,
            "known_gaps": list(self.known_gaps),
            "field_basis": {key: list(rows) for key, rows in self.field_basis},
        }


@dataclass(frozen=True)
class CompatibilityObservation:
    field: str
    state: CompatibilityState
    claim_value: Any
    evidence_value: Any
    basis: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "field": self.field,
            "state": self.state,
            "claim_value": self.claim_value,
            "evidence_value": self.evidence_value,
            "basis": self.basis,
        }


@dataclass(frozen=True)
class PreflightCompatibilityV0:
    observations: tuple[CompatibilityObservation, ...]
    notes: tuple[str, ...] = field(default_factory=tuple)

    def as_dict(self) -> dict[str, Any]:
        return {
            "schema": "preflight-compatibility-v0",
            "observations": [row.as_dict() for row in self.observations],
            "notes": list(self.notes),
        }
