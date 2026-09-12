from __future__ import annotations

from collections import Counter
from typing import Any

from proposition_authoring.backend import FrozenPredecessorBackend
from proposition_authoring.engine import AuthoringEngine
from proposition_authoring.model import AuthoringRequest


def _children_from_contract(contract_a: dict[str, Any] | None) -> list[str]:
    if contract_a is None:
        return []
    decomposition = contract_a.get("decomposition", {})
    if decomposition.get("state") != "declared":
        return []
    return [row["text"] for row in decomposition["children"]]


def _root(request: AuthoringRequest) -> dict[str, Any]:
    return {
        "root_id": request.root_id,
        "root_text": request.root_text,
        "context_text": request.context_text(),
        "family": "v0-runtime",
    }


def c0_force_not_decomposed(request: AuthoringRequest, backend: FrozenPredecessorBackend) -> dict[str, Any]:
    del request, backend
    return {"state": "NOT_NEEDED", "children": []}


def c1_first_proposal(request: AuthoringRequest, backend: FrozenPredecessorBackend) -> dict[str, Any]:
    proposals = backend.proposals(_root(request))
    ordered = [candidate for proposer in sorted(proposals) for candidate in proposals[proposer]]
    if not ordered:
        return {"state": "NOT_NEEDED", "children": []}
    candidate = ordered[0]
    return {
        "state": "DECLARED",
        "children": [row["text"] for row in candidate["children"]],
    }


def c2_majority_proposer(request: AuthoringRequest, backend: FrozenPredecessorBackend) -> dict[str, Any]:
    proposals = backend.proposals(_root(request))
    surfaces = [
        tuple(row["text"] for row in candidate["children"])
        for proposer in sorted(proposals)
        for candidate in proposals[proposer]
    ]
    if not surfaces:
        return {"state": "NOT_NEEDED", "children": []}
    counts = Counter(surfaces)
    max_count = max(counts.values())
    winners = sorted(surface for surface, count in counts.items() if count == max_count)
    return {"state": "DECLARED", "children": list(winners[0])}


def c3_silent_abstention_coercion(
    request: AuthoringRequest,
    backend: FrozenPredecessorBackend,
) -> dict[str, Any]:
    result = AuthoringEngine(backend).author(request)
    if result.state == "ABSTAINED":
        return {"state": "NOT_NEEDED", "children": []}
    return {"state": result.state, "children": _children_from_contract(result.contract_a)}


CONTROLS = {
    "C0_FORCE_NOT_DECOMPOSED": c0_force_not_decomposed,
    "C1_FIRST_PROPOSAL": c1_first_proposal,
    "C2_MAJORITY_PROPOSER": c2_majority_proposer,
    "C3_SILENT_ABSTENTION_COERCION": c3_silent_abstention_coercion,
}
