from __future__ import annotations

import json
import unittest
from pathlib import Path

from proposition_authoring.claim_profile import build_claim_profile
from proposition_authoring.engine import AuthoringEngine
from proposition_authoring.evidence_gate import build_evidence_world_profile
from proposition_authoring.model import AuthoringRequest, SourceRepresentation
from proposition_authoring.preflight import compare_profiles, run_paired_preflight
from proposition_authoring.shadow_models import SourceMetadata, TaskMetadata

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "integration" / "claimgate_v1_candidate" / "fixtures"


class PairedGatesShadowTests(unittest.TestCase):
    def request(
        self, sources: tuple[SourceRepresentation, ...] | None = None
    ) -> AuthoringRequest:
        return AuthoringRequest(
            handoff_id="handoff-shadow-1",
            producer_id="test",
            producer_version="0",
            work_id="work-shadow-1",
            root_id="claim-shadow-1",
            root_text="Unit Amber approved File A.",
            sources=sources or (),
        )

    def fixture_request(self, name: str) -> AuthoringRequest:
        raw = json.loads((FIXTURES / f"{name}.json").read_text(encoding="utf-8"))
        return AuthoringRequest(
            handoff_id=raw["handoff_id"],
            producer_id=raw["producer_id"],
            producer_version=raw["producer_version"],
            work_id=raw["work_id"],
            root_id=raw["root_id"],
            root_text=raw["root_text"],
            sources=tuple(SourceRepresentation(**row) for row in raw.get("sources", [])),
            context_source_id=raw.get("context_source_id"),
        )

    def test_shadow_wrapper_does_not_change_authoring_result(self) -> None:
        request = self.request()
        direct = AuthoringEngine().author(request)
        shadow = run_paired_preflight(request)
        self.assertEqual(shadow.authoring.state, direct.state)
        self.assertEqual(shadow.authoring.reason, direct.reason)
        self.assertEqual(shadow.authoring.contract_a, direct.contract_a)
        self.assertEqual(shadow.authoring.receipt, direct.receipt)

    def test_profiles_emit_for_all_frozen_front_door_states(self) -> None:
        expected = {
            "declared": "DECLARED",
            "not_needed": "NOT_NEEDED",
            "abstained": "ABSTAINED",
        }
        for fixture, state in expected.items():
            with self.subTest(fixture=fixture):
                request = self.fixture_request(fixture)
                direct = AuthoringEngine().author(request)
                shadow = run_paired_preflight(request)
                self.assertEqual(direct.state, state)
                self.assertEqual(shadow.authoring.state, state)
                self.assertEqual(shadow.authoring.contract_a, direct.contract_a)
                self.assertEqual(shadow.authoring.receipt, direct.receipt)
                self.assertTrue(shadow.claim_profile["profile_sha256"].startswith("sha256:"))
                self.assertTrue(
                    shadow.evidence_world_profile["profile_sha256"].startswith("sha256:")
                )

    def test_claim_profile_characterizes_without_authoring_authority(self) -> None:
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
            TaskMetadata(
                domain="healthcare",
                verification_world="open",
                jurisdiction="Canada",
            ),
        )
        self.assertTrue(
            {"comparative", "numeric", "temporal"} <= set(profile["claim_families"])
        )
        self.assertIn("measurement", profile["expected_evidence_forms"])
        self.assertEqual(profile["temporal_scope"], "2025")
        self.assertEqual(profile["domain"], "healthcare")
        self.assertEqual(profile["verification_world"], "open")
        self.assertEqual(profile["jurisdiction"], "Canada")

    def test_evidence_world_is_source_order_invariant(self) -> None:
        a = SourceRepresentation("s-a", "application/pdf", "alpha")
        b = SourceRepresentation("s-b", "application/json", "beta")
        metadata = (
            SourceMetadata(
                "s-a",
                provenance="issuer-a",
                source_role="primary",
                temporal_coverage="2025",
            ),
            SourceMetadata(
                "s-b",
                provenance="issuer-b",
                source_role="registry",
                jurisdictional_coverage="Canada",
            ),
        )
        first = build_evidence_world_profile(
            self.request((a, b)), source_metadata=metadata
        )
        second = build_evidence_world_profile(
            self.request((b, a)), source_metadata=metadata
        )
        self.assertEqual(first, second)

    def test_source_content_and_provenance_mutations_change_identity(self) -> None:
        request = self.request((SourceRepresentation("s", "text/plain", "alpha"),))
        baseline = build_evidence_world_profile(
            request,
            source_metadata=(SourceMetadata("s", provenance="issuer-a"),),
        )
        content_changed = build_evidence_world_profile(
            self.request((SourceRepresentation("s", "text/plain", "changed"),)),
            source_metadata=(SourceMetadata("s", provenance="issuer-a"),),
        )
        provenance_changed = build_evidence_world_profile(
            request,
            source_metadata=(SourceMetadata("s", provenance="issuer-b"),),
        )
        self.assertNotEqual(
            baseline["profile_sha256"], content_changed["profile_sha256"]
        )
        self.assertNotEqual(
            baseline["profile_sha256"], provenance_changed["profile_sha256"]
        )

    def test_media_type_parameters_are_mechanically_normalized(self) -> None:
        world = build_evidence_world_profile(
            self.request(
                (SourceRepresentation("s", "text/plain; charset=utf-8", "alpha"),)
            )
        )
        self.assertEqual(world["source_inventory"][0]["evidence_form"], "document_text")

    def test_unknowns_are_not_forced(self) -> None:
        request = self.request(
            (SourceRepresentation("s", "application/octet-stream", "bytes"),)
        )
        claim = build_claim_profile(request)
        world = build_evidence_world_profile(request)
        self.assertEqual(claim["domain"], "unknown")
        self.assertEqual(claim["verification_world"], "unknown")
        self.assertEqual(claim["jurisdiction"], "unknown")
        self.assertEqual(world["verification_world"], "unknown")
        self.assertEqual(world["source_inventory"][0]["evidence_form"], "unknown")

    def test_replay_is_deterministic(self) -> None:
        request = self.fixture_request("not_needed")
        first = run_paired_preflight(request)
        second = run_paired_preflight(request)
        self.assertEqual(first.authoring.receipt, second.authoring.receipt)
        self.assertEqual(first.claim_profile, second.claim_profile)
        self.assertEqual(first.claim_profile_receipt, second.claim_profile_receipt)
        self.assertEqual(first.evidence_world_profile, second.evidence_world_profile)
        self.assertEqual(first.evidence_world_receipt, second.evidence_world_receipt)
        self.assertEqual(first.compatibility, second.compatibility)
        self.assertEqual(first.compatibility_receipt, second.compatibility_receipt)

    def test_preflight_is_observational_only(self) -> None:
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
        self.assertEqual(states["evidence_forms"], "partial")
        self.assertEqual(states["temporal_scope"], "match")
        self.assertEqual(states["jurisdiction"], "match")
        self.assertEqual(states["verification_world"], "match")
        serialized = json.dumps(result).lower()
        for forbidden in ("supports", "refutes", "retrieve", "rank", "admit"):
            self.assertNotIn(forbidden, serialized)


if __name__ == "__main__":
    unittest.main()
