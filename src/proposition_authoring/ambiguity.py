from __future__ import annotations

import re
from typing import Any

_REPORTING_PREDICATE = re.compile(
    r"\b(reported|stated|claimed|said|asserted|concluded|observed|confirmed|indicated|showed|found)\b",
    re.IGNORECASE,
)
_COORD = re.compile(r"\b(and|or)\b", re.IGNORECASE)
_FINITEISH = re.compile(
    r"\b(?:is|are|was|were|be|been|has|have|had|do|does|did|can|could|may|might|must|shall|should|will|would|"
    r"pass(?:ed|es)?|fail(?:ed|s)?|stop(?:ped|s)?|start(?:ed|s)?|restart(?:ed|s)?|approve(?:d|s)?|"
    r"reject(?:ed|s)?|meet(?:s)?|exceed(?:ed|s)?|remain(?:ed|s)?|increase(?:d|s)?|decrease(?:d|s)?|"
    r"contain(?:ed|s)?|support(?:ed|s)?|require(?:d|s)?|allow(?:ed|s)?|occur(?:red|s)?|"
    r"complete(?:d|s)?|close(?:d|s)?|open(?:ed|s)?|ship(?:ped|s)?|arrive(?:d|s)?)\b",
    re.IGNORECASE,
)
_TRAILING_ADJUNCT = re.compile(
    r"\s+(during|after|before|in|at|under|within|on)\s+([^,;.!?]+?)\s*$",
    re.IGNORECASE,
)
_SENTENTIAL_NEGATION = re.compile(
    r"^(?:it\s+(?:is|was)\s+not\s+(?:true|established|confirmed|shown)\s+that|"
    r"it\s+(?:has|had)\s+not\s+been\s+(?:established|confirmed|shown)\s+that)\s+(.+)$",
    re.IGNORECASE,
)


def _surface(text: str) -> str:
    value = " ".join(text.strip().split())
    value = re.sub(r"[.!?]+$", "", value).strip()
    # A comma before a coordinator is not treated as a semantic disambiguator.
    value = re.sub(r",\s+(and|or)\b", r" \1", value, flags=re.IGNORECASE)
    return value


def _split_coord(text: str) -> tuple[str, str, str] | None:
    match = _COORD.search(text)
    if match is None:
        return None
    left = text[: match.start()].strip(" ,")
    right = text[match.end() :].strip(" ,")
    if not left or not right:
        return None
    return left, match.group(1).lower(), right


def _looks_clause(text: str) -> bool:
    words = re.findall(r"[A-Za-z][A-Za-z'-]*", text)
    return len(words) >= 2 and _FINITEISH.search(text) is not None


def _finding(family: str, trigger: str, a: str, b: str) -> dict[str, Any]:
    return {
        "family": family,
        "trigger": trigger,
        "material": True,
        "alternatives": sorted([a, b]),
    }


def _matrix_scope_findings(text: str) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    matrix = _REPORTING_PREDICATE.search(text)
    if matrix is None:
        return findings

    tail = text[matrix.end() :].strip()
    split = _split_coord(tail)
    if split is None:
        return findings
    left, coordinator, right = split

    # Explicit bounded disambiguators. `that` introduces one coordinated
    # complement in this profile; repeated matrix predicates make the second
    # conjunct independently scoped; `both` explicitly distributes matrix scope.
    if re.match(r"^that\b", tail, flags=re.IGNORECASE):
        return findings
    if re.search(r"\bboth\b", tail[: tail.lower().find(coordinator)], flags=re.IGNORECASE):
        return findings
    if _REPORTING_PREDICATE.search(right):
        return findings
    if re.match(r"^that\b", right, flags=re.IGNORECASE):
        return findings

    if _looks_clause(left) and _looks_clause(right):
        predicate = matrix.group(1).lower()
        findings.append(
            _finding(
                "MATRIX_ATTRIBUTION_SCOPE",
                f"{predicate}+{coordinator}",
                "matrix predicate scopes over both coordinated clauses",
                "matrix predicate scopes over the first clause only; second clause is independently asserted",
            )
        )
    return findings


def _trailing_adjunct_findings(text: str) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    adjunct = _TRAILING_ADJUNCT.search(text)
    if adjunct is None:
        return findings

    before = text[: adjunct.start()].strip()
    split = _split_coord(before)
    if split is None:
        return findings
    left, coordinator, right = split
    if not (_looks_clause(left) and _looks_clause(right)):
        return findings

    phrase = f"{adjunct.group(1).lower()} {adjunct.group(2).strip().lower()}"
    # Repetition on the first conjunct establishes a local/distributed reading
    # for this bounded profile rather than leaving a shared-vs-local choice open.
    if phrase in left.lower():
        return findings

    findings.append(
        _finding(
            "TRAILING_ADJUNCT_SCOPE",
            f"{coordinator}+{adjunct.group(1).lower()}",
            "trailing adjunct modifies only the second conjunct",
            "trailing adjunct modifies the coordinated proposition",
        )
    )
    return findings


def _sentential_negation_findings(text: str) -> list[dict[str, Any]]:
    match = _SENTENTIAL_NEGATION.match(text)
    if match is None:
        return []
    tail = match.group(1).strip()
    split = _split_coord(tail)
    if split is None:
        return []
    left, coordinator, right = split
    if not (_looks_clause(left) and _looks_clause(right)):
        return []
    return [
        _finding(
            "SENTENTIAL_NEGATION_SCOPE",
            f"sentential-negation+{coordinator}",
            "sentential negation scopes over the coordinated proposition",
            "negation is distributed or attached to a narrower constituent",
        )
    ]


def analyze_root_scope(root_text: str) -> list[dict[str, Any]]:
    """Return deterministic, bounded material root-scope findings.

    Findings are veto evidence only. An empty result does not prove that the root
    is unambiguous outside the bounded RC1 profile.
    """

    text = _surface(root_text)
    findings = [
        *_matrix_scope_findings(text),
        *_trailing_adjunct_findings(text),
        *_sentential_negation_findings(text),
    ]
    unique = {
        (row["family"], row["trigger"], tuple(row["alternatives"])): row for row in findings
    }
    return [unique[key] for key in sorted(unique)]
