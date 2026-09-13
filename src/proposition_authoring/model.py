from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

AuthoringState = Literal["NOT_NEEDED", "DECLARED", "ABSTAINED", "FAILED"]


@dataclass(frozen=True)
class SourceRepresentation:
    source_id: str
    media_type: str
    content: str


@dataclass(frozen=True)
class AuthoringRequest:
    handoff_id: str
    producer_id: str
    producer_version: str
    work_id: str
    root_id: str
    root_text: str
    sources: tuple[SourceRepresentation, ...] = ()
    context_source_id: str | None = None

    def context_text(self) -> str:
        if self.context_source_id is None:
            return ""
        matches = [s.content for s in self.sources if s.source_id == self.context_source_id]
        if len(matches) != 1:
            raise ValueError("context_source_id must identify exactly one supplied source")
        return matches[0]


@dataclass(frozen=True)
class CandidateEvaluation:
    candidate_id: str
    proposer: str
    variant: str
    children: tuple[str, ...]
    authority_disposition: str
    authority_sha256: str | None
    semantic_cluster: str | None = None


@dataclass(frozen=True)
class AuthoringResult:
    state: AuthoringState
    reason: str
    receipt: dict[str, Any]
    contract_a: dict[str, Any] | None = None
    evaluations: tuple[CandidateEvaluation, ...] = field(default_factory=tuple)
