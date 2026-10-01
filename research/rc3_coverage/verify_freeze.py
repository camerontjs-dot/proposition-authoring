from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = Path(__file__).with_name("FREEZE.json")


def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    failures: list[str] = []
    for row in manifest["frozen_files"]:
        path = ROOT / row["path"]
        if not path.exists():
            failures.append("missing:" + row["path"])
            continue
        blob = subprocess.check_output(
            ["git", "hash-object", str(path.relative_to(ROOT))],
            cwd=ROOT,
            text=True,
        ).strip()
        if blob != row["git_blob"]:
            failures.append("blob:" + row["path"])
    if failures:
        raise SystemExit("freeze verification failed\n" + "\n".join(failures))
    print(f"verified {len(manifest['frozen_files'])} frozen files")


if __name__ == "__main__":
    main()
