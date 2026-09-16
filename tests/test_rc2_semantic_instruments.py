from __future__ import annotations

import inspect
import unittest

import proposition_authoring.conservation as conservation_module
from proposition_authoring.authority import evaluate_candidate
from proposition_authoring.backend import FrozenPredecessorBackend
from proposition_authoring.conservation import INSTRUMENT_ID, audit_candidate


def candidate(case_id: str, root: str, children: tuple[str, str]) -> dict:
    return {
        "case_id": case_id,
        "root_id": case_id,
        "root_text": root,
        "context_text": "",
        "profile_id": "pc-evaluator-rc1-binding-v1",
        "candidate_state": "DECLARED",
        "operator": "all_of",
        "children": [
            {"child_id": case_id + "-1", "text": children[0]},
            {"child_id": case_id + "-2", "text": children[1]},
        ],
        "proposal_meta": {"proposer": "development", "variant": "manual"},
    }


class ExplodingBackend:
    def evaluate(self, row):
        raise AssertionError("frozen evaluator should not run after root ambiguity veto")


class RC2DevelopmentTests(unittest.TestCase):
    def test_independent_implementation_path(self):
        source = inspect.getsource(conservation_module)
        for forbidden in ("from .backend", "importlib", "parse_root", "parse_child"):
            self.assertNotIn(forbidden, source)

    def test_successor_conservation_identity_is_explicit(self):
        self.assertEqual("surface-scope-conservation-v2", INSTRUMENT_ID)

    def test_r22_wrong_candidate_is_rejected(self):
        root = "Committee Pine reported both Unit Amber passed and Unit Cobalt failed."
        children = ("Committee Pine reported both Unit Amber passed.", "Unit Cobalt failed.")
        result = audit_candidate(root, children)
        self.assertEqual("FAIL", result.disposition)
        self.assertIn("SHARED_MATRIX_ATTRIBUTION_LOST", result.findings)

    def test_r22_conservative_candidate_passes(self):
        root = "Committee Pine reported both Unit Amber passed and Unit Cobalt failed."
        children = (
            "Committee Pine reported Unit Amber passed.",
            "Committee Pine reported Unit Cobalt failed.",
        )
        self.assertEqual("PASS", audit_candidate(root, children).disposition)

    def test_q18_local_negation_passes(self):
        root = "Gateway Umber did not authenticate token quartz and logged denial event."
        children = (
            "Gateway Umber did not authenticate token quartz.",
            "Gateway Umber logged denial event.",
        )
        self.assertEqual("PASS", audit_candidate(root, children).disposition)

    def test_f14_explicit_repeated_local_negation_passes(self):
        root = "Unit Brisk did not cache File C and did not cache File D."
        children = (
            "Unit Brisk did not cache File C.",
            "Unit Brisk did not cache File D.",
        )
        result = audit_candidate(root, children)
        self.assertEqual("PASS", result.disposition)
        self.assertIn("LOCAL_NEGATION", result.families)

    def test_f14_repeated_local_negation_loss_is_rejected(self):
        root = "Unit Brisk did not cache File C and did not cache File D."
        children = (
            "Unit Brisk did not cache File C.",
            "Unit Brisk cached File D.",
        )
        result = audit_candidate(root, children)
        self.assertEqual("FAIL", result.disposition)
        self.assertIn("REPEATED_LOCAL_NEGATION_BINDING_LOST", result.findings)

    def test_single_local_negation_must_not_propagate(self):
        root = "Gateway Umber did not authenticate token quartz and logged denial event."
        children = (
            "Gateway Umber did not authenticate token quartz.",
            "Gateway Umber did not log denial event.",
        )
        result = audit_candidate(root, children)
        self.assertEqual("FAIL", result.disposition)
        self.assertIn("LOCAL_NEGATION_OVERDISTRIBUTED", result.findings)

    def test_shared_qualifier_loss_is_rejected(self):
        root = (
            "During validation window, Controller Aspen logged alarm amber and archived incident report."
        )
        children = (
            "During validation window, Controller Aspen logged alarm amber.",
            "Controller Aspen archived incident report.",
        )
        self.assertEqual("FAIL", audit_candidate(root, children).disposition)

    def test_q29_is_blocked_before_evaluator(self):
        row = candidate(
            "q29-dev",
            "Auditor Pine reported Unit Cedar passed and Unit Birch failed.",
            ("Auditor Pine reported Unit Cedar passed.", "Unit Birch failed."),
        )
        result = evaluate_candidate(row, ExplodingBackend())
        self.assertEqual("BLOCK", result.disposition)
        self.assertEqual("ROOT_SCOPE_AMBIGUITY", result.reason)
        self.assertEqual(INSTRUMENT_ID, result.conservation["instrument"])

    def test_real_frozen_evaluator_r22_blind_spot_is_caught(self):
        backend = FrozenPredecessorBackend()
        root = {
            "root_id": "r22-dev",
            "root_text": "Committee Pine reported both Unit Amber passed and Unit Cobalt failed.",
            "context_text": "",
            "family": "development",
        }
        proposals = backend.proposals(root)
        self.assertEqual(1, len(proposals["P2"]))
        row = proposals["P2"][0]
        self.assertEqual(
            ["Committee Pine reported both Unit Amber passed.", "Unit Cobalt failed."],
            [child["text"] for child in row["children"]],
        )
        self.assertEqual("ACCEPTABLE_WITHIN_PROFILE", backend.evaluate(row)["disposition"])
        composed = evaluate_candidate(row, backend)
        self.assertEqual("BLOCK", composed.disposition)
        self.assertEqual("CONSERVATION_FAIL", composed.reason)


if __name__ == "__main__":
    unittest.main()
