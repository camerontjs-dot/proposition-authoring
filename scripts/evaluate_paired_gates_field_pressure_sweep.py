from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from proposition_authoring.claim_profile import build_claim_profile
from proposition_authoring.evidence_gate import build_evidence_world_profile
from proposition_authoring.feature_registry import build_feature_registry
from proposition_authoring.model import AuthoringRequest, SourceRepresentation
from proposition_authoring.preflight import compare_profiles
from proposition_authoring.shadow_models import SourceMetadata, TaskMetadata

SUBJECT_COMMIT = "e29a165b682d060f5dc2a0f3c7d64a7f29b172b4"
MATRIX_PATH = Path("research/paired_gates_field_pressure_sweep_v0/FIELD-SWEEP-MATRIX.json")


def _claim_case(case_id: str, field: str, text: str, expected: Any, *, mode: str = "equals", task: dict[str, Any] | None = None, sources: list[dict[str, str]] | None = None, context_source_id: str | None = None, note: str = "") -> dict[str, Any]:
    return {
        "case_id": case_id,
        "field_id": f"claim.{field}",
        "kind": "claim",
        "input": {
            "root_text": text,
            "task": task or {},
            "sources": sources or [],
            "context_source_id": context_source_id,
        },
        "selector": {"type": "profile_key", "key": field},
        "expect": {"mode": mode, "value": expected},
        "note": note,
    }


def _evidence_case(case_id: str, field: str, sources: list[dict[str, str]], expected: Any, *, metadata: list[dict[str, Any]] | None = None, task: dict[str, Any] | None = None, selector_type: str = "world_key", key: str | None = None, source_id: str | None = None, mode: str = "equals", note: str = "") -> dict[str, Any]:
    selector: dict[str, Any] = {"type": selector_type}
    if key is not None:
        selector["key"] = key
    if source_id is not None:
        selector["source_id"] = source_id
    return {
        "case_id": case_id,
        "field_id": f"evidence.{field}",
        "kind": "evidence",
        "input": {
            "sources": sources,
            "source_metadata": metadata or [],
            "task": task or {},
        },
        "selector": selector,
        "expect": {"mode": mode, "value": expected},
        "note": note,
    }


def _preflight_case(case_id: str, field: str, claim: dict[str, Any], world: dict[str, Any], expected_state: str, *, expected_evidence_value: Any | None = None, note: str = "") -> dict[str, Any]:
    expect: dict[str, Any] = {"mode": "observation_state", "value": expected_state}
    if expected_evidence_value is not None:
        expect["evidence_value"] = expected_evidence_value
    return {
        "case_id": case_id,
        "field_id": f"preflight.{field}",
        "kind": "preflight",
        "input": {"claim_profile": claim, "evidence_profile": world},
        "selector": {"type": "observation", "field": field},
        "expect": expect,
        "note": note,
    }


def frozen_cases() -> list[dict[str, Any]]:
    c: list[dict[str, Any]] = []
    add = c.append

    # ClaimGate: family, structure, relation, declared metadata, expectations, and surface flags.
    add(_claim_case("CF-01", "claim_families", "Group A had a higher rate than Group B.", ["comparative"], mode="contains_all"))
    add(_claim_case("CF-02", "claim_families", "The outage caused the delay.", ["causal"], mode="contains_all"))
    add(_claim_case("CF-03", "claim_families", "The audit found the unit compliant.", ["attributional", "status_state", "compliance"], mode="contains_all"))
    add(_claim_case("CF-04", "claim_families", "The standard deviation was 4.2.", ["numeric"], mode="set_equals", note="Statistical 'standard' should not by itself classify a compliance claim."))
    add(_claim_case("CF-05", "claim_families", "Foobar quux.", ["unknown"], mode="set_equals"))

    add(_claim_case("CS-01", "claim_structure_shape", "Valve Cerulean was inactive.", "single_clause_surface"))
    add(_claim_case("CS-02", "claim_structure_shape", "Valve A failed and Valve B passed.", "compound_or_scope_bearing_surface"))
    add(_claim_case("CS-03", "claim_structure_shape", "Research and Development LLC was active.", "single_clause_surface", note="Coordination inside a proper-name-like subject should not automatically make the proposition structurally compound."))

    for field in ("entities", "relation_targets"):
        add(_claim_case(f"REL-{field}-01", field, "Women had a higher rate than Men.", ["Women", "Men"]))
        add(_claim_case(f"REL-{field}-02", field, "Group A had a lower rate than Group B in 2025.", ["Group A", "Group B"]))
        add(_claim_case(f"REL-{field}-03", field, "The rate for Group A was higher than Group B.", ["Group A", "Group B"], note="Common comparative surface outside the single 'had' grammar should still expose relation participants if this field is to be generally useful."))

    add(_claim_case("DOM-01", "domain", "Any claim.", "healthcare", task={"domain": "healthcare"}))
    add(_claim_case("DOM-02", "domain", "Any claim.", "unknown"))
    add(_claim_case("VW-01", "verification_world", "Any claim.", "closed", task={"verification_world": "closed"}))
    add(_claim_case("VW-02", "verification_world", "Any claim.", "unknown"))

    add(_claim_case("TS-01", "temporal_scope", "The system was active in 2025.", "2025"))
    add(_claim_case("TS-02", "temporal_scope", "The system was active from 2020 through 2025.", "range:2020..2025", note="Temporal scope should distinguish a bounded range from an unordered list of endpoint years."))
    add(_claim_case("TS-03", "temporal_scope", "The system was active in 2025.", "Q1-2025", task={"temporal_scope": "Q1-2025"}))
    add(_claim_case("TS-04", "temporal_scope", "The system was active.", "unknown"))

    add(_claim_case("JUR-01", "jurisdiction", "Any claim.", "Canada", task={"jurisdiction": "Canada"}))
    add(_claim_case("JUR-02", "jurisdiction", "Any claim.", "unknown"))

    add(_claim_case("EEF-01", "expected_evidence_forms", "Group A had a higher rate than Group B.", ["document_text", "measurement"], mode="set_equals"))
    add(_claim_case("EEF-02", "expected_evidence_forms", "The outage caused the delay.", ["document_text", "event_record", "measurement"], mode="set_equals"))
    add(_claim_case("EEF-03", "expected_evidence_forms", "Auditor stated the valve was active.", ["authoritative_declaration", "database_record", "document_text", "registry_entry"], mode="contains_all"))
    add(_claim_case("EEF-04", "expected_evidence_forms", "Foobar quux.", ["unknown"], mode="set_equals"))

    context_sources = [{"source_id": "ctx", "media_type": "text/plain", "content": "Background material."}]
    add(_claim_case("CTX-01", "context_dependence", "Valve A was active.", "no_context_supplied"))
    add(_claim_case("CTX-02", "context_dependence", "Valve A was active.", "no_context_needed", sources=context_sources, context_source_id="ctx", note="Presence of context does not imply semantic dependence."))
    add(_claim_case("CTX-03", "context_dependence", "This system was active.", "context_required", note="Deictic text can depend on missing context."))

    add(_claim_case("SA-01", "scope_ambiguity", "Valve A was inactive.", "none_mechanically_observed"))
    add(_claim_case("SA-02", "scope_ambiguity", "Valve A failed and Valve B passed.", "possible_surface_scope"))
    add(_claim_case("SA-03", "scope_ambiguity", "Research and Development LLC was active.", "none_mechanically_observed"))

    add(_claim_case("NEG-01", "negation", "Valve A was not active.", "present"))
    add(_claim_case("NEG-02", "negation", "Valve A cannot operate.", "present", note="'cannot' is an ordinary negation form."))
    add(_claim_case("NEG-03", "negation", "Valve A was active.", "absent"))

    add(_claim_case("MOD-01", "modality", "Valve A may fail.", "present"))
    add(_claim_case("MOD-02", "modality", "Valve A will likely fail.", "present"))
    add(_claim_case("MOD-03", "modality", "Valve A will fail.", "present", note="Future modality is a useful boundary case."))
    add(_claim_case("MOD-04", "modality", "Valve A failed.", "absent"))

    add(_claim_case("ATT-01", "attribution", "The auditor reported Valve A failed.", "present"))
    add(_claim_case("ATT-02", "attribution", "According to the auditor, Valve A failed.", "present", note="Common attribution construction."))
    add(_claim_case("ATT-03", "attribution", "Valve A failed.", "absent"))

    # EvidenceGate: exact supplied world, declared metadata, mechanical MIME mappings, and relation hygiene.
    s1 = [{"source_id": "s1", "media_type": "text/plain", "content": "alpha"}]
    s2 = [{"source_id": "s2", "media_type": "application/pdf", "content": "beta"}]
    add(_evidence_case("ESI-01", "source_identity", s1, ["s1"], selector_type="inventory_field_all", key="source_id", mode="set_equals"))
    add(_evidence_case("ESI-02", "source_identity", s1 + s2, ["s1", "s2"], selector_type="inventory_field_all", key="source_id", mode="set_equals"))

    add(_evidence_case("ECI-01", "content_identity", s1, "sha256:" + hashlib.sha256(b"alpha").hexdigest(), selector_type="inventory_field", key="content_sha256", source_id="s1"))
    add(_evidence_case("ECI-02", "content_identity", [{"source_id": "s1", "media_type": "text/plain", "content": "changed"}], "sha256:" + hashlib.sha256(b"changed").hexdigest(), selector_type="inventory_field", key="content_sha256", source_id="s1"))

    for case_id, field, key, declared in (
        ("PROV", "provenance", "provenance", "regulator"),
        ("ISS", "issuer", "issuer", "Health Canada"),
        ("ROLE", "source_role", "source_role", "primary"),
        ("AUTHB", "authority_basis", "authority_basis", "issuer"),
    ):
        add(_evidence_case(f"{case_id}-01", field, s1, declared, metadata=[{"source_id": "s1", key: declared}], selector_type="inventory_field", key=key, source_id="s1"))
        add(_evidence_case(f"{case_id}-02", field, s1, "unknown", selector_type="inventory_field", key=key, source_id="s1"))

    add(_evidence_case("DT-01", "document_type", [{"source_id": "s1", "media_type": "application/pdf; charset=binary", "content": "a"}], "pdf_document", selector_type="inventory_field", key="document_type", source_id="s1"))
    add(_evidence_case("DT-02", "document_type", s1, "inspection_report", metadata=[{"source_id": "s1", "document_type": "inspection_report"}], selector_type="inventory_field", key="document_type", source_id="s1"))
    add(_evidence_case("DT-03", "document_type", [{"source_id": "s1", "media_type": "image/png", "content": "a"}], "unknown", selector_type="inventory_field", key="document_type", source_id="s1"))

    add(_evidence_case("EF-01", "evidence_form", [{"source_id": "s1", "media_type": "application/pdf", "content": "a"}], "document_text", selector_type="inventory_field", key="evidence_form", source_id="s1"))
    add(_evidence_case("EF-02", "evidence_form", [{"source_id": "s1", "media_type": "text/csv", "content": "a,b"}], "database_record", selector_type="inventory_field", key="evidence_form", source_id="s1"))
    add(_evidence_case("EF-03", "evidence_form", s1, "measurement", metadata=[{"source_id": "s1", "evidence_form": "measurement"}], selector_type="inventory_field", key="evidence_form", source_id="s1"))
    add(_evidence_case("EF-04", "evidence_form", [{"source_id": "s1", "media_type": "image/png", "content": "a"}], "unknown", selector_type="inventory_field", key="evidence_form", source_id="s1"))

    add(_evidence_case("ETC-01", "temporal_coverage", s1, "2025", metadata=[{"source_id": "s1", "temporal_coverage": "2025"}], selector_type="inventory_field", key="temporal_coverage", source_id="s1"))
    add(_evidence_case("ETC-02", "temporal_coverage", [{"source_id": "s1", "media_type": "text/plain", "content": "Report for 2025"}], "unknown", selector_type="inventory_field", key="temporal_coverage", source_id="s1", note="Registry declares source_metadata-only basis; V0 should not invent content-derived coverage."))

    add(_evidence_case("EJC-01", "jurisdictional_coverage", s1, "Canada", metadata=[{"source_id": "s1", "jurisdictional_coverage": "Canada"}], selector_type="inventory_field", key="jurisdictional_coverage", source_id="s1"))
    add(_evidence_case("EJC-02", "jurisdictional_coverage", s1, "unknown", selector_type="inventory_field", key="jurisdictional_coverage", source_id="s1"))

    add(_evidence_case("VER-01", "version", s1, "v2", metadata=[{"source_id": "s1", "version": "v2"}], selector_type="inventory_field", key="version", source_id="s1"))
    add(_evidence_case("VER-02", "version", s1, "unknown", selector_type="inventory_field", key="version", source_id="s1"))
    add(_evidence_case("CUR-01", "currency_state", s1, "current", metadata=[{"source_id": "s1", "currency_state": "current"}], selector_type="inventory_field", key="currency_state", source_id="s1"))
    add(_evidence_case("CUR-02", "currency_state", s1, "unknown", selector_type="inventory_field", key="currency_state", source_id="s1"))

    duplicates = [
        {"source_id": "s1", "media_type": "text/plain", "content": "same"},
        {"source_id": "s2", "media_type": "application/pdf", "content": "same"},
    ]
    add(_evidence_case("DUP-01", "duplicate_source_groups", duplicates, [["s1", "s2"]], key="duplicate_source_groups"))
    add(_evidence_case("DUP-02", "duplicate_source_groups", [{"source_id": "s1", "media_type": "text/plain", "content": "same"}, {"source_id": "s2", "media_type": "text/plain", "content": "same "}], [], key="duplicate_source_groups", note="Near-duplicate bytes should not be silently treated as exact duplicates."))
    add(_evidence_case("DUP-03", "duplicate_source_groups", list(reversed(duplicates)), [["s1", "s2"]], key="duplicate_source_groups"))

    add(_evidence_case("CON-01", "conflict_observations", s1 + s2, [["s1", "s2"]], metadata=[{"source_id": "s1", "conflicts_with": ["s2"]}, {"source_id": "s2"}], key="conflict_observations"))
    add(_evidence_case("CON-02", "conflict_observations", s1, [], metadata=[{"source_id": "s1", "conflicts_with": ["s1"]}], key="conflict_observations", note="A source should not be allowed to conflict with itself."))

    add(_evidence_case("SUP-01", "supersession_observations", s1 + s2, [["s2", "s1"]], metadata=[{"source_id": "s1"}, {"source_id": "s2", "supersedes": ["s1"]}], key="supersession_observations"))
    add(_evidence_case("SUP-02", "supersession_observations", s1, [], metadata=[{"source_id": "s1", "supersedes": ["s1"]}], key="supersession_observations", note="A source should not supersede itself."))

    add(_evidence_case("EVW-01", "verification_world", s1, "closed", task={"verification_world": "closed"}, key="verification_world"))
    add(_evidence_case("EVW-02", "verification_world", s1, "unknown", key="verification_world"))
    add(_evidence_case("SCOPE-01", "corpus_scope", s1, "packet-2025", task={"corpus_scope": "packet-2025"}, key="corpus_scope"))
    add(_evidence_case("SCOPE-02", "corpus_scope", s1, "unknown", key="corpus_scope"))
    add(_evidence_case("COMP-01", "completeness_state", s1, "declared_complete", task={"completeness_state": "declared_complete"}, key="completeness_state"))
    add(_evidence_case("COMP-02", "completeness_state", s1, "unknown", key="completeness_state"))
    add(_evidence_case("GAP-01", "known_gaps", s1, ["missing registry"], task={"known_gaps": ["missing registry"]}, key="known_gaps"))
    gap_inconclusive = _evidence_case("GAP-02", "known_gaps", s1, None, task={"known_gaps": []}, key="known_gaps", note="Input model cannot distinguish 'no gaps declared' from an explicit declaration of zero gaps.")
    gap_inconclusive["expect"] = {"mode": "inconclusive", "value": None}
    add(gap_inconclusive)

    # Preflight: all five compatibility states where relevant plus semantic boundary cases.
    claim_forms = {"expected_evidence_forms": ["document_text", "measurement"]}
    add(_preflight_case("PF-EF-01", "evidence_forms", claim_forms, {"evidence_forms": ["document_text", "measurement"]}, "match"))
    add(_preflight_case("PF-EF-02", "evidence_forms", claim_forms, {"evidence_forms": ["document_text"]}, "partial"))
    add(_preflight_case("PF-EF-03", "evidence_forms", claim_forms, {"evidence_forms": ["registry_entry"]}, "mismatch"))
    add(_preflight_case("PF-EF-04", "evidence_forms", claim_forms, {"evidence_forms": []}, "unknown"))
    add(_preflight_case("PF-EF-05", "evidence_forms", {"expected_evidence_forms": ["unknown"]}, {"evidence_forms": ["document_text"]}, "not_applicable"))

    add(_preflight_case("PF-MISS-01", "missing_expected_evidence_forms", claim_forms, {"evidence_forms": ["document_text", "measurement"]}, "match", expected_evidence_value=[]))
    add(_preflight_case("PF-MISS-02", "missing_expected_evidence_forms", claim_forms, {"evidence_forms": ["document_text"]}, "partial", expected_evidence_value=["measurement"]))
    add(_preflight_case("PF-MISS-03", "missing_expected_evidence_forms", claim_forms, {"evidence_forms": ["registry_entry"]}, "mismatch", expected_evidence_value=["document_text", "measurement"]))
    add(_preflight_case("PF-MISS-04", "missing_expected_evidence_forms", claim_forms, {"evidence_forms": []}, "unknown"))
    add(_preflight_case("PF-MISS-05", "missing_expected_evidence_forms", {"expected_evidence_forms": ["unknown"]}, {"evidence_forms": ["document_text"]}, "not_applicable"))

    add(_preflight_case("PF-TIME-01", "temporal_scope", {"temporal_scope": "2025"}, {"temporal_coverage": ["2025"]}, "match"))
    add(_preflight_case("PF-TIME-02", "temporal_scope", {"temporal_scope": "2025"}, {"temporal_coverage": []}, "unknown"))
    add(_preflight_case("PF-TIME-03", "temporal_scope", {"temporal_scope": "unknown"}, {"temporal_coverage": ["2025"]}, "not_applicable"))
    add(_preflight_case("PF-TIME-04", "temporal_scope", {"temporal_scope": "2025"}, {"temporal_coverage": ["2024-2026"]}, "match", note="A year contained within a declared range should be temporally compatible; exact-string comparison is too brittle."))

    add(_preflight_case("PF-JUR-01", "jurisdiction", {"jurisdiction": "Canada"}, {"jurisdictional_coverage": ["Canada"]}, "match"))
    add(_preflight_case("PF-JUR-02", "jurisdiction", {"jurisdiction": "Canada"}, {"jurisdictional_coverage": []}, "unknown"))
    add(_preflight_case("PF-JUR-03", "jurisdiction", {"jurisdiction": "unknown"}, {"jurisdictional_coverage": ["Canada"]}, "not_applicable"))
    add(_preflight_case("PF-JUR-04", "jurisdiction", {"jurisdiction": "Ontario, Canada"}, {"jurisdictional_coverage": ["Canada"]}, "match", note="A sub-jurisdiction inside national coverage should not be a hard mismatch if this field is to express coverage compatibility."))

    add(_preflight_case("PF-VW-01", "verification_world", {"verification_world": "closed"}, {"verification_world": "closed"}, "match"))
    add(_preflight_case("PF-VW-02", "verification_world", {"verification_world": "closed"}, {"verification_world": "unknown"}, "unknown"))
    add(_preflight_case("PF-VW-03", "verification_world", {"verification_world": "unknown"}, {"verification_world": "closed"}, "not_applicable"))
    add(_preflight_case("PF-VW-04", "verification_world", {"verification_world": "closed"}, {"verification_world": "open"}, "mismatch"))

    add(_preflight_case("PF-AP-01", "corpus_aperture", {}, {"source_inventory": [{"source_id": "s1"}], "corpus_scope": "packet"}, "match"))
    add(_preflight_case("PF-AP-02", "corpus_aperture", {}, {"source_inventory": [], "corpus_scope": "packet"}, "unknown"))
    add(_preflight_case("PF-AP-03", "corpus_aperture", {}, {"source_inventory": [{"source_id": "s1"}], "corpus_scope": "unknown"}, "match", note="V0 aperture means the supplied source universe is inventoried; completeness is separate."))

    add(_preflight_case("PF-COMP-01", "corpus_completeness", {}, {"completeness_state": "declared_complete"}, "match"))
    add(_preflight_case("PF-COMP-02", "corpus_completeness", {}, {"completeness_state": "partial"}, "partial"))
    add(_preflight_case("PF-COMP-03", "corpus_completeness", {}, {"completeness_state": "unknown"}, "unknown"))
    add(_preflight_case("PF-COMP-04", "corpus_completeness", {}, {"completeness_state": "probably complete"}, "unknown"))

    add(_preflight_case("PF-GAP-01", "known_gaps", {}, {"known_gaps": ["missing registry"], "completeness_state": "partial"}, "partial"))
    add(_preflight_case("PF-GAP-02", "known_gaps", {}, {"known_gaps": [], "completeness_state": "declared_complete"}, "match"))
    add(_preflight_case("PF-GAP-03", "known_gaps", {}, {"known_gaps": [], "completeness_state": "unknown"}, "unknown"))

    return c


def _request(raw: dict[str, Any], suffix: str) -> AuthoringRequest:
    return AuthoringRequest(
        handoff_id=f"field-sweep-{suffix}",
        producer_id="paired-gates-field-sweep",
        producer_version="v0",
        work_id=f"work-{suffix}",
        root_id=f"claim-{suffix}",
        root_text=raw.get("root_text", "Field sweep evidence fixture."),
        sources=tuple(SourceRepresentation(**row) for row in raw.get("sources", [])),
        context_source_id=raw.get("context_source_id"),
    )


def _task(raw: dict[str, Any] | None) -> TaskMetadata:
    raw = raw or {}
    return TaskMetadata(
        domain=raw.get("domain", "unknown"),
        verification_world=raw.get("verification_world", "unknown"),
        temporal_scope=raw.get("temporal_scope", "unknown"),
        jurisdiction=raw.get("jurisdiction", "unknown"),
        corpus_scope=raw.get("corpus_scope", "unknown"),
        completeness_state=raw.get("completeness_state", "unknown"),
        known_gaps=tuple(raw.get("known_gaps", [])),
    )


def _source_metadata(raw: list[dict[str, Any]]) -> tuple[SourceMetadata, ...]:
    rows: list[SourceMetadata] = []
    for value in raw:
        item = dict(value)
        item["supersedes"] = tuple(item.get("supersedes", []))
        item["conflicts_with"] = tuple(item.get("conflicts_with", []))
        rows.append(SourceMetadata(**item))
    return tuple(rows)


def _select(profile: dict[str, Any], selector: dict[str, Any]) -> Any:
    kind = selector["type"]
    if kind in {"profile_key", "world_key"}:
        return profile.get(selector["key"])
    if kind == "inventory_field":
        source_id = selector["source_id"]
        matches = [row for row in profile.get("source_inventory", []) if row.get("source_id") == source_id]
        if len(matches) != 1:
            raise ValueError(f"source selector {source_id!r} matched {len(matches)} rows")
        return matches[0].get(selector["key"])
    if kind == "inventory_field_all":
        return [row.get(selector["key"]) for row in profile.get("source_inventory", [])]
    raise ValueError(f"unsupported selector type: {kind}")


def _observation(compatibility: dict[str, Any], field: str) -> dict[str, Any]:
    matches = [row for row in compatibility.get("observations", []) if row.get("field") == field]
    if len(matches) != 1:
        raise ValueError(f"observation selector {field!r} matched {len(matches)} rows")
    return matches[0]


def _compare(actual: Any, expected: Any, mode: str) -> bool:
    if mode == "equals":
        return actual == expected
    if mode == "set_equals":
        return set(actual or []) == set(expected or [])
    if mode == "contains_all":
        return set(expected or []) <= set(actual or [])
    raise ValueError(f"unsupported comparison mode: {mode}")


def _run_case(case: dict[str, Any]) -> dict[str, Any]:
    expectation = case["expect"]
    if expectation["mode"] == "inconclusive":
        return {"case_id": case["case_id"], "field_id": case["field_id"], "result": "INCONCLUSIVE", "expected": expectation, "actual": None, "note": case.get("note", "")}

    raw = case["input"]
    if case["kind"] == "claim":
        profile = build_claim_profile(_request(raw, case["case_id"]), _task(raw.get("task")))
        actual = _select(profile, case["selector"])
        passed = _compare(actual, expectation["value"], expectation["mode"])
    elif case["kind"] == "evidence":
        profile = build_evidence_world_profile(
            _request(raw, case["case_id"]),
            task=_task(raw.get("task")),
            source_metadata=_source_metadata(raw.get("source_metadata", [])),
        )
        actual = _select(profile, case["selector"])
        passed = _compare(actual, expectation["value"], expectation["mode"])
    elif case["kind"] == "preflight":
        compatibility = compare_profiles(raw.get("claim_profile", {}), raw.get("evidence_profile", {}))
        actual = _observation(compatibility, case["selector"]["field"])
        passed = actual["state"] == expectation["value"]
        if passed and "evidence_value" in expectation:
            passed = actual["evidence_value"] == expectation["evidence_value"]
    else:
        raise ValueError(f"unsupported case kind: {case['kind']}")

    return {"case_id": case["case_id"], "field_id": case["field_id"], "result": "PASS" if passed else "FAIL", "expected": expectation, "actual": actual, "note": case.get("note", "")}


def evaluate() -> dict[str, Any]:
    manifest = json.loads(MATRIX_PATH.read_text(encoding="utf-8"))
    cases = frozen_cases()
    registry = build_feature_registry(SUBJECT_COMMIT)
    registry_fields = {row["field_id"] for row in registry["entries"]}
    manifest_fields = set(manifest["fields"])
    case_fields = {row["field_id"] for row in cases}

    if manifest["subject_commit"] != SUBJECT_COMMIT:
        raise ValueError("manifest subject does not match evaluator subject")
    if manifest["field_count"] != 41 or len(registry_fields) != 41:
        raise ValueError("field count drift")
    if manifest["case_count"] != len(cases):
        raise ValueError(f"case count drift: manifest={manifest['case_count']} evaluator={len(cases)}")
    if registry_fields != manifest_fields or registry_fields != case_fields:
        raise ValueError(
            f"field coverage mismatch registry-minus-cases={sorted(registry_fields - case_fields)} cases-minus-registry={sorted(case_fields - registry_fields)}"
        )
    if any(row.get("authority_status") != "IMPLEMENTED_SHADOW" for row in registry["entries"]):
        raise ValueError("baseline sweep requires every field to remain IMPLEMENTED_SHADOW")

    case_results = [_run_case(case) for case in cases]
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in case_results:
        grouped[row["field_id"]].append(row)

    field_results: list[dict[str, Any]] = []
    for field_id in sorted(registry_fields):
        rows = grouped[field_id]
        if any(row["result"] == "FAIL" for row in rows):
            disposition = "FALSIFIED_BASELINE"
        elif any(row["result"] == "INCONCLUSIVE" for row in rows):
            disposition = "INCONCLUSIVE"
        else:
            disposition = "SUPPORTED_BASELINE"
        field_results.append(
            {
                "field_id": field_id,
                "disposition": disposition,
                "case_count": len(rows),
                "pass_count": sum(row["result"] == "PASS" for row in rows),
                "fail_count": sum(row["result"] == "FAIL" for row in rows),
                "inconclusive_count": sum(row["result"] == "INCONCLUSIVE" for row in rows),
                "counterexamples": [row for row in rows if row["result"] != "PASS"],
            }
        )

    summary = {
        state: sum(row["disposition"] == state for row in field_results)
        for state in ("SUPPORTED_BASELINE", "FALSIFIED_BASELINE", "INCONCLUSIVE")
    }
    return {
        "schema": "paired-gates-field-pressure-sweep-result-v0",
        "subject_commit": SUBJECT_COMMIT,
        "field_count": len(field_results),
        "case_count": len(case_results),
        "summary": summary,
        "field_results": field_results,
        "case_results": case_results,
        "authority_effect": "NONE_ALL_FIELDS_REMAIN_IMPLEMENTED_SHADOW",
        "interpretation": "Baseline field pressure-test only. Results do not promote, remove, or repair fields.",
    }


def _markdown(result: dict[str, Any]) -> str:
    lines = [
        "# Paired Gates Field Pressure Sweep V0",
        "",
        f"- subject: `{result['subject_commit']}`",
        f"- fields: {result['field_count']}",
        f"- cases: {result['case_count']}",
        f"- supported baseline: {result['summary']['SUPPORTED_BASELINE']}",
        f"- falsified baseline: {result['summary']['FALSIFIED_BASELINE']}",
        f"- inconclusive: {result['summary']['INCONCLUSIVE']}",
        "",
        "| Field | Disposition | Pass | Fail | Inconclusive |",
        "| --- | --- | ---: | ---: | ---: |",
    ]
    for row in result["field_results"]:
        lines.append(f"| `{row['field_id']}` | `{row['disposition']}` | {row['pass_count']} | {row['fail_count']} | {row['inconclusive_count']} |")
    lines.extend(["", "## Preserved counterexamples", ""])
    for row in result["field_results"]:
        if not row["counterexamples"]:
            continue
        lines.extend([f"### `{row['field_id']}`", ""])
        for case in row["counterexamples"]:
            lines.append(f"- `{case['case_id']}` — **{case['result']}**")
            lines.append(f"  - expected: `{json.dumps(case['expected'], sort_keys=True)}`")
            lines.append(f"  - observed: `{json.dumps(case['actual'], sort_keys=True)}`")
            if case.get("note"):
                lines.append(f"  - note: {case['note']}")
        lines.append("")
    lines.extend(["## Authority", "", "No authority promotion is authorized by this sweep. Every field remains `IMPLEMENTED_SHADOW`.", ""])
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json-out", required=True)
    parser.add_argument("--markdown-out", required=True)
    args = parser.parse_args()

    result = evaluate()
    json_path = Path(args.json_out)
    markdown_path = Path(args.markdown_out)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    markdown_path.write_text(_markdown(result), encoding="utf-8")
    print(json.dumps(result["summary"], sort_keys=True))


if __name__ == "__main__":
    main()
