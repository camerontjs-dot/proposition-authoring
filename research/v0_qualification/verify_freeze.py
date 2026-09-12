from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def git_blob_sha(data: bytes) -> str:
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True)
    args = parser.parse_args()

    manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    for row in manifest["frozen_files"]:
        path = Path(row["path"])
        data = path.read_bytes()
        actual = git_blob_sha(data)
        if actual != row["git_blob"]:
            raise SystemExit(
                f"freeze mismatch {path}: actual={actual} expected={row['git_blob']}"
            )
        print(f"verified {path} {actual}")


if __name__ == "__main__":
    main()
