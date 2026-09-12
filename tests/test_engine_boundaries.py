from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from proposition_authoring.engine import AuthoringEngine
from proposition_authoring.model import AuthoringRequest


class FakeBackend:
    def __init__(self, *, root_status="ok", root_frames=2, root_reason="", candidates=None):
        self.root_status = root_status
        self.root_frames = root_frames
        self.root_reason = root_reason
        self.candidates = candidates or {}

    def proposals(self, root):
        return self.candidates

    def root_frame_count(self, root_text, context_text):
        return self.root_status, self.root_frames, self.root_reason

    def evaluate(self, candidate):
        return {
            "disposition": candidate.get("disposition", "REJECT_UNSAFE"),
            "canonical_sha256": "sha256:" + "0" * 64,
        }

    def cluster_key(self, candidate):
        return candidate["cluster"]


def candidate(cid, cluster, disposition="ACCEPTABLE_WITHIN_PROFILE"):
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


class EngineBoundaryTests(unittest.TestCase):
    def request(self, root_text="A and B."):
        return AuthoringRequest(
            handoff_id="h1",
            producer_id="proposition-authoring",
            producer_version="test",
            work_id="w1",
            root_id="r1",
            root_text=root_text,
        )

    def test_no_proposal_is_not_automatically_not_decomposed(self):
        engine = AuthoringEngine(FakeBackend(root_status="unsupported", root_frames=0, root_reason="X"))
        result = engine.author(self.request())
        self.assertEqual(result.state, "ABSTAINED")
        self.assertIsNone(result.contract_a)

    def test_single_root_frame_can_emit_not_decomposed(self):
        engine = AuthoringEngine(FakeBackend(root_status="ok", root_frames=1))
        result = engine.author(self.request(root_text="Panel Cedar approved plan amber."))
        self.assertEqual(result.state, "NOT_NEEDED")
        self.assertEqual(result.contract_a["decomposition"]["state"], "not_decomposed")

    def test_single_frame_with_composition_hazard_abstains(self):
        engine = AuthoringEngine(FakeBackend(root_status="ok", root_frames=1))
        result = engine.author(self.request(root_text="Panel Cedar approved plan amber and Board Maple reported Plan bronze."))
        self.assertEqual(result.state, "ABSTAINED")
        self.assertEqual(result.reason, "NOT_NEEDED_BLOCKED_BY_COMPOSITION_HAZARD")
        self.assertIsNone(result.contract_a)

    def test_one_surviving_cluster_declares(self):
        c1 = candidate("P1-c1", "cluster-a")
        c2 = candidate("P2-c1", "cluster-a")
        engine = AuthoringEngine(FakeBackend(candidates={"P1": [c1], "P2": [c2]}))
        result = engine.author(self.request())
        self.assertEqual(result.state, "DECLARED")
        self.assertEqual(result.contract_a["decomposition"]["state"], "declared")

    def test_two_surviving_clusters_abstain(self):
        c1 = candidate("P1-c1", "cluster-a")
        c2 = candidate("P2-c1", "cluster-b")
        engine = AuthoringEngine(FakeBackend(candidates={"P1": [c1], "P2": [c2]}))
        result = engine.author(self.request())
        self.assertEqual(result.state, "ABSTAINED")
        self.assertIsNone(result.contract_a)


if __name__ == "__main__":
    unittest.main()
