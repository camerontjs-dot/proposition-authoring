from __future__ import annotations

import copy
import unittest

from proposition_authoring.engine import AuthoringEngine
from proposition_authoring.gate_v1 import (
    EvidenceTaskV1,
    GateV1Error,
    SourceMetadataV1,
    build_evidence_gate_output_v1,
    classify_claim_v1,
    standardize_gates_v1,
    validate_claim_gate_output_v1,
    validate_evidence_gate_output_v1,
)
from proposition_authoring.model import AuthoringRequest, SourceRepresentation


class GateV1Tests(unittest.TestCase):
    def request(
        self,
        *,
        text: str = "Valve Cerulean was inactive.",
        sources: tuple[SourceRepresentation, ...] = (),
    ) -> AuthoringRequest:
        return AuthoringRequest(
            handoff_id="gate-v1-handoff",
            producer_id="gate-v1-test",
            producer_version="1",
            work_id="gate-v1-work",
            root_id="gate-v1-root",
            root_text=text,
            sources=sources,
        )

    def test_categories_are_finite_and_standard_deviation_is_not_compliance(self) -> None:
        self.assertEqual(classify_claim_v1("Women had a higher rate than Men."), ("comparative", "quantitative"))
        self.assertEqual(classify_claim_v1("The standard deviation was 4.2."), ("quantitative",))
        self.assertIn("attribution", classify_claim_v1("According to Agency A, the device was active."))
        self.assertIn("status", classify_claim_v1("The licence was approved."))
        self.assertIn("compliance", classify_claim_v1("The system complied with the regulation."))
        self.assertEqual(classify_claim_v1("Blue widgets exist."), ("existence",))
        self.assertEqual(classify_claim_v1("Widget cobalt is blue."), ("other",))

    def test_claim_gate_preserves_authoritative_authoring_bytes(self) -> None:
        request = self.request()
        direct = AuthoringEngine().author(request)
        result = standardize_gates_v1(request, implementation_identity="test-head")
        self.assertEqual(result.authoring.state, direct.state)
        self.assertEqual(result.authoring.reason, direct.reason)
        self.assertEqual(result.authoring.contract_a, direct.contract_a)
        self.assertEqual(result.authoring.receipt, direct.receipt)
        self.assertEqual(result.claim_gate["claim"]["text"], request.root_text)
        self.assertEqual(result.claim_gate["claim"]["text_sha256"], direct.contract_a["root_proposition"]["text_sha256"])
        self.assertEqual(result.claim_gate["contract_a_binding"]["state"], "present")
        self.assertEqual(
            result.claim_gate["contract_a_binding"]["handoff_sha256"],
            direct.contract_a["handoff_sha256"],
        )

    def test_abstained_claim_is_still_standardized_without_contract_a_binding(self) -> None:
        request = self.request(
            text="Auditor Bracken reported Unit Cedar passed and Unit Daffodil failed."
        )
        result = standardize_gates_v1(request)
        self.assertEqual(result.authoring.state, "ABSTAINED")
        self.assertEqual(result.claim_gate["contract_a_binding"], {"state": "absent", "handoff_sha256": None})
        self.assertEqual(result.claim_gate["lineage"]["decomposition"]["state"], "unresolved")
        self.assertIn("attribution", result.claim_gate["claim"]["categories"]["values"])
        validate_claim_gate_output_v1(result.claim_gate)

    def test_evidence_gate_is_source_order_invariant_and_omits_raw_content(self) -> None:
        s1 = SourceRepresentation("s1", "application/pdf", "first source bytes")
        s2 = SourceRepresentation("s2", "application/json", "second source bytes")
        metadata = (
            SourceMetadataV1(
                "s1",
                provenance="official publication",
                issuer="Agency A",
                source_role="regulator_primary",
                authority_basis="official_issuer",
                temporal_coverage="2025",
                jurisdictional_coverage="Canada",
                version="4",
                currency_state="current",
            ),
        )
        task = EvidenceTaskV1(
            verification_world="closed",
            corpus_scope="supplied packet",
            completeness_state="partial",
            known_gaps_state="declared_some",
            known_gaps=("missing 2026 update",),
        )
        first = build_evidence_gate_output_v1(
            self.request(sources=(s1, s2)),
            task=task,
            source_metadata=metadata,
            implementation_identity="test-head",
        )
        second = build_evidence_gate_output_v1(
            self.request(sources=(s2, s1)),
            task=task,
            source_metadata=metadata,
            implementation_identity="test-head",
        )
        self.assertEqual(first, second)
        self.assertEqual(first["source_count"], 2)
        self.assertEqual(first["sources"][0]["source_id"], "s1")
        self.assertEqual(first["sources"][0]["provenance"]["issuer"]["value"], "Agency A")
        self.assertEqual(first["sources"][0]["classification"]["document_type"]["value"], "pdf_document")
        self.assertEqual(first["sources"][1]["classification"]["evidence_form"]["value"], "database_record")
        self.assertEqual(first["corpus"]["known_gaps"]["state"], "declared_some")
        self.assertNotIn("content", first["sources"][0])
        validate_evidence_gate_output_v1(first)

    def test_unknown_source_metadata_remains_explicit_unknown(self) -> None:
        source = SourceRepresentation("s1", "application/octet-stream", "opaque")
        output = build_evidence_gate_output_v1(self.request(sources=(source,)))
        row = output["sources"][0]
        self.assertEqual(row["provenance"]["issuer"]["state"], "unknown")
        self.assertIsNone(row["provenance"]["issuer"]["value"])
        self.assertEqual(row["classification"]["document_type"]["state"], "unknown")
        self.assertEqual(output["corpus"]["known_gaps"]["state"], "unknown")

    def test_gap_declaration_distinguishes_unknown_none_and_some(self) -> None:
        request = self.request()
        unknown = build_evidence_gate_output_v1(request)
        none = build_evidence_gate_output_v1(
            request,
            task=EvidenceTaskV1(known_gaps_state="declared_none"),
        )
        some = build_evidence_gate_output_v1(
            request,
            task=EvidenceTaskV1(
                known_gaps_state="declared_some",
                known_gaps=("gap-a",),
            ),
        )
        self.assertEqual(unknown["corpus"]["known_gaps"]["state"], "unknown")
        self.assertEqual(none["corpus"]["known_gaps"]["state"], "declared_none")
        self.assertEqual(some["corpus"]["known_gaps"]["state"], "declared_some")
        with self.assertRaises(GateV1Error):
            build_evidence_gate_output_v1(
                request,
                task=EvidenceTaskV1(known_gaps_state="declared_some"),
            )

    def test_evidence_content_mutation_changes_world_and_output_identity(self) -> None:
        original = build_evidence_gate_output_v1(
            self.request(sources=(SourceRepresentation("s1", "text/plain", "alpha"),))
        )
        mutated = build_evidence_gate_output_v1(
            self.request(sources=(SourceRepresentation("s1", "text/plain", "beta"),))
        )
        self.assertNotEqual(original["evidence_world_id"], mutated["evidence_world_id"])
        self.assertNotEqual(original["output_sha256"], mutated["output_sha256"])

    def test_standardization_replay_is_deterministic(self) -> None:
        source = SourceRepresentation("s1", "text/plain", "Inspection record")
        request = self.request(sources=(source,))
        kwargs = {
            "evidence_task": EvidenceTaskV1(
                verification_world="closed",
                corpus_scope="packet",
                known_gaps_state="declared_none",
            ),
            "source_metadata": (SourceMetadataV1("s1", provenance="supplied record"),),
            "implementation_identity": "test-head",
        }
        first = standardize_gates_v1(request, **kwargs)
        second = standardize_gates_v1(request, **kwargs)
        self.assertEqual(first.claim_gate, second.claim_gate)
        self.assertEqual(first.evidence_gate, second.evidence_gate)
        self.assertEqual(first.receipt, second.receipt)

    def test_validators_reject_unknown_owned_fields_and_hash_tamper(self) -> None:
        result = standardize_gates_v1(self.request())
        claim = copy.deepcopy(result.claim_gate)
        claim["unexpected"] = True
        with self.assertRaises(GateV1Error):
            validate_claim_gate_output_v1(claim)

        evidence = copy.deepcopy(result.evidence_gate)
        evidence["output_sha256"] = "sha256:" + "0" * 64
        with self.assertRaises(GateV1Error):
            validate_evidence_gate_output_v1(evidence)

    def test_outputs_exclude_downstream_semantic_and_routing_fields(self) -> None:
        result = standardize_gates_v1(self.request())
        forbidden = {
            "support",
            "refutation",
            "verdict",
            "query",
            "rank",
            "admission",
            "decision",
            "authorization",
            "expected_evidence_forms",
        }

        def keys(value: object) -> set[str]:
            found: set[str] = set()
            if isinstance(value, dict):
                for key, child in value.items():
                    found.add(str(key))
                    found.update(keys(child))
            elif isinstance(value, list):
                for child in value:
                    found.update(keys(child))
            return found

        self.assertTrue(forbidden.isdisjoint(keys(result.claim_gate)))
        self.assertTrue(forbidden.isdisjoint(keys(result.evidence_gate)))


if __name__ == "__main__":
    unittest.main()
