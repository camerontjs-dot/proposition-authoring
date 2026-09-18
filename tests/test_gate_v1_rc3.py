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

    def evidence(self, media_type: str = "text/html") -> tuple[SourceRepresentation, ...]:
        return (
            SourceRepresentation(
                "hc-product",
                media_type,
                "Current status: Approved. Product name: OZEMPIC. DIN: 02562618.",
            ),
            SourceRepresentation(
                "hc-context",
                "text/html",
                "Health Canada Drug Product Database online query.",
            ),
        )

    def metadata(self) -> tuple[SourceMetadataV1RC3, ...]:
        return (
            SourceMetadataV1RC3(
                "hc-product",
                origin_type="official_database",
                locator_kind="web_uri",
                locator_value=(
                    "https://health-products.canada.ca/dpd-bdpp/"
                    "info?code=106547&lang=eng"
                ),
                issuer="Health Canada",
                source_role="official_regulatory_product_record",
                source_authority_basis_kind="official_issuer",
                source_authority_basis_detail=(
                    "Official Health Canada Drug Product Database record"
                ),
                document_type="database_record",
                evidence_form="registry_entry",
                temporal_coverage="status date 2025-11-04",
                jurisdictional_coverage="Canada",
            ),
            SourceMetadataV1RC3(
                "hc-context",
                origin_type="official_database",
                locator_kind="web_uri",
                locator_value="https://health-products.canada.ca/dpd-bdpp/",
                issuer="Health Canada",
                source_role="official_database_context",
                source_authority_basis_kind="official_issuer",
                source_authority_basis_detail="Official Health Canada database interface",
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

    def standardize(self):
        return standardize_gates_v1_rc3(
            self.request(sources=self.evidence()),
            evidence_task=self.task(),
            source_metadata=self.metadata(),
            implementation_identity="a" * 40,
        )

    def test_positive_semantic_quantitative_classification(self) -> None:
        cases = {
            "Ozempic DIN 02562618 is approved in Canada.": ("status",),
            "DIN No. 02562618 is approved.": ("status",),
            "DIN number 02562618 is approved.": ("status",),
            "ISO 13485 compliant.": ("compliance", "status"),
            "The device was approved under 21 CFR Part 11.": ("status",),
            "The licence was approved on 2025-11-04.": ("status", "temporal"),
            "Version 2 was approved.": ("status",),
            "There were 25 rejected records.": ("quantitative", "status"),
            "The failure rate was 4.2 percent.": ("quantitative",),
            "The dose was 5 mg.": ("quantitative",),
            "Revenue was $25.": ("quantitative",),
        }
        for text, expected in cases.items():
            with self.subTest(text=text):
                self.assertEqual(classify_claim_v1_rc3(text), expected)

    def test_media_type_is_representation_identity(self) -> None:
        html = build_evidence_gate_output_v1_rc3(
            self.request(sources=self.evidence("text/html")),
            source_metadata=self.metadata(),
        )
        plain = build_evidence_gate_output_v1_rc3(
            self.request(sources=self.evidence("text/plain")),
            source_metadata=self.metadata(),
        )
        html_product = next(row for row in html["sources"] if row["source_id"] == "hc-product")
        plain_product = next(row for row in plain["sources"] if row["source_id"] == "hc-product")
        self.assertEqual(
            html_product["content_sha256"],
            plain_product["content_sha256"],
        )
        self.assertNotEqual(
            html_product["representation_id"],
            plain_product["representation_id"],
        )
        self.assertNotEqual(html["evidence_world_id"], plain["evidence_world_id"])

    def test_media_type_parameters_normalize(self) -> None:
        plain = build_evidence_gate_output_v1_rc3(
            self.request(sources=self.evidence("text/html")),
            source_metadata=self.metadata(),
        )
        parameterized = build_evidence_gate_output_v1_rc3(
            self.request(sources=self.evidence("text/html; charset=utf-8")),
            source_metadata=self.metadata(),
        )
        self.assertEqual(plain, parameterized)

    def test_same_evidence_world_is_claim_independent(self) -> None:
        first = self.standardize()
        second = standardize_gates_v1_rc3(
            self.request(
                root_id="claim-b",
                text="Ozempic is approved in Canada.",
                sources=self.evidence(),
            ),
            evidence_task=self.task(),
            source_metadata=self.metadata(),
            implementation_identity="a" * 40,
        )
        self.assertEqual(first.evidence_gate, second.evidence_gate)
        self.assertNotEqual(first.receipt["receipt_sha256"], second.receipt["receipt_sha256"])

    def test_invalid_web_uri_fails_closed(self) -> None:
        rows = list(self.metadata())
        rows[0] = SourceMetadataV1RC3(
            **{**rows[0].__dict__, "locator_value": "definitely not a URI"}
        )
        with self.assertRaises(GateV1Error):
            build_evidence_gate_output_v1_rc3(
                self.request(sources=self.evidence()),
                source_metadata=tuple(rows),
            )

    def test_origin_type_vocabulary_fails_closed(self) -> None:
        rows = list(self.metadata())
        rows[0] = SourceMetadataV1RC3(
            **{**rows[0].__dict__, "origin_type": "anything-goes-value"}
        )
        with self.assertRaises(GateV1Error):
            build_evidence_gate_output_v1_rc3(
                self.request(sources=self.evidence()),
                source_metadata=tuple(rows),
            )

    def test_source_authority_basis_is_typed(self) -> None:
        output = build_evidence_gate_output_v1_rc3(
            self.request(sources=self.evidence()),
            source_metadata=self.metadata(),
        )
        basis = output["sources"][0]["provenance"]["source_authority_basis"]
        self.assertEqual(basis["state"], "known")
        self.assertEqual(basis["kind"], "official_issuer")
        self.assertNotIn("authority_basis", output["sources"][0]["provenance"])

    def test_invalid_authority_basis_kind_fails_closed(self) -> None:
        rows = list(self.metadata())
        rows[0] = SourceMetadataV1RC3(
            **{**rows[0].__dict__, "source_authority_basis_kind": "proves_claim"}
        )
        with self.assertRaises(GateV1Error):
            build_evidence_gate_output_v1_rc3(
                self.request(sources=self.evidence()),
                source_metadata=tuple(rows),
            )

    def test_schema_authority_constants_are_runtime_authority(self) -> None:
        result = self.standardize()
        tampered = copy.deepcopy(result.evidence_gate)
        tampered["authority"]["retrieval_authority"] = True
        tampered["output_sha256"] = bound_object_hash(tampered, "output_sha256")
        with self.assertRaises(GateV1Error):
            validate_evidence_gate_output_v1_rc3(tampered)

        claim = copy.deepcopy(result.claim_gate)
        claim["authority"]["retrieval_authority"] = True
        claim["output_sha256"] = bound_object_hash(claim, "output_sha256")
        with self.assertRaises(GateV1Error):
            validate_claim_gate_output_v1_rc3(claim)

    def test_schema_hash_shape_is_runtime_authority(self) -> None:
        result = self.standardize()
        tampered = copy.deepcopy(result.evidence_gate)
        tampered["sources"][0]["content_sha256"] = "not-a-sha256"
        tampered["output_sha256"] = bound_object_hash(tampered, "output_sha256")
        with self.assertRaises(GateV1Error):
            validate_evidence_gate_output_v1_rc3(tampered)

    def test_bundle_verifier_accepts_exact_bundle(self) -> None:
        result = self.standardize()
        verified = verify_standardized_gate_bundle_v1_rc3(
            result.claim_gate,
            result.evidence_gate,
            result.authoring.contract_a,
            result.receipt,
        )
        self.assertEqual(verified["state"], "VERIFIED")

    def test_bundle_verifier_rejects_evidence_substitution(self) -> None:
        result = self.standardize()
        receipt = copy.deepcopy(result.receipt)
        receipt["evidence_world_id"] = "sha256:" + "0" * 64
        receipt["receipt_sha256"] = bound_object_hash(receipt, "receipt_sha256")
        with self.assertRaises(GateV1Error):
            verify_standardized_gate_bundle_v1_rc3(
                result.claim_gate,
                result.evidence_gate,
                result.authoring.contract_a,
                receipt,
            )

    def test_bundle_verifier_rejects_claim_hash_substitution(self) -> None:
        result = self.standardize()
        receipt = copy.deepcopy(result.receipt)
        receipt["claim_gate_output_sha256"] = "sha256:" + "1" * 64
        receipt["receipt_sha256"] = bound_object_hash(receipt, "receipt_sha256")
        with self.assertRaises(GateV1Error):
            verify_standardized_gate_bundle_v1_rc3(
                result.claim_gate,
                result.evidence_gate,
                result.authoring.contract_a,
                receipt,
            )

    def test_bundle_verifier_rejects_contract_a_substitution(self) -> None:
        result = self.standardize()
        contract_a = copy.deepcopy(result.authoring.contract_a)
        assert contract_a is not None
        contract_a["root_proposition"]["text"] = "Different proposition."
        contract_a["root_proposition"]["text_sha256"] = (
            "sha256:" + "2" * 64
        )
        contract_a["handoff_sha256"] = bound_object_hash(contract_a, "handoff_sha256")
        with self.assertRaises(GateV1Error):
            verify_standardized_gate_bundle_v1_rc3(
                result.claim_gate,
                result.evidence_gate,
                contract_a,
                result.receipt,
            )


if __name__ == "__main__":
    unittest.main()
