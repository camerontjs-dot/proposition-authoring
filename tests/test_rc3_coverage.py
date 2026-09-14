from __future__ import annotations

import unittest

from proposition_authoring.coverage_backend import CoverageBackend
from proposition_authoring.engine import AuthoringEngine
from proposition_authoring.model import AuthoringRequest


def request(case_id: str, text: str) -> AuthoringRequest:
    return AuthoringRequest(
        handoff_id=f"rc3-dev::{case_id}",
        producer_id="proposition-authoring",
        producer_version="rc3-development",
        work_id=f"rc3-dev::{case_id}",
        root_id=case_id,
        root_text=text,
    )


def child_texts(result) -> tuple[str, ...]:
    if result.contract_a is None or result.state != "DECLARED":
        return ()
    return tuple(row["text"] for row in result.contract_a["decomposition"]["children"])


class ReorderedBackend(CoverageBackend):
    def proposals(self, root):
        proposals = super().proposals(root)
        return {
            name: list(reversed(proposals[name]))
            for name in sorted(proposals, reverse=True)
        }


class DuplicateBackend(CoverageBackend):
    def proposals(self, root):
        proposals = super().proposals(root)
        out = {name: list(rows) for name, rows in proposals.items()}
        for name in sorted(out):
            if not out[name]:
                continue
            duplicate = dict(out[name][0])
            duplicate["case_id"] = duplicate["case_id"] + "::duplicate"
            duplicate["proposal_meta"] = {
                "proposer": "P6",
                "variant": "duplicate-control",
            }
            out["P6"] = [duplicate]
            break
        return out


class RC3CoverageDevelopmentTests(unittest.TestCase):
    def author(self, arm: str, case_id: str, text: str):
        return AuthoringEngine(CoverageBackend(arm)).author(request(case_id, text))

    def test_q09_baseline_abstains(self):
        result = self.author(
            "baseline",
            "q09-dev",
            "Archive service stored report delta and encrypted backup copy.",
        )
        self.assertEqual("ABSTAINED", result.state)

    def test_p4_recovers_q09(self):
        result = self.author(
            "p4",
            "q09-dev",
            "Archive service stored report delta and encrypted backup copy.",
        )
        self.assertEqual("DECLARED", result.state)
        self.assertEqual(
            {
                "Archive service stored report delta.",
                "Archive service encrypted backup copy.",
            },
            set(child_texts(result)),
        )

    def test_p4_generalizes_predicate_looking_subject_collision(self):
        text = "Archive node logged alarm bronze and stored incident silver."
        baseline = self.author("baseline", "p4-generalization", text)
        recovered = self.author("p4", "p4-generalization", text)
        self.assertEqual("ABSTAINED", baseline.state)
        self.assertEqual("DECLARED", recovered.state)
        self.assertEqual(
            {
                "Archive node logged alarm bronze.",
                "Archive node stored incident silver.",
            },
            set(child_texts(recovered)),
        )

    def test_q21_baseline_abstains(self):
        result = self.author(
            "baseline",
            "q21-dev",
            "Committee Alder reported that Unit Quartz passed and Unit Jade failed.",
        )
        self.assertEqual("ABSTAINED", result.state)

    def test_p5_recovers_q21(self):
        result = self.author(
            "p5",
            "q21-dev",
            "Committee Alder reported that Unit Quartz passed and Unit Jade failed.",
        )
        self.assertEqual("DECLARED", result.state)
        self.assertEqual(
            {
                "Committee Alder reported that Unit Quartz passed.",
                "Committee Alder reported that Unit Jade failed.",
            },
            set(child_texts(result)),
        )

    def test_p5_generalizes_explicit_shared_attribution(self):
        text = "Board Maple stated that Unit Bronze passed and Unit Silver failed."
        baseline = self.author("baseline", "p5-generalization", text)
        recovered = self.author("p5", "p5-generalization", text)
        self.assertEqual("ABSTAINED", baseline.state)
        self.assertEqual("DECLARED", recovered.state)
        self.assertEqual(
            {
                "Board Maple stated that Unit Bronze passed.",
                "Board Maple stated that Unit Silver failed.",
            },
            set(child_texts(recovered)),
        )

    def test_q18_remains_frozen_authority_limit(self):
        result = self.author(
            "pooled",
            "q18-dev",
            "Gateway Umber did not authenticate token quartz and logged denial event.",
        )
        self.assertEqual("ABSTAINED", result.state)

    def test_q29_unmarked_attribution_remains_fail_closed(self):
        result = self.author(
            "pooled",
            "q29-dev",
            "Auditor Pine reported Unit Cedar passed and Unit Birch failed.",
        )
        self.assertEqual("ABSTAINED", result.state)

    def test_proposer_and_candidate_order_do_not_change_authority(self):
        req = request(
            "order-dev",
            "Archive service stored report delta and encrypted backup copy.",
        )
        ordinary = AuthoringEngine(CoverageBackend("pooled")).author(req)
        reordered = AuthoringEngine(ReorderedBackend("pooled")).author(req)
        self.assertEqual(ordinary.state, reordered.state)
        self.assertEqual(ordinary.contract_a, reordered.contract_a)

    def test_duplicate_proposal_count_does_not_change_authority(self):
        req = request(
            "dup-dev",
            "Committee Alder reported that Unit Quartz passed and Unit Jade failed.",
        )
        ordinary = AuthoringEngine(CoverageBackend("pooled")).author(req)
        duplicated = AuthoringEngine(DuplicateBackend("pooled")).author(req)
        self.assertEqual(ordinary.state, duplicated.state)
        self.assertEqual(ordinary.contract_a, duplicated.contract_a)


if __name__ == "__main__":
    unittest.main()
