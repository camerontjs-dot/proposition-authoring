from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from proposition_authoring.contract_a import emit_declared
from proposition_authoring.engine import AuthoringEngine
from proposition_authoring.model import AuthoringRequest


class FakeBackend:
    def __init__(
        self,
        *,
        candidates=None,
        root_status="ok",
        root_frames=2,
        root_reason="",
    ):
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
            "canonical_sha256": "sha256:" + "1" * 64,
        }

    def cluster_key(self, candidate):
        return candidate["cluster"]


class ExplodingBackend(FakeBackend):
    def proposals(self, root):
        raise RuntimeError("synthetic processing failure")


def candidate(
    cid: str,
    cluster: str,
    children: tuple[str, str],
    disposition="ACCEPTABLE_WITHIN_PROFILE",
):
    return {
        "case_id": cid,
        "root_id": "r1",
        "root_text": "A and B.",
        "context_text": "",
        "candidate_state": "DECLARED",
        "operator": "all_of",
        "children": [
            {"child_id": cid + "-1", "text": children[0]},
            {"child_id": cid + "-2", "text": children[1]},
        ],
        "proposal_meta": {"proposer": cid.split("-")[0], "variant": "test"},
        "cluster": cluster,
        "disposition": disposition,
    }


class ConvergenceChoiceTests(unittest.TestCase):
    def request(self, root_text="A and B."):
        return AuthoringRequest(
            handoff_id="h1",
            producer_id="proposition-authoring",
            producer_version="test",
            work_id="w1",
            root_id="r1",
            root_text=root_text,
        )

    def test_representative_selection_is_proposer_order_invariant(self):
        zulu = candidate("P1-z", "cluster-a", ("Zulu A.", "Zulu B."))
        alpha = candidate("P2-a", "cluster-a", ("Alpha A.", "Alpha B."))
        first = AuthoringEngine(
            FakeBackend(candidates={"P1": [zulu], "P2": [alpha]})
        ).author(self.request())
        second = AuthoringEngine(
            FakeBackend(candidates={"P2": [alpha], "P1": [zulu]})
        ).author(self.request())
        self.assertEqual(first.state, "DECLARED")
        self.assertEqual(second.state, "DECLARED")
        self.assertEqual(first.contract_a, second.contract_a)
        self.assertEqual(first.receipt, second.receipt)
        self.assertEqual(
            [row["text"] for row in first.contract_a["decomposition"]["children"]],
            ["Alpha A.", "Alpha B."],
        )

    def test_candidate_list_order_is_receipt_invariant(self):
        zulu = candidate("P1-z", "cluster-a", ("Zulu A.", "Zulu B."))
        alpha = candidate("P1-a", "cluster-a", ("Alpha A.", "Alpha B."))
        first = AuthoringEngine(FakeBackend(candidates={"P1": [zulu, alpha]})).author(
            self.request()
        )
        second = AuthoringEngine(FakeBackend(candidates={"P1": [alpha, zulu]})).author(
            self.request()
        )
        self.assertEqual(first.state, "DECLARED")
        self.assertEqual(first.contract_a, second.contract_a)
        self.assertEqual(first.receipt, second.receipt)

    def test_child_ids_are_stable_under_semantically_irrelevant_all_of_reorder(self):
        forward = emit_declared(
            self.request(),
            decomposition_id="d1",
            child_texts=("Alpha A.", "Beta B."),
        )
        reverse = emit_declared(
            self.request(),
            decomposition_id="d1",
            child_texts=("Beta B.", "Alpha A."),
        )
        forward_ids = {
            row["text"]: row["proposition_id"]
            for row in forward["decomposition"]["children"]
        }
        reverse_ids = {
            row["text"]: row["proposition_id"]
            for row in reverse["decomposition"]["children"]
        }
        self.assertEqual(forward_ids, reverse_ids)

    def test_processing_failure_is_failed_not_semantic_abstention(self):
        result = AuthoringEngine(ExplodingBackend()).author(self.request())
        self.assertEqual(result.state, "FAILED")
        self.assertEqual(result.contract_a["decomposition"], {"state": "failed"})
        self.assertTrue(result.reason.startswith("PROCESSING_FAILURE:"))

    def test_semantic_ambiguity_is_abstained_not_failed(self):
        result = AuthoringEngine(
            FakeBackend(root_status="ambiguous", root_frames=0, root_reason="AMBIGUOUS")
        ).author(self.request())
        self.assertEqual(result.state, "ABSTAINED")
        self.assertIsNone(result.contract_a)


if __name__ == "__main__":
    unittest.main()
