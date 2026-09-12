from __future__ import annotations

from collections import defaultdict
from typing import Any

from .backend import FrozenPredecessorBackend, SemanticBackend
from .canonical import canonical_json, sha256_text
from .contract_a import emit_declared, emit_failed, emit_not_decomposed
from .model import AuthoringRequest, AuthoringResult, CandidateEvaluation
from .profile import not_needed_profile_allows
from .receipt import build_receipt


class AuthoringEngine:
    def __init__(self, backend: SemanticBackend | None = None) -> None:
        self.backend = backend or FrozenPredecessorBackend()

    def author(self, request: AuthoringRequest) -> AuthoringResult:
        try:
            return self._author(request)
        except Exception as exc:
            contract_a = emit_failed(request)
            receipt = build_receipt(
                request,
                state="FAILED",
                reason=f"PROCESSING_FAILURE:{type(exc).__name__}",
                evaluations=[],
                surviving_clusters={},
                selected_cluster=None,
                selected_candidate_id=None,
                contract_a=contract_a,
            )
            return AuthoringResult(
                state="FAILED",
                reason=f"PROCESSING_FAILURE:{type(exc).__name__}",
                receipt=receipt,
                contract_a=contract_a,
            )

    def _author(self, request: AuthoringRequest) -> AuthoringResult:
        context_text = request.context_text()
        root = {
            "root_id": request.root_id,
            "root_text": request.root_text,
            "context_text": context_text,
            "family": "v0-runtime",
        }
        proposals = self.backend.proposals(root)
        evaluations: list[CandidateEvaluation] = []
        cluster_members: dict[str, list[dict[str, Any]]] = defaultdict(list)

        for proposer in sorted(proposals):
            for candidate in proposals[proposer]:
                result = self.backend.evaluate(candidate)
                cluster: str | None = None
                if result["disposition"] == "ACCEPTABLE_WITHIN_PROFILE":
                    cluster = self.backend.cluster_key(candidate)
                    cluster_members[cluster].append(candidate)
                evaluations.append(
                    CandidateEvaluation(
                        candidate_id=candidate["case_id"],
                        proposer=candidate["proposal_meta"]["proposer"],
                        variant=candidate["proposal_meta"]["variant"],
                        children=tuple(x["text"] for x in candidate["children"]),
                        authority_disposition=result["disposition"],
                        authority_sha256=result.get("canonical_sha256"),
                        semantic_cluster=cluster,
                    )
                )

        surviving = {
            cluster: sorted(c["case_id"] for c in candidates)
            for cluster, candidates in sorted(cluster_members.items())
        }

        if len(cluster_members) == 1:
            cluster = next(iter(cluster_members))
            representative = min(
                cluster_members[cluster],
                key=lambda c: canonical_json([x["text"] for x in c["children"]]),
            )
            child_texts = [x["text"] for x in representative["children"]]
            decomposition_id = f"decomp::{request.root_id}::{sha256_text(cluster)[7:19]}"
            contract_a = emit_declared(
                request,
                decomposition_id=decomposition_id,
                child_texts=child_texts,
            )
            receipt = build_receipt(
                request,
                state="DECLARED",
                reason="ONE_SURVIVING_SEMANTIC_CLUSTER",
                evaluations=evaluations,
                surviving_clusters=surviving,
                selected_cluster=cluster,
                selected_candidate_id=representative["case_id"],
                contract_a=contract_a,
            )
            return AuthoringResult(
                state="DECLARED",
                reason="ONE_SURVIVING_SEMANTIC_CLUSTER",
                receipt=receipt,
                contract_a=contract_a,
                evaluations=tuple(evaluations),
            )

        if len(cluster_members) > 1:
            reason = "MULTIPLE_SURVIVING_SEMANTIC_CLUSTERS"
            receipt = build_receipt(
                request,
                state="ABSTAINED",
                reason=reason,
                evaluations=evaluations,
                surviving_clusters=surviving,
                selected_cluster=None,
                selected_candidate_id=None,
                contract_a=None,
            )
            return AuthoringResult(
                state="ABSTAINED",
                reason=reason,
                receipt=receipt,
                evaluations=tuple(evaluations),
            )

        status, frame_count, parse_reason = self.backend.root_frame_count(
            request.root_text, context_text
        )
        if status == "ok" and frame_count == 1 and not_needed_profile_allows(request.root_text):
            contract_a = emit_not_decomposed(request)
            receipt = build_receipt(
                request,
                state="NOT_NEEDED",
                reason="BOUNDED_ROOT_IS_SINGLE_PROPOSITION",
                evaluations=evaluations,
                surviving_clusters=surviving,
                selected_cluster=None,
                selected_candidate_id=None,
                contract_a=contract_a,
            )
            return AuthoringResult(
                state="NOT_NEEDED",
                reason="BOUNDED_ROOT_IS_SINGLE_PROPOSITION",
                receipt=receipt,
                contract_a=contract_a,
                evaluations=tuple(evaluations),
            )

        if status == "ok" and frame_count == 1:
            reason = "NOT_NEEDED_BLOCKED_BY_COMPOSITION_HAZARD"
        else:
            reason = f"NO_UNIQUE_WARRANTED_DECLARATION:{status}:{parse_reason or 'none'}"
        receipt = build_receipt(
            request,
            state="ABSTAINED",
            reason=reason,
            evaluations=evaluations,
            surviving_clusters=surviving,
            selected_cluster=None,
            selected_candidate_id=None,
            contract_a=None,
        )
        return AuthoringResult(
            state="ABSTAINED",
            reason=reason,
            receipt=receipt,
            evaluations=tuple(evaluations),
        )
