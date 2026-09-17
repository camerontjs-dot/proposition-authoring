from __future__ import annotations

import json

from proposition_authoring.claim_profile import build_claim_profile
from proposition_authoring.engine import AuthoringEngine
from proposition_authoring.evidence_gate import build_evidence_world_profile
from proposition_authoring.model import AuthoringRequest, SourceRepresentation
from proposition_authoring.preflight import compare_profiles, run_paired_preflight
from proposition_authoring.shadow_models import SourceMetadata, TaskMetadata


def _request(sources: tuple[SourceRepresentation, ...] | None = None) -> AuthoringRequest:
    return AuthoringRequest(
        handoff_id="handoff-shadow-1",
        producer_id="test",
        producer_version="0",
        work_id="work-shadow-1",
        root_id="claim-shadow-1",
        root_text="Unit Amber approved File A.",
        sources=sources or (),
    )


def test_shadow_wrapper_does_not_change_authoring_result() -> None:
    request = _request()
    direct = AuthoringEngine().author(request)
    shadow = run_paired_preflight(request)
    assert shadow.authoring.state == direct.state
    assert shadow.authoring.reason == direct.reason
    assert shadow.authoring.contract_a == direct.contract_a
    assert shadow.authoring.receipt == direct.receipt


def test_claim_profile_characterizes_without_authoring_authority() -> None:
    request = AuthoringRequest(
        handoff_id="h",
        producer_id="p",
        producer_version="0",
        work_id="w",
        root_id="c",
        root_text="Drug A had 20% higher response than Drug B in 2025.",
    )
    profile = build_claim_profile(
        request,
        TaskMetadata(domain="healthcare", verification_world="open", jurisdiction="Canada"),
    )
    assert {"comparative", "numeric", "temporal"} <= set(profile["claim_families"])
    assert "measurement" in profile["expected_evidence_forms"]
    assert profile["temporal_scope"] == "2025"
    assert profile["domain"] == "healthcare"
    assert profile["verification_world"] == "open"
    assert profile["jurisdiction"] == "Canada"


def test_evidence_world_is_source_order_invariant() -> None:
    a = SourceRepresentation("s-a", "application/pdf", "alpha")
    b = SourceRepresentation("s-b", "application/json", "beta")
    metadata = (
        SourceMetadata("s-a", provenance="issuer-a", source_role="primary", temporal_coverage="2025"),
        SourceMetadata("s-b", provenance="issuer-b", source_role="registry", jurisdictional_coverage="Canada"),
    )
    first = build_evidence_world_profile(_request((a, b)), source_metadata=metadata)
    second = build_evidence_world_profile(_request((b, a)), source_metadata=metadata)
    assert first == second


def test_evidence_content_mutation_changes_profile_identity() -> None:
    first = build_evidence_world_profile(
        _request((SourceRepresentation("s", "text/plain", "alpha"),))
    )
    second = build_evidence_world_profile(
        _request((SourceRepresentation("s", "text/plain", "changed"),))
    )
    assert first["profile_sha256"] != second["profile_sha256"]


def test_unknowns_are_not_forced() -> None:
    request = _request((SourceRepresentation("s", "application/octet-stream", "bytes"),))
    claim = build_claim_profile(request)
    world = build_evidence_world_profile(request)
    assert claim["domain"] == "unknown"
    assert claim["verification_world"] == "unknown"
    assert claim["jurisdiction"] == "unknown"
    assert world["verification_world"] == "unknown"
    assert world["source_inventory"][0]["evidence_form"] == "unknown"


def test_preflight_is_observational_only() -> None:
    claim = {
        "expected_evidence_forms": ["measurement", "document_text"],
        "temporal_scope": "2025",
        "jurisdiction": "Canada",
        "verification_world": "closed",
    }
    world = {
        "evidence_forms": ["document_text"],
        "temporal_coverage": ["2025"],
        "jurisdictional_coverage": ["Canada"],
        "verification_world": "closed",
    }
    result = compare_profiles(claim, world)
    states = {row["field"]: row["state"] for row in result["observations"]}
    assert states["evidence_forms"] == "partial"
    assert states["temporal_scope"] == "match"
    assert states["jurisdiction"] == "match"
    assert states["verification_world"] == "match"
    serialized = json.dumps(result).lower()
    for forbidden in ("supports", "refutes", "retrieve", "rank", "admit"):
        assert forbidden not in serialized
