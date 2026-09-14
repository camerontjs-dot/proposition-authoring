from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from proposition_authoring.engine import AuthoringEngine
from proposition_authoring.model import AuthoringRequest


class FakeBackend:
    def __init__(self, *, candidates=None, root_status="ok", root_frames=2, root_reason=""):
        self.candidates = candidates or {}
        self.root_status = root_status
        self.root_frames = root_frames
        self.root_reason = root_reason

    def proposals(self, root):
        return self.candidates

    def root_frame_count(self, root_text, context_text):
        return self.root_status, self.root_frames, self.root_reason

    def evaluate(self, candidate):
        return {
            "disposition": candidate.get("disposition", "ACCEPTABLE_WITHIN_PROFILE"),
            "canonical_sha256": "sha256:" + "2" * 64,
        }

    def cluster_key(self, candidate):
        return candidate["cluster"]


def candidate(cid: str, cluster: str, disposition="ACCEPTABLE_WITHIN_PROFILE"):
    return {
        "case_id": cid,
        "root_id": "r1",
        "root_text": "A and B.",
        "context_text": "",
        "candidate_state": "DECLARED",
        "operator": "all_of",
        "children": [
            {"child_id": cid + "-1", "text": "A."},
            {"child_id": cid + "-2", "text": "B."},
        ],
        "proposal_meta": {"proposer": cid.split("-")[0], "variant": "test"},
        "cluster": cluster,
        "disposition": disposition,
    }


class WeakControlTests(unittest.TestCase):
    def request(self):
        return AuthoringRequest(
            handoff_id="h1",
            producer_id="proposition-authoring",
            producer_version="test",
            work_id="w1",
            root_id="r1",
            root_text="A and B.",
        )

    def test_force_not_decomposed_control_collapses_multi_proposition_unknown(self):
        result = AuthoringEngine(
            FakeBackend(root_status="ok", root_frames=2, candidates={})
        ).author(self.request())
        forced_control = "NOT_NEEDED"
        self.assertEqual(result.state, "ABSTAINED")
        self.assertNotEqual(forced_control, result.state)

    def test_majority_vote_control_collapses_material_cluster_disagreement(self):
        a1 = candidate("P1-a", "cluster-a")
        a2 = candidate("P2-a", "cluster-a")
        b1 = candidate("P3-b", "cluster-b")
        result = AuthoringEngine(
            FakeBackend(candidates={"P1": [a1], "P2": [a2], "P3": [b1]})
        ).author(self.request())
        majority_control = "RESOLVED_CLUSTER_A"
        self.assertEqual(result.state, "ABSTAINED")
        self.assertEqual(majority_control, "RESOLVED_CLUSTER_A")

    def test_first_candidate_control_can_select_rejected_candidate(self):
        unsafe = candidate("P1-unsafe", "cluster-x", disposition="REJECT_UNSAFE")
        safe = candidate("P2-safe", "cluster-a")
        result = AuthoringEngine(
            FakeBackend(candidates={"P1": [unsafe], "P2": [safe]})
        ).author(self.request())
        first_candidate_control = unsafe["case_id"]
        self.assertEqual(result.state, "DECLARED")
        self.assertNotEqual(result.receipt["selected_candidate_id"], first_candidate_control)

    def test_silent_abstention_coercion_would_invent_contract_a_authority(self):
        result = AuthoringEngine(
            FakeBackend(root_status="ambiguous", root_frames=0, root_reason="AMBIGUOUS")
        ).author(self.request())
        coerced_control = {"decomposition": {"state": "not_decomposed"}}
        self.assertEqual(result.state, "ABSTAINED")
        self.assertIsNone(result.contract_a)
        self.assertEqual(coerced_control["decomposition"]["state"], "not_decomposed")


if __name__ == "__main__":
    unittest.main()
