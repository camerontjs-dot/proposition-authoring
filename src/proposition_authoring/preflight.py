from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .canonical import bound_object_hash
from .claim_profile import build_claim_profile, build_claim_profile_receipt
from .engine import AuthoringEngine
from .evidence_gate import build_evidence_world_profile, build_evidence_world_receipt
from .model import AuthoringRequest, AuthoringResult
from .shadow_models import (
    CompatibilityObservation,
    PreflightCompatibilityV0,
    SourceMetadata,
    TaskMetadata,
    UNKNOWN,
)


@dataclass(frozen=True)
class PairedPreflightResult:
    authoring: AuthoringResult
    claim_profile: dict[str, Any]
    claim_profile_receipt: dict[str, Any]
    evidence_world_profile: dict[str, Any]
    evidence_world_receipt: dict[str, Any]
    compatibility: dict[str, Any]
    compatibility_receipt: dict[str, Any]


def _scalar_compare(field: str, claim_value: str, evidence_values: list[str]) -> CompatibilityObservation:
    if claim_value == UNKNOWN:
        return CompatibilityObservation(field, "not_applicable", claim_value, evidence_values, "claim value unknown")
    if not evidence_values:
        return CompatibilityObservation(field, "unknown", claim_value, evidence_values, "evidence coverage absent")
    if claim_value in evidence_values:
        return CompatibilityObservation(field, "match", claim_value, evidence_values, "exact declared/mechanical match")
    return CompatibilityObservation(field, "mismatch", claim_value, evidence_values, "no exact declared/mechanical match")


def compare_profiles(claim_profile: dict[str, Any], evidence_profile: dict[str, Any]) -> dict[str, Any]:
    expected = set(claim_profile.get("expected_evidence_forms", [])) - {UNKNOWN}
    available = set(evidence_profile.get("evidence_forms", [])) - {UNKNOWN}
    if not expected:
        evidence_form_obs = CompatibilityObservation(
            "evidence_forms", "not_applicable", sorted(expected), sorted(available), "claim expectation unknown"
        )
    elif not available:
        evidence_form_obs = CompatibilityObservation(
            "evidence_forms", "unknown", sorted(expected), sorted(available), "evidence forms unavailable"
        )
    elif expected <= available:
        evidence_form_obs = CompatibilityObservation(
            "evidence_forms", "match", sorted(expected), sorted(available), "all expected forms available"
        )
    elif expected & available:
        evidence_form_obs = CompatibilityObservation(
            "evidence_forms", "partial", sorted(expected), sorted(available), "some expected forms available"
        )
    else:
        evidence_form_obs = CompatibilityObservation(
            "evidence_forms", "mismatch", sorted(expected), sorted(available), "no expected forms available"
        )

    verification_claim = claim_profile.get("verification_world", UNKNOWN)
    verification_evidence = evidence_profile.get("verification_world", UNKNOWN)
    if verification_claim == UNKNOWN:
        verification_obs = CompatibilityObservation(
            "verification_world", "not_applicable", verification_claim, verification_evidence, "claim verification world unknown"
        )
    elif verification_evidence == UNKNOWN:
        verification_obs = CompatibilityObservation(
            "verification_world", "unknown", verification_claim, verification_evidence, "evidence verification world unknown"
        )
    elif verification_claim == verification_evidence:
        verification_obs = CompatibilityObservation(
            "verification_world", "match", verification_claim, verification_evidence, "exact declared match"
        )
    else:
        verification_obs = CompatibilityObservation(
            "verification_world", "mismatch", verification_claim, verification_evidence, "declared verification worlds differ"
        )

    compatibility = PreflightCompatibilityV0(
        observations=(
            evidence_form_obs,
            _scalar_compare(
                "temporal_scope",
                claim_profile.get("temporal_scope", UNKNOWN),
                list(evidence_profile.get("temporal_coverage", [])),
            ),
            _scalar_compare(
                "jurisdiction",
                claim_profile.get("jurisdiction", UNKNOWN),
                list(evidence_profile.get("jurisdictional_coverage", [])),
            ),
            verification_obs,
        ),
        notes=("shadow-only; emits observations, not retrieval or CAL instructions",),
    ).as_dict()
    compatibility["compatibility_sha256"] = bound_object_hash(
        compatibility, "compatibility_sha256"
    )
    return compatibility


def build_compatibility_receipt(
    claim_profile: dict[str, Any], evidence_profile: dict[str, Any], compatibility: dict[str, Any]
) -> dict[str, Any]:
    receipt = {
        "schema": "preflight-compatibility-receipt-v0",
        "claim_profile_sha256": claim_profile["profile_sha256"],
        "evidence_world_profile_sha256": evidence_profile["profile_sha256"],
        "compatibility_sha256": compatibility["compatibility_sha256"],
        "authority_conferring": False,
        "nonclaims": [
            "does not judge support or refutation",
            "does not instruct retrieval",
            "does not alter Contract A or Contract B",
        ],
    }
    receipt["receipt_sha256"] = bound_object_hash(receipt, "receipt_sha256")
    return receipt


def run_paired_preflight(
    request: AuthoringRequest,
    *,
    claim_task: TaskMetadata | None = None,
    evidence_task: TaskMetadata | None = None,
    source_metadata: tuple[SourceMetadata, ...] = (),
    engine: AuthoringEngine | None = None,
) -> PairedPreflightResult:
    authoring_engine = engine or AuthoringEngine()
    authoring = authoring_engine.author(request)
    claim_profile = build_claim_profile(request, claim_task)
    claim_receipt = build_claim_profile_receipt(request, claim_profile)
    evidence_profile = build_evidence_world_profile(
        request, task=evidence_task, source_metadata=source_metadata
    )
    evidence_receipt = build_evidence_world_receipt(request, evidence_profile)
    compatibility = compare_profiles(claim_profile, evidence_profile)
    compatibility_receipt = build_compatibility_receipt(
        claim_profile, evidence_profile, compatibility
    )
    return PairedPreflightResult(
        authoring=authoring,
        claim_profile=claim_profile,
        claim_profile_receipt=claim_receipt,
        evidence_world_profile=evidence_profile,
        evidence_world_receipt=evidence_receipt,
        compatibility=compatibility,
        compatibility_receipt=compatibility_receipt,
    )
