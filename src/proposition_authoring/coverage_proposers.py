from __future__ import annotations

import re
from typing import Any

PROFILE_ID = "pc-evaluator-rc1-binding-v1"

P4_VERBS = (
    "approved",
    "archived",
    "authenticated",
    "cached",
    "delivered",
    "encrypted",
    "examined",
    "filed",
    "inspected",
    "labeled",
    "logged",
    "measured",
    "recorded",
    "reviewed",
    "shipped",
    "signed",
    "stored",
    "transferred",
)
REPORTING = ("reported", "stated", "confirmed", "noted", "claimed")
EMBEDDED_PREDICATES = (
    "active",
    "approved",
    "compliant",
    "failed",
    "inactive",
    "passed",
    "ready",
    "rejected",
    "restarted",
    "stopped",
)

_P4_ALT = "|".join(P4_VERBS)
_P4_RE = re.compile(
    rf"^(?P<subject>.+?)\s+(?P<v1>{_P4_ALT})\s+(?P<o1>.+?)\s+and\s+"
    rf"(?P<v2>{_P4_ALT})\s+(?P<o2>.+)$",
    re.IGNORECASE,
)
_REPORT_ALT = "|".join(REPORTING)
_P5_RE = re.compile(
    rf"^(?P<matrix>.+?\s+(?:{_REPORT_ALT}))\s+that\s+(?P<body>.+)$",
    re.IGNORECASE,
)


def _norm(text: str) -> str:
    return " ".join(text.strip().rstrip(".").split())


def _sentence(text: str) -> str:
    return _norm(text) + "."


def _candidate(
    root: dict[str, Any], proposer: str, variant: str, children: list[str]
) -> dict[str, Any]:
    return {
        "case_id": f"{root['root_id']}::{proposer}::{variant}",
        "root_id": root["root_id"],
        "root_text": root["root_text"],
        "context_text": root.get("context_text", ""),
        "profile_id": PROFILE_ID,
        "candidate_state": "DECLARED",
        "operator": "all_of",
        "children": [
            {
                "child_id": f"{root['root_id']}::{proposer}::{variant}::c{index}",
                "text": _sentence(text),
            }
            for index, text in enumerate(children, start=1)
        ],
        "proposal_meta": {"proposer": proposer, "variant": variant},
    }


def _has_scope_hazard(text: str) -> bool:
    low = f" {_norm(text).lower()} "
    if "," in text:
        return True
    if any(token in low for token in (" or ", " and/or ", " both ", " did not ", " not ")):
        return True
    if any(f" {modal} " in low for modal in ("may", "might", "must", "should", "can", "could", "will", "would")):
        return True
    if any(f" {verb} " in low for verb in REPORTING):
        return True
    return " that " in low


def proposer_p4(root: dict[str, Any]) -> list[dict[str, Any]]:
    """Bounded fallback for plain affirmative shared-subject action conjunctions."""
    text = _norm(root["root_text"])
    if _has_scope_hazard(text):
        return []
    match = _P4_RE.fullmatch(text)
    if not match:
        return []
    subject = _norm(match.group("subject"))
    if not 1 <= len(subject.split()) <= 5:
        return []
    left = f"{subject} {match.group('v1')} {match.group('o1')}"
    right = f"{subject} {match.group('v2')} {match.group('o2')}"
    return [_candidate(root, "P4", "shared-subject-fallback", [left, right])]


def _embedded_clause_supported(text: str) -> bool:
    low = _norm(text).lower()
    if any(token in f" {low} " for token in (" or ", " and/or ", " did not ", " not ", " both ")):
        return False
    if any(f" {modal} " in f" {low} " for modal in ("may", "might", "must", "should", "can", "could", "will", "would")):
        return False
    tokens = low.split()
    return len(tokens) >= 2 and any(token in EMBEDDED_PREDICATES for token in tokens)


def proposer_p5(root: dict[str, Any]) -> list[dict[str, Any]]:
    """Expand an explicit `reported that A and B` scope onto both children."""
    text = _norm(root["root_text"])
    if "," in text or " or " in f" {text.lower()} " or " both " in f" {text.lower()} ":
        return []
    match = _P5_RE.fullmatch(text)
    if not match:
        return []
    body = _norm(match.group("body"))
    if body.lower().count(" and ") != 1:
        return []
    left, right = (part.strip() for part in re.split(r"\s+and\s+", body, maxsplit=1, flags=re.IGNORECASE))
    if right.lower().startswith("that "):
        right = right[5:].strip()
    if not (_embedded_clause_supported(left) and _embedded_clause_supported(right)):
        return []
    matrix = _norm(match.group("matrix"))
    return [
        _candidate(
            root,
            "P5",
            "explicit-shared-attribution",
            [f"{matrix} that {left}", f"{matrix} that {right}"],
        )
    ]


NEW_PROPOSERS = {"P4": proposer_p4, "P5": proposer_p5}
