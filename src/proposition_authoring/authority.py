from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .ambiguity import analyze_root_scope
from .conservation import INSTRUMENT_ID, audit_candidate


@dataclass(frozen=True)
class ComposedAuthorityResult:
    disposition: str
    reason: str
    evaluator_disposition: str | None
    conservation: dict[str, object]
    root_scope_findings: tuple[dict[str, object], ...]

    def as_dict(self) -> dict[str, object]:
        return {
            "disposition": self.disposition,
            "reason": self.reason,
            "evaluator_disposition": self.evaluator_disposition,
            "conservation": self.conservation,
            "root_scope_findings": list(self.root_scope_findings),
        }


def evaluate_candidate(candidate: dict[str, Any], backend: Any) -> ComposedAuthorityResult:
    root_findings = tuple(analyze_root_scope(candidate["root_text"]))
    if root_findings:
        return ComposedAuthorityResult(
            disposition="BLOCK",
            reason="ROOT_SCOPE_AMBIGUITY",
            evaluator_disposition=None,
            conservation={
                "instrument": INSTRUMENT_ID,
                "disposition": "NOT_RUN",
                "findings": [],
                "families": [],
            },
            root_scope_findings=root_findings,
        )

    evaluator = backend.evaluate(candidate)
    evaluator_disposition = evaluator["disposition"]
    children = tuple(row["text"] for row in candidate["children"])
    conservation = audit_candidate(candidate["root_text"], children)

    if evaluator_disposition != "ACCEPTABLE_WITHIN_PROFILE":
        return ComposedAuthorityResult(
            "BLOCK",
            "FROZEN_EVALUATOR_REJECTED",
            evaluator_disposition,
            conservation.as_dict(),
            (),
        )
    if conservation.disposition != "PASS":
        return ComposedAuthorityResult(
            "BLOCK",
            f"CONSERVATION_{conservation.disposition}",
            evaluator_disposition,
            conservation.as_dict(),
            (),
        )
    return ComposedAuthorityResult(
        "ALLOW",
        "INDEPENDENT_INSTRUMENTS_PASS",
        evaluator_disposition,
        conservation.as_dict(),
        (),
    )
