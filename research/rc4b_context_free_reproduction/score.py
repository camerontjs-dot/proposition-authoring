from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any


AUTHORITATIVE = {"DECLARED", "NOT_NEEDED"}


def load_jsonl(path: Path) -> dict[str, dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            row = json.loads(line)
            rows[row["case_id"]] = row
    return rows


def normalized_children(values: list[str]) -> tuple[str, ...]:
    return tuple(sorted(" ".join(value.strip().split()) for value in values))


def exact_case_correct(actual: dict[str, Any], expected: dict[str, Any]) -> bool:
    pooled = actual["pooled_result"]
    if pooled["state"] != expected["expected_state"]:
        return False
    if expected["expected_state"] == "DECLARED":
        allowed = {
            normalized_children(children)
            for children in expected.get("allowed_child_sets", [])
        }
        return normalized_children(pooled.get("children", [])) in allowed
    return True


def load_validator(path: Path):
    spec = importlib.util.spec_from_file_location("rc4b_contract_a_validator", path)
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
    parser.add_argument("--candidate-dir", required=True)
    parser.add_argument("--provision-a", required=True)
    parser.add_argument("--provision-b", required=True)
    parser.add_argument("--replay-receipt", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    raw = load_jsonl(Path(args.raw))
    gold = load_jsonl(Path(args.gold))
    if set(raw) != set(gold):
        raise SystemExit("raw/gold case-id mismatch")

    provision_a = json.loads(Path(args.provision_a).read_text(encoding="utf-8"))
    provision_b = json.loads(Path(args.provision_b).read_text(encoding="utf-8"))
    replay = json.loads(Path(args.replay_receipt).read_text(encoding="utf-8"))
    validator = load_validator(
        Path(args.candidate_dir) / "vendor" / "frozen" / "contract_a_rc2.py"
    )

    required_families = {
        "P5_SAFE": 12,
        "P4_SAFE": 6,
        "BASELINE_SAFE": 6,
        "SINGLE": 4,
        "P5_OUT_OF_PROFILE": 4,
        "FAIL_CLOSED": 8,
    }
    family_ids: dict[str, list[str]] = {name: [] for name in required_families}
    for case_id, expected in gold.items():
        family = expected["class"]
        if family not in family_ids:
            raise SystemExit(f"unknown family {family}")
        family_ids[family].append(case_id)

    correct: dict[str, list[str]] = {name: [] for name in required_families}
    incorrect: list[str] = []
    unsafe_authority: list[str] = []
    wrong_safe_authority: list[str] = []
    processing_failures: list[str] = []
    contract_errors: list[str] = []
    abstention_contract_leaks: list[str] = []
    p5_profile_leaks: list[str] = []
    p5_missing_in_profile: list[str] = []
    p4_missing_in_profile: list[str] = []
    weak_control_hits: list[str] = []
    contract_emissions = 0

    for case_id, expected in gold.items():
        actual = raw[case_id]
        pooled = actual["pooled_result"]
        family = expected["class"]
        is_correct = exact_case_correct(actual, expected)

        if family == "P5_SAFE" and not actual["aligned_p5_proposals"]:
            p5_missing_in_profile.append(case_id)
            is_correct = False
        if family == "P4_SAFE" and not actual["aligned_p4_proposals"]:
            p4_missing_in_profile.append(case_id)
            is_correct = False
        if family == "P5_OUT_OF_PROFILE":
            if actual["aligned_p5_proposals"]:
                p5_profile_leaks.append(case_id)
                is_correct = False
            if actual["weak_prealignment_p5_proposals"]:
                weak_control_hits.append(case_id)

        if pooled["state"] == "FAILED":
            processing_failures.append(case_id)

        if pooled["state"] in AUTHORITATIVE:
            contract_emissions += 1
            if pooled.get("contract_a") is None:
                contract_errors.append(f"{case_id}:missing_contract")
            else:
                try:
                    validator.validate_candidate(pooled["contract_a"])
                except Exception as exc:  # noqa: BLE001
                    contract_errors.append(
                        f"{case_id}:{type(exc).__name__}:{exc}"
                    )
        elif pooled.get("contract_a") is not None:
            abstention_contract_leaks.append(case_id)

        if expected["expected_state"] == "ABSTAINED" and pooled["state"] in AUTHORITATIVE:
            unsafe_authority.append(case_id)
        elif (
            expected["expected_state"] in AUTHORITATIVE
            and pooled["state"] in AUTHORITATIVE
            and not is_correct
        ):
            wrong_safe_authority.append(case_id)

        if is_correct:
            correct[family].append(case_id)
        else:
            incorrect.append(case_id)

    safe_families = [
        "P5_SAFE",
        "P4_SAFE",
        "BASELINE_SAFE",
        "SINGLE",
        "P5_OUT_OF_PROFILE",
    ]
    safe_total = sum(len(family_ids[name]) for name in safe_families)
    safe_correct = sum(len(correct[name]) for name in safe_families)

    def fraction(name: str) -> float:
        total = len(family_ids[name])
        return len(correct[name]) / total if total else 0.0

    family_minimums_met = all(
        len(family_ids[name]) >= minimum
        for name, minimum in required_families.items()
    )
    reconstruction_match = (
        provision_a["candidate_tree_sha256"]
        == provision_b["candidate_tree_sha256"]
        and replay["candidate_tree_match"]
        and replay["raw_byte_identical"]
        and replay["provision_receipts_byte_identical"]
    )
    exact_identity_preserved = (
        provision_a["runtime_files"] == provision_b["runtime_files"]
        and provision_a["bootstrap_artifacts"] == provision_b["bootstrap_artifacts"]
        and provision_a["p5_competence"] == provision_b["p5_competence"]
    )

    hard_failures: list[str] = []
    if unsafe_authority:
        hard_failures.append("UNSAFE_AUTHORITATIVE_OUTCOME")
    if wrong_safe_authority:
        hard_failures.append("WRONG_AUTHORITATIVE_DECOMPOSITION")
    if p5_profile_leaks:
        hard_failures.append("P5_COMPETENCE_ENVELOPE_VIOLATION")
    if contract_errors or abstention_contract_leaks:
        hard_failures.append("CONTRACT_A_BOUNDARY_FAILURE")
    if not reconstruction_match or not exact_identity_preserved:
        hard_failures.append("MATERIAL_RECONSTRUCTION_MISMATCH")

    positive_gates = {
        "family_minimums_met": family_minimums_met,
        "overall_safe_at_least_90_percent": (
            safe_correct / safe_total if safe_total else 0.0
        ) >= 0.90,
        "p5_safe_at_least_90_percent": fraction("P5_SAFE") >= 0.90,
        "p4_safe_at_least_90_percent": fraction("P4_SAFE") >= 0.90,
        "baseline_safe_at_least_90_percent": fraction("BASELINE_SAFE") >= 0.90,
        "single_100_percent": fraction("SINGLE") == 1.0,
        "out_of_profile_100_percent": fraction("P5_OUT_OF_PROFILE") == 1.0,
        "fail_closed_100_percent": fraction("FAIL_CLOSED") == 1.0,
        "no_p5_profile_leaks": not p5_profile_leaks,
        "weak_control_discriminates": bool(weak_control_hits),
        "no_processing_failures": not processing_failures,
        "all_contracts_valid": not contract_errors,
        "abstentions_emit_no_contract": not abstention_contract_leaks,
        "reconstruction_match": reconstruction_match,
        "exact_identity_preserved": exact_identity_preserved,
    }

    if hard_failures:
        governance = "FALSIFIED"
        classification = "FALSIFIED"
    elif not all(positive_gates.values()):
        governance = "INCONCLUSIVE"
        classification = "INCONCLUSIVE_RC4B_REPRODUCTION"
    else:
        governance = "SUPPORTED FOR PROMOTION"
        classification = "SUPPORTED_FOR_RC5_CONSUMER_CONFORMANCE"

    report = {
        "schema": "rc4b-context-free-score-1",
        "governance_disposition": governance,
        "experiment_classification": classification,
        "total_cases": len(gold),
        "family_counts": {
            name: len(ids) for name, ids in sorted(family_ids.items())
        },
        "family_correct": {
            name: len(ids) for name, ids in sorted(correct.items())
        },
        "safe_total": safe_total,
        "safe_correct": safe_correct,
        "safe_correct_fraction": (
            safe_correct / safe_total if safe_total else 0.0
        ),
        "incorrect_cases": sorted(set(incorrect)),
        "unsafe_authoritative_outcomes": sorted(set(unsafe_authority)),
        "wrong_safe_authority": sorted(set(wrong_safe_authority)),
        "p5_profile_leaks": sorted(set(p5_profile_leaks)),
        "p5_missing_in_profile": sorted(set(p5_missing_in_profile)),
        "p4_missing_in_profile": sorted(set(p4_missing_in_profile)),
        "weak_control_hits": sorted(set(weak_control_hits)),
        "processing_failures": sorted(set(processing_failures)),
        "contract_a_emissions": contract_emissions,
        "contract_a_errors": contract_errors,
        "abstention_contract_leaks": sorted(set(abstention_contract_leaks)),
        "candidate_tree_sha256": provision_a["candidate_tree_sha256"],
        "raw_sha256": replay["raw_a_sha256"],
        "provision_receipt_sha256": replay["provision_a_sha256"],
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
