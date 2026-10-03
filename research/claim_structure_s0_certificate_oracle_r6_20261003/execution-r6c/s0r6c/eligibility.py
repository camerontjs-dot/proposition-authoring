"""R6c eligibility.

Every calibration item must copy the certificate fields exactly. A known-good
item must then be ACCEPT_COMPLETE. A hard mutation must then be a parsed
verdict other than ACCEPT_COMPLETE. A mismatch makes the profile ineligible
even when the verdict would otherwise pass.
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
        if not record["inspection_match"]:
            failures.append(
                {"item": stem, "reason": "inspection_mismatch", "verdict": verdict}
            )
        if kind == "known_good" and verdict != "ACCEPT_COMPLETE":
            failures.append(
                {"item": stem, "reason": "known_good_not_accepted", "verdict": verdict}
            )
        if kind == "mutation" and verdict == "ACCEPT_COMPLETE":
            failures.append(
                {"item": stem, "reason": "hard_mutation_accepted", "verdict": verdict}
            )
    return {"eligible": not failures, "failures": failures}
