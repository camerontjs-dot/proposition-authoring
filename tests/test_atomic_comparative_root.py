from __future__ import annotations

import unittest

from proposition_authoring.comparative_root import is_bounded_atomic_comparative
from proposition_authoring.engine import AuthoringEngine
from proposition_authoring.model import AuthoringRequest


class AtomicComparativeRootTests(unittest.TestCase):
    def test_bounded_positive_surface_forms(self) -> None:
        for text in (
            "Women had a higher rate than Men.",
            "Group A had a lower rate than Group B.",
            "The treatment arm had fewer events than the control arm.",
            "Version 2 had greater latency than Version 1.",
        ):
            with self.subTest(text=text):
                self.assertTrue(is_bounded_atomic_comparative(text))

    def test_hard_negatives_remain_outside_profile(self) -> None:
        for text in (
            "Women had a higher rate than Men and lower mortality than Children.",
            "Women had a higher rate than Men, according to the report, in 2024.",
            "Women did not have a higher rate than Men.",
            "Women had a higher rate.",
            "Women and Men had a higher rate than Children.",
        ):
            with self.subTest(text=text):
                self.assertFalse(is_bounded_atomic_comparative(text))

    def test_context_bearing_root_is_not_promoted_by_surface_recognizer(self) -> None:
        self.assertFalse(
            is_bounded_atomic_comparative(
                "Women had a higher rate than Men.",
                "The report defines a special population scope.",
            )
        )

    def test_a1a_root_reaches_not_needed_without_claim_profile_authority(self) -> None:
        request = AuthoringRequest(
            handoff_id="test-a1a",
            producer_id="test",
            producer_version="v0",
            work_id="test-a1a",
            root_id="A1A-C1",
            root_text="Women had a higher rate than Men.",
            sources=(),
        )
        result = AuthoringEngine().author(request)
        self.assertEqual(result.state, "NOT_NEEDED")
        self.assertEqual(result.reason, "BOUNDED_ROOT_IS_SINGLE_PROPOSITION")
        self.assertIsNotNone(result.contract_a)


if __name__ == "__main__":
    unittest.main()
