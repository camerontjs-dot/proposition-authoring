from __future__ import annotations

from pathlib import Path
from typing import Any

from .authority import evaluate_candidate
from .backend import FrozenPredecessorBackend
from .canonical import canonical_json, sha256_text
from .coverage_proposers import proposer_p4, proposer_p5


class CoverageBackend:
    """Research-only proposal-arm wrapper over the exact frozen RC2 authority boundary."""

    VALID_ARMS = {"baseline", "p4", "p5", "pooled"}

    def __init__(self, arm: str = "pooled", vendor_dir: str | Path = "vendor/frozen") -> None:
        if arm not in self.VALID_ARMS:
            raise ValueError(f"unknown RC3 arm: {arm}")
        self.arm = arm
        self.base = FrozenPredecessorBackend(vendor_dir)

    def proposals(self, root: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
        out: dict[str, list[dict[str, Any]]] = {}
        if self.arm in {"baseline", "pooled"}:
            out.update(self.base.proposals(root))
        if self.arm in {"p4", "pooled"}:
            out["P4"] = proposer_p4(root)
        if self.arm in {"p5", "pooled"}:
            out["P5"] = proposer_p5(root)
        return out

    def root_frame_count(self, root_text: str, context_text: str) -> tuple[str, int, str]:
        return self.base.root_frame_count(root_text, context_text)

    def evaluate(self, candidate: dict[str, Any]) -> dict[str, Any]:
        composed = evaluate_candidate(candidate, self.base)
        payload = composed.as_dict()
        return {
            "disposition": (
                "ACCEPTABLE_WITHIN_PROFILE"
                if composed.disposition == "ALLOW"
                else "REJECT_UNSAFE"
            ),
            "canonical_sha256": sha256_text(canonical_json(payload)),
            "rc2_composed_authority": payload,
        }

    def cluster_key(self, candidate: dict[str, Any]) -> str:
        return self.base.cluster_key(candidate)
