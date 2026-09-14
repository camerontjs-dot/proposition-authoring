from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import urllib.parse
import urllib.request
from pathlib import Path


def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tree_digest(root: Path) -> str:
    rows: list[str] = []
    for path in sorted(p for p in root.rglob("*") if p.is_file() and "__pycache__" not in p.parts):
        rows.append(f"{path.relative_to(root).as_posix()}\t{sha256_file(path)}")
    return hashlib.sha256(("\n".join(rows) + "\n").encode("utf-8")).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--packet", required=True)
    parser.add_argument("--dest", required=True)
    parser.add_argument("--receipt", required=True)
    args = parser.parse_args()

    packet_path = Path(args.packet)
    packet = json.loads(packet_path.read_text(encoding="utf-8"))
    dest = Path(args.dest)
    if dest.exists() and any(dest.iterdir()):
        raise SystemExit("APPARATUS_INVALID: destination must be absent or empty")
    dest.mkdir(parents=True, exist_ok=True)

    repo = packet["repository"]
    commit = packet["candidate_commit"]
    observed: list[dict[str, str]] = []
    for spec in packet["runtime_files"]:
        path = spec["path"]
        quoted = "/".join(urllib.parse.quote(part) for part in path.split("/"))
        url = f"https://raw.githubusercontent.com/{repo}/{commit}/{quoted}"
        with urllib.request.urlopen(url, timeout=60) as response:
            data = response.read()
        actual_blob = git_blob_sha(data)
        if actual_blob != spec["git_blob"]:
            raise SystemExit(
                f"APPARATUS_INVALID: {path} blob mismatch {actual_blob} != {spec['git_blob']}"
            )
        target = dest / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        observed.append({"path": path, "git_blob": actual_blob, "sha256": hashlib.sha256(data).hexdigest()})

    bootstrap = subprocess.run(
        [sys.executable, "scripts/fetch_frozen_predecessors.py"],
        cwd=dest,
        check=False,
        capture_output=True,
        text=True,
    )
    if bootstrap.returncode != 0:
        raise SystemExit("APPARATUS_INVALID: pinned predecessor bootstrap failed\n" + bootstrap.stderr)

    receipt = {
        "schema": "rc4-provision-receipt-1",
        "packet_sha256": hashlib.sha256(packet_path.read_bytes()).hexdigest(),
        "repository": repo,
        "candidate_commit": commit,
        "runtime_files": observed,
        "bootstrap_stdout": [line for line in bootstrap.stdout.splitlines() if line.strip()],
        "candidate_tree_sha256": tree_digest(dest),
    }
    receipt_path = Path(args.receipt)
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.write_text(json.dumps(receipt, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
