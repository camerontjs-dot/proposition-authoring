from __future__ import annotations

import copy
import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Callable

from jsonschema import Draft202012Validator, ValidationError

from proposition_authoring.canonical import bound_object_hash
from proposition_authoring.engine import AuthoringEngine
from proposition_authoring.gate_v1 import EvidenceTaskV1, GateV1Error
import proposition_authoring.gate_v1_rc2 as rc2
from proposition_authoring.gate_v1_rc2 import (
    SourceMetadataV1RC2,
    build_evidence_gate_output_v1_rc2,
    build_provenance_inputs_v1_rc2,
    classify_claim_v1_rc2,
    standardize_gates_v1_rc2,
    validate_claim_gate_output_v1_rc2,
    validate_evidence_gate_output_v1_rc2,
)
from proposition_authoring.model import AuthoringRequest, SourceRepresentation

SUBJECT = "8c10bd703a747f5448c424fbe7ce1e2521b7647e"
SUPPORTED = "SUPPORTED_SURFACE"
FALSIFIED = "FALSIFIED_SURFACE"
INCONCLUSIVE = "INCONCLUSIVE_DESIGN"


@dataclass
class Case:
    case_id: str
    axis: str
    disposition: str
    expected: Any
    observed: Any
    detail: str


CASES: list[Case] = []


def record(
    case_id: str,
    axis: str,
    disposition: str,
    expected: Any,
    observed: Any,
    detail: str,
) -> None:
    CASES.append(Case(case_id, axis, disposition, expected, observed, detail))


def expect_equal(case_id: str, axis: str, expected: Any, observed: Any, detail: str) -> None:
    record(
        case_id,
        axis,
        SUPPORTED if observed == expected else FALSIFIED,
        expected,
        observed,
        detail,
    )


def expect_true(case_id: str, axis: str, condition: bool, observed: Any, detail: str) -> None:
    record(
        case_id,
        axis,
        SUPPORTED if condition else FALSIFIED,
        True,
        observed,
        detail,
    )


def request(
    *,
    root_id: str = "claim-a",
    text: str = "Ozempic DIN 02562618 is approved in Canada.",
    sources: tuple[SourceRepresentation, ...] = (),
    context_source_id: str | None = None,
) -> AuthoringRequest:
    return AuthoringRequest(
        handoff_id=f"handoff-{root_id}",
        producer_id="surface-pressure",
        producer_version="1",
        work_id="surface-pressure-work",
        root_id=root_id,
        root_text=text,
        sources=sources,
        context_source_id=context_source_id,
    )


def evidence() -> tuple[SourceRepresentation, ...]:
    return (
        SourceRepresentation(
            "hc-product",
            "text/html",
            "Current status: Approved. Product name: OZEMPIC. DIN: 02562618.",
        ),
        SourceRepresentation(
            "hc-context",
            "text/html",
            "Health Canada Drug Product Database online query.",
        ),
    )


def metadata() -> tuple[SourceMetadataV1RC2, ...]:
    return (
        SourceMetadataV1RC2(
            "hc-product",
            origin_type="official_regulatory_database",
            source_uri="https://health-products.canada.ca/dpd-bdpp/info?code=106547&lang=eng",
            issuer="Health Canada",
            source_role="official_regulatory_product_record",
            authority_basis="official Health Canada Drug Product Database record",
            document_type="database_record",
            evidence_form="registry_entry",
            temporal_coverage="status date 2025-11-04",
            jurisdictional_coverage="Canada",
            version="retrieved 2026-09-17",
            currency_state="current_as_retrieved",
        ),
        SourceMetadataV1RC2(
            "hc-context",
            origin_type="official_regulatory_database",
            source_uri="https://health-products.canada.ca/dpd-bdpp/",
            issuer="Health Canada",
            source_role="official_database_context",
            authority_basis="official Health Canada database interface",
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
    observed = classify_claim_v1_rc2(text)
    expect_equal(
        case_id,
        "claim_category",
        list(expected),
        list(observed),
        text,
    )


def schema_validator(path: str) -> Draft202012Validator:
    schema = json.loads(Path(path).read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema)


CLAIM_SCHEMA = schema_validator("schema/gates/1.0.0-rc.2/claim-gate-output.schema.json")
EVIDENCE_SCHEMA = schema_validator("schema/gates/1.0.0-rc.2/evidence-gate-output.schema.json")
RECEIPT_SCHEMA = schema_validator("schema/gates/1.0.0-rc.2/standardization-receipt.schema.json")


def schema_accepts(validator: Draft202012Validator, value: Any) -> bool:
    try:
        validator.validate(value)
        return True
    except ValidationError:
        return False


def python_accepts(fn: Callable[[Any], Any], value: Any) -> bool:
    try:
        fn(value)
        return True
    except (GateV1Error, KeyError, TypeError, ValueError):
        return False


def rehash(value: dict[str, Any], field: str) -> None:
    value[field] = bound_object_hash(value, field)


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


def run_identity_pressure() -> tuple[Any, Any]:
    base = standardize_gates_v1_rc2(
        request(sources=evidence()),
        evidence_task=task(),
        source_metadata=metadata(),
        implementation_identity=SUBJECT,
    )
    claim_changed = standardize_gates_v1_rc2(
        request(root_id="claim-b", text="Ozempic is approved in Canada.", sources=evidence()),
        evidence_task=task(),
        source_metadata=metadata(),
        implementation_identity=SUBJECT,
    )
    expect_equal(
        "ID-01",
        "evidence_identity",
        base.evidence_gate,
        claim_changed.evidence_gate,
        "Changing only the claim must not change intrinsic EvidenceGate.",
    )

    reordered = standardize_gates_v1_rc2(
        request(sources=tuple(reversed(evidence()))),
        evidence_task=task(),
        source_metadata=tuple(reversed(metadata())),
        implementation_identity=SUBJECT,
    )
    expect_equal(
        "ID-02",
        "evidence_identity",
        base.evidence_gate,
        reordered.evidence_gate,
        "Source and metadata row order must not affect EvidenceGate.",
    )

    rows = list(metadata())
    rows[0] = SourceMetadataV1RC2(**{**rows[0].__dict__, "source_role": "alternate_role"})
    meta_changed = standardize_gates_v1_rc2(
        request(sources=evidence()),
        evidence_task=task(),
        source_metadata=tuple(rows),
        implementation_identity=SUBJECT,
    )
    expect_true(
        "ID-03",
        "evidence_identity",
        base.evidence_gate["evidence_world_id"] == meta_changed.evidence_gate["evidence_world_id"]
        and base.evidence_gate["output_sha256"] != meta_changed.evidence_gate["output_sha256"],
        {
            "base_world": base.evidence_gate["evidence_world_id"],
            "changed_world": meta_changed.evidence_gate["evidence_world_id"],
            "base_output": base.evidence_gate["output_sha256"],
            "changed_output": meta_changed.evidence_gate["output_sha256"],
        },
        "Metadata change should preserve byte-world identity but change Gate output identity.",
    )

    rows = list(metadata())
    rows[0] = SourceMetadataV1RC2(
        **{**rows[0].__dict__, "source_uri": "https://example.invalid/alternate"}
    )
    uri_changed = standardize_gates_v1_rc2(
        request(sources=evidence()),
        evidence_task=task(),
        source_metadata=tuple(rows),
        implementation_identity=SUBJECT,
    )
    expect_true(
        "ID-04",
        "evidence_identity",
        base.evidence_gate["evidence_world_id"] == uri_changed.evidence_gate["evidence_world_id"]
        and base.evidence_gate["output_sha256"] != uri_changed.evidence_gate["output_sha256"],
        {
            "base_world": base.evidence_gate["evidence_world_id"],
            "changed_world": uri_changed.evidence_gate["evidence_world_id"],
        },
        "Source-origin URI is characterization, not intrinsic byte-world identity.",
    )

    mutated_sources = (
        SourceRepresentation("hc-product", "text/html", "Current status: Revoked."),
        evidence()[1],
    )
    bytes_changed = standardize_gates_v1_rc2(
        request(sources=mutated_sources),
        evidence_task=task(),
        source_metadata=metadata(),
        implementation_identity=SUBJECT,
    )
    expect_true(
        "ID-05",
        "evidence_identity",
        base.evidence_gate["evidence_world_id"] != bytes_changed.evidence_gate["evidence_world_id"],
        {
            "base": base.evidence_gate["evidence_world_id"],
            "changed": bytes_changed.evidence_gate["evidence_world_id"],
        },
        "Byte mutation must change evidence-world identity.",
    )

    renamed_sources = (
        SourceRepresentation("hc-product-renamed", evidence()[0].media_type, evidence()[0].content),
        evidence()[1],
    )
    renamed_metadata = (
        SourceMetadataV1RC2(
            "hc-product-renamed",
            origin_type=metadata()[0].origin_type,
            source_uri=metadata()[0].source_uri,
            issuer=metadata()[0].issuer,
            source_role=metadata()[0].source_role,
            authority_basis=metadata()[0].authority_basis,
            document_type=metadata()[0].document_type,
            evidence_form=metadata()[0].evidence_form,
            temporal_coverage=metadata()[0].temporal_coverage,
            jurisdictional_coverage=metadata()[0].jurisdictional_coverage,
            version=metadata()[0].version,
            currency_state=metadata()[0].currency_state,
        ),
        metadata()[1],
    )
    renamed = standardize_gates_v1_rc2(
        request(sources=renamed_sources),
        evidence_task=task(),
        source_metadata=renamed_metadata,
        implementation_identity=SUBJECT,
    )
    expect_true(
        "ID-06",
        "evidence_identity",
        base.evidence_gate["evidence_world_id"] != renamed.evidence_gate["evidence_world_id"],
        {
            "base": base.evidence_gate["evidence_world_id"],
            "renamed": renamed.evidence_gate["evidence_world_id"],
        },
        "Participant/source identity is part of evidence-world identity.",
    )

    media_sources = (
        SourceRepresentation("hc-product", "application/json", evidence()[0].content),
        evidence()[1],
    )
    media_changed = standardize_gates_v1_rc2(
        request(sources=media_sources),
        evidence_task=task(),
        source_metadata=metadata(),
        implementation_identity=SUBJECT,
    )
    record(
        "ID-07",
        "evidence_identity",
        INCONCLUSIVE,
        "explicit programme decision",
        {
            "same_world": base.evidence_gate["evidence_world_id"] == media_changed.evidence_gate["evidence_world_id"],
            "same_output": base.evidence_gate["output_sha256"] == media_changed.evidence_gate["output_sha256"],
        },
        "RC2 treats same source_id+bytes with a different media_type as the same intrinsic evidence world but a different standardized output. Decide whether media type is representation identity or characterization.",
    )

    try:
        build_evidence_gate_output_v1_rc2(
            request(
                sources=(
                    SourceRepresentation("dup", "text/plain", "a"),
                    SourceRepresentation("dup", "text/plain", "b"),
                )
            )
        )
        dup_rejected = False
    except GateV1Error:
        dup_rejected = True
    expect_true("ID-08", "evidence_identity", dup_rejected, dup_rejected, "Duplicate source IDs must fail closed.")

    try:
        build_evidence_gate_output_v1_rc2(
            request(sources=evidence()),
            source_metadata=(SourceMetadataV1RC2("not-supplied", issuer="X"),),
        )
        bad_meta_rejected = False
    except GateV1Error:
        bad_meta_rejected = True
    expect_true(
        "ID-09",
        "evidence_identity",
        bad_meta_rejected,
        bad_meta_rejected,
        "Metadata for an unsupplied source must fail closed.",
    )

    empty = standardize_gates_v1_rc2(
        request(root_id="empty", text="Widget cobalt is blue.", sources=()),
        implementation_identity=SUBJECT,
    )
    expect_true(
        "ID-10",
        "evidence_identity",
        empty.evidence_gate["source_count"] == 0
        and empty.evidence_gate["corpus"]["known_gaps"]["state"] == "unknown",
        {
            "source_count": empty.evidence_gate["source_count"],
            "known_gaps": empty.evidence_gate["corpus"]["known_gaps"]["state"],
        },
        "An explicit empty evidence world should remain representable without invented completeness.",
    )
    return base, claim_changed


def run_provenance_pressure(base: Any, claim_changed: Any) -> None:
    invalid_uri_meta = list(metadata())
    invalid_uri_meta[0] = SourceMetadataV1RC2(
        **{**invalid_uri_meta[0].__dict__, "source_uri": "definitely not a URI"}
    )
    try:
        invalid = standardize_gates_v1_rc2(
            request(sources=evidence()),
            evidence_task=task(),
            source_metadata=tuple(invalid_uri_meta),
            implementation_identity=SUBJECT,
        )
        accepted = True
        schema_ok = schema_accepts(EVIDENCE_SCHEMA, invalid.evidence_gate)
    except (GateV1Error, ValidationError):
        accepted = False
        schema_ok = False
    expect_true(
        "PROV-01",
        "source_provenance",
        not accepted,
        {"accepted": accepted, "schema_accepts": schema_ok},
        "A field named source_uri should reject a known non-URI rather than standardize it as a valid source locator.",
    )

    arbitrary_origin = list(metadata())
    arbitrary_origin[0] = SourceMetadataV1RC2(
        **{**arbitrary_origin[0].__dict__, "origin_type": "anything-goes-value"}
    )
    arbitrary = standardize_gates_v1_rc2(
        request(sources=evidence()),
        evidence_task=task(),
        source_metadata=tuple(arbitrary_origin),
        implementation_identity=SUBJECT,
    )
    record(
        "PROV-02",
        "source_provenance",
        INCONCLUSIVE,
        "controlled vocabulary or explicitly declared free text",
        arbitrary.evidence_gate["sources"][0]["provenance"]["origin"]["origin_type"],
        "origin_type is syntactically typed but semantically unconstrained. Decide whether downstream standardization needs a vocabulary.",
    )

    claim_relative = list(metadata())
    claim_relative[0] = SourceMetadataV1RC2(
        **{
            **claim_relative[0].__dict__,
            "authority_basis": "this source proves the Ozempic approval claim",
        }
    )
    accepted = standardize_gates_v1_rc2(
        request(sources=evidence()),
        evidence_task=task(),
        source_metadata=tuple(claim_relative),
        implementation_identity=SUBJECT,
    )
    record(
        "PROV-03",
        "source_provenance",
        INCONCLUSIVE,
        "source-relative authority basis only",
        accepted.evidence_gate["sources"][0]["provenance"]["authority_basis"],
        "The free-text authority_basis can carry proposition-relative wording even though Gate authority flags deny semantic authority. Consider naming/validation to reduce semantic smuggling risk.",
    )

    output_keys = json.dumps(base.evidence_gate, sort_keys=True)
    forbidden = ["retention", "github_artifact", "local_cas", "object_store", "filesystem"]
    expect_true(
        "PROV-04",
        "source_provenance",
        not any(token in output_keys for token in forbidden),
        {token: token in output_keys for token in forbidden},
        "EvidenceGate must not absorb pipeline-retention locator state.",
    )

    claim_input_a, evidence_input_a = build_provenance_inputs_v1_rc2(
        request(sources=evidence()), evidence_task=task(), source_metadata=metadata()
    )
    claim_input_b, evidence_input_b = build_provenance_inputs_v1_rc2(
        request(root_id="claim-b", text="Ozempic is approved in Canada.", sources=evidence()),
        evidence_task=task(),
        source_metadata=metadata(),
    )
    expect_equal(
        "PROV-05",
        "reconstruction",
        evidence_input_a,
        evidence_input_b,
        "EvidenceGate reconstruction input should be claim-independent for identical evidence bytes/declarations.",
    )
    expect_true(
        "PROV-06",
        "reconstruction",
        claim_input_a != claim_input_b
        and claim_input_a["request"]["sources"][0]["content"] == evidence()[0].content,
        {
            "claim_inputs_differ": claim_input_a != claim_input_b,
            "source_bytes_retained": claim_input_a["request"]["sources"][0]["content"] == evidence()[0].content,
        },
        "ClaimGate reconstruction input must preserve the exact request, including source bytes that ClaimGate may inspect.",
    )


def run_validator_pressure(base: Any) -> None:
    # Evidence authority firewall tamper.
    tampered = copy.deepcopy(base.evidence_gate)
    tampered["authority"]["retrieval_authority"] = True
    rehash(tampered, "output_sha256")
    py_ok = python_accepts(validate_evidence_gate_output_v1_rc2, tampered)
    schema_ok = schema_accepts(EVIDENCE_SCHEMA, tampered)
    expect_true(
        "VAL-01",
        "validator_parity",
        not py_ok and not schema_ok,
        {"python_accepts": py_ok, "schema_accepts": schema_ok},
        "Python validator and wire schema must both reject authority escalation even if the object hash is recomputed.",
    )

    # Malformed source content commitment with all dependent hashes recomputed.
    tampered = copy.deepcopy(base.evidence_gate)
    tampered["sources"][0]["content_sha256"] = "not-a-sha256"
    tampered["evidence_world_id"] = rc2._evidence_world_id_from_sources(tampered["sources"])
    rehash(tampered, "output_sha256")
    py_ok = python_accepts(validate_evidence_gate_output_v1_rc2, tampered)
    schema_ok = schema_accepts(EVIDENCE_SCHEMA, tampered)
    expect_true(
        "VAL-02",
        "validator_parity",
        not py_ok and not schema_ok,
        {"python_accepts": py_ok, "schema_accepts": schema_ok},
        "Validator parity must reject malformed content commitments after internally consistent rehashing.",
    )

    # Malformed nested URI observation.
    tampered = copy.deepcopy(base.evidence_gate)
    tampered["sources"][0]["provenance"]["origin"]["source_uri"]["value"] = 12345
    rehash(tampered, "output_sha256")
    py_ok = python_accepts(validate_evidence_gate_output_v1_rc2, tampered)
    schema_ok = schema_accepts(EVIDENCE_SCHEMA, tampered)
    expect_true(
        "VAL-03",
        "validator_parity",
        not py_ok and not schema_ok,
        {"python_accepts": py_ok, "schema_accepts": schema_ok},
        "Nested observation types must be enforced equally by Python and JSON Schema validators.",
    )

    claim = copy.deepcopy(base.claim_gate)
    claim["authority"]["retrieval_authority"] = True
    rehash(claim, "output_sha256")
    py_ok = python_accepts(validate_claim_gate_output_v1_rc2, claim)
    schema_ok = schema_accepts(CLAIM_SCHEMA, claim)
    expect_true(
        "VAL-04",
        "validator_parity",
        not py_ok and not schema_ok,
        {"python_accepts": py_ok, "schema_accepts": schema_ok},
        "ClaimGate authority escalation must fail in both validation paths.",
    )

    claim = copy.deepcopy(base.claim_gate)
    claim["claim"]["categories"]["state"] = "unknown"
    rehash(claim, "output_sha256")
    py_ok = python_accepts(validate_claim_gate_output_v1_rc2, claim)
    schema_ok = schema_accepts(CLAIM_SCHEMA, claim)
    expect_true(
        "VAL-05",
        "validator_parity",
        not py_ok and not schema_ok,
        {"python_accepts": py_ok, "schema_accepts": schema_ok},
        "Claim category state/value structure must be enforced by both validation paths.",
    )

    stale = copy.deepcopy(base.evidence_gate)
    stale["source_count"] = 999
    py_ok = python_accepts(validate_evidence_gate_output_v1_rc2, stale)
    expect_true(
        "VAL-06",
        "validator_parity",
        not py_ok,
        {"python_accepts": py_ok},
        "Stale-hash/tampered output must fail closed.",
    )


def run_receipt_pressure(base: Any) -> None:
    receipt_ok = (
        base.receipt["root_id"] == base.claim_gate["claim"]["proposition_id"]
        and base.receipt["evidence_world_id"] == base.evidence_gate["evidence_world_id"]
        and base.receipt["claim_gate_output_sha256"] == base.claim_gate["output_sha256"]
        and base.receipt["evidence_gate_output_sha256"] == base.evidence_gate["output_sha256"]
        and base.receipt["contract_a_handoff_sha256"]
        == base.claim_gate["contract_a_binding"]["handoff_sha256"]
    )
    expect_true(
        "REC-01",
        "paired_receipt",
        receipt_ok,
        receipt_ok,
        "Generated receipt must bind the exact ClaimGate, EvidenceGate, and Contract A identities.",
    )

    tampered = copy.deepcopy(base.receipt)
    tampered["evidence_world_id"] = "sha256:" + "0" * 64
    rehash(tampered, "receipt_sha256")
    schema_ok = schema_accepts(RECEIPT_SCHEMA, tampered)
    has_bundle_verifier = hasattr(rc2, "validate_standardization_bundle_v1_rc2")
    expect_true(
        "REC-02",
        "paired_receipt",
        not schema_ok or has_bundle_verifier,
        {"schema_accepts_cross_mismatch": schema_ok, "bundle_verifier_present": has_bundle_verifier},
        "A downstream consumer needs a canonical cross-artifact verifier; JSON Schema alone cannot detect a validly rehashed receipt pointing at the wrong evidence world.",
    )

    tampered = copy.deepcopy(base.receipt)
    tampered["claim_gate_output_sha256"] = "sha256:" + "1" * 64
    rehash(tampered, "receipt_sha256")
    schema_ok = schema_accepts(RECEIPT_SCHEMA, tampered)
    expect_true(
        "REC-03",
        "paired_receipt",
        not schema_ok or has_bundle_verifier,
        {"schema_accepts_cross_mismatch": schema_ok, "bundle_verifier_present": has_bundle_verifier},
        "Cross-object ClaimGate binding must be mechanically verifiable, not merely well-formed.",
    )


def run_authority_and_determinism(base: Any) -> None:
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
        out: set[str] = set()
        if isinstance(value, dict):
            for key, child in value.items():
                out.add(str(key))
                out |= keys(child)
        elif isinstance(value, list):
            for child in value:
                out |= keys(child)
        return out

    observed_forbidden = sorted((keys(base.claim_gate) | keys(base.evidence_gate)) & forbidden)
    expect_equal(
        "AUTH-01",
        "authority_firewall",
        [],
        observed_forbidden,
        "Gate outputs must not expose downstream routing/semantic/decision fields.",
    )

    authority_ok = (
        base.claim_gate["authority"]["retrieval_authority"] is False
        and base.claim_gate["authority"]["evidence_relation_authority"] is False
        and base.claim_gate["authority"]["decision_authority"] is False
        and base.claim_gate["authority"]["authorization_authority"] is False
        and base.evidence_gate["authority"]["retrieval_authority"] is False
        and base.evidence_gate["authority"]["evidence_relation_authority"] is False
        and base.evidence_gate["authority"]["decision_authority"] is False
        and base.evidence_gate["authority"]["authorization_authority"] is False
    )
    expect_true("AUTH-02", "authority_firewall", authority_ok, authority_ok, "All downstream authority flags must remain false.")

    direct = AuthoringEngine().author(request(sources=evidence()))
    expect_equal(
        "AUTH-03",
        "claim_authority",
        direct.contract_a,
        base.authoring.contract_a,
        "RC2 standardization must not alter authoritative ClaimGate/Contract A bytes.",
    )

    replay = standardize_gates_v1_rc2(
        request(sources=evidence()),
        evidence_task=task(),
        source_metadata=metadata(),
        implementation_identity=SUBJECT,
    )
    expect_true(
        "DET-01",
        "determinism",
        replay.claim_gate == base.claim_gate
        and replay.evidence_gate == base.evidence_gate
        and replay.receipt == base.receipt,
        {
            "claim_equal": replay.claim_gate == base.claim_gate,
            "evidence_equal": replay.evidence_gate == base.evidence_gate,
            "receipt_equal": replay.receipt == base.receipt,
        },
        "Same exact inputs and implementation identity must replay byte-equivalently at object level.",
    )


def main() -> None:
    run_claim_category_pressure()
    base, claim_changed = run_identity_pressure()
    run_provenance_pressure(base, claim_changed)
    run_validator_pressure(base)
    run_receipt_pressure(base)
    run_authority_and_determinism(base)

    counts = {SUPPORTED: 0, FALSIFIED: 0, INCONCLUSIVE: 0}
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
    (out / "RESULT.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    lines = [
        "# Gate V1 RC2 Surface Pressure Result",
        "",
        f"- subject: `{SUBJECT}`",
        f"- cases: **{len(CASES)}**",
        f"- supported: **{counts[SUPPORTED]}**",
        f"- falsified: **{counts[FALSIFIED]}**",
        f"- inconclusive design: **{counts[INCONCLUSIVE]}**",
        "",
        "| Case | Axis | Disposition | Detail |",
        "|---|---|---|---|",
    ]
    for case in CASES:
        detail = case.detail.replace("|", "\\|").replace("\n", " ")
        lines.append(f"| {case.case_id} | {case.axis} | {case.disposition} | {detail} |")
    (out / "RESULT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(json.dumps(result["counts"], sort_keys=True))
    print(f"cases={len(CASES)}")


if __name__ == "__main__":
    main()
