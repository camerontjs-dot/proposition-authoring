from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


BASE = Path("research/rc4b_context_free_reproduction")
CASES = BASE / "fresh_cases.jsonl"
GOLD = BASE / "GOLD" / "fresh_gold.jsonl"


def git_blob(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--enforce-fresh-absence", action="store_true")
    args = parser.parse_args()

    manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    for row in manifest["frozen_files"]:
        path = Path(row["path"])
        actual = git_blob(path)
        if actual != row["git_blob"]:
            raise SystemExit(
                f"freeze mismatch {path}: {actual} != {row['git_blob']}"
            )

    if args.enforce_fresh_absence:
        if CASES.exists() or GOLD.exists():
            raise SystemExit("target-freeze violation: RC4b fresh surface already exists")
        if not manifest.get("no_fresh_surface_at_target_freeze"):
            raise SystemExit("target-freeze manifest lacks no-fresh-surface statement")

    if manifest.get("fresh_cases_git_blob"):
        if not CASES.exists() or git_blob(CASES) != manifest["fresh_cases_git_blob"]:
            raise SystemExit("fresh cases blob mismatch")
    if manifest.get("fresh_gold_git_blob"):
        if not GOLD.exists() or git_blob(GOLD) != manifest["fresh_gold_git_blob"]:
            raise SystemExit("fresh gold blob mismatch")

    print("RC4b freeze verified")


if __name__ == "__main__":
    main()
