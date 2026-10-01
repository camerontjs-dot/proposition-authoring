from __future__ import annotations

import unittest

from proposition_authoring.ambiguity import analyze_root_scope
from proposition_authoring.engine import AuthoringEngine
from proposition_authoring.model import AuthoringRequest


class OneCandidateBackend:
    def proposals(self, root):
        return {
            "P2": [
                {
                    "case_id": f"{root['root_id']}::P2::candidate",
                    "root_text": root["root_text"],
                    "context_text": root["context_text"],
                    "children": [
                        {"id": "c1", "text": "Auditor Pine reported Unit Cedar passed."},
                        {"id": "c2", "text": "Unit Birch failed."},
                    ],
                    "proposal_meta": {"proposer": "P2", "variant": "candidate"},
                }
            ]
        }

    def evaluate(self, candidate):
        return {"disposition": "ACCEPTABLE_WITHIN_PROFILE", "canonical_sha256": "sha256:test"}

    def cluster_key(self, candidate):
        return "sha256:one-cluster"

    def root_frame_count(self, root_text, context_text):
        return "ok", 2, ""


def request(root_text: str) -> AuthoringRequest:
    return AuthoringRequest(
        handoff_id="handoff-test",
        producer_id="test",
        producer_version="1",
        work_id="work-test",
        root_id="root-test",
        root_text=root_text,
    )


class ScopeAnalyzerTests(unittest.TestCase):
    def families(self, text: str) -> set[str]:
        return {row["family"] for row in analyze_root_scope(text)}

    def test_q29_family_is_detected(self):
        text = "Auditor Pine reported Unit Cedar passed and Unit Birch failed."
        self.assertIn("MATRIX_ATTRIBUTION_SCOPE", self.families(text))

    def test_comma_does_not_resolve_q29_family(self):
        text = "Auditor Pine reported Unit Cedar passed, and Unit Birch failed."
        self.assertIn("MATRIX_ATTRIBUTION_SCOPE", self.families(text))

    def test_that_complement_is_clear_in_bounded_profile(self):
        text = "Auditor Pine reported that Unit Cedar passed and Unit Birch failed."
        self.assertNotIn("MATRIX_ATTRIBUTION_SCOPE", self.families(text))

    def test_repeated_matrix_predicate_is_clear(self):
        text = (
            "Auditor Pine reported Unit Cedar passed and Auditor Pine reported Unit Birch failed."
        )
        self.assertNotIn("MATRIX_ATTRIBUTION_SCOPE", self.families(text))

    def test_both_is_clear(self):
        text = "Auditor Pine reported both Unit Cedar passed and Unit Birch failed."
        self.assertNotIn("MATRIX_ATTRIBUTION_SCOPE", self.families(text))

    def test_trailing_adjunct_scope_is_detected(self):
        text = "Unit Cedar passed and Unit Birch failed in Zone Red."
        self.assertIn("TRAILING_ADJUNCT_SCOPE", self.families(text))

    def test_prefix_shared_adjunct_is_not_trailing_ambiguity(self):
        text = "In Zone Red, Unit Cedar passed and Unit Birch failed."
        self.assertNotIn("TRAILING_ADJUNCT_SCOPE", self.families(text))

    def test_repeated_local_adjunct_is_clear(self):
        text = "Unit Cedar passed in Zone Red and Unit Birch failed in Zone Red."
        self.assertNotIn("TRAILING_ADJUNCT_SCOPE", self.families(text))

    def test_sentential_negation_scope_is_detected(self):
        text = "It is not true that Unit Cedar passed and Unit Birch failed."
        self.assertIn("SENTENTIAL_NEGATION_SCOPE", self.families(text))

    def test_ordinary_local_negation_is_not_promoted_to_ambiguity(self):
        text = "Unit Cedar did not pass and Unit Birch failed."
        self.assertNotIn("SENTENTIAL_NEGATION_SCOPE", self.families(text))

    def test_single_proposition_has_no_finding(self):
        self.assertEqual([], analyze_root_scope("Unit Cedar passed."))


class EngineGateTests(unittest.TestCase):
    def test_material_scope_finding_vetoes_one_surviving_cluster(self):
        result = AuthoringEngine(backend=OneCandidateBackend()).author(
            request("Auditor Pine reported Unit Cedar passed and Unit Birch failed.")
        )
        self.assertEqual("ABSTAINED", result.state)
        self.assertEqual("MATERIAL_ROOT_SCOPE_AMBIGUITY", result.reason)
        self.assertIsNone(result.contract_a)
        self.assertEqual("MATRIX_ATTRIBUTION_SCOPE", result.receipt["root_scope_findings"][0]["family"])

    def test_clear_counterpart_preserves_normal_resolution(self):
        result = AuthoringEngine(backend=OneCandidateBackend()).author(
            request("Auditor Pine reported that Unit Cedar passed and Unit Birch failed.")
        )
        self.assertEqual("DECLARED", result.state)
        self.assertIsNotNone(result.contract_a)
        self.assertEqual([], result.receipt["root_scope_findings"])


if __name__ == "__main__":
    unittest.main()
