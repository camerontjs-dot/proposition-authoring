from __future__ import annotations

import unittest

from proposition_authoring.ambiguity import analyze_root_scope
from proposition_authoring.engine import AuthoringEngine
from proposition_authoring.model import AuthoringRequest


def request(root_id: str, root_text: str) -> AuthoringRequest:
    return AuthoringRequest(
        handoff_id=f"rc1-dev::{root_id}",
        producer_id="proposition-authoring",
        producer_version="rc1-development",
        work_id=f"rc1-dev::{root_id}",
        root_id=root_id,
        root_text=root_text,
    )


class RC1RevealedDevelopmentCases(unittest.TestCase):
    def test_v0_q29_is_now_fail_closed(self):
        result = AuthoringEngine().author(
            request(
                "q29-dev",
                "Auditor Pine reported Unit Cedar passed and Unit Birch failed.",
            )
        )
        self.assertEqual("ABSTAINED", result.state)
        self.assertEqual("MATERIAL_ROOT_SCOPE_AMBIGUITY", result.reason)
        self.assertIsNone(result.contract_a)
        self.assertEqual(
            ["MATRIX_ATTRIBUTION_SCOPE"],
            [row["family"] for row in result.receipt["root_scope_findings"]],
        )

    def test_v0_q21_explicit_that_is_not_flagged_as_scope_ambiguous(self):
        root = "Committee Alder reported that Unit Quartz passed and Unit Jade failed."
        self.assertNotIn(
            "MATRIX_ATTRIBUTION_SCOPE",
            {row["family"] for row in analyze_root_scope(root)},
        )

    def test_q29_terminal_comma_variant_is_same_hazard(self):
        plain = analyze_root_scope(
            "Auditor Pine reported Unit Cedar passed and Unit Birch failed."
        )
        comma = analyze_root_scope(
            "Auditor Pine reported Unit Cedar passed, and Unit Birch failed."
        )
        self.assertEqual(plain, comma)


if __name__ == "__main__":
    unittest.main()
