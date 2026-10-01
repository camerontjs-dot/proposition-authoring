from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

SEED = "gate-v1-naturalistic-pressure-rc0::89ca88c7::20261001"
STRATA = ("plain", "coordination", "attribution", "qualified")
PER_STRATUM = 3


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def score(claim_id: str) -> str:
    return sha256_bytes(SEED.encode("utf-8") + b"\0" + claim_id.encode("utf-8"))


def load_pool(path: Path) -> list[dict]:
    rows: list[dict] = []
    seen: set[str] = set()
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        row = json.loads(line)
        claim_id = row.get("claim_id")
        stratum = row.get("stratum")
        if not isinstance(claim_id, str) or not claim_id:
            raise SystemExit(f"line {number}: missing claim_id")
        if claim_id in seen:
            raise SystemExit(f"duplicate claim_id: {claim_id}")
        if stratum not in STRATA:
            raise SystemExit(f"line {number}: invalid stratum {stratum!r}")
        seen.add(claim_id)
        rows.append(row)
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("pool")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    pool_path = Path(args.pool)
    out_path = Path(args.out)
    rows = load_pool(pool_path)

    selected: list[dict] = []
    counts: dict[str, int] = {}
    for stratum in STRATA:
        eligible = [row for row in rows if row["stratum"] == stratum]
        counts[stratum] = len(eligible)
        if len(eligible) < PER_STRATUM:
            raise SystemExit(
                f"BLOCKED_INSUFFICIENT_NATURALISTIC_POOL: "
                f"{stratum} has {len(eligible)}, need {PER_STRATUM}"
            )
        eligible.sort(key=lambda row: (score(row["claim_id"]), row["claim_id"]))
        for row in eligible[:PER_STRATUM]:
            selected.append(
                {
                    "claim_id": row["claim_id"],
                    "stratum": stratum,
                    "selection_score_sha256": score(row["claim_id"]),
                }
            )

    output = {
        "schema": "gate-v1-naturalistic-pressure-selection-v1",
        "seed": SEED,
        "algorithm": "sha256(seed || NUL || claim_id), ascending within stratum",
        "per_stratum": PER_STRATUM,
        "pool_sha256": sha256_bytes(pool_path.read_bytes()),
        "pool_count": len(rows),
        "pool_counts_by_stratum": counts,
        "selected": selected,
    }
    out_path.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(output, sort_keys=True))


if __name__ == "__main__":
    main()
