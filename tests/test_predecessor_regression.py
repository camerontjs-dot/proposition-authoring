from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from proposition_authoring.engine import AuthoringEngine
from proposition_authoring.model import AuthoringRequest, SourceRepresentation


class PredecessorRegressionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        vendor = ROOT / "vendor" / "frozen"
        cls.roots_path = vendor / "predecessor_fresh_roots.jsonl"
        cls.gold_path = vendor / "predecessor_fresh_gold.jsonl"
        cls.validator_path = vendor / "contract_a_rc2.py"
        if not (cls.roots_path.exists() and cls.gold_path.exists() and cls.validator_path.exists()):
            raise unittest.SkipTest("frozen predecessor evidence not bootstrapped")
        spec = importlib.util.spec_from_file_location("pa_contract_a_validator", cls.validator_path)
        assert spec is not None and spec.loader is not None
        cls.validator = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = cls.validator
        spec.loader.exec_module(cls.validator)

    @staticmethod
    def _rows(path: Path) -> list[dict]:
        return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]

    def test_v0_preserves_predecessor_semantic_boundary(self) -> None:
        roots = {row["root_id"]: row for row in self._rows(self.roots_path)}
        gold = {row["root_id"]: row for row in self._rows(self.gold_path)}
        self.assertEqual(set(roots), set(gold))

        # PR #65 preserved these three semantically resolvable roots as bounded false negatives.
        expected_false_negatives = {"F18", "F19", "F20"}
        declared = 0
        abstained = 0
        not_needed = 0
        engine = AuthoringEngine()

        for root_id in sorted(roots):
            row = roots[root_id]
            source_rows = ()
            context_source_id = None
            if row.get("context_text"):
                source_rows = (
                    SourceRepresentation(
                        source_id=f"context::{root_id}",
                        media_type="text/plain; charset=utf-8",
                        content=row["context_text"],
                    ),
                )
                context_source_id = f"context::{root_id}"

            request = AuthoringRequest(
                handoff_id=f"predecessor-regression::{root_id}",
                producer_id="proposition-authoring",
                producer_version="v0-development-regression",
                work_id=f"predecessor::{root_id}",
                root_id=root_id,
                root_text=row["root_text"],
                sources=source_rows,
                context_source_id=context_source_id,
            )
            result = engine.author(request)

            if gold[root_id]["expected"] == "FAIL_CLOSED" or root_id in expected_false_negatives:
                self.assertEqual(result.state, "ABSTAINED", root_id)
                self.assertIsNone(result.contract_a, root_id)
                abstained += 1
                continue

            self.assertEqual(result.state, "DECLARED", root_id)
            self.assertIsNotNone(result.contract_a, root_id)
            self.validator.validate_candidate(result.contract_a)
            child_texts = [c["text"] for c in result.contract_a["decomposition"]["children"]]
            self.assertIn(child_texts, gold[root_id]["allowed_child_sets"], root_id)
            declared += 1

        self.assertEqual(declared, 19)
        self.assertEqual(abstained, 5)
        self.assertEqual(not_needed, 0)


if __name__ == "__main__":
    unittest.main()
