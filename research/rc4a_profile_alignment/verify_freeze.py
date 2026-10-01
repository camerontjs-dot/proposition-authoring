from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]


def git_blob_sha(data: bytes) -> str:
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def verify_entries(entries: list[dict[str, Any]]) -> None:
    for item in entries:
        path = ROOT / item["path"]
        if not path.is_file():
            raise SystemExit(f"missing frozen file: {item['path']}")
        actual = git_blob_sha(path.read_bytes())
        if actual != item["git_blob"]:
            raise SystemExit(
                f"blob drift {item['path']}: {actual} != {item['git_blob']}"
            )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--manifest",
        default="research/rc4a_profile_alignment/FREEZE.json",
    )
    args = parser.parse_args()
    manifest = json.loads((ROOT / args.manifest).read_text(encoding="utf-8"))
    verify_entries(manifest["frozen_files"])
    verify_entries(manifest["unchanged_semantic_authority"])
    print("RC4a freeze verified")


if __name__ == "__main__":
    main()
