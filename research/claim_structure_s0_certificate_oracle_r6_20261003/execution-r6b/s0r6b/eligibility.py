"""Apply the frozen eligibility rule to saved review records.

A profile is eligible only when every known-good item is ACCEPT_COMPLETE and
no hard mutation is ACCEPT_COMPLETE. Unparsable output is not an accept.
"""

from __future__ import annotations


def item_kind(stem: str) -> str:
    if "--" in stem:
        return "mutation"
    return "known_good"


def score_profile(records: list[dict]) -> dict:
    failures = []
    for record in records:
        stem = record["item"]
        verdict = record["verdict"]
        kind = item_kind(stem)
        if kind == "known_good" and verdict != "ACCEPT_COMPLETE":
            failures.append(
                {"item": stem, "reason": "known_good_not_accepted", "verdict": verdict}
            )
        if kind == "mutation" and verdict == "ACCEPT_COMPLETE":
            failures.append(
                {"item": stem, "reason": "hard_mutation_accepted", "verdict": verdict}
            )
    return {"eligible": not failures, "failures": failures}
