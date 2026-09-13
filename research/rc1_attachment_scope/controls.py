from __future__ import annotations

import re
from collections import Counter
from typing import Any

import proposition_authoring.engine as engine_module
from proposition_authoring.backend import FrozenPredecessorBackend
from proposition_authoring.model import AuthoringRequest

_REPORTING = re.compile(
    r"\b(?:reported|stated|claimed|said|asserted|concluded|observed|confirmed|indicated|showed|found)\b",
    re.IGNORECASE,
)
_COORD = re.compile(r"\b(?:and|or)\b", re.IGNORECASE)
_COMMA_COORD = re.compile(r",\s+(?:and|or)\b", re.IGNORECASE)


def _children(contract_a: dict[str, Any] | None) -> list[str]:
    if contract_a is None:
        return []
    decomposition = contract_a.get("decomposition", {})
    if decomposition.get("state") != "declared":
        return []
    return [row["text"] for row in decomposition["children"]]


def _prediction(result) -> dict[str, Any]:
    return {"state": result.state, "children": _children(result.contract_a)}


def _root(request: AuthoringRequest) -> dict[str, Any]:
    return {
        "root_id": request.root_id,
        "root_text": request.root_text,
        "context_text": request.context_text(),
        "family": "rc1-control",
    }


def legacy_v0(request: AuthoringRequest, backend: FrozenPredecessorBackend) -> dict[str, Any]:
    original = engine_module.analyze_root_scope
    engine_module.analyze_root_scope = lambda _text: []
    try:
        return _prediction(engine_module.AuthoringEngine(backend).author(request))
    finally:
        engine_module.analyze_root_scope = original


def blanket_reporting_coordination(
    request: AuthoringRequest, backend: FrozenPredecessorBackend
) -> dict[str, Any]:
    if _REPORTING.search(request.root_text) and _COORD.search(request.root_text):
        return {"state": "ABSTAINED", "children": []}
    return legacy_v0(request, backend)


def punctuation_only(request: AuthoringRequest, backend: FrozenPredecessorBackend) -> dict[str, Any]:
    if _COMMA_COORD.search(request.root_text):
        return {"state": "ABSTAINED", "children": []}
    return legacy_v0(request, backend)


def first_proposal(request: AuthoringRequest, backend: FrozenPredecessorBackend) -> dict[str, Any]:
    proposals = backend.proposals(_root(request))
    ordered = [candidate for proposer in sorted(proposals) for candidate in proposals[proposer]]
    if not ordered:
        return {"state": "NOT_NEEDED", "children": []}
    candidate = ordered[0]
    return {"state": "DECLARED", "children": [row["text"] for row in candidate["children"]]}


def majority_proposer(request: AuthoringRequest, backend: FrozenPredecessorBackend) -> dict[str, Any]:
    proposals = backend.proposals(_root(request))
    surfaces = [
        tuple(row["text"] for row in candidate["children"])
        for proposer in sorted(proposals)
        for candidate in proposals[proposer]
    ]
    if not surfaces:
        return {"state": "NOT_NEEDED", "children": []}
    counts = Counter(surfaces)
    top = max(counts.values())
    winners = sorted(surface for surface, count in counts.items() if count == top)
    return {"state": "DECLARED", "children": list(winners[0])}


CONTROLS = {
    "C0_LEGACY_V0": legacy_v0,
    "C1_BLANKET_REPORTING_COORDINATION": blanket_reporting_coordination,
    "C2_PUNCTUATION_ONLY": punctuation_only,
    "C3_FIRST_PROPOSAL": first_proposal,
    "C4_MAJORITY_PROPOSER": majority_proposer,
}
