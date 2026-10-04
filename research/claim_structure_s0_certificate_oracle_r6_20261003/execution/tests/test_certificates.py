"""Mechanical checks for the S0-R6 certificate packet."""

from __future__ import annotations

import json
from pathlib import Path

from s0r6.build import build_certificate, resolve_requirements
from s0r6.mutate import MUTATION_NAMES, apply_mutation
from s0r6.specs import PREDECESSOR_ROOTS, all_specs, calibration_specs, decisive_specs
from s0r6.validate import load_json, validate_certificate

ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = ROOT / "CERTIFICATE-SCHEMA.json"

MINIMUM_FAMILIES = {
    "atomic": 2,
    "all_of": 2,
    "conjunction": 2,
    "disjunction": 2,
    "attribution_scope": 2,
    "negation_scope": 2,
    "temporal_location_scope": 2,
    "modality_condition": 2,
    "ambiguous": 2,
}

HARD_CALIBRATION = {
    "s0r6-cal-kim": ["drop_subject", "drop_object", "drop_qualifier", "alter_span", "invent_proposition"],
    "s0r6-cal-or": ["or_to_and"],
    "s0r6-cal-amb": ["drop_live_reading", "drop_negation"],
    "s0r6-cal-attr": ["reattach_attribution"],
    "s0r6-cal-must": ["change_modality"],
}


def setup_module():
    global SCHEMA
    SCHEMA = load_json(SCHEMA_PATH)


def _built():
    built = []
    for spec in all_specs():
        certificate = build_certificate(spec)
        requirements = resolve_requirements(spec)
        built.append((spec, certificate, requirements))
    return built


def test_known_goods_pass():
    for spec, certificate, requirements in _built():
        errors = validate_certificate(certificate, SCHEMA, requirements)
        assert errors == [], f"{spec['certificate_id']}: {errors}"


def test_family_minimums_and_predecessor_exclusion():
    counts = {family: 0 for family in MINIMUM_FAMILIES}
    roots = []
    for spec in decisive_specs():
        roots.append(spec["text"])
        for family in spec["families"]:
            if family in counts:
                counts[family] += 1
        assert spec["text"] not in PREDECESSOR_ROOTS
        assert spec["packet"] == "decisive"
    assert len(roots) == len(set(roots))
    missing = {family: count for family, count in counts.items() if count < MINIMUM_FAMILIES[family]}
    assert missing == {}
    assert len(decisive_specs()) >= 8
    assert {spec["certificate_id"] for spec in calibration_specs()} == set(HARD_CALIBRATION)


def test_applicable_hard_mutations_fail():
    schema = SCHEMA
    accepted = []
    for spec, certificate, requirements in _built():
        for name in MUTATION_NAMES:
            mutated = apply_mutation(certificate, name)
            if mutated is None:
                continue
            errors = validate_certificate(mutated, schema, requirements)
            if not errors:
                accepted.append(f"{spec['certificate_id']} {name}")
            assert mutated["root"]["text"] == certificate["root"]["text"]
            assert mutated["certificate_id"] != certificate["certificate_id"]
    assert accepted == []


def test_required_calibration_mutations_exist_and_fail():
    by_id = {}
    for spec, certificate, requirements in _built():
        by_id[spec["certificate_id"]] = (certificate, requirements)
    for certificate_id, names in HARD_CALIBRATION.items():
        certificate, requirements = by_id[certificate_id]
        for name in names:
            mutated = apply_mutation(certificate, name)
            assert mutated is not None, f"{certificate_id} {name} was not applicable"
            errors = validate_certificate(mutated, SCHEMA, requirements)
            assert errors, f"{certificate_id} {name} was accepted: no errors"


def test_promoting_peter_rejected_reading_exceeds_the_external_maximum():
    spec = next(item for item in decisive_specs() if item["claim_id"] == "n02")
    certificate = build_certificate(spec)
    requirements = resolve_requirements(spec)
    for reading in certificate["readings"]:
        if reading["reading_id"] == "rd-rejected":
            reading["status"] = "MATERIALLY_LIVE"
    errors = validate_certificate(certificate, SCHEMA, requirements)
    assert any("at most 1" in error for error in errors)


def test_packet_round_trip_is_deterministic():
    first = json.dumps([build_certificate(spec) for spec in all_specs()], sort_keys=True)
    second = json.dumps([build_certificate(spec) for spec in all_specs()], sort_keys=True)
    assert first == second
