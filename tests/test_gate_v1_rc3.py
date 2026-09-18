from __future__ import annotations

import copy
import unittest

from proposition_authoring.canonical import bound_object_hash
from proposition_authoring.gate_v1 import EvidenceTaskV1, GateV1Error
from proposition_authoring.gate_v1_rc3 import (
    SourceMetadataV1RC3,
    build_evidence_gate_output_v1_rc3,
    classify_claim_v1_rc3,
    standardize_gates_v1_rc3,
    validate_claim_gate_output_v1_rc3,
    validate_evidence_gate_output_v1_rc3,
    verify_standardized_gate_bundle_v1_rc3,
)
from proposition_authoring.model import AuthoringRequest, SourceRepresentation


class GateV1RC3Tests(unittest.TestCase):
    def request(
        self,
        *,
        root_id: str = "claim-a",
        text: str = "Ozempic DIN 02562618 is approved in Canada.",
        sources: tuple[SourceRepresentation, ...] = (),
    ) -> AuthoringRequest:
        return AuthoringRequest(
            handoff_id=f"handoff-{root_id}",
            producer_id="gate-v1-rc3-test",
            producer_version="1",
            work_id="gate-v1-rc3-work",
            root_id=root_id,
            root_text=text,
            sources=sources,
        )

    def sources(self) -> tuple[SourceRepresentation, ...]:
        return (
            SourceRepresentation("hc-product", "text/html", "Current status: Approved."),
            SourceRepresentation("hc-context", "text/plain", "Health Canada DPD."),
        )

    def metadata(self) -> tuple[SourceMetadataV1RC3, ...]:
        return (
            SourceMetadataV1RC3(
                "hc-product",
                origin_type="official_database",
                locator_kind="web_uri",
                locator_value="https://health-products.canada.ca/dpd-bdpp/info?code=106547",
                issuer="Health Canada",
                source_role="official_regulatory_product_record",
                source_authority_basis="Issued through the official Health Canada DPD.",
                document_type="database_record",
                evidence_form="registry_entry",
                jurisdictional_coverage="Canada",
            ),
            SourceMetadataV1RC3(
                "hc-context",
                origin_type="official_website",
                locator_kind="web_uri",
                locator_value="https://health-products.canada.ca/dpd-bdpp/",
                issuer="Health Canada",
                source_role="official_database_context",
                source_authority_basis="Published by Health Canada.",
                document_type="web_page",
                evidence_form="document_text",
                jurisdictional_coverage="Canada",
            ),
        )

    def task(self) -> EvidenceTaskV1:
        return EvidenceTaskV1(
            verification_world="closed",
            corpus_scope="two frozen Health Canada pages",
            completeness_state="partial",
            known_gaps_state="declared_some",
            known_gaps=("product monograph omitted",),
        )

    def result(self):
        return standardize_gates_v1_rc3(
            self.request(sources=self.sources()),
            evidence_task=self.task(),
            source_metadata=self.metadata(),
            implementation_identity="a" * 40,
        )

    def test_quantitative_requires_positive_semantics(self) -> None:
        negatives = {
            "DIN No. 02562618 is approved.": ("status",),
            "DIN number 02562618 is approved.": ("status",),
            "ISO 13485 compliant.": ("compliance", "status"),
            "The device was approved under 21 CFR Part 11.": ("status",),
            "The licence was approved on 2025-11-04.": ("status", "temporal"),
            "Version 2 was approved.": ("status",),
        }
        for text, expected in negatives.items():
            with self.subTest(text=text):
                self.assertEqual(classify_claim_v1_rc3(text), expected)
        self.assertEqual(
            classify_claim_v1_rc3("There were 25 rejected records."),
            ("quantitative", "status"),
        )
        self.assertEqual(
            classify_claim_v1_rc3("The failure rate was 4.2 percent."),
            ("quantitative",),
        )
        self.assertEqual(
            classify_claim_v1_rc3("The temperature was 25 °C."),
            ("quantitative",),
        )
        self.assertEqual(
            classify_claim_v1_rc3("Group A was 5 higher than Group B."),
            ("comparative", "quantitative"),
        )

    def test_representation_identity_includes_media_type(self) -> None:
        first = self.result()
        changed_sources = (
            SourceRepresentation("hc-product", "application/json", self.sources()[0].content),
            self.sources()[1],
        )
        second = standardize_gates_v1_rc3(
            self.request(sources=changed_sources),
            evidence_task=self.task(),
            source_metadata=self.metadata(),
            implementation_identity="a" * 40,
        )
        self.assertEqual(
            first.evidence_gate["sources"][0]["content_sha256"],
            second.evidence_gate["sources"][0]["content_sha256"],
        )
        self.assertNotEqual(
            first.evidence_gate["sources"][0]["representation_id"],
            second.evidence_gate["sources"][0]["representation_id"],
        )
        self.assertNotEqual(
            first.evidence_gate["evidence_world_id"],
            second.evidence_gate["evidence_world_id"],
        )

    def test_evidence_world_remains_claim_independent(self) -> None:
        first = self.result()
        second = standardize_gates_v1_rc3(
            self.request(
                root_id="claim-b",
                text="Ozempic is approved in Canada.",
                sources=self.sources(),
            ),
            evidence_task=self.task(),
            source_metadata=self.metadata(),
            implementation_identity="a" * 40,
        )
        self.assertEqual(first.evidence_gate, second.evidence_gate)
        self.assertNotEqual(first.receipt["receipt_sha256"], second.receipt["receipt_sha256"])

    def test_web_uri_is_validated(self) -> None:
        bad = list(self.metadata())
        bad[0] = SourceMetadataV1RC3(
            **{**bad[0].__dict__, "locator_value": "definitely not a URI"}
        )
        with self.assertRaises(GateV1Error):
            standardize_gates_v1_rc3(
                self.request(sources=self.sources()),
                evidence_task=self.task(),
                source_metadata=tuple(bad),
            )

    def test_origin_type_is_bounded(self) -> None:
        bad = list(self.metadata())
        bad[0] = SourceMetadataV1RC3(
            **{**bad[0].__dict__, "origin_type": "anything-goes"}
        )
        with self.assertRaises(GateV1Error):
            standardize_gates_v1_rc3(
                self.request(sources=self.sources()),
                evidence_task=self.task(),
                source_metadata=tuple(bad),
            )

    def test_runtime_validation_uses_wire_contract(self) -> None:
        result = self.result()

        evidence = copy.deepcopy(result.evidence_gate)
        evidence["authority"]["retrieval_authority"] = True
        evidence["output_sha256"] = bound_object_hash(evidence, "output_sha256")
        with self.assertRaises(GateV1Error):
            validate_evidence_gate_output_v1_rc3(evidence)

        claim = copy.deepcopy(result.claim_gate)
        claim["authority"]["retrieval_authority"] = True
        claim["output_sha256"] = bound_object_hash(claim, "output_sha256")
        with self.assertRaises(GateV1Error):
            validate_claim_gate_output_v1_rc3(claim)

    def test_bundle_verifier_rejects_validly_rehashed_substitutions(self) -> None:
        result = self.result()

        bad_receipt = copy.deepcopy(result.receipt)
        bad_receipt["evidence_world_id"] = "sha256:" + "0" * 64
        bad_receipt["receipt_sha256"] = bound_object_hash(bad_receipt, "receipt_sha256")
        with self.assertRaises(GateV1Error):
            verify_standardized_gate_bundle_v1_rc3(
                result.claim_gate,
                result.evidence_gate,
                bad_receipt,
                contract_a=result.authoring.contract_a,
            )

        bad_receipt = copy.deepcopy(result.receipt)
        bad_receipt["claim_gate_output_sha256"] = "sha256:" + "1" * 64
        bad_receipt["receipt_sha256"] = bound_object_hash(bad_receipt, "receipt_sha256")
        with self.assertRaises(GateV1Error):
            verify_standardized_gate_bundle_v1_rc3(
                result.claim_gate,
                result.evidence_gate,
                bad_receipt,
                contract_a=result.authoring.contract_a,
            )

    def test_bundle_verifier_accepts_generated_bundle(self) -> None:
        result = self.result()
        verified = verify_standardized_gate_bundle_v1_rc3(
            result.claim_gate,
            result.evidence_gate,
            result.receipt,
            contract_a=result.authoring.contract_a,
        )
        self.assertEqual(verified["state"], "VERIFIED")

    def test_metadata_changes_characterization_not_evidence_world(self) -> None:
        first = self.result()
        rows = list(self.metadata())
        rows[0] = SourceMetadataV1RC3(
            **{**rows[0].__dict__, "source_role": "alternate_descriptive_role"}
        )
        second = standardize_gates_v1_rc3(
            self.request(sources=self.sources()),
            evidence_task=self.task(),
            source_metadata=tuple(rows),
            implementation_identity="a" * 40,
        )
        self.assertEqual(first.evidence_gate["evidence_world_id"], second.evidence_gate["evidence_world_id"])
        self.assertNotEqual(first.evidence_gate["output_sha256"], second.evidence_gate["output_sha256"])

    def test_source_provenance_does_not_contain_retention_locator(self) -> None:
        result = self.result()
        rendered = repr(result.evidence_gate)
        for token in ("github_artifact", "local_cas", "object_store", "retention"):
            self.assertNotIn(token, rendered)

    def test_duplicate_source_ids_fail_closed(self) -> None:
        with self.assertRaises(GateV1Error):
            build_evidence_gate_output_v1_rc3(
                self.request(
                    sources=(
                        SourceRepresentation("dup", "text/plain", "a"),
                        SourceRepresentation("dup", "text/plain", "b"),
                    )
                )
            )
