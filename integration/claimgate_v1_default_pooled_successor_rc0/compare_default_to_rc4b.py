from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

from proposition_authoring.coverage_backend import CoverageBackend
from proposition_authoring.engine import AuthoringEngine
from proposition_authoring.model import AuthoringRequest, SourceRepresentation

AUTHORITATIVE = {"DECLARED", "NOT_NEEDED"}


def canonical(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )


def normalized_children(values: list[str]) -> tuple[str, ...]:
    return tuple(sorted(" ".join(value.strip().split()) for value in values))


def load_jsonl(path: Path) -> dict[str, dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            row = json.loads(line)
            rows[row["case_id"]] = row
    return rows


def load_validator(path: Path):
    spec = importlib.util.spec_from_file_location("successor_contract_a_validator", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load validator {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def request_from(row: dict[str, Any]) -> AuthoringRequest:
    req = row["request"]
    return AuthoringRequest(
        handoff_id=req["handoff_id"],
        producer_id=req["producer_id"],
        producer_version=req["producer_version"],
        work_id=req["work_id"],
        root_id=req["root_id"],
        root_text=req["root_text"],
        sources=tuple(SourceRepresentation(**item) for item in req.get("sources", [])),
        context_source_id=req.get("context_source_id"),
    )


def project(result: Any) -> dict[str, Any]:
    children: list[str] = []
    if result.contract_a is not None and result.state == "DECLARED":
        children = [row["text"] for row in result.contract_a["decomposition"]["children"]]
    return {
        "state": result.state,
        "reason": result.reason,
        "children": children,
        "contract_a": result.contract_a,
        "receipt": result.receipt,
    }


def expected_match(actual: dict[str, Any], expected: dict[str, Any]) -> bool:
    if actual["state"] != expected["expected_state"]:
        return False
    if expected["expected_state"] == "DECLARED":
        allowed = {
            normalized_children(group)
            for group in expected.get("allowed_child_sets", [])
        }
        return normalized_children(actual["children"]) in allowed
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cases", type=Path, required=True)
    parser.add_argument("--gold", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    rows = load_jsonl(args.cases)
    gold = load_jsonl(args.gold)
    if set(rows) != set(gold):
        raise SystemExit("RC4b case/gold identity mismatch")

    default_engine = AuthoringEngine()
    explicit_engine = AuthoringEngine(CoverageBackend("pooled"))
    if not isinstance(default_engine.backend, CoverageBackend) or default_engine.backend.arm != "pooled":
        raise SystemExit("default runtime is not CoverageBackend('pooled')")

    validator = load_validator(Path("vendor/frozen/contract_a_rc2.py"))
    observations: list[dict[str, Any]] = []
    mismatches: list[dict[str, Any]] = []
    gold_misses: list[str] = []
    contract_errors: list[str] = []
    abstention_contract_leaks: list[str] = []
    unsafe_authority: list[str] = []

    for case_id in sorted(rows):
        request = request_from(rows[case_id])
        default = project(default_engine.author(request))
        explicit = project(explicit_engine.author(request))
        equal = canonical(default) == canonical(explicit)
        correct = expected_match(default, gold[case_id])

        if not equal:
            mismatches.append(
                {
                    "case_id": case_id,
                    "default": default,
                    "explicit_pooled": explicit,
                }
            )
        if not correct:
            gold_misses.append(case_id)
        if gold[case_id]["expected_state"] == "ABSTAINED" and default["state"] in AUTHORITATIVE:
            unsafe_authority.append(case_id)
        if default["state"] in AUTHORITATIVE:
            if default["contract_a"] is None:
                contract_errors.append(f"{case_id}:missing_contract")
            else:
                try:
                    validator.validate_candidate(default["contract_a"])
                except Exception as exc:  # noqa: BLE001 - preserve validator evidence
                    contract_errors.append(f"{case_id}:{type(exc).__name__}:{exc}")
        elif default["contract_a"] is not None:
            abstention_contract_leaks.append(case_id)

        observations.append(
            {
                "case_id": case_id,
                "default_equals_explicit_pooled": equal,
                "matches_rc4b_gold": correct,
                "state": default["state"],
                "reason": default["reason"],
                "children": default["children"],
            }
        )

    result = {
        "schema": "claimgate-default-pooled-equivalence-v2",
        "case_count": len(rows),
        "default_equals_explicit_pooled_all_cases": not mismatches,
        "matches_rc4b_gold_all_cases": not gold_misses,
        "unsafe_authoritative_outcomes": unsafe_authority,
        "contract_a_errors": contract_errors,
        "abstention_contract_leaks": abstention_contract_leaks,
        "observations": observations,
        "mismatches": mismatches,
        "gold_misses": gold_misses,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "case_count": len(rows),
                "all_equal": not mismatches,
                "all_gold_correct": not gold_misses,
                "contract_errors": len(contract_errors),
                "unsafe_authority": len(unsafe_authority),
            },
            sort_keys=True,
        )
    )
    if len(rows) != 44:
        raise SystemExit(f"expected exact 44-case RC4b surface, got {len(rows)}")
    if mismatches:
        raise SystemExit("default runtime diverges from explicit pooled RC4b subject")
    if gold_misses or unsafe_authority or contract_errors or abstention_contract_leaks:
        raise SystemExit("successor does not reproduce exact RC4b qualified envelope")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
