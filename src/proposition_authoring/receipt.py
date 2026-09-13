from __future__ import annotations

from typing import Any

from .canonical import bound_object_hash, sha256_text
from .model import AuthoringRequest, CandidateEvaluation

RECEIPT_SCHEMA = "proposition-authoring-receipt-v0"


def build_receipt(
    request: AuthoringRequest,
    *,
    state: str,
    reason: str,
    evaluations: list[CandidateEvaluation],
    surviving_clusters: dict[str, list[str]],
    selected_cluster: str | None,
    selected_candidate_id: str | None,
    contract_a: dict[str, Any] | None,
) -> dict[str, Any]:
    value: dict[str, Any] = {
        "schema": RECEIPT_SCHEMA,
        "apparatus": "proposition-authoring-v0-convergence",
        "qualification_state": "UNQUALIFIED_CONVERGENCE_CANDIDATE",
        "input": {
            "handoff_id": request.handoff_id,
            "producer_id": request.producer_id,
            "producer_version": request.producer_version,
            "work_id": request.work_id,
            "root_id": request.root_id,
            "root_text_sha256": sha256_text(request.root_text),
            "context_source_id": request.context_source_id,
            "source_ids": [s.source_id for s in request.sources],
            "source_content_sha256": {
                s.source_id: sha256_text(s.content) for s in request.sources
            },
        },
        "state": state,
        "reason": reason,
        "candidate_ledger": [
            {
                "candidate_id": row.candidate_id,
                "proposer": row.proposer,
                "variant": row.variant,
                "children": list(row.children),
                "authority_disposition": row.authority_disposition,
                "authority_sha256": row.authority_sha256,
                "semantic_cluster": row.semantic_cluster,
            }
            for row in evaluations
        ],
        "surviving_clusters": surviving_clusters,
        "selected_cluster": selected_cluster,
        "selected_candidate_id": selected_candidate_id,
        "contract_a_handoff_sha256": (
            contract_a.get("handoff_sha256") if contract_a is not None else None
        ),
        "nonclaims": [
            "not production-authorized",
            "not universal semantic parsing",
            "not decomposition truth proof",
            "not retrieval/CAL/Decision-derived authority",
        ],
    }
    value["receipt_sha256"] = bound_object_hash(value, "receipt_sha256")
    return value
