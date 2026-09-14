from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path


def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tree_digest(root: Path) -> str:
    rows: list[str] = []
    for path in sorted(
        p for p in root.rglob("*") if p.is_file() and "__pycache__" not in p.parts
    ):
        rows.append(f"{path.relative_to(root).as_posix()}\t{sha256_file(path)}")
    return hashlib.sha256(("\n".join(rows) + "\n").encode("utf-8")).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--packet", required=True)
    parser.add_argument("--repository-root", required=True)
    parser.add_argument("--dest", required=True)
    parser.add_argument("--receipt", required=True)
    args = parser.parse_args()

    packet_path = Path(args.packet)
    packet = json.loads(packet_path.read_text(encoding="utf-8"))
    repository_root = Path(args.repository_root).resolve()
    dest = Path(args.dest)
    if dest.exists() and any(dest.iterdir()):
        raise SystemExit("APPARATUS_INVALID: destination must be absent or empty")
    dest.mkdir(parents=True, exist_ok=True)

    commit = packet["candidate_commit"]
    observed: list[dict[str, str]] = []
    for spec in packet["runtime_files"]:
        path = spec["path"]
        shown = subprocess.run(
            ["git", "show", f"{commit}:{path}"],
            cwd=repository_root,
            check=False,
            capture_output=True,
        )
        if shown.returncode != 0:
            raise SystemExit(
                f"APPARATUS_INVALID: cannot reconstruct {path} at {commit}"
            )
        data = shown.stdout
        actual_blob = git_blob_sha(data)
        if actual_blob != spec["git_blob"]:
            raise SystemExit(
                f"APPARATUS_INVALID: {path} blob mismatch {actual_blob} != {spec['git_blob']}"
            )
        target = dest / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        observed.append(
            {
                "path": path,
                "git_blob": actual_blob,
                "sha256": hashlib.sha256(data).hexdigest(),
            }
        )

    bootstrap = subprocess.run(
        [sys.executable, "scripts/fetch_frozen_predecessors.py"],
        cwd=dest,
        check=False,
        capture_output=True,
        text=True,
    )
    if bootstrap.returncode != 0:
        raise SystemExit(
            "APPARATUS_INVALID: pinned predecessor bootstrap failed\n" + bootstrap.stderr
        )

    bootstrap_observed: list[dict[str, str]] = []
    for spec in packet["bootstrap_artifacts"]:
        path = dest / spec["path"]
        data = path.read_bytes()
        actual_blob = git_blob_sha(data)
        if actual_blob != spec["git_blob"]:
            raise SystemExit(
                f"APPARATUS_INVALID: {spec['path']} blob mismatch "
                f"{actual_blob} != {spec['git_blob']}"
            )
        bootstrap_observed.append(
            {
                "path": spec["path"],
                "role": spec["role"],
                "git_blob": actual_blob,
                "sha256": hashlib.sha256(data).hexdigest(),
            }
        )

    env = os.environ.copy()
    env["PYTHONPATH"] = str((dest / "src").resolve())
    probe = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "import json;"
                "from proposition_authoring.coverage_proposers import "
                "P5_AUTHORITY_COMPATIBLE_EMBEDDED_PREDICATES as P;"
                "print(json.dumps(list(P), separators=(',',':')))"
            ),
        ],
        cwd=dest,
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )
    if probe.returncode != 0:
        raise SystemExit(
            "APPARATUS_INVALID: aligned P5 competence probe failed\n" + probe.stderr
        )
    actual_competence = json.loads(probe.stdout.strip())
    expected_competence = packet["p5_competence"]["embedded_predicates"]
    if actual_competence != expected_competence:
        raise SystemExit(
            "APPARATUS_INVALID: aligned P5 competence declaration mismatch "
            f"{actual_competence!r} != {expected_competence!r}"
        )

    receipt = {
        "schema": "rc4b-provision-receipt-1",
        "packet_sha256": hashlib.sha256(packet_path.read_bytes()).hexdigest(),
        "repository": packet["repository"],
        "candidate_commit": commit,
        "candidate_target_freeze": packet["candidate_target_freeze"],
        "runtime_files": observed,
        "bootstrap_artifacts": bootstrap_observed,
        "p5_competence": actual_competence,
        "bootstrap_stdout": [
            line for line in bootstrap.stdout.splitlines() if line.strip()
        ],
        "candidate_tree_sha256": tree_digest(dest),
    }
    receipt_path = Path(args.receipt)
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.write_text(
        json.dumps(receipt, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
