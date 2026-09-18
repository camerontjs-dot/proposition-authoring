from __future__ import annotations

import copy
import unittest

from proposition_authoring.gate_v1 import EvidenceTaskV1, GateV1Error
from proposition_authoring.gate_v1_rc2 import (
    SourceMetadataV1RC2,
    build_evidence_gate_output_v1_rc2,
    build_provenance_inputs_v1_rc2,
    classify_claim_v1_rc2,
    standardize_gates_v1_rc2,
    validate_evidence_gate_output_v1_rc2,
)
from proposition_authoring.model import AuthoringRequest, SourceRepresentation


class GateV1RC2Tests(unittest.TestCase):
    def request(
        self,
        *,
        root_id: str = "claim-a",
        text: str = "Ozempic DIN 02562618 is approved in Canada.",
        sources: tuple[SourceRepresentation, ...] = (),
    ) -> AuthoringRequest:
        return AuthoringRequest(
            handoff_id=f"handoff-{root_id}",
            producer_id="gate-v1-rc2-test",
            producer_version="1",
            work_id="gate-v1-rc2-work",
            root_id=root_id,
            root_text=text,
            sources=sources,
        )

    def evidence(self) -> tuple[SourceRepresentation, ...]:
        return (
            SourceRepresentation(
                "hc-dpd-product-106547",
                "text/html",
                "Current status: Approved. Product name: OZEMPIC. DIN: 02562618.",
            ),
            SourceRepresentation(
                "hc-dpd-query-context",
                "text/html",
                "Health Canada Drug Product Database online query.",
            ),
        )

    def metadata(self) -> tuple[SourceMetadataV1RC2, ...]:
        return (
            SourceMetadataV1RC2(
                "hc-dpd-product-106547",
                origin_type="official_regulatory_database",
                source_uri="https://health-products.canada.ca/dpd-bdpp/info?code=106547&lang=eng",
                issuer="Health Canada",
                source_role="official_regulatory_product_record",
                authority_basis="official Health Canada Drug Product Database record",
                document_type="database_record",
                evidence_form="registry_entry",
                jurisdictional_coverage="Canada",
            ),
            SourceMetadataV1RC2(
                "hc-dpd-query-context",
                origin_type="official_regulatory_database",
                source_uri="https://health-products.canada.ca/dpd-bdpp/",
                issuer="Health Canada",
                source_role="official_database_context",
                authority_basis="official Health Canada database interface",
                document_type="web_page",
                evidence_form="document_text",
                jurisdictional_coverage="Canada",
            ),
        )

    def test_identifier_tokens_do_not_create_quantitative_category(self) -> None:
        self.assertEqual(
            classify_claim_v1_rc2("Ozempic DIN 02562618 is approved in Canada."),
            ("status",),
        )
        self.assertEqual(
            classify_claim_v1_rc2("Lot number 123456 was rejected."),
            ("status",),
        )
        self.assertEqual(
            classify_claim_v1_rc2("Document no. 77881 was approved."),
            ("status",),
        )
        self.assertEqual(
            classify_claim_v1_rc2("There were 25 rejected records."),
            ("quantitative", "status"),
        )
        self.assertEqual(
            classify_claim_v1_rc2("The failure rate was 4.2 percent."),
            ("quantitative",),
        )

    def test_same_evidence_world_is_claim_independent(self) -> None:
        sources = self.evidence()
        task = EvidenceTaskV1(
            verification_world="closed",
            corpus_scope="two frozen Health Canada pages",
            completeness_state="partial",
            known_gaps_state="declared_some",
            known_gaps=("product monograph omitted",),
        )
        first = standardize_gates_v1_rc2(
            self.request(root_id="claim-a", sources=sources),
            evidence_task=task,
            source_metadata=self.metadata(),
            implementation_identity="a" * 40,
        )
        second = standardize_gates_v1_rc2(
            self.request(
                root_id="claim-b",
                text="Ozempic is approved in Canada.",
                sources=sources,
            ),
            evidence_task=task,
            source_metadata=self.metadata(),
            implementation_identity="a" * 40,
        )
        self.assertEqual(first.evidence_gate, second.evidence_gate)
        self.assertEqual(
            first.evidence_gate["evidence_world_id"],
            second.evidence_gate["evidence_world_id"],
        )
        self.assertNotEqual(first.receipt["receipt_sha256"], second.receipt["receipt_sha256"])
        self.assertEqual(first.receipt["root_id"], "claim-a")
        self.assertEqual(second.receipt["root_id"], "claim-b")

    def test_evidence_gate_has_no_claim_root_field(self) -> None:
        output = build_evidence_gate_output_v1_rc2(
            self.request(sources=self.evidence()),
            source_metadata=self.metadata(),
        )
        self.assertNotIn("root_id", output)
        validate_evidence_gate_output_v1_rc2(output)

    def test_source_origin_is_typed_and_separate_from_retention(self) -> None:
        output = build_evidence_gate_output_v1_rc2(
            self.request(sources=self.evidence()),
            source_metadata=self.metadata(),
        )
        origin = output["sources"][0]["provenance"]["origin"]
        self.assertEqual(origin["origin_type"]["value"], "official_regulatory_database")
        self.assertTrue(origin["source_uri"]["value"].startswith("https://"))
        self.assertNotIn("locator", output)
        self.assertNotIn("retention", output)

    def test_metadata_change_changes_output_not_evidence_world(self) -> None:
        sources = self.evidence()
        original = build_evidence_gate_output_v1_rc2(
            self.request(sources=sources),
            source_metadata=self.metadata(),
        )
        rows = list(self.metadata())
        rows[0] = SourceMetadataV1RC2(
            **{
                **rows[0].__dict__,
                "source_role": "alternate_descriptive_role",
            }
        )
        changed = build_evidence_gate_output_v1_rc2(
            self.request(sources=sources),
            source_metadata=tuple(rows),
        )
        self.assertEqual(original["evidence_world_id"], changed["evidence_world_id"])
        self.assertNotEqual(original["output_sha256"], changed["output_sha256"])

    def test_source_byte_change_changes_evidence_world(self) -> None:
        original = build_evidence_gate_output_v1_rc2(
            self.request(sources=self.evidence()),
            source_metadata=self.metadata(),
        )
        mutated_sources = (
            SourceRepresentation(
                "hc-dpd-product-106547",
                "text/html",
                "Current status: Revoked. Product name: OZEMPIC. DIN: 02562618.",
            ),
            self.evidence()[1],
        )
        mutated = build_evidence_gate_output_v1_rc2(
            self.request(sources=mutated_sources),
            source_metadata=self.metadata(),
        )
        self.assertNotEqual(original["evidence_world_id"], mutated["evidence_world_id"])

    def test_provenance_reconstruction_inputs_capture_causal_gate_inputs(self) -> None:
        request = self.request(sources=self.evidence())
        task = EvidenceTaskV1(
            verification_world="closed",
            corpus_scope="bounded packet",
            completeness_state="partial",
            known_gaps_state="declared_some",
            known_gaps=("product monograph omitted",),
        )
        claim_input, evidence_input = build_provenance_inputs_v1_rc2(
            request,
            evidence_task=task,
            source_metadata=self.metadata(),
        )
        self.assertEqual(
            claim_input["request"]["sources"][0]["content"],
            self.evidence()[0].content,
        )
        self.assertEqual(
            evidence_input["source_metadata"][0]["source_uri"],
            self.metadata()[0].source_uri,
        )
        self.assertEqual(
            evidence_input["evidence_task"]["known_gaps_state"],
            "declared_some",
        )

    def test_validator_rejects_reintroduced_claim_binding(self) -> None:
        output = build_evidence_gate_output_v1_rc2(
            self.request(sources=self.evidence()),
            source_metadata=self.metadata(),
        )
        tampered = copy.deepcopy(output)
        tampered["root_id"] = "claim-a"
        with self.assertRaises(GateV1Error):
            validate_evidence_gate_output_v1_rc2(tampered)
