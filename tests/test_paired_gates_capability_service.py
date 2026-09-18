from __future__ import annotations

import json
import unittest

from proposition_authoring.capability_service import PairedGatesCapabilityService
from proposition_authoring.engine import AuthoringEngine
from proposition_authoring.evidence_gate import build_evidence_world_profile
from proposition_authoring.feature_registry import (
    build_feature_registry,
    project_eb_hint,
    qualified_hint_fields,
)
from proposition_authoring.model import AuthoringRequest, SourceRepresentation
from proposition_authoring.preflight import compare_profiles
from proposition_authoring.shadow_models import SourceMetadata, TaskMetadata


class PairedGatesCapabilityServiceTests(unittest.TestCase):
    def request(
        self,
        *,
        text: str = "Women had a higher rate than Men.",
        sources: tuple[SourceRepresentation, ...] = (),
    ) -> AuthoringRequest:
        return AuthoringRequest(
            handoff_id="handoff-capability-v0",
            producer_id="test",
            producer_version="0",
            work_id="work-capability-v0",
            root_id="claim-capability-v0",
            root_text=text,
            sources=sources,
        )

    def test_service_preserves_authoring_bytes(self) -> None:
        request = self.request()
        direct = AuthoringEngine().author(request)
        observed = PairedGatesCapabilityService("test-head").run(request)
        self.assertEqual(observed.authoring.state, direct.state)
        self.assertEqual(observed.authoring.reason, direct.reason)
        self.assertEqual(observed.authoring.contract_a, direct.contract_a)
        self.assertEqual(observed.authoring.receipt, direct.receipt)

    def test_claim_profile_exposes_complete_v0_surface_with_basis(self) -> None:
        result = PairedGatesCapabilityService().run(
            self.request(text="Drug A had a higher response than Drug B in 2025."),
            claim_task=TaskMetadata(
                domain="healthcare",
                verification_world="closed",
                jurisdiction="Canada",
            ),
        )
        profile = result.claim_profile
        required = {
            "claim_families",
            "expected_evidence_forms",
            "claim_structure_shape",
            "entities",
            "relation_targets",
            "domain",
            "verification_world",
            "temporal_scope",
            "jurisdiction",
            "context_dependence",
            "scope_ambiguity",
            "negation",
            "modality",
            "attribution",
            "field_basis",
        }
        self.assertTrue(required <= set(profile))
        self.assertEqual(profile["relation_targets"], ["Drug A", "Drug B"])
        self.assertEqual(profile["domain"], "healthcare")
        self.assertEqual(profile["temporal_scope"], "2025")
        self.assertEqual(set(profile["field_basis"]), required - {"field_basis"})

    def test_evidence_world_exposes_duplicates_supersession_and_conflicts(self) -> None:
        sources = (
            SourceRepresentation("s1", "application/pdf", "same bytes"),
            SourceRepresentation("s2", "application/pdf", "same bytes"),
            SourceRepresentation("s3", "application/json", "different"),
        )
        metadata = (
            SourceMetadata(
                "s1",
                provenance="regulator",
                issuer="Agency A",
                source_role="primary",
                authority_basis="issuer",
                temporal_coverage="2025",
                jurisdictional_coverage="Canada",
                version="2",
                currency_state="current",
                supersedes=("s0",),
                conflicts_with=("s3",),
            ),
            SourceMetadata("s2", provenance="mirror"),
            SourceMetadata("s3", evidence_form="registry_entry"),
        )
        world = build_evidence_world_profile(
            self.request(sources=sources),
            task=TaskMetadata(
                verification_world="closed",
                corpus_scope="packet-2025",
                completeness_state="partial",
                known_gaps=("missing 2026 update",),
            ),
            source_metadata=metadata,
        )
        self.assertIn(["s1", "s2"], world["duplicate_source_groups"])
        self.assertIn(["s1", "s0"], world["supersession_observations"])
        self.assertIn(["s1", "s3"], world["conflict_observations"])
        self.assertIn("Agency A", world["issuers"])
        self.assertIn("pdf_document", world["document_types"])
        self.assertEqual(world["completeness_state"], "partial")
        self.assertEqual(world["known_gaps"], ["missing 2026 update"])

    def test_preflight_completes_aperture_completeness_and_gap_observations(self) -> None:
        claim = {
            "expected_evidence_forms": ["measurement", "document_text"],
            "temporal_scope": "2025",
            "jurisdiction": "Canada",
            "verification_world": "closed",
        }
        world = {
            "source_inventory": [{"source_id": "s1"}],
            "evidence_forms": ["document_text"],
            "temporal_coverage": ["2025"],
            "jurisdictional_coverage": ["Canada"],
            "verification_world": "closed",
            "corpus_scope": "packet-2025",
            "completeness_state": "partial",
            "known_gaps": ["measurement table missing"],
        }
        result = compare_profiles(claim, world)
        states = {row["field"]: row["state"] for row in result["observations"]}
        self.assertEqual(states["evidence_forms"], "partial")
        self.assertEqual(states["missing_expected_evidence_forms"], "partial")
        self.assertEqual(states["temporal_scope"], "match")
        self.assertEqual(states["jurisdiction"], "match")
        self.assertEqual(states["verification_world"], "match")
        self.assertEqual(states["corpus_aperture"], "match")
        self.assertEqual(states["corpus_completeness"], "partial")
        self.assertEqual(states["known_gaps"], "partial")
        serialized = json.dumps(result).lower()
        for forbidden in ("supports", "refutes", "retrieve", "rank", "admit"):
            self.assertNotIn(forbidden, serialized)

    def test_preflight_does_not_invent_completeness_from_no_declared_gaps(self) -> None:
        result = compare_profiles(
            {"expected_evidence_forms": ["document_text"]},
            {
                "source_inventory": [{"source_id": "s1"}],
                "evidence_forms": ["document_text"],
                "completeness_state": "unknown",
                "known_gaps": [],
            },
        )
        states = {row["field"]: row["state"] for row in result["observations"]}
        self.assertEqual(states["corpus_completeness"], "unknown")
        self.assertEqual(states["known_gaps"], "unknown")

    def test_feature_registry_defaults_to_shadow_and_firewall_blocks_eb_hint(self) -> None:
        registry = build_feature_registry("test-head")
        self.assertEqual(registry["implementation_identity"], "test-head")
        self.assertTrue(registry["entries"])
        self.assertTrue(
            all(
                row["authority_status"] == "IMPLEMENTED_SHADOW"
                for row in registry["entries"]
            )
        )
        self.assertEqual(qualified_hint_fields(registry), ())
        with self.assertRaises(PermissionError):
            project_eb_hint(
                registry,
                {"claim.expected_evidence_forms": ["measurement"]},
                ("claim.expected_evidence_forms",),
            )

    def test_replay_is_deterministic_including_registry(self) -> None:
        source = SourceRepresentation("s1", "text/plain", "alpha")
        service = PairedGatesCapabilityService("stable-test")
        first = service.run(self.request(sources=(source,)))
        second = service.run(self.request(sources=(source,)))
        self.assertEqual(first.claim_profile, second.claim_profile)
        self.assertEqual(first.evidence_world_profile, second.evidence_world_profile)
        self.assertEqual(first.compatibility, second.compatibility)
        self.assertEqual(first.feature_registry, second.feature_registry)
        self.assertEqual(first.compatibility_receipt, second.compatibility_receipt)


if __name__ == "__main__":
    unittest.main()
