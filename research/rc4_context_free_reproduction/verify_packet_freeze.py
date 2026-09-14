from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def git_blob(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True)
    args = parser.parse_args()
    manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    for row in manifest["frozen_files"]:
        path = Path(row["path"])
        actual = git_blob(path)
        if actual != row["git_blob"]:
            raise SystemExit(f"freeze mismatch {path}: {actual} != {row['git_blob']}")
    cases = Path("research/rc4_context_free_reproduction/fresh_cases.jsonl")
    if cases.exists() and manifest.get("fresh_cases_git_blob"):
        if git_blob(cases) != manifest["fresh_cases_git_blob"]:
            raise SystemExit("fresh cases blob mismatch")
    gold = Path("research/rc4_context_free_reproduction/GOLD/fresh_gold.jsonl")
    if gold.exists() and manifest.get("fresh_gold_git_blob"):
        if git_blob(gold) != manifest["fresh_gold_git_blob"]:
            raise SystemExit("fresh gold blob mismatch")
    print("RC4 freeze verified")


if __name__ == "__main__":
    main()
