from __future__ import annotations

import hashlib
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "vendor" / "frozen"

FILES = {
    "proposers.py": {
        "url": "https://raw.githubusercontent.com/camerontjs-dot/evidence-bundler/b25fa4743e16f40186d29bec3757c378733b7791/research/proposition_compiler_multiproposer_rc0/proposers.py",
        "git_blob": "b2684f1752a1eb841dd6ee85b1e81ae523b03810",
    },
    "resolver_predecessor.py": {
        "url": "https://raw.githubusercontent.com/camerontjs-dot/evidence-bundler/b25fa4743e16f40186d29bec3757c378733b7791/research/proposition_compiler_multiproposer_rc0/resolver.py",
        "git_blob": "ca2fbf63855f21551c2e1ebb46019768753746e4",
    },
    "predecessor_fresh_roots.jsonl": {
        "url": "https://raw.githubusercontent.com/camerontjs-dot/evidence-bundler/b25fa4743e16f40186d29bec3757c378733b7791/research/proposition_compiler_multiproposer_rc0/fresh_roots.jsonl",
        "git_blob": "e51ec542898a0f40489e0140bbd0455e1429e0bb",
    },
    "predecessor_fresh_gold.jsonl": {
        "url": "https://raw.githubusercontent.com/camerontjs-dot/evidence-bundler/b25fa4743e16f40186d29bec3757c378733b7791/research/proposition_compiler_multiproposer_rc0/GOLD/fresh_gold.jsonl",
        "git_blob": "da169fcc9b0efc096cbb3c68a744da9d7beaa03d",
    },
    "evaluator.py": {
        "url": "https://raw.githubusercontent.com/camerontjs-dot/evidence-bundler/26539c53781148543e980fe1f07b25f1ad9c2005/research/proposition_compiler_evaluator_rc1/evaluator.py",
        "git_blob": "e675b55559af17d50b65cd6af01ac23b0881bb43",
        "sha256": "1091169da8e960cdf93242ee4c629c7a1a814009c8f80554f4a190f5b3fe989d",
    },
    "contract_a_rc2.py": {
        "url": "https://raw.githubusercontent.com/camerontjs-dot/apparatus-contracts/contract-a-v2.0.0/validators/contract_a_rc2.py",
        "git_blob": "42e5f5b3bf38d677445e9d01ea130ba604e53409",
    },
    "contract_a_schema.json": {
        "url": "https://raw.githubusercontent.com/camerontjs-dot/apparatus-contracts/contract-a-v2.0.0/schema/contract-a/2.0.0/schema.json",
        "git_blob": "ff5cddfeacf4511136a3dd3b47db1a794b631cd9",
    },
    "contract_a_wire_spec.md": {
        "url": "https://raw.githubusercontent.com/camerontjs-dot/apparatus-contracts/contract-a-v2.0.0/schema/contract-a/2.0.0/wire-spec.md",
        "git_blob": "2e7c37fca9aa6bdd1090fb527a663bdbe606ebcb",
    },
}


def git_blob_sha(data: bytes) -> str:
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def main() -> None:
    DEST.mkdir(parents=True, exist_ok=True)
    for name, spec in FILES.items():
        with urllib.request.urlopen(spec["url"], timeout=60) as response:
            data = response.read()
        actual_blob = git_blob_sha(data)
        if actual_blob != spec["git_blob"]:
            raise SystemExit(
                f"{name}: git blob mismatch {actual_blob} != {spec['git_blob']}"
            )
        if "sha256" in spec:
            actual_sha256 = hashlib.sha256(data).hexdigest()
            if actual_sha256 != spec["sha256"]:
                raise SystemExit(
                    f"{name}: sha256 mismatch {actual_sha256} != {spec['sha256']}"
                )
        (DEST / name).write_bytes(data)
        print(f"verified {name} {actual_blob}")


if __name__ == "__main__":
    main()
