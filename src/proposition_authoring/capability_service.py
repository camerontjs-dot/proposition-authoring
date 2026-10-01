from __future__ import annotations

from dataclasses import dataclass

from .engine import AuthoringEngine
from .model import AuthoringRequest
from .preflight import PairedPreflightResult, run_paired_preflight
from .shadow_models import SourceMetadata, TaskMetadata


@dataclass(frozen=True)
class PairedGatesCapabilityService:
    implementation_identity: str = "runtime"

    def run(
        self,
        request: AuthoringRequest,
        *,
        claim_task: TaskMetadata | None = None,
        evidence_task: TaskMetadata | None = None,
        source_metadata: tuple[SourceMetadata, ...] = (),
        engine: AuthoringEngine | None = None,
    ) -> PairedPreflightResult:
        return run_paired_preflight(
            request,
            claim_task=claim_task,
            evidence_task=evidence_task,
            source_metadata=source_metadata,
            engine=engine,
            implementation_identity=self.implementation_identity,
        )
