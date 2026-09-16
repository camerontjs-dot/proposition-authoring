from __future__ import annotations

import unittest

from proposition_authoring.coverage_backend import CoverageBackend
from proposition_authoring.coverage_proposers import (
    P5_AUTHORITY_COMPATIBLE_EMBEDDED_PREDICATES,
    P5_PREALIGNMENT_EMBEDDED_PREDICATES,
    proposer_p5,
    proposer_p5_prealignment_control,
)


class RC4aProfileAlignmentTests(unittest.TestCase):
    def setUp(self) -> None:
        self.backend = CoverageBackend("p5")

    @staticmethod
    def root(root_id: str, text: str) -> dict[str, str]:
        return {"root_id": root_id, "root_text": text, "context_text": ""}

    @staticmethod
    def manual_candidate(root: dict[str, str], left: str, right: str) -> dict:
        matrix = root["root_text"].split(" that ", 1)[0]
        return {
            "case_id": f"{root['root_id']}::authority-probe",
            "root_id": root["root_id"],
            "root_text": root["root_text"],
            "context_text": "",
            "profile_id": "pc-evaluator-rc1-binding-v1",
            "candidate_state": "DECLARED",
            "operator": "all_of",
            "children": [
                {"child_id": f"{root['root_id']}::probe::c1", "text": f"{matrix} that {left}."},
                {"child_id": f"{root['root_id']}::probe::c2", "text": f"{matrix} that {right}."},
            ],
        }

    def test_alignment_removes_only_revealed_proposer_only_token(self) -> None:
        aligned = set(P5_AUTHORITY_COMPATIBLE_EMBEDDED_PREDICATES)
        old = set(P5_PREALIGNMENT_EMBEDDED_PREDICATES)
        self.assertEqual(old - aligned, {"rejected"})
        self.assertEqual(aligned - old, set())

    def test_every_declared_p5_predicate_is_authority_warrantable(self) -> None:
        for index, predicate in enumerate(P5_AUTHORITY_COMPATIBLE_EMBEDDED_PREDICATES, start=1):
            root = self.root(
                f"dev-authority-{index}",
                f"Panel Cedar reported that Unit Amber was {predicate} and Unit Cobalt was approved.",
            )
            proposals = proposer_p5(root)
            self.assertEqual(len(proposals), 1, predicate)
            result = self.backend.evaluate(proposals[0])
            self.assertEqual(result["disposition"], "ACCEPTABLE_WITHIN_PROFILE", predicate)

    def test_revealed_rc4_rejected_cases_are_suppressed_prospectively(self) -> None:
        roots = [
            self.root(
                "c09-revealed",
                "Committee Birch reported that Plan Coral was approved and Plan Ivory was rejected.",
            ),
            self.root(
                "c14-revealed",
                "Board Elm reported that Route Indigo was approved and Route Violet was rejected.",
            ),
        ]
        for root in roots:
            self.assertEqual(proposer_p5(root), [])
            weak = proposer_p5_prealignment_control(root)
            self.assertEqual(len(weak), 1)
            self.assertNotEqual(
                self.backend.evaluate(weak[0])["disposition"],
                "ACCEPTABLE_WITHIN_PROFILE",
            )

    def test_authority_can_be_broader_without_expanding_p5(self) -> None:
        root = self.root(
            "dev-authority-only",
            "Panel Cedar reported that Unit Amber was reviewed and Unit Cobalt was approved.",
        )
        self.assertEqual(proposer_p5(root), [])
        self.assertEqual(proposer_p5_prealignment_control(root), [])
        candidate = self.manual_candidate(
            root,
            "Unit Amber was reviewed",
            "Unit Cobalt was approved",
        )
        self.assertEqual(
            self.backend.evaluate(candidate)["disposition"],
            "ACCEPTABLE_WITHIN_PROFILE",
        )


if __name__ == "__main__":
    unittest.main()
