from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .canonical import bound_object_hash
from .claim_profile import build_claim_profile, build_claim_profile_receipt
from .engine import AuthoringEngine
from .evidence_gate import build_evidence_world_profile, build_evidence_world_receipt
from .feature_registry import assert_no_causal_authority, build_feature_registry
from .model import AuthoringRequest, AuthoringResult
from .shadow_models import (
    UNKNOWN,
    CompatibilityObservation,
    PreflightCompatibilityV0,
    SourceMetadata,
    TaskMetadata,
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
    feature_registry: dict[str, Any]


def _scalar_compare(
    field: str, claim_value: str, evidence_values: list[str]
) -> CompatibilityObservation:
    if claim_value == UNKNOWN:
        return CompatibilityObservation(
            field,
            "not_applicable",
            claim_value,
            evidence_values,
            "claim value unknown",
        )
    if not evidence_values:
        return CompatibilityObservation(
            field,
            "unknown",
            claim_value,
            evidence_values,
            "evidence coverage absent",
        )
    if claim_value in evidence_values:
        return CompatibilityObservation(
            field,
            "match",
            claim_value,
            evidence_values,
            "exact declared/mechanical match",
        )
    return CompatibilityObservation(
        field,
        "mismatch",
        claim_value,
        evidence_values,
        "no exact declared/mechanical match",
    )


def _evidence_form_observations(
    claim_profile: dict[str, Any], evidence_profile: dict[str, Any]
) -> tuple[CompatibilityObservation, CompatibilityObservation]:
    expected = set(claim_profile.get("expected_evidence_forms", [])) - {UNKNOWN}
    available = set(evidence_profile.get("evidence_forms", [])) - {UNKNOWN}
    missing = sorted(expected - available)

    if not expected:
        form_obs = CompatibilityObservation(
            "evidence_forms",
            "not_applicable",
            sorted(expected),
            sorted(available),
            "claim expectation unknown",
        )
        missing_obs = CompatibilityObservation(
            "missing_expected_evidence_forms",
            "not_applicable",
            sorted(expected),
            missing,
            "claim expectation unknown",
        )
    elif not available:
        form_obs = CompatibilityObservation(
            "evidence_forms",
            "unknown",
            sorted(expected),
            sorted(available),
            "evidence forms unavailable",
        )
        missing_obs = CompatibilityObservation(
            "missing_expected_evidence_forms",
            "unknown",
            sorted(expected),
            missing,
            "available evidence forms unknown or absent",
        )
    elif expected <= available:
        form_obs = CompatibilityObservation(
            "evidence_forms",
            "match",
            sorted(expected),
            sorted(available),
            "all expected forms available",
        )
        missing_obs = CompatibilityObservation(
            "missing_expected_evidence_forms",
            "match",
            sorted(expected),
            [],
            "no expected form absent from characterized world",
        )
    elif expected & available:
        form_obs = CompatibilityObservation(
            "evidence_forms",
            "partial",
            sorted(expected),
            sorted(available),
            "some expected forms available",
        )
        missing_obs = CompatibilityObservation(
            "missing_expected_evidence_forms",
            "partial",
            sorted(expected),
            missing,
            "some expected forms absent from characterized world",
        )
    else:
        form_obs = CompatibilityObservation(
            "evidence_forms",
            "mismatch",
            sorted(expected),
            sorted(available),
            "no expected forms available",
        )
        missing_obs = CompatibilityObservation(
            "missing_expected_evidence_forms",
            "mismatch",
            sorted(expected),
            missing,
            "all expected forms absent from characterized world",
        )
    return form_obs, missing_obs


def _verification_world_observation(
    claim_profile: dict[str, Any], evidence_profile: dict[str, Any]
) -> CompatibilityObservation:
    claim_value = claim_profile.get("verification_world", UNKNOWN)
    evidence_value = evidence_profile.get("verification_world", UNKNOWN)
    if claim_value == UNKNOWN:
        state = "not_applicable"
        basis = "claim verification world unknown"
    elif evidence_value == UNKNOWN:
        state = "unknown"
        basis = "evidence verification world unknown"
    elif claim_value == evidence_value:
        state = "match"
        basis = "exact declared match"
    else:
        state = "mismatch"
        basis = "declared verification worlds differ"
    return CompatibilityObservation(
        "verification_world", state, claim_value, evidence_value, basis
    )


def _aperture_observation(evidence_profile: dict[str, Any]) -> CompatibilityObservation:
    inventory = evidence_profile.get("source_inventory", [])
    scope = evidence_profile.get("corpus_scope", UNKNOWN)
    if not inventory:
        state = "unknown"
        basis = "no supplied source inventory"
    else:
        state = "match"
        basis = "supplied source aperture is explicitly inventoried"
    return CompatibilityObservation(
        "corpus_aperture",
        state,
        "supplied_pre_retrieval_world",
        {"source_count": len(inventory), "corpus_scope": scope},
        basis,
    )


def _completeness_observation(evidence_profile: dict[str, Any]) -> CompatibilityObservation:
    value = str(evidence_profile.get("completeness_state", UNKNOWN))
    normalized = value.strip().lower()
    if normalized == UNKNOWN:
        state = "unknown"
        basis = "corpus completeness not declared"
    elif normalized in {"complete", "declared_complete", "closed_complete"}:
        state = "match"
        basis = "corpus declared complete; declaration is not independently proven"
    elif normalized in {"partial", "incomplete", "known_incomplete", "unavailable"}:
        state = "partial"
        basis = "corpus explicitly not complete/available"
    else:
        state = "unknown"
        basis = "unrecognized completeness declaration retained without interpretation"
    return CompatibilityObservation(
        "corpus_completeness",
        state,
        "not_applicable",
        value,
        basis,
    )


def _known_gaps_observation(evidence_profile: dict[str, Any]) -> CompatibilityObservation:
    gaps = list(evidence_profile.get("known_gaps", []))
    completeness = str(evidence_profile.get("completeness_state", UNKNOWN)).lower()
    if gaps:
        state = "partial"
        basis = "explicit known gaps declared"
    elif completeness in {"complete", "declared_complete", "closed_complete"}:
        state = "match"
        basis = "no known gaps declared in a declared-complete world"
    else:
        state = "unknown"
        basis = "absence of declared gaps is not evidence of completeness"
    return CompatibilityObservation("known_gaps", state, "not_applicable", gaps, basis)


def compare_profiles(
    claim_profile: dict[str, Any], evidence_profile: dict[str, Any]
) -> dict[str, Any]:
    evidence_form_obs, missing_form_obs = _evidence_form_observations(
        claim_profile, evidence_profile
    )
    compatibility = PreflightCompatibilityV0(
        observations=(
            evidence_form_obs,
            missing_form_obs,
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
            _verification_world_observation(claim_profile, evidence_profile),
            _aperture_observation(evidence_profile),
            _completeness_observation(evidence_profile),
            _known_gaps_observation(evidence_profile),
        ),
        notes=(
            "shadow-only; observations describe compatibility/aperture and do not control EB or CAL",
            "complete/partial/mismatch states are preflight observations, not evidence sufficiency judgments",
        ),
    ).as_dict()
    compatibility["compatibility_sha256"] = bound_object_hash(
        compatibility, "compatibility_sha256"
    )
    return compatibility


def build_compatibility_receipt(
    claim_profile: dict[str, Any],
    evidence_profile: dict[str, Any],
    compatibility: dict[str, Any],
    feature_registry: dict[str, Any],
) -> dict[str, Any]:
    receipt = {
        "schema": "preflight-compatibility-receipt-v0",
        "claim_profile_sha256": claim_profile["profile_sha256"],
        "evidence_world_profile_sha256": evidence_profile["profile_sha256"],
        "compatibility_sha256": compatibility["compatibility_sha256"],
        "feature_registry_sha256": feature_registry["registry_sha256"],
        "authority_conferring": False,
        "nonclaims": [
            "does not judge support or refutation",
            "does not instruct retrieval",
            "does not alter Contract A or Contract B",
            "does not authorize action",
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
    implementation_identity: str = "runtime",
) -> PairedPreflightResult:
    authoring_engine = engine or AuthoringEngine()
    authoring = authoring_engine.author(request)
    feature_registry = build_feature_registry(implementation_identity)
    assert_no_causal_authority(feature_registry)
    claim_profile = build_claim_profile(request, claim_task)
    claim_receipt = build_claim_profile_receipt(request, claim_profile)
    evidence_profile = build_evidence_world_profile(
        request,
        task=evidence_task,
        source_metadata=source_metadata,
    )
    evidence_receipt = build_evidence_world_receipt(request, evidence_profile)
    compatibility = compare_profiles(claim_profile, evidence_profile)
    compatibility_receipt = build_compatibility_receipt(
        claim_profile,
        evidence_profile,
        compatibility,
        feature_registry,
    )
    return PairedPreflightResult(
        authoring=authoring,
        claim_profile=claim_profile,
        claim_profile_receipt=claim_receipt,
        evidence_world_profile=evidence_profile,
        evidence_world_receipt=evidence_receipt,
        compatibility=compatibility,
        compatibility_receipt=compatibility_receipt,
        feature_registry=feature_registry,
    )
