from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "research" / "rc4_context_free_reproduction" / "TASK_PACKET.json"
RUNNER = ROOT / "research" / "rc4_context_free_reproduction" / "run_reproduction.py"
PROVISIONER = ROOT / "research" / "rc4_context_free_reproduction" / "provision_candidate.py"


class RC4PacketTests(unittest.TestCase):
    def test_packet_is_narrow_and_freshness_safe(self):
        packet = json.loads(PACKET.read_text(encoding="utf-8"))
        self.assertEqual("50a943c401f8a09d5bb940472bdad43b54dca5d0", packet["candidate_commit"])
        self.assertEqual(len(packet["runtime_files"]), len({row["path"] for row in packet["runtime_files"]}))
        text = PACKET.read_text(encoding="utf-8")
        for forbidden in ("36/36", "14 safe gains", "R01", "Q09", "pull/17", "issue #7"):
            self.assertNotIn(forbidden, text)

    def test_pre_reveal_execution_code_has_no_gold_access(self):
        for path in (RUNNER, PROVISIONER):
            text = path.read_text(encoding="utf-8").lower()
            self.assertNotIn("fresh_gold", text)
            self.assertNotIn("/gold/", text)

    def test_fresh_surface_absent_before_freeze(self):
        self.assertFalse((ROOT / "research" / "rc4_context_free_reproduction" / "fresh_cases.jsonl").exists())
        self.assertFalse((ROOT / "research" / "rc4_context_free_reproduction" / "GOLD" / "fresh_gold.jsonl").exists())


if __name__ == "__main__":
    unittest.main()
