from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "research" / "rc4b_context_free_reproduction"
PACKET = BASE / "TASK_PACKET.json"
RUNNER = BASE / "run_reproduction.py"
PROVISIONER = BASE / "provision_candidate.py"


class RC4bPacketTests(unittest.TestCase):
    def test_packet_is_narrow_and_identity_pinned(self):
        packet = json.loads(PACKET.read_text(encoding="utf-8"))
        self.assertEqual(
            "f9d0ae9ba81756c51d7f1d433616d699eb9b6fd3",
            packet["candidate_commit"],
        )
        self.assertEqual(
            [
                "active",
                "approved",
                "compliant",
                "failed",
                "inactive",
                "passed",
                "ready",
                "restarted",
                "stopped",
            ],
            packet["p5_competence"]["embedded_predicates"],
        )
        self.assertEqual(
            len(packet["runtime_files"]),
            len({row["path"] for row in packet["runtime_files"]}),
        )
        text = PACKET.read_text(encoding="utf-8")
        for forbidden in (
            "C09",
            "C14",
            "34/36",
            "18/18",
            "6/6 proposer",
            "07f62c0d",
            "ca550480",
        ):
            self.assertNotIn(forbidden, text)

    def test_pre_reveal_execution_code_has_no_gold_access(self):
        for path in (RUNNER, PROVISIONER):
            text = path.read_text(encoding="utf-8").lower()
            self.assertNotIn("fresh_gold", text)
            self.assertNotIn("/gold/", text)
            self.assertNotIn("expected_state", text)


if __name__ == "__main__":
    unittest.main()
