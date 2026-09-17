from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

CompatibilityState = Literal["match", "mismatch", "partial", "unknown", "not_applicable"]
UNKNOWN = "unknown"


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
    source_role: str = UNKNOWN
    evidence_form: str = UNKNOWN
    temporal_coverage: str = UNKNOWN
    jurisdictional_coverage: str = UNKNOWN


@dataclass(frozen=True)
class ClaimProfileV0:
    root_id: str
    claim_families: tuple[str, ...]
    expected_evidence_forms: tuple[str, ...]
    domain: str = UNKNOWN
    verification_world: str = UNKNOWN
    temporal_scope: str = UNKNOWN
    jurisdiction: str = UNKNOWN
    notes: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, Any]:
        return {
            "schema": "claim-profile-v0",
            "root_id": self.root_id,
            "claim_families": list(self.claim_families),
            "expected_evidence_forms": list(self.expected_evidence_forms),
            "domain": self.domain,
            "verification_world": self.verification_world,
            "temporal_scope": self.temporal_scope,
            "jurisdiction": self.jurisdiction,
            "notes": list(self.notes),
        }


@dataclass(frozen=True)
class EvidenceWorldProfileV0:
    source_inventory: tuple[dict[str, Any], ...]
    evidence_forms: tuple[str, ...]
    source_roles: tuple[str, ...]
    temporal_coverage: tuple[str, ...]
    jurisdictional_coverage: tuple[str, ...]
    verification_world: str = UNKNOWN
    corpus_scope: str = UNKNOWN
    completeness_state: str = UNKNOWN
    known_gaps: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, Any]:
        return {
            "schema": "evidence-world-profile-v0",
            "source_inventory": list(self.source_inventory),
            "evidence_forms": list(self.evidence_forms),
            "source_roles": list(self.source_roles),
            "temporal_coverage": list(self.temporal_coverage),
            "jurisdictional_coverage": list(self.jurisdictional_coverage),
            "verification_world": self.verification_world,
            "corpus_scope": self.corpus_scope,
            "completeness_state": self.completeness_state,
            "known_gaps": list(self.known_gaps),
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
