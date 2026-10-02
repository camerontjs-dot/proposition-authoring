from __future__ import annotations

import unittest

from proposition_authoring.contract_a import emit_not_decomposed
from proposition_authoring.engine import AuthoringEngine
from proposition_authoring.gate_v1_rc3 import standardize_gates_v1_rc3
from proposition_authoring.model import AuthoringRequest, AuthoringResult, SourceRepresentation
from proposition_authoring.production_slice import (
    CONTRACT_A_SOURCE_REPRESENTATION_UNSUPPORTED,
    standardize_gate_production_slice_v1,
)
from proposition_authoring.receipt import build_receipt


class _NotNeededEngine(AuthoringEngine):
    def author(self, request: AuthoringRequest) -> AuthoringResult:
        contract_a = emit_not_decomposed(request)
        receipt = build_receipt(
            request,
            state="NOT_NEEDED",
            reason="BOUNDED_ROOT_IS_SINGLE_PROPOSITION",
            evaluations=[],
            surviving_clusters={},
            selected_cluster=None,
            selected_candidate_id=None,
            contract_a=contract_a,
            root_scope_findings=[],
        )
        return AuthoringResult(
            state="NOT_NEEDED",
            reason="BOUNDED_ROOT_IS_SINGLE_PROPOSITION",
            receipt=receipt,
            contract_a=contract_a,
        )


class ProductionSliceTests(unittest.TestCase):
    def request(self, media_type: str) -> AuthoringRequest:
        return AuthoringRequest(
            handoff_id="handoff-slice-test",
            producer_id="slice-test",
            producer_version="1",
            work_id="work-slice-test",
            root_id="claim-slice-test",
            root_text="The device is approved.",
            sources=(
                SourceRepresentation(
                    source_id="source-1",
                    media_type=media_type,
                    content="Current status: Approved.",
                ),
            ),
        )

    def test_unsupported_representation_fails_closed_without_relabeling(self) -> None:
        result = standardize_gate_production_slice_v1(
            self.request("text/html"),
            engine=_NotNeededEngine(),
            implementation_identity="slice-test",
        )

        self.assertEqual(result.authoring.state, "FAILED")
        self.assertEqual(
            result.authoring.reason,
            CONTRACT_A_SOURCE_REPRESENTATION_UNSUPPORTED,
        )
        self.assertIsNone(result.authoring.contract_a)
        self.assertEqual(
            result.claim_gate["contract_a_binding"],
            {"state": "absent", "handoff_sha256": None},
        )
        self.assertEqual(result.receipt["contract_a_state"], "absent")
        self.assertIsNone(result.receipt["contract_a_handoff_sha256"])
        self.assertFalse(
            result.receipt["downstream_authority"][
                "evidence_bundler_may_consume_contract_a"
            ]
        )
        self.assertEqual(result.evidence_gate["sources"][0]["media_type"], "text/html")

    def test_exact_plain_representation_preserves_v1_bytes(self) -> None:
        request = self.request("text/plain; charset=utf-8")
        predecessor = standardize_gates_v1_rc3(
            request,
            engine=_NotNeededEngine(),
            implementation_identity="slice-test",
        )
        candidate = standardize_gate_production_slice_v1(
            request,
            engine=_NotNeededEngine(),
            implementation_identity="slice-test",
        )
        self.assertEqual(candidate, predecessor)

    def test_exact_markdown_representation_preserves_v1_bytes(self) -> None:
        request = self.request("text/markdown; charset=utf-8")
        predecessor = standardize_gates_v1_rc3(
            request,
            engine=_NotNeededEngine(),
            implementation_identity="slice-test",
        )
        candidate = standardize_gate_production_slice_v1(
            request,
            engine=_NotNeededEngine(),
            implementation_identity="slice-test",
        )
        self.assertEqual(candidate, predecessor)

    def test_media_type_shorthand_is_not_silently_rewritten(self) -> None:
        result = standardize_gate_production_slice_v1(
            self.request("text/plain"),
            engine=_NotNeededEngine(),
            implementation_identity="slice-test",
        )
        self.assertEqual(result.authoring.state, "FAILED")
        self.assertIsNone(result.authoring.contract_a)
        self.assertEqual(result.evidence_gate["sources"][0]["media_type"], "text/plain")


if __name__ == "__main__":
    unittest.main()
