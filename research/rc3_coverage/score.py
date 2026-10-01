from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

AUTHORITY_STATES = {"DECLARED", "NOT_NEEDED"}


def load_jsonl(path: str) -> list[dict[str, Any]]:
    return [json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines() if line.strip()]


def normalized_children(values: list[str]) -> tuple[str, ...]:
    return tuple(sorted(" ".join(value.strip().split()) for value in values))


def is_correct(actual: dict[str, Any], gold: dict[str, Any]) -> bool:
    if actual["state"] != gold["expected_state"]:
        return False
    if gold["expected_state"] != "DECLARED":
        return True
    actual_children = normalized_children(actual["children"])
    allowed = {
        normalized_children(children)
        for children in gold.get("allowed_child_sets", [])
    }
    return actual_children in allowed


def load_validator(path: str):
    spec = importlib.util.spec_from_file_location("rc3_contract_a_validator", path)
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
    arm_names = ("baseline", "p4", "p5", "pooled")
    arm_metrics: dict[str, dict[str, Any]] = {}
    correct_by_arm: dict[str, set[str]] = {}
    safe_ids = {case_id for case_id, row in gold.items() if row["class"].startswith("SAFE_")}
    fail_closed_ids = {case_id for case_id, row in gold.items() if row["class"] == "FAIL_CLOSED"}

    for arm in arm_names:
        correct_ids: set[str] = set()
        unsafe_authority: list[str] = []
        wrong_authority: list[str] = []
        for case_id, expected in gold.items():
            actual = raw[case_id]["arms"][arm]
            if is_correct(actual, expected):
                correct_ids.add(case_id)
            if case_id in fail_closed_ids and actual["state"] in AUTHORITY_STATES:
                unsafe_authority.append(case_id)
            if case_id in safe_ids and actual["state"] in AUTHORITY_STATES and not is_correct(actual, expected):
                wrong_authority.append(case_id)
        correct_by_arm[arm] = correct_ids
        arm_metrics[arm] = {
            "safe_correct": len(correct_ids & safe_ids),
            "safe_total": len(safe_ids),
            "fail_closed_correct": len(correct_ids & fail_closed_ids),
            "fail_closed_total": len(fail_closed_ids),
            "unsafe_authority": sorted(unsafe_authority),
            "wrong_safe_authority": sorted(wrong_authority),
            "exact_correct": len(correct_ids),
            "total": len(gold),
        }

    contract_errors: list[str] = []
    pooled_emissions = 0
    for case_id in sorted(gold):
        actual = raw[case_id]["arms"]["pooled"]
        if actual["state"] not in AUTHORITY_STATES:
            continue
        pooled_emissions += 1
        try:
            validator.validate_candidate(actual["contract_a"])
        except Exception as exc:  # noqa: BLE001 - score must preserve validator failure text
            contract_errors.append(f"{case_id}:{type(exc).__name__}:{exc}")

    baseline_safe = correct_by_arm["baseline"] & safe_ids
    pooled_safe = correct_by_arm["pooled"] & safe_ids
    gain_ids = sorted(pooled_safe - baseline_safe)
    lost_baseline_ids = sorted(baseline_safe - pooled_safe)
    gain_families = sorted({gold[case_id]["family"] for case_id in gain_ids})
    preservation = 1.0 if not baseline_safe else len(baseline_safe & pooled_safe) / len(baseline_safe)

    weak_unsafe = sorted(
        case_id
        for case_id in fail_closed_ids
        if raw[case_id]["weak_controls"]["first_pooled_proposal"]["state"] == "DECLARED"
    )

    hard_failures: list[str] = []
    if arm_metrics["pooled"]["unsafe_authority"]:
        hard_failures.append("POOLED_UNSAFE_AUTHORITY")
    if arm_metrics["pooled"]["wrong_safe_authority"]:
        hard_failures.append("POOLED_WRONG_SAFE_AUTHORITY")
    if contract_errors:
        hard_failures.append("CONTRACT_A_VALIDATION_FAILURE")
    if preservation < 0.90:
        hard_failures.append("BASELINE_PRESERVATION_BELOW_90_PERCENT")

    coverage_pass = len(gain_ids) >= 6 and len(gain_families) >= 2
    control_pass = bool(weak_unsafe)
    if hard_failures:
        governance = "FALSIFIED"
        experiment = "FALSIFIED"
    elif not coverage_pass or not control_pass:
        governance = "INCONCLUSIVE"
        experiment = "INCONCLUSIVE_FOR_RC4"
    else:
        governance = "SUPPORTED_FOR_PROMOTION"
        experiment = "SUPPORTED_FOR_RC4_INDEPENDENT_REPRODUCTION"

    report = {
        "governance_disposition": governance,
        "experiment_classification": experiment,
        "arm_metrics": arm_metrics,
        "safe_gain_ids": gain_ids,
        "safe_gain_families": gain_families,
        "safe_gain_count": len(gain_ids),
        "lost_baseline_safe_ids": lost_baseline_ids,
        "baseline_preservation": preservation,
        "pooled_contract_a_emissions": pooled_emissions,
        "contract_a_errors": contract_errors,
        "weak_control_unsafe_declared": weak_unsafe,
        "coverage_gate_pass": coverage_pass,
        "weak_control_gate_pass": control_pass,
        "hard_failures": hard_failures,
    }
    Path(args.output).write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
