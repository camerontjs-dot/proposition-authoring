from __future__ import annotations

from typing import Any

from .canonical import bound_object_hash
from .engine import AuthoringEngine
from .gate_v1 import EvidenceTaskV1
from .gate_v1_rc3 import (
    PairedGateV1RC3Result,
    SourceMetadataV1RC3,
    standardize_gates_v1_rc3,
)
from .model import AuthoringRequest, AuthoringResult

CONTRACT_A_2_0_SOURCE_MEDIA_TYPES = frozenset(
    {
        "text/plain; charset=utf-8",
        "text/markdown; charset=utf-8",
    }
)
CONTRACT_A_SOURCE_REPRESENTATION_UNSUPPORTED = (
    "CONTRACT_A_SOURCE_REPRESENTATION_UNSUPPORTED"
)


class _FrozenAuthoringEngine(AuthoringEngine):
    def __init__(self, result: AuthoringResult) -> None:
        self._result = result

    def author(self, request: AuthoringRequest) -> AuthoringResult:
        return self._result


def _contract_a_media_types_supported(contract_a: dict[str, Any]) -> bool:
    return all(
        source.get("media_type") in CONTRACT_A_2_0_SOURCE_MEDIA_TYPES
        for source in contract_a.get("sources", [])
    )


def _fail_closed_authoring(authoring: AuthoringResult) -> AuthoringResult:
    receipt = dict(authoring.receipt)
    receipt["state"] = "FAILED"
    receipt["reason"] = CONTRACT_A_SOURCE_REPRESENTATION_UNSUPPORTED
    receipt["contract_a_handoff_sha256"] = None
    receipt["receipt_sha256"] = bound_object_hash(receipt, "receipt_sha256")
    return AuthoringResult(
        state="FAILED",
        reason=CONTRACT_A_SOURCE_REPRESENTATION_UNSUPPORTED,
        receipt=receipt,
        contract_a=None,
        evaluations=authoring.evaluations,
    )


def standardize_gate_production_slice_v1(
    request: AuthoringRequest,
    *,
    evidence_task: EvidenceTaskV1 | None = None,
    source_metadata: tuple[SourceMetadataV1RC3, ...] = (),
    engine: AuthoringEngine | None = None,
    implementation_identity: str = "runtime",
) -> PairedGateV1RC3Result:
    """Run the minimal paired-Gate V1 slice against released Contract A 2.0.

    Gate V1 remains free to describe any supplied representation in EvidenceGate.
    Contract A is emitted only when every source representation is already
    representable by the exact released Contract A 2.0 media vocabulary. No
    source bytes or media labels are transformed to manufacture conformance.
    """

    result = standardize_gates_v1_rc3(
        request,
        evidence_task=evidence_task,
        source_metadata=source_metadata,
        engine=engine,
        implementation_identity=implementation_identity,
    )

    contract_a = result.authoring.contract_a
    if contract_a is None or _contract_a_media_types_supported(contract_a):
        return result

    failed_authoring = _fail_closed_authoring(result.authoring)
    return standardize_gates_v1_rc3(
        request,
        evidence_task=evidence_task,
        source_metadata=source_metadata,
        engine=_FrozenAuthoringEngine(failed_authoring),
        implementation_identity=implementation_identity,
    )
