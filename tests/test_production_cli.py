from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "research" / "gates_v1_rc3" / "health-canada-001.json"


class ProductionCliTests(unittest.TestCase):
    def _packet(self, root: Path, label: str, media_type: str) -> Path:
        packet = json.loads(FIXTURE.read_text(encoding="utf-8"))
        for row in packet["request"]["sources"]:
            row["media_type"] = media_type
        packet["request"]["handoff_id"] += f"-cli-{label}"
        packet["request"]["work_id"] += f"-cli-{label}"
        path = root / f"{label}.json"
        path.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return path

    def _tree(self, root: Path) -> dict[str, bytes]:
        return {
            str(path.relative_to(root)): path.read_bytes()
            for path in sorted(root.rglob("*"))
            if path.is_file()
        }

    def _run(self, argv: list[str]) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            argv,
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_installed_cli_matches_qualified_script_byte_for_byte(self) -> None:
        installed = shutil.which("proposition-authoring-v1")
        self.assertIsNotNone(installed, "installed production CLI is missing")

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            for label, media_type in (
                ("plain", "text/plain; charset=utf-8"),
                ("markdown", "text/markdown; charset=utf-8"),
                ("html", "text/html"),
            ):
                packet = self._packet(tmp_path, label, media_type)
                script_out = tmp_path / f"script-{label}"
                cli_out = tmp_path / f"cli-{label}"
                args = [
                    str(packet),
                    "--out-dir",
                    str(script_out),
                    "--implementation-identity",
                    "gate-v1-installed-cli-parity",
                ]
                script = self._run(
                    [sys.executable, "scripts/run_gate_production_slice_v1.py", *args]
                )
                self.assertEqual(script.returncode, 0, script.stderr)

                cli_args = [
                    str(packet),
                    "--out-dir",
                    str(cli_out),
                    "--implementation-identity",
                    "gate-v1-installed-cli-parity",
                ]
                cli = self._run([str(installed), *cli_args])
                self.assertEqual(cli.returncode, 0, cli.stderr)
                self.assertEqual(cli.stdout, script.stdout)
                self.assertEqual(cli.stderr, script.stderr)
                self.assertEqual(self._tree(cli_out), self._tree(script_out))

                if media_type == "text/html":
                    self.assertFalse((cli_out / "CONTRACT-A.json").exists())
                else:
                    self.assertTrue((cli_out / "CONTRACT-A.json").exists())


if __name__ == "__main__":
    unittest.main()
