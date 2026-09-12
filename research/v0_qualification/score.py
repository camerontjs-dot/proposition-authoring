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
    spec = importlib.util.spec_from_file_location("pa_decisive_contract_a_validator", path)
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
    target_counts = Counter()
    advanced_families: set[str] = set()
    target_details: list[dict[str, Any]] = []
    controls: dict[str, Counter] = {}

    for case_id in sorted(gold_rows):
        gold = gold_rows[case_id]
        row = raw_rows[case_id]
        target = row["target"]
        pred = {"state": target["state"], "children": target.get("children", [])}
        correct = prediction_correct(pred, gold)
        unsafe = unsafe_authoritative(pred, gold)

        if target.get("contract_a") is not None:
            validator.validate_candidate(target["contract_a"])
            target_counts["contract_a_valid"] += 1

        target_counts["cases"] += 1
        target_counts[f"state::{target['state']}"] += 1
        target_counts[f"class::{gold['class']}"] += 1
        if correct:
            target_counts["correct"] += 1
            target_counts[f"correct::{gold['class']}"] += 1
            if gold["class"] == "ADVANCED_DECLARED":
                advanced_families.add(gold["family"])
        if unsafe:
            target_counts["unsafe_authoritative"] += 1
        if gold["expected_state"] == "DECLARED" and target["state"] in {"ABSTAINED", "FAILED"}:
            target_counts["safe_false_negative"] += 1
        if target["state"] == "FAILED":
            target_counts["processing_failed"] += 1

        target_details.append(
            {
                "case_id": case_id,
                "class": gold["class"],
                "family": gold["family"],
                "expected_state": gold["expected_state"],
                "actual_state": target["state"],
                "correct": correct,
                "unsafe_authoritative": unsafe,
                "reason": target.get("reason"),
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

    fail_closed_correct = target_counts["correct::FAIL_CLOSED"]
    safe_authored = (
        target_counts["correct::NOT_NEEDED"]
        + target_counts["correct::CORE_DECLARED"]
        + target_counts["correct::ADVANCED_DECLARED"]
    )
    hard_safety = (
        target_counts["unsafe_authoritative"] == 0
        and fail_closed_correct == 8
    )
    coverage = (
        target_counts["correct::NOT_NEEDED"] == 6
        and target_counts["correct::CORE_DECLARED"] == 8
        and target_counts["correct::ADVANCED_DECLARED"] >= 5
        and safe_authored >= 19
        and len(advanced_families) >= 3
    )
    weak_discrimination = all(
        counts["unsafe_authoritative"] > 0
        or counts["correct::CORE_DECLARED"] < 8
        or counts["correct::NOT_NEEDED"] < 6
        for counts in controls.values()
    )

    if not hard_safety:
        disposition = "FALSIFIED"
    elif coverage and weak_discrimination:
        disposition = "SUPPORTED_FOR_INDEPENDENT_QUALIFICATION"
    else:
        disposition = "INCONCLUSIVE"

    result = {
        "disposition": disposition,
        "hard_safety_gate": hard_safety,
        "positive_coverage_gate": coverage,
        "weak_control_discrimination_gate": weak_discrimination,
        "target": dict(sorted(target_counts.items())),
        "safe_authored": safe_authored,
        "advanced_correct_family_count": len(advanced_families),
        "advanced_correct_families": sorted(advanced_families),
        "controls": {name: dict(sorted(counts.items())) for name, counts in sorted(controls.items())},
        "details": target_details,
    }
    Path(args.output).write_text(
        json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(disposition)


if __name__ == "__main__":
    main()
