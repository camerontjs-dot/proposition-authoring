from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = Path(__file__).with_name("FREEZE.json")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_blob(path: Path) -> str:
    return subprocess.check_output(
        ["git", "hash-object", str(path.relative_to(ROOT))],
        cwd=ROOT,
        text=True,
    ).strip()


def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    failures: list[str] = []
    for row in manifest["frozen_files"]:
        path = ROOT / row["path"]
        if not path.exists():
            failures.append(f"missing:{row['path']}")
            continue
        actual_blob = git_blob(path)
        if actual_blob != row["git_blob"]:
            failures.append(f"git_blob:{row['path']}:{actual_blob}")
        expected_sha = row.get("sha256")
        if expected_sha is not None:
            actual_sha = sha256(path)
            if actual_sha != expected_sha:
                failures.append(f"sha256:{row['path']}:{actual_sha}")
    if failures:
        raise SystemExit("freeze verification failed\n" + "\n".join(failures))
    print(f"verified {len(manifest['frozen_files'])} frozen files")


if __name__ == "__main__":
    main()
