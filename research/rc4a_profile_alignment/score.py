from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

AUTHORITY_STATES = {"DECLARED", "NOT_NEEDED"}


def load_jsonl(path: str) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in Path(path).read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def normalized_children(values: list[str]) -> tuple[str, ...]:
    return tuple(sorted(" ".join(value.strip().split()) for value in values))


def declared_correct(actual: dict[str, Any], gold: dict[str, Any]) -> bool:
    if actual["state"] != "DECLARED":
        return False
    allowed = {
        normalized_children(children)
        for children in gold.get("allowed_child_sets", [])
    }
    return normalized_children(actual["children"]) in allowed


def load_validator(path: str):
    spec = importlib.util.spec_from_file_location("rc4a_contract_a_validator", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load Contract A validator")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw", required=True)
    parser.add_argument("--gold", required=True)
    parser.add_argument("--validator", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    raw = {row["case_id"]: row for row in load_jsonl(args.raw)}
    gold = {row["case_id"]: row for row in load_jsonl(args.gold)}
    if set(raw) != set(gold):
        raise SystemExit("raw/gold case-id mismatch")

    validator = load_validator(args.validator)
    by_family: dict[str, list[str]] = {}
    for case_id, row in gold.items():
        by_family.setdefault(row["family"], []).append(case_id)

    intersection = set(by_family.get("INTERSECTION_SAFE", []))
    proposer_only = set(by_family.get("PROPOSER_ONLY_BLOCKED", []))
    authority_only = set(by_family.get("AUTHORITY_ONLY_BLOCKED", []))
    fail_closed = set(by_family.get("FAIL_CLOSED", []))

    aligned_leaks = sorted(
        case_id
        for case_id in proposer_only | authority_only | fail_closed
        if raw[case_id]["aligned_p5_proposals"]
    )
    weak_misalignment_hits = sorted(
        case_id
        for case_id in proposer_only
        if raw[case_id]["weak_prealignment_p5_proposals"]
    )
    authority_only_probe_accepts = sorted(
        case_id
        for case_id in authority_only
        if raw[case_id]["authority_probe"]["disposition"]
        == "ACCEPTABLE_WITHIN_PROFILE"
    )

    intersection_correct = sorted(
        case_id
        for case_id in intersection
        if raw[case_id]["aligned_p5_proposals"]
        and declared_correct(raw[case_id]["p5_result"], gold[case_id])
    )
    wrong_intersection_authority = sorted(
        case_id
        for case_id in intersection
        if raw[case_id]["p5_result"]["state"] in AUTHORITY_STATES
        and not declared_correct(raw[case_id]["p5_result"], gold[case_id])
    )
    proposer_only_abstains = sorted(
        case_id
        for case_id in proposer_only
        if raw[case_id]["p5_result"]["state"] == "ABSTAINED"
    )
    authority_only_abstains = sorted(
        case_id
        for case_id in authority_only
        if raw[case_id]["p5_result"]["state"] == "ABSTAINED"
    )
    unsafe_pooled = sorted(
        case_id
        for case_id in fail_closed
        if raw[case_id]["pooled_result"]["state"] in AUTHORITY_STATES
    )
    fail_closed_correct = sorted(
        case_id
        for case_id in fail_closed
        if raw[case_id]["pooled_result"]["state"] == "ABSTAINED"
    )

    processing_failures = sorted(
        f"{case_id}:{lane}"
        for case_id, row in raw.items()
        for lane in ("p5_result", "pooled_result")
        if row[lane]["state"] == "FAILED"
    )

    contract_errors: list[str] = []
    contract_emissions = 0
    for case_id, row in raw.items():
        for lane in ("p5_result", "pooled_result"):
            actual = row[lane]
            if actual["state"] not in AUTHORITY_STATES:
                continue
            contract_emissions += 1
            try:
                validator.validate_candidate(actual["contract_a"])
            except Exception as exc:  # noqa: BLE001 - preserve exact validator failure
                contract_errors.append(
                    f"{case_id}:{lane}:{type(exc).__name__}:{exc}"
                )

    intersection_fraction = (
        len(intersection_correct) / len(intersection) if intersection else 0.0
    )
    proposer_only_fraction = (
        len(proposer_only_abstains) / len(proposer_only) if proposer_only else 0.0
    )
    weak_control_fraction = (
        len(weak_misalignment_hits) / len(proposer_only) if proposer_only else 0.0
    )
    authority_only_fraction = (
        len(authority_only_abstains) / len(authority_only) if authority_only else 0.0
    )
    authority_probe_fraction = (
        len(authority_only_probe_accepts) / len(authority_only) if authority_only else 0.0
    )
    fail_closed_fraction = (
        len(fail_closed_correct) / len(fail_closed) if fail_closed else 0.0
    )

    hard_failures: list[str] = []
    if unsafe_pooled:
        hard_failures.append("UNSAFE_POOLED_AUTHORITY")
    if wrong_intersection_authority:
        hard_failures.append("WRONG_IN_PROFILE_AUTHORITY")
    if aligned_leaks:
        hard_failures.append("ALIGNED_P5_PROPOSAL_OUTSIDE_DECLARED_PROFILE")
    if contract_errors:
        hard_failures.append("CONTRACT_A_VALIDATION_FAILURE")

    positive_gates = {
        "intersection_safe_at_least_90_percent": intersection_fraction >= 0.90,
        "proposer_only_abstention_100_percent": proposer_only_fraction == 1.0,
        "weak_misalignment_control_100_percent": weak_control_fraction == 1.0,
        "authority_only_abstention_100_percent": authority_only_fraction == 1.0,
        "authority_only_probe_100_percent": authority_probe_fraction == 1.0,
        "fail_closed_100_percent": fail_closed_fraction == 1.0,
        "no_processing_failures": not processing_failures,
    }

    if hard_failures:
        governance = "FALSIFIED"
        experiment = "FALSIFIED"
    elif not all(positive_gates.values()):
        governance = "INCONCLUSIVE"
        experiment = "INCONCLUSIVE_PROFILE_ALIGNMENT"
    else:
        governance = "SUPPORTED_FOR_PROMOTION"
        experiment = "SUPPORTED_FOR_SUCCESSOR_RC4_REPRODUCTION"

    report = {
        "schema": "rc4a-profile-alignment-score-1",
        "governance_disposition": governance,
        "experiment_classification": experiment,
        "total_cases": len(gold),
        "family_counts": {family: len(ids) for family, ids in sorted(by_family.items())},
        "intersection_correct": len(intersection_correct),
        "intersection_total": len(intersection),
        "intersection_fraction": intersection_fraction,
        "proposer_only_abstains": len(proposer_only_abstains),
        "proposer_only_total": len(proposer_only),
        "weak_misalignment_hits": len(weak_misalignment_hits),
        "authority_only_abstains": len(authority_only_abstains),
        "authority_only_total": len(authority_only),
        "authority_only_probe_accepts": len(authority_only_probe_accepts),
        "fail_closed_correct": len(fail_closed_correct),
        "fail_closed_total": len(fail_closed),
        "unsafe_pooled_authority": unsafe_pooled,
        "wrong_intersection_authority": wrong_intersection_authority,
        "aligned_profile_leaks": aligned_leaks,
        "processing_failures": processing_failures,
        "contract_a_emissions": contract_emissions,
        "contract_a_errors": contract_errors,
        "positive_gates": positive_gates,
        "hard_failures": hard_failures,
    }
    Path(args.output).write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
