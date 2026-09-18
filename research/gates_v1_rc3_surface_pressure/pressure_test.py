from __future__ import annotations

import copy
import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from proposition_authoring.canonical import bound_object_hash
from proposition_authoring.engine import AuthoringEngine
from proposition_authoring.gate_v1 import EvidenceTaskV1, GateV1Error
from proposition_authoring.gate_v1_rc3 import (
    SourceMetadataV1RC3,
    build_evidence_gate_output_v1_rc3,
    build_provenance_inputs_v1_rc3,
    classify_claim_v1_rc3,
    standardize_gates_v1_rc3,
    validate_claim_gate_output_v1_rc3,
    validate_evidence_gate_output_v1_rc3,
    verify_standardized_gate_bundle_v1_rc3,
)
from proposition_authoring.model import AuthoringRequest, SourceRepresentation

SUBJECT = os.environ.get("GATE_SUBJECT", "runtime")
SUPPORTED = "SUPPORTED_SURFACE"
FALSIFIED = "FALSIFIED_SURFACE"


@dataclass
class Case:
    case_id: str
    axis: str
    disposition: str
    expected: Any
    observed: Any
    detail: str


CASES: list[Case] = []


def record(case_id: str, axis: str, ok: bool, expected: Any, observed: Any, detail: str) -> None:
    CASES.append(
        Case(
            case_id,
            axis,
            SUPPORTED if ok else FALSIFIED,
            expected,
            observed,
            detail,
        )
    )


def request(
    *,
    root_id: str = "claim-a",
    text: str = "Ozempic DIN 02562618 is approved in Canada.",
    sources: tuple[SourceRepresentation, ...] = (),
) -> AuthoringRequest:
    return AuthoringRequest(
        handoff_id=f"handoff-{root_id}",
        producer_id="surface-pressure",
        producer_version="1",
        work_id="surface-pressure-work",
        root_id=root_id,
        root_text=text,
        sources=sources,
    )


def evidence(media_type: str = "text/html") -> tuple[SourceRepresentation, ...]:
    return (
        SourceRepresentation(
            "hc-product",
            media_type,
            "Current status: Approved. Product name: OZEMPIC. DIN: 02562618.",
        ),
        SourceRepresentation(
            "hc-context",
            "text/html",
            "Health Canada Drug Product Database online query.",
        ),
    )


def metadata() -> tuple[SourceMetadataV1RC3, ...]:
    return (
        SourceMetadataV1RC3(
            "hc-product",
            origin_type="official_database",
            locator_kind="web_uri",
            locator_value="https://health-products.canada.ca/dpd-bdpp/info?code=106547&lang=eng",
            issuer="Health Canada",
            source_role="official_regulatory_product_record",
            source_authority_basis_kind="official_issuer",
            source_authority_basis_detail="Official Health Canada Drug Product Database record",
            document_type="database_record",
            evidence_form="registry_entry",
            temporal_coverage="status date 2025-11-04",
            jurisdictional_coverage="Canada",
            version="retrieved 2026-09-17",
            currency_state="current_as_retrieved",
        ),
        SourceMetadataV1RC3(
            "hc-context",
            origin_type="official_database",
            locator_kind="web_uri",
            locator_value="https://health-products.canada.ca/dpd-bdpp/",
            issuer="Health Canada",
            source_role="official_database_context",
            source_authority_basis_kind="official_issuer",
            source_authority_basis_detail="Official Health Canada database interface",
            document_type="web_page",
            evidence_form="document_text",
            jurisdictional_coverage="Canada",
            version="retrieved 2026-09-17",
            currency_state="current_as_retrieved",
        ),
    )


def task() -> EvidenceTaskV1:
    return EvidenceTaskV1(
        verification_world="closed",
        corpus_scope="two frozen Health Canada pages",
        completeness_state="partial",
        known_gaps_state="declared_some",
        known_gaps=("product monograph omitted",),
    )


def categories(case_id: str, text: str, expected: tuple[str, ...]) -> None:
    observed = classify_claim_v1_rc3(text)
    record(case_id, "claim_category", observed == expected, list(expected), list(observed), text)


def rejects(fn) -> bool:
    try:
        fn()
    except GateV1Error:
        return True
    return False


def run_claim_category_pressure() -> None:
    categories("CAT-01", "Ozempic DIN 02562618 is approved in Canada.", ("status",))
    categories("CAT-02", "Ozempic DIN: 02562618 is approved in Canada.", ("status",))
    categories("CAT-03", "Ozempic NDC 0002-8215-01 is approved.", ("status",))
    categories("CAT-04", "Lot number 123456 was rejected.", ("status",))
    categories("CAT-05", "Serial No. 77881 was approved.", ("status",))
    categories("CAT-06", "Document No. 77881 was approved.", ("status",))
    categories("CAT-07", "DIN No. 02562618 is approved.", ("status",))
    categories("CAT-08", "DIN number 02562618 is approved.", ("status",))
    categories("CAT-09", "ISO 13485 compliant.", ("compliance", "status"))
    categories("CAT-10", "The device was approved under 21 CFR Part 11.", ("status",))
    categories("CAT-11", "The licence was approved on 2025-11-04.", ("status", "temporal"))
    categories("CAT-12", "Version 2 was approved.", ("status",))
    categories("CAT-13", "There were 25 rejected records.", ("quantitative", "status"))
    categories("CAT-14", "DIN 02562618 had a 4.2 percent failure rate.", ("quantitative",))
    categories("CAT-15", "The system was inactive in 2025.", ("status", "temporal"))


def run_identity_pressure():
    base = standardize_gates_v1_rc3(
        request(sources=evidence()),
        evidence_task=task(),
        source_metadata=metadata(),
        implementation_identity=SUBJECT,
    )
    claim_changed = standardize_gates_v1_rc3(
        request(root_id="claim-b", text="Ozempic is approved in Canada.", sources=evidence()),
        evidence_task=task(),
        source_metadata=metadata(),
        implementation_identity=SUBJECT,
    )
    record(
        "ID-01",
        "evidence_identity",
        base.evidence_gate == claim_changed.evidence_gate,
        "byte-identical EvidenceGate",
        base.evidence_gate == claim_changed.evidence_gate,
        "Changing only the claim must not change intrinsic EvidenceGate.",
    )

    reordered = standardize_gates_v1_rc3(
        request(sources=tuple(reversed(evidence()))),
        evidence_task=task(),
        source_metadata=tuple(reversed(metadata())),
        implementation_identity=SUBJECT,
    )
    record(
        "ID-02",
        "evidence_identity",
        base.evidence_gate == reordered.evidence_gate,
        "order invariant",
        base.evidence_gate == reordered.evidence_gate,
        "Source and metadata order must not affect EvidenceGate.",
    )

    rows = list(metadata())
    rows[0] = SourceMetadataV1RC3(**{**rows[0].__dict__, "source_role": "alternate_role"})
    changed = standardize_gates_v1_rc3(
        request(sources=evidence()),
        evidence_task=task(),
        source_metadata=tuple(rows),
        implementation_identity=SUBJECT,
    )
    ok = (
        base.evidence_gate["evidence_world_id"] == changed.evidence_gate["evidence_world_id"]
        and base.evidence_gate["output_sha256"] != changed.evidence_gate["output_sha256"]
    )
    record("ID-03", "evidence_identity", ok, True, ok, "Metadata changes characterization, not intrinsic world identity.")

    rows = list(metadata())
    rows[0] = SourceMetadataV1RC3(
        **{**rows[0].__dict__, "locator_value": "https://example.invalid/alternate"}
    )
    changed = standardize_gates_v1_rc3(
        request(sources=evidence()),
        evidence_task=task(),
        source_metadata=tuple(rows),
        implementation_identity=SUBJECT,
    )
    ok = (
        base.evidence_gate["evidence_world_id"] == changed.evidence_gate["evidence_world_id"]
        and base.evidence_gate["output_sha256"] != changed.evidence_gate["output_sha256"]
    )
    record("ID-04", "evidence_identity", ok, True, ok, "Source-origin locator is characterization, not evidence identity.")

    mutated_sources = (
        SourceRepresentation("hc-product", "text/html", "Current status: Revoked."),
        evidence()[1],
    )
    changed = standardize_gates_v1_rc3(
        request(sources=mutated_sources),
        evidence_task=task(),
        source_metadata=metadata(),
        implementation_identity=SUBJECT,
    )
    ok = base.evidence_gate["evidence_world_id"] != changed.evidence_gate["evidence_world_id"]
    record("ID-05", "evidence_identity", ok, True, ok, "Byte mutation must change evidence-world identity.")

    renamed_sources = (
        SourceRepresentation("hc-product-renamed", evidence()[0].media_type, evidence()[0].content),
        evidence()[1],
    )
    first = metadata()[0]
    renamed_metadata = (
        SourceMetadataV1RC3(**{**first.__dict__, "source_id": "hc-product-renamed"}),
        metadata()[1],
    )
    changed = standardize_gates_v1_rc3(
        request(sources=renamed_sources),
        evidence_task=task(),
        source_metadata=renamed_metadata,
        implementation_identity=SUBJECT,
    )
    ok = base.evidence_gate["evidence_world_id"] != changed.evidence_gate["evidence_world_id"]
    record("ID-06", "evidence_identity", ok, True, ok, "Source identity is part of representation identity.")

    media_changed = standardize_gates_v1_rc3(
        request(sources=evidence("text/plain")),
        evidence_task=task(),
        source_metadata=metadata(),
        implementation_identity=SUBJECT,
    )
    ok = base.evidence_gate["evidence_world_id"] != media_changed.evidence_gate["evidence_world_id"]
    record("ID-07", "evidence_identity", ok, True, ok, "Normalized media type is part of representation identity.")

    duplicate_rejected = rejects(
        lambda: build_evidence_gate_output_v1_rc3(
            request(
                sources=(
                    SourceRepresentation("dup", "text/plain", "a"),
                    SourceRepresentation("dup", "text/plain", "b"),
                )
            )
        )
    )
    record("ID-08", "evidence_identity", duplicate_rejected, True, duplicate_rejected, "Duplicate source IDs fail closed.")

    orphan_rejected = rejects(
        lambda: build_evidence_gate_output_v1_rc3(
            request(sources=evidence()),
            source_metadata=(SourceMetadataV1RC3("not-supplied", issuer="X"),),
        )
    )
    record("ID-09", "evidence_identity", orphan_rejected, True, orphan_rejected, "Metadata for unsupplied source fails closed.")

    empty = standardize_gates_v1_rc3(
        request(root_id="empty", text="Widget cobalt is blue.", sources=()),
        implementation_identity=SUBJECT,
    )
    ok = (
        empty.evidence_gate["source_count"] == 0
        and empty.evidence_gate["corpus"]["known_gaps"]["state"] == "unknown"
    )
    record("ID-10", "evidence_identity", ok, True, ok, "Empty evidence world remains explicit and honest.")
    return base


def run_provenance_pressure(base) -> None:
    rows = list(metadata())
    rows[0] = SourceMetadataV1RC3(**{**rows[0].__dict__, "locator_value": "definitely not a URI"})
    rejected = rejects(
        lambda: standardize_gates_v1_rc3(
            request(sources=evidence()),
            evidence_task=task(),
            source_metadata=tuple(rows),
            implementation_identity=SUBJECT,
        )
    )
    record("PROV-01", "source_provenance", rejected, True, rejected, "Invalid web URI fails closed.")

    rows = list(metadata())
    rows[0] = SourceMetadataV1RC3(**{**rows[0].__dict__, "origin_type": "anything-goes-value"})
    rejected = rejects(
        lambda: standardize_gates_v1_rc3(
            request(sources=evidence()),
            evidence_task=task(),
            source_metadata=tuple(rows),
            implementation_identity=SUBJECT,
        )
    )
    record("PROV-02", "source_provenance", rejected, True, rejected, "Unregistered origin type fails closed.")

    rows = list(metadata())
    rows[0] = SourceMetadataV1RC3(
        **{**rows[0].__dict__, "source_authority_basis_kind": "proves_claim"}
    )
    rejected = rejects(
        lambda: standardize_gates_v1_rc3(
            request(sources=evidence()),
            evidence_task=task(),
            source_metadata=tuple(rows),
            implementation_identity=SUBJECT,
        )
    )
    record("PROV-03", "source_provenance", rejected, True, rejected, "Proposition-relative authority kind cannot enter source-authority vocabulary.")

    serialized = json.dumps(base.evidence_gate, sort_keys=True)
    forbidden = ["retention", "github_artifact", "local_cas", "object_store", "filesystem"]
    ok = not any(token in serialized for token in forbidden)
    record("PROV-04", "source_provenance", ok, True, ok, "Pipeline-retention state stays outside EvidenceGate.")

    _, first = build_provenance_inputs_v1_rc3(
        request(sources=evidence()), evidence_task=task(), source_metadata=metadata()
    )
    _, second = build_provenance_inputs_v1_rc3(
        request(root_id="claim-b", text="Ozempic is approved in Canada.", sources=evidence()),
        evidence_task=task(),
        source_metadata=metadata(),
    )
    record("PROV-05", "reconstruction", first == second, "claim-independent", first == second, "Evidence reconstruction input is claim-independent.")

    claim_input, _ = build_provenance_inputs_v1_rc3(
        request(sources=evidence()), evidence_task=task(), source_metadata=metadata()
    )
    ok = claim_input["request"]["sources"][0]["content"] == evidence()[0].content
    record("PROV-06", "reconstruction", ok, True, ok, "Claim reconstruction retains exact visible source bytes.")


def run_validator_pressure(base) -> None:
    tampered = copy.deepcopy(base.evidence_gate)
    tampered["authority"]["retrieval_authority"] = True
    tampered["output_sha256"] = bound_object_hash(tampered, "output_sha256")
    rejected = rejects(lambda: validate_evidence_gate_output_v1_rc3(tampered))
    record("VAL-01", "validator_parity", rejected, True, rejected, "Authority escalation is rejected after rehash.")

    tampered = copy.deepcopy(base.evidence_gate)
    tampered["sources"][0]["content_sha256"] = "not-a-sha256"
    tampered["output_sha256"] = bound_object_hash(tampered, "output_sha256")
    rejected = rejects(lambda: validate_evidence_gate_output_v1_rc3(tampered))
    record("VAL-02", "validator_parity", rejected, True, rejected, "Malformed content commitment fails structural authority.")

    tampered = copy.deepcopy(base.evidence_gate)
    tampered["sources"][0]["provenance"]["source_origin"]["locator"]["value"] = 12345
    tampered["output_sha256"] = bound_object_hash(tampered, "output_sha256")
    rejected = rejects(lambda: validate_evidence_gate_output_v1_rc3(tampered))
    record("VAL-03", "validator_parity", rejected, True, rejected, "Malformed nested provenance fails structural authority.")

    tampered = copy.deepcopy(base.claim_gate)
    tampered["authority"]["retrieval_authority"] = True
    tampered["output_sha256"] = bound_object_hash(tampered, "output_sha256")
    rejected = rejects(lambda: validate_claim_gate_output_v1_rc3(tampered))
    record("VAL-04", "validator_parity", rejected, True, rejected, "Claim authority escalation is rejected.")

    tampered = copy.deepcopy(base.claim_gate)
    tampered["claim"]["categories"]["state"] = "unknown"
    tampered["output_sha256"] = bound_object_hash(tampered, "output_sha256")
    rejected = rejects(lambda: validate_claim_gate_output_v1_rc3(tampered))
    record("VAL-05", "validator_parity", rejected, True, rejected, "Invalid category state/value shape is rejected.")

    tampered = copy.deepcopy(base.evidence_gate)
    tampered["source_count"] = 999
    rejected = rejects(lambda: validate_evidence_gate_output_v1_rc3(tampered))
    record("VAL-06", "validator_parity", rejected, True, rejected, "Stale/tampered output fails closed.")


def run_receipt_pressure(base) -> None:
    verified = verify_standardized_gate_bundle_v1_rc3(
        base.claim_gate,
        base.evidence_gate,
        base.authoring.contract_a,
        base.receipt,
    )
    record("REC-01", "paired_receipt", verified["state"] == "VERIFIED", "VERIFIED", verified["state"], "Exact bundle verifies.")

    tampered = copy.deepcopy(base.receipt)
    tampered["evidence_world_id"] = "sha256:" + "0" * 64
    tampered["receipt_sha256"] = bound_object_hash(tampered, "receipt_sha256")
    rejected = rejects(
        lambda: verify_standardized_gate_bundle_v1_rc3(
            base.claim_gate, base.evidence_gate, base.authoring.contract_a, tampered
        )
    )
    record("REC-02", "paired_receipt", rejected, True, rejected, "Evidence-world substitution fails bundle verification.")

    tampered = copy.deepcopy(base.receipt)
    tampered["claim_gate_output_sha256"] = "sha256:" + "1" * 64
    tampered["receipt_sha256"] = bound_object_hash(tampered, "receipt_sha256")
    rejected = rejects(
        lambda: verify_standardized_gate_bundle_v1_rc3(
            base.claim_gate, base.evidence_gate, base.authoring.contract_a, tampered
        )
    )
    record("REC-03", "paired_receipt", rejected, True, rejected, "ClaimGate substitution fails bundle verification.")


def run_authority_and_determinism(base) -> None:
    forbidden = {
        "support",
        "refutation",
        "verdict",
        "query",
        "rank",
        "admission",
        "decision",
        "authorization",
        "expected_evidence_forms",
    }

    def keys(value: Any) -> set[str]:
        found: set[str] = set()
        if isinstance(value, dict):
            for key, child in value.items():
                found.add(str(key))
                found |= keys(child)
        elif isinstance(value, list):
            for child in value:
                found |= keys(child)
        return found

    bad = sorted((keys(base.claim_gate) | keys(base.evidence_gate)) & forbidden)
    record("AUTH-01", "authority_firewall", bad == [], [], bad, "No downstream routing/semantic/decision fields.")

    authority = base.claim_gate["authority"] | base.evidence_gate["authority"]
    ok = (
        base.claim_gate["authority"]["retrieval_authority"] is False
        and base.claim_gate["authority"]["evidence_relation_authority"] is False
        and base.claim_gate["authority"]["decision_authority"] is False
        and base.claim_gate["authority"]["authorization_authority"] is False
        and base.evidence_gate["authority"]["retrieval_authority"] is False
        and base.evidence_gate["authority"]["evidence_relation_authority"] is False
        and base.evidence_gate["authority"]["decision_authority"] is False
        and base.evidence_gate["authority"]["authorization_authority"] is False
    )
    record("AUTH-02", "authority_firewall", ok, True, authority, "All downstream authority flags remain false.")

    direct = AuthoringEngine().author(request(sources=evidence()))
    record("AUTH-03", "claim_authority", direct.contract_a == base.authoring.contract_a, "same Contract A", direct.contract_a == base.authoring.contract_a, "RC3 does not rewrite authoritative Contract A.")

    replay = standardize_gates_v1_rc3(
        request(sources=evidence()),
        evidence_task=task(),
        source_metadata=metadata(),
        implementation_identity=SUBJECT,
    )
    ok = (
        replay.claim_gate == base.claim_gate
        and replay.evidence_gate == base.evidence_gate
        and replay.receipt == base.receipt
    )
    record("DET-01", "determinism", ok, True, ok, "Exact replay is object-identical.")


def main() -> None:
    run_claim_category_pressure()
    base = run_identity_pressure()
    run_provenance_pressure(base)
    run_validator_pressure(base)
    run_receipt_pressure(base)
    run_authority_and_determinism(base)

    counts = {SUPPORTED: 0, FALSIFIED: 0}
    for case in CASES:
        counts[case.disposition] += 1

    result = {
        "subject": SUBJECT,
        "case_count": len(CASES),
        "counts": counts,
        "cases": [asdict(case) for case in CASES],
        "authority_effect": "NONE_PRESSURE_TEST_ONLY",
    }
    out = Path("pressure-result")
    out.mkdir(exist_ok=True)
    (out / "RESULT.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(counts, sort_keys=True))
    print(f"cases={len(CASES)}")
    if counts[FALSIFIED]:
        raise SystemExit(f"surface falsified: {counts[FALSIFIED]} cases")


if __name__ == "__main__":
    main()
