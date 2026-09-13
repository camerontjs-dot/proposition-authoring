from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


def rows(path: str) -> list[dict[str, Any]]:
    return [json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines() if line.strip()]


def load_validator(path: str):
    spec = importlib.util.spec_from_file_location("rc2_contract_a_validator", path)
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
    raw = {x["case_id"]: x for x in rows(args.raw)}
    gold = {x["case_id"]: x for x in rows(args.gold)}
    if set(raw) != set(gold):
        raise SystemExit("raw/gold identity mismatch")
    validator = load_validator(args.validator)
    target = Counter()
    controls: dict[str, Counter] = {}
    safe_families: set[str] = set()
    details = []

    for case_id in sorted(gold):
        g = gold[case_id]
        r = raw[case_id]
        actual = r["target"]["disposition"]
        correct = actual == g["expected"]
        unsafe_allow = actual == "ALLOW" and g["expected"] == "BLOCK"
        target["cases"] += 1
        target[f"class::{g['class']}"] += 1
        if correct:
            target["correct"] += 1
        if unsafe_allow:
            target["unsafe_allow"] += 1
        if g["expected"] == "ALLOW":
            target["safe_total"] += 1
            if actual == "ALLOW":
                target["safe_allow"] += 1
                safe_families.add(g["family"])
        contract_a = r["target"].get("contract_a")
        if contract_a is not None:
            validator.validate_candidate(contract_a)
            target["contract_a_valid"] += 1
        details.append({"case_id": case_id, "class": g["class"], "family": g["family"], "expected": g["expected"], "actual": actual, "correct": correct, "unsafe_allow": unsafe_allow, "reason": r["target"].get("reason")})

        for name, value in r["controls"].items():
            c = controls.setdefault(name, Counter())
            c["cases"] += 1
            if value == g["expected"]:
                c["correct"] += 1
            if value == "ALLOW" and g["expected"] == "BLOCK":
                c["unsafe_allow"] += 1
            if g["expected"] == "ALLOW" and value == "ALLOW":
                c["safe_allow"] += 1

    hard_safety = target["unsafe_allow"] == 0
    coverage = target["safe_total"] > 0 and target["safe_allow"] / target["safe_total"] >= 0.80 and len(safe_families) >= 4
    weak_discrimination = all(c["unsafe_allow"] > 0 or c["safe_allow"] + 2 <= target["safe_allow"] for c in controls.values())
    if not hard_safety:
        disposition = "FALSIFIED"
    elif coverage and weak_discrimination:
        disposition = "SUPPORTED_FOR_RC3_COVERAGE_TESTING"
    else:
        disposition = "INCONCLUSIVE"

    result = {
        "disposition": disposition,
        "hard_safety_gate": hard_safety,
        "coverage_gate": coverage,
        "weak_control_discrimination_gate": weak_discrimination,
        "target": dict(sorted(target.items())),
        "safe_family_count": len(safe_families),
        "safe_families": sorted(safe_families),
        "controls": {k: dict(sorted(v.items())) for k, v in sorted(controls.items())},
        "details": details,
    }
    Path(args.output).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(disposition)


if __name__ == "__main__":
    main()
