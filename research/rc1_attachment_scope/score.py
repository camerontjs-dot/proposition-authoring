from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


def load_jsonl(path: str) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in Path(path).read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def load_validator(path: str):
    spec = importlib.util.spec_from_file_location("pa_rc1_contract_a_validator", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load Contract A validator")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def prediction_correct(pred: dict[str, Any], gold: dict[str, Any]) -> bool:
    if pred["state"] != gold["expected_state"]:
        return False
    if pred["state"] != "DECLARED":
        return True
    return pred.get("children", []) in gold.get("allowed_child_sets", [])


def unsafe_authoritative(pred: dict[str, Any], gold: dict[str, Any]) -> bool:
    if pred["state"] == "DECLARED":
        return gold["expected_state"] != "DECLARED" or not prediction_correct(pred, gold)
    if pred["state"] == "NOT_NEEDED":
        return gold["expected_state"] != "NOT_NEEDED"
    return False


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw", required=True)
    parser.add_argument("--gold", required=True)
    parser.add_argument("--validator", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    raw_rows = {row["case_id"]: row for row in load_jsonl(args.raw)}
    gold_rows = {row["case_id"]: row for row in load_jsonl(args.gold)}
    if set(raw_rows) != set(gold_rows):
        raise SystemExit("raw/gold case identity mismatch")

    validator = load_validator(args.validator)
    target = Counter()
    controls: dict[str, Counter] = {}
    details: list[dict[str, Any]] = []
    class_totals = Counter(row["class"] for row in gold_rows.values())

    for case_id in sorted(gold_rows):
        gold = gold_rows[case_id]
        row = raw_rows[case_id]
        output = row["target"]
        pred = {"state": output["state"], "children": output.get("children", [])}
        correct = prediction_correct(pred, gold)
        unsafe = unsafe_authoritative(pred, gold)

        target["cases"] += 1
        target[f"state::{pred['state']}"] += 1
        target[f"class::{gold['class']}"] += 1
        if correct:
            target["correct"] += 1
            target[f"correct::{gold['class']}"] += 1
        if unsafe:
            target["unsafe_authoritative"] += 1
        if gold["expected_state"] == "DECLARED" and pred["state"] in {"ABSTAINED", "FAILED"}:
            target["safe_false_negative"] += 1
        if pred["state"] == "FAILED":
            target["processing_failed"] += 1

        contract_a = output.get("contract_a")
        if contract_a is not None:
            validator.validate_candidate(contract_a)
            target["contract_a_valid"] += 1

        findings = output.get("receipt", {}).get("root_scope_findings", [])
        for finding in findings:
            target[f"finding::{finding.get('family', 'UNKNOWN')}"] += 1

        details.append(
            {
                "case_id": case_id,
                "class": gold["class"],
                "family": gold["family"],
                "expected_state": gold["expected_state"],
                "actual_state": pred["state"],
                "correct": correct,
                "unsafe_authoritative": unsafe,
                "reason": output.get("reason"),
                "finding_families": sorted(
                    finding.get("family", "UNKNOWN") for finding in findings
                ),
            }
        )

        for name, cpred in row["controls"].items():
            counts = controls.setdefault(name, Counter())
            counts["cases"] += 1
            if prediction_correct(cpred, gold):
                counts["correct"] += 1
                counts[f"correct::{gold['class']}"] += 1
            if unsafe_authoritative(cpred, gold):
                counts["unsafe_authoritative"] += 1

    hard_safety = (
        target["unsafe_authoritative"] == 0
        and target["processing_failed"] == 0
        and target["correct::AMBIGUOUS"] == class_totals["AMBIGUOUS"]
    )
    positive = (
        target["correct::CLEAR_REQUIRED"] == class_totals["CLEAR_REQUIRED"]
        and target["correct::NOT_NEEDED"] == class_totals["NOT_NEEDED"]
    )
    diagnostic_safe = all(
        not detail["unsafe_authoritative"]
        for detail in details
        if detail["class"] == "CLEAR_DIAGNOSTIC"
    )
    weak_discrimination = all(
        counts["unsafe_authoritative"] > 0
        or counts["correct::CLEAR_REQUIRED"] < target["correct::CLEAR_REQUIRED"]
        or counts["correct::NOT_NEEDED"] < target["correct::NOT_NEEDED"]
        for counts in controls.values()
    )

    if not hard_safety:
        disposition = "FALSIFIED"
    elif positive and diagnostic_safe and weak_discrimination:
        disposition = "SUPPORTED_FOR_SUCCESSOR_INTEGRATION"
    else:
        disposition = "INCONCLUSIVE"

    result = {
        "disposition": disposition,
        "hard_safety_gate": hard_safety,
        "positive_required_gate": positive,
        "diagnostic_safe_gate": diagnostic_safe,
        "weak_control_discrimination_gate": weak_discrimination,
        "class_totals": dict(sorted(class_totals.items())),
        "target": dict(sorted(target.items())),
        "controls": {name: dict(sorted(counts.items())) for name, counts in sorted(controls.items())},
        "details": details,
    }
    Path(args.output).write_text(
        json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(disposition)


if __name__ == "__main__":
    main()
