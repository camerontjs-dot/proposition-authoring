from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from proposition_authoring.contract_a import emit_declared, emit_not_decomposed
from proposition_authoring.model import AuthoringRequest, SourceRepresentation


class ContractATests(unittest.TestCase):
    def request(self) -> AuthoringRequest:
        return AuthoringRequest(
            handoff_id="handoff-test-001",
            producer_id="proposition-authoring",
            producer_version="test-version",
            work_id="work-001",
            root_id="root-001",
            root_text="Panel Cedar approved plan amber and Panel Maple approved plan bronze.",
            sources=(
                SourceRepresentation(
                    source_id="src-001",
                    media_type="text/plain; charset=utf-8",
                    content="Panel Cedar approved plan amber. Panel Maple approved plan bronze.",
                ),
            ),
        )

    def _validate_if_vendor_present(self, value: dict) -> None:
        path = ROOT / "vendor" / "frozen" / "contract_a_rc2.py"
        if not path.exists():
            return
        spec = importlib.util.spec_from_file_location("contract_a_validator_test", path)
        assert spec is not None and spec.loader is not None
        mod = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = mod
        spec.loader.exec_module(mod)
        mod.validate_candidate(value)

    def test_declared_object_is_self_bound(self) -> None:
        value = emit_declared(
            self.request(),
            decomposition_id="decomp-test-001",
            child_texts=(
                "Panel Cedar approved plan amber.",
                "Panel Maple approved plan bronze.",
            ),
        )
        self.assertEqual(value["decomposition"]["state"], "declared")
        self.assertTrue(value["handoff_sha256"].startswith("sha256:"))
        self._validate_if_vendor_present(value)

    def test_not_decomposed_object_is_self_bound(self) -> None:
        value = emit_not_decomposed(self.request())
        self.assertEqual(value["decomposition"], {"state": "not_decomposed"})
        self._validate_if_vendor_present(value)


if __name__ == "__main__":
    unittest.main()
