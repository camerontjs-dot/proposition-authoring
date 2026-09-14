from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from types import ModuleType


def load_jsonl(path: Path) -> dict[str, dict]:
    rows: dict[str, dict] = {}
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                row = json.loads(line)
                rows[row["case_id"]] = row
    return rows


def load_validator(path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location("rc4_contract_a_validator", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load Contract A validator")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def child_set(row: dict) -> frozenset[str]:
    return frozenset(row.get("children", []))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw", required=True)
    parser.add_argument("--gold", required=True)
    parser.add_argument("--candidate-dir", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--provision-a", required=True)
    parser.add_argument("--provision-b", required=True)
    args = parser.parse_args()

    raw = load_jsonl(Path(args.raw))
    gold = load_jsonl(Path(args.gold))
    provision_a = json.loads(Path(args.provision_a).read_text(encoding="utf-8"))
    provision_b = json.loads(Path(args.provision_b).read_text(encoding="utf-8"))
    validator = load_validator(Path(args.candidate_dir) / "vendor" / "frozen" / "contract_a_rc2.py")

    families = {name: {"total": 0, "correct": 0} for name in ("P4_SAFE", "P5_SAFE", "BASELINE_SAFE", "SINGLE", "FAIL_CLOSED")}
    unsafe: list[str] = []
    incorrect: list[str] = []
    processing_failures: list[str] = []
    valid_contracts = 0
    emitted_contracts = 0
    safe_total = 0
    safe_correct = 0

    for case_id, expected in gold.items():
        actual = raw.get(case_id)
        family = expected["class"]
        families[family]["total"] += 1
        if family != "FAIL_CLOSED":
            safe_total += 1
        if actual is None:
            incorrect.append(case_id)
            continue
        state = actual["state"]
        if state == "FAILED":
            processing_failures.append(case_id)
        contract_a = actual.get("contract_a")
        if contract_a is not None:
            emitted_contracts += 1
            try:
                validator.validate_candidate(contract_a)
            except Exception:  # noqa: BLE001
                pass
            else:
                valid_contracts += 1

        expected_state = expected["expected_state"]
        correct = state == expected_state
        if expected_state == "DECLARED":
            allowed = [frozenset(children) for children in expected.get("allowed_child_sets", [])]
            correct = correct and child_set(actual) in allowed
            if state in {"DECLARED", "NOT_NEEDED"} and not correct:
                unsafe.append(case_id)
        elif expected_state == "NOT_NEEDED":
            if state == "DECLARED":
                unsafe.append(case_id)
        elif expected_state == "ABSTAINED":
            if state in {"DECLARED", "NOT_NEEDED"}:
                unsafe.append(case_id)

        if correct:
            families[family]["correct"] += 1
            if family != "FAIL_CLOSED":
                safe_correct += 1
        else:
            incorrect.append(case_id)

    def frac(name: str) -> float:
        total = families[name]["total"]
        return families[name]["correct"] / total if total else 0.0

    tree_match = provision_a["candidate_tree_sha256"] == provision_b["candidate_tree_sha256"]
    contract_fraction = valid_contracts / emitted_contracts if emitted_contracts else 1.0
    safe_fraction = safe_correct / safe_total if safe_total else 0.0

    if unsafe or frac("FAIL_CLOSED") < 1.0:
        governance = "FALSIFIED"
        classification = "FALSIFIED_REPRODUCTION_SAFETY_DIVERGENCE"
    elif processing_failures or not tree_match:
        governance = "INCONCLUSIVE"
        classification = "INCONCLUSIVE_REPRODUCTION_APPARATUS_DIVERGENCE"
    elif (
        safe_fraction >= 0.90
        and frac("P4_SAFE") >= 0.80
        and frac("P5_SAFE") >= 0.80
        and frac("BASELINE_SAFE") >= 0.90
        and frac("SINGLE") == 1.0
        and contract_fraction == 1.0
    ):
        governance = "SUPPORTED FOR PROMOTION"
        classification = "SUPPORTED_FOR_RC5_CONSUMER_CONFORMANCE"
    else:
        governance = "INCONCLUSIVE"
        classification = "INCONCLUSIVE_REPRODUCTION_COVERAGE_DIVERGENCE"

    result = {
        "schema": "rc4-context-free-score-1",
        "governance_disposition": governance,
        "classification": classification,
        "total_cases": len(gold),
        "exact_correct": len(gold) - len(set(incorrect)),
        "safe_total": safe_total,
        "safe_correct": safe_correct,
        "safe_correct_fraction": safe_fraction,
        "families": families,
        "unsafe_authoritative_outcomes": sorted(set(unsafe)),
        "processing_failures": sorted(set(processing_failures)),
        "incorrect_cases": sorted(set(incorrect)),
        "emitted_contracts": emitted_contracts,
        "valid_contracts": valid_contracts,
        "contract_a_validation_fraction": contract_fraction,
        "independent_provision_tree_match": tree_match,
        "candidate_tree_sha256": provision_a["candidate_tree_sha256"],
    }
    Path(args.output).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
