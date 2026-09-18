from __future__ import annotations

import copy
import json
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

SUPPORTED = "SUPPORTED_SURFACE"
FALSIFIED = "FALSIFIED_SURFACE"
CASES: list[dict[str, Any]] = []


def record(case_id: str, axis: str, ok: bool, detail: str, observed: Any = None) -> None:
    CASES.append(
        {
            "case_id": case_id,
            "axis": axis,
            "disposition": SUPPORTED if ok else FALSIFIED,
            "detail": detail,
            "observed": observed,
        }
    )


def request(
    *,
    root_id: str = "claim-a",
    text: str = "Ozempic DIN 02562618 is approved in Canada.",
    sources: tuple[SourceRepresentation, ...] = (),
) -> AuthoringRequest:
    return AuthoringRequest(
        handoff_id=f"handoff-{root_id}",
        producer_id="surface-pressure-rc3",
        producer_version="1",
        work_id="surface-pressure-work",
        root_id=root_id,
        root_text=text,
        sources=sources,
    )


def evidence() -> tuple[SourceRepresentation, ...]:
    return (
        SourceRepresentation("hc-product", "text/html", "Current status: Approved."),
        SourceRepresentation("hc-context", "text/plain", "Health Canada DPD."),
    )


def metadata() -> tuple[SourceMetadataV1RC3, ...]:
    return (
        SourceMetadataV1RC3(
            "hc-product",
            origin_type="official_database",
            locator_kind="web_uri",
            locator_value="https://health-products.canada.ca/dpd-bdpp/info?code=106547",
            issuer="Health Canada",
            source_role="official_regulatory_product_record",
            source_authority_basis="Issued through the official Health Canada DPD.",
            document_type="database_record",
            evidence_form="registry_entry",
            temporal_coverage="status date 2025-11-04",
            jurisdictional_coverage="Canada",
            version="retrieved 2026-09-17",
            currency_state="current_as_retrieved",
        ),
        SourceMetadataV1RC3(
            "hc-context",
            origin_type="official_website",
            locator_kind="web_uri",
            locator_value="https://health-products.canada.ca/dpd-bdpp/",
            issuer="Health Canada",
            source_role="official_database_context",
            source_authority_basis="Published by Health Canada.",
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


def standard(
    req: AuthoringRequest | None = None,
    *,
    metas: tuple[SourceMetadataV1RC3, ...] | None = None,
):
    return standardize_gates_v1_rc3(
        req or request(sources=evidence()),
        evidence_task=task(),
        source_metadata=metadata() if metas is None else metas,
        implementation_identity="rc3-pressure",
    )


def run_categories() -> None:
    matrix = [
        ("CAT-01", "Ozempic DIN 02562618 is approved in Canada.", ("status",)),
        ("CAT-02", "Ozempic DIN: 02562618 is approved in Canada.", ("status",)),
        ("CAT-03", "Ozempic NDC 0002-8215-01 is approved.", ("status",)),
        ("CAT-04", "Lot number 123456 was rejected.", ("status",)),
        ("CAT-05", "Serial No. 77881 was approved.", ("status",)),
        ("CAT-06", "Document No. 77881 was approved.", ("status",)),
        ("CAT-07", "DIN No. 02562618 is approved.", ("status",)),
        ("CAT-08", "DIN number 02562618 is approved.", ("status",)),
        ("CAT-09", "ISO 13485 compliant.", ("compliance", "status")),
        ("CAT-10", "The device was approved under 21 CFR Part 11.", ("status",)),
        ("CAT-11", "The licence was approved on 2025-11-04.", ("status", "temporal")),
        ("CAT-12", "Version 2 was approved.", ("status",)),
        ("CAT-13", "There were 25 rejected records.", ("quantitative", "status")),
        ("CAT-14", "DIN 02562618 had a 4.2 percent failure rate.", ("quantitative",)),
        ("CAT-15", "The system was inactive in 2025.", ("status", "temporal")),
    ]
    for case_id, text, expected in matrix:
        observed = classify_claim_v1_rc3(text)
        record(case_id, "claim_category", observed == expected, text, list(observed))


def run_identity() -> Any:
    base = standard()
    claim_changed = standard(
        request(
            root_id="claim-b",
            text="Ozempic is approved in Canada.",
            sources=evidence(),
        )
    )
    record("ID-01", "evidence_identity", base.evidence_gate == claim_changed.evidence_gate,
           "Changing only claim must not alter EvidenceGate.")

    reordered = standard(
        request(sources=tuple(reversed(evidence()))),
        metas=tuple(reversed(metadata())),
    )
    record("ID-02", "evidence_identity", base.evidence_gate == reordered.evidence_gate,
           "Source and metadata order invariance.")

    rows = list(metadata())
    rows[0] = SourceMetadataV1RC3(**{**rows[0].__dict__, "source_role": "alternate_role"})
    changed = standard(metas=tuple(rows))
    record("ID-03", "evidence_identity",
           base.evidence_gate["evidence_world_id"] == changed.evidence_gate["evidence_world_id"]
           and base.evidence_gate["output_sha256"] != changed.evidence_gate["output_sha256"],
           "Metadata changes characterization not intrinsic world.")

    rows = list(metadata())
    rows[0] = SourceMetadataV1RC3(
        **{**rows[0].__dict__, "locator_value": "https://example.com/alternate"}
    )
    changed = standard(metas=tuple(rows))
    record("ID-04", "evidence_identity",
           base.evidence_gate["evidence_world_id"] == changed.evidence_gate["evidence_world_id"],
           "Origin locator change does not alter intrinsic world.")

    changed_sources = (
        SourceRepresentation("hc-product", "text/html", "Current status: Revoked."),
        evidence()[1],
    )
    changed = standard(request(sources=changed_sources))
    record("ID-05", "evidence_identity",
           base.evidence_gate["evidence_world_id"] != changed.evidence_gate["evidence_world_id"],
           "Byte mutation changes evidence-world identity.")

    renamed_sources = (
        SourceRepresentation("hc-product-renamed", "text/html", evidence()[0].content),
        evidence()[1],
    )
    renamed_meta = (
        SourceMetadataV1RC3(
            "hc-product-renamed",
            **{k: v for k, v in metadata()[0].__dict__.items() if k != "source_id"},
        ),
        metadata()[1],
    )
    changed = standard(request(sources=renamed_sources), metas=renamed_meta)
    record("ID-06", "evidence_identity",
           base.evidence_gate["evidence_world_id"] != changed.evidence_gate["evidence_world_id"],
           "Source identity mutation changes evidence-world identity.")

    media_sources = (
        SourceRepresentation("hc-product", "application/json", evidence()[0].content),
        evidence()[1],
    )
    changed = standard(request(sources=media_sources))
    record("ID-07", "evidence_identity",
           base.evidence_gate["sources"][0]["content_sha256"]
           == changed.evidence_gate["sources"][0]["content_sha256"]
           and base.evidence_gate["sources"][0]["representation_id"]
           != changed.evidence_gate["sources"][0]["representation_id"]
           and base.evidence_gate["evidence_world_id"]
           != changed.evidence_gate["evidence_world_id"],
           "Media type is representation identity in V1.")

    try:
        build_evidence_gate_output_v1_rc3(
            request(
                sources=(
                    SourceRepresentation("dup", "text/plain", "a"),
                    SourceRepresentation("dup", "text/plain", "b"),
                )
            )
        )
        ok = False
    except GateV1Error:
        ok = True
    record("ID-08", "evidence_identity", ok, "Duplicate source IDs fail closed.")

    try:
        build_evidence_gate_output_v1_rc3(
            request(sources=evidence()),
            source_metadata=(SourceMetadataV1RC3("not-supplied", issuer="X"),),
        )
        ok = False
    except GateV1Error:
        ok = True
    record("ID-09", "evidence_identity", ok, "Unsupplied-source metadata fails closed.")

    empty = standardize_gates_v1_rc3(
        request(root_id="empty", text="Widget cobalt is blue.", sources=()),
        implementation_identity="rc3-pressure",
    )
    record("ID-10", "evidence_identity",
           empty.evidence_gate["source_count"] == 0
           and empty.evidence_gate["corpus"]["known_gaps"]["state"] == "unknown",
           "Empty evidence world remains explicit.")
    return base


def run_provenance(base: Any) -> None:
    rows = list(metadata())
    rows[0] = SourceMetadataV1RC3(
        **{**rows[0].__dict__, "locator_value": "definitely not a URI"}
    )
    try:
        standard(metas=tuple(rows))
        ok = False
    except GateV1Error:
        ok = True
    record("PROV-01", "source_provenance", ok, "web_uri rejects non-URI.")

    rows = list(metadata())
    rows[0] = SourceMetadataV1RC3(
        **{**rows[0].__dict__, "origin_type": "anything-goes-value"}
    )
    try:
        standard(metas=tuple(rows))
        ok = False
    except GateV1Error:
        ok = True
    record("PROV-02", "source_provenance", ok, "origin_type uses bounded V1 vocabulary.")

    provenance = base.evidence_gate["sources"][0]["provenance"]
    ok = (
        "source_authority_basis" in provenance
        and "authority_basis" not in provenance
        and base.evidence_gate["authority"]["evidence_relation_authority"] is False
    )
    record("PROV-03", "source_provenance", ok,
           "Authority basis is explicitly source-relative and carries no evidence-relation authority.")

    rendered = json.dumps(base.evidence_gate, sort_keys=True)
    forbidden = ["github_artifact", "local_cas", "object_store", "retention"]
    record("PROV-04", "source_provenance",
           not any(token in rendered for token in forbidden),
           "Source provenance excludes pipeline-retention state.")

    claim_input_a, evidence_input_a = build_provenance_inputs_v1_rc3(
        request(sources=evidence()), evidence_task=task(), source_metadata=metadata()
    )
    claim_input_b, evidence_input_b = build_provenance_inputs_v1_rc3(
        request(root_id="claim-b", text="Ozempic is approved in Canada.", sources=evidence()),
        evidence_task=task(), source_metadata=metadata()
    )
    record("PROV-05", "reconstruction", evidence_input_a == evidence_input_b,
           "Evidence reconstruction input is claim-independent.")
    record("PROV-06", "reconstruction",
           claim_input_a != claim_input_b
           and claim_input_a["request"]["sources"][0]["content"] == evidence()[0].content,
           "Claim reconstruction preserves exact visible request/source bytes.")


def run_validators(base: Any) -> None:
    evidence_mutations = [
        ("VAL-01", lambda x: x["authority"].__setitem__("retrieval_authority", True)),
        ("VAL-02", lambda x: x["sources"][0].__setitem__("content_sha256", "not-a-sha256")),
        (
            "VAL-03",
            lambda x: x["sources"][0]["provenance"]["source_origin"].__setitem__(
                "origin_type", 12345
            ),
        ),
    ]
    for case_id, mutate in evidence_mutations:
        value = copy.deepcopy(base.evidence_gate)
        mutate(value)
        value["output_sha256"] = bound_object_hash(value, "output_sha256")
        try:
            validate_evidence_gate_output_v1_rc3(value)
            ok = False
        except GateV1Error:
            ok = True
        record(case_id, "validator_parity", ok, "Wire-invalid EvidenceGate mutation rejected.")

    claim = copy.deepcopy(base.claim_gate)
    claim["authority"]["retrieval_authority"] = True
    claim["output_sha256"] = bound_object_hash(claim, "output_sha256")
    try:
        validate_claim_gate_output_v1_rc3(claim)
        ok = False
    except GateV1Error:
        ok = True
    record("VAL-04", "validator_parity", ok, "Claim authority escalation rejected.")

    claim = copy.deepcopy(base.claim_gate)
    claim["claim"]["categories"]["state"] = "unknown"
    claim["output_sha256"] = bound_object_hash(claim, "output_sha256")
    try:
        validate_claim_gate_output_v1_rc3(claim)
        ok = False
    except GateV1Error:
        ok = True
    record("VAL-05", "validator_parity", ok, "Invalid claim category state rejected.")

    stale = copy.deepcopy(base.evidence_gate)
    stale["source_count"] = 999
    try:
        validate_evidence_gate_output_v1_rc3(stale)
        ok = False
    except GateV1Error:
        ok = True
    record("VAL-06", "validator_parity", ok, "Stale/tampered hash fails closed.")


def run_receipt(base: Any) -> None:
    try:
        verify_standardized_gate_bundle_v1_rc3(
            base.claim_gate,
            base.evidence_gate,
            base.receipt,
            contract_a=base.authoring.contract_a,
        )
        ok = True
    except GateV1Error:
        ok = False
    record("REC-01", "paired_receipt", ok, "Generated bundle verifies.")

    for case_id, field, fake in [
        ("REC-02", "evidence_world_id", "sha256:" + "0" * 64),
        ("REC-03", "claim_gate_output_sha256", "sha256:" + "1" * 64),
    ]:
        receipt = copy.deepcopy(base.receipt)
        receipt[field] = fake
        receipt["receipt_sha256"] = bound_object_hash(receipt, "receipt_sha256")
        try:
            verify_standardized_gate_bundle_v1_rc3(
                base.claim_gate,
                base.evidence_gate,
                receipt,
                contract_a=base.authoring.contract_a,
            )
            ok = False
        except GateV1Error:
            ok = True
        record(case_id, "paired_receipt", ok, "Validly rehashed cross-artifact substitution rejected.")


def run_authority_and_determinism(base: Any) -> None:
    forbidden = {
        "support", "refutation", "verdict", "query", "rank", "admission",
        "decision", "authorization", "expected_evidence_forms",
    }

    def keys(value: Any) -> set[str]:
        out: set[str] = set()
        if isinstance(value, dict):
            for key, child in value.items():
                out.add(str(key))
                out |= keys(child)
        elif isinstance(value, list):
            for child in value:
                out |= keys(child)
        return out

    observed = sorted((keys(base.claim_gate) | keys(base.evidence_gate)) & forbidden)
    record("AUTH-01", "authority_firewall", observed == [], "No prohibited downstream fields.", observed)

    flags = [
        base.claim_gate["authority"]["retrieval_authority"],
        base.claim_gate["authority"]["evidence_relation_authority"],
        base.claim_gate["authority"]["decision_authority"],
        base.claim_gate["authority"]["authorization_authority"],
        base.evidence_gate["authority"]["retrieval_authority"],
        base.evidence_gate["authority"]["evidence_relation_authority"],
        base.evidence_gate["authority"]["decision_authority"],
        base.evidence_gate["authority"]["authorization_authority"],
    ]
    record("AUTH-02", "authority_firewall", flags == [False] * 8,
           "All downstream authority flags remain false.")

    direct = AuthoringEngine().author(request(sources=evidence()))
    record("AUTH-03", "claim_authority", direct.contract_a == base.authoring.contract_a,
           "RC3 leaves authoritative Contract A bytes unchanged.")

    replay = standard()
    record("DET-01", "determinism",
           replay.claim_gate == base.claim_gate
           and replay.evidence_gate == base.evidence_gate
           and replay.receipt == base.receipt,
           "Exact replay is deterministic.")


def main() -> None:
    run_categories()
    base = run_identity()
    run_provenance(base)
    run_validators(base)
    run_receipt(base)
    run_authority_and_determinism(base)

    counts = {SUPPORTED: 0, FALSIFIED: 0}
    for case in CASES:
        counts[case["disposition"]] += 1
    result = {
        "case_count": len(CASES),
        "counts": counts,
        "cases": CASES,
        "authority_effect": "NONE_QUALIFICATION_ONLY",
    }
    out = Path("pressure-result")
    out.mkdir(exist_ok=True)
    (out / "RESULT.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(counts, sort_keys=True))
    if len(CASES) != 44:
        raise SystemExit(f"expected 44 inherited cases, got {len(CASES)}")
    if counts[FALSIFIED]:
        raise SystemExit(f"surface still falsified: {counts}")


if __name__ == "__main__":
    main()
