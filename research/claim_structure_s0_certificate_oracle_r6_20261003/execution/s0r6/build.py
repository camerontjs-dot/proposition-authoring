"""Build source-bound certificates from explicit span specs.

A spec is not a certificate. This module only copies declared surfaces onto
exact root offsets, then fills the completeness ledger. It does not decide
what a sentence means.
"""

from __future__ import annotations

from s0r6.validate import WORD_RE, sha256_text

SCHEMA_ID = "claim-structure-scope-obligation-certificate-v0"

OBLIGATION_KIND = {
    "NEGATION": "NEGATION",
    "MODALITY": "MODALITY",
    "ATTRIBUTION": "ATTRIBUTION",
    "TEMPORAL": "TEMPORAL",
    "LOCATION": "LOCATION",
    "JURISDICTION": "JURISDICTION",
    "QUANTIFIER": "QUANTITY",
    "CONDITION": "CONDITION",
    "EXCEPTION": "OTHER",
    "OTHER": "OTHER",
}


def locate(text: str, surface: str, occurrence: int = 0) -> dict:
    if not surface or surface != surface.strip():
        raise ValueError(f"surface must be a non-empty exact substring, got {surface!r}")
    start = 0
    found = 0
    while True:
        index = text.find(surface, start)
        if index < 0:
            raise ValueError(
                f"{surface!r} occurrence {occurrence} not found as a whole span in {text!r}"
            )
        end = index + len(surface)
        before_ok = index == 0 or not _continues_word(text[index - 1])
        after_ok = end == len(text) or not _continues_word(text[end])
        if before_ok and after_ok:
            if found == occurrence:
                return {"start": index, "end": end, "text": text[index:end]}
            found += 1
        start = index + 1


def _continues_word(char: str) -> bool:
    return char.isalnum() or char in {"'", "’"}


def build_certificate(spec: dict) -> dict:
    root = spec["text"]
    predicates = []
    objects: list[tuple[str, dict]] = []
    for predicate in spec["predicates"]:
        span = locate(root, predicate["surface"], predicate.get("occurrence", 0))
        roles = []
        for role in predicate["roles"]:
            role_span = locate(root, role["surface"], role.get("occurrence", 0))
            roles.append(
                {
                    "role_id": role["id"],
                    "role": role["role"],
                    "surface": role_span["text"],
                    "span": role_span,
                }
            )
            objects.append((role["id"], role_span))
        predicates.append(
            {
                "predicate_id": predicate["id"],
                "surface": span["text"],
                "span": span,
                "roles": roles,
            }
        )
        objects.append((predicate["id"], span))

    readings = []
    for reading in spec["readings"]:
        propositions = []
        for proposition in reading["propositions"]:
            propositions.append(
                {
                    "proposition_id": proposition["id"],
                    "text": proposition["text"],
                    "predicate_ids": list(proposition["predicates"]),
                }
            )
        bindings = []
        for binding in reading.get("bindings", []):
            span = locate(root, binding["surface"], binding.get("occurrence", 0))
            bindings.append(
                {
                    "binding_id": binding["id"],
                    "kind": binding["kind"],
                    "surface": span["text"],
                    "span": span,
                    "targets": list(binding["targets"]),
                }
            )
            objects.append((binding["id"], span))
        readings.append(
            {
                "reading_id": reading["id"],
                "operator": reading["operator"],
                "propositions": propositions,
                "scope_bindings": bindings,
                "status": reading["status"],
            }
        )

    obligations = []
    for reading in spec["readings"]:
        if reading["status"] not in {"MATERIALLY_LIVE", "WARRANTED"}:
            continue
        for binding in reading.get("bindings", []):
            span = locate(root, binding["surface"], binding.get("occurrence", 0))
            obligations.append(
                {
                    "obligation_id": f"ob-{binding['id']}",
                    "kind": OBLIGATION_KIND[binding["kind"]],
                    "description": binding.get(
                        "description",
                        f"{binding['kind']} span {binding['surface']!r} is bound in {reading['id']}.",
                    ),
                    "source_spans": [span],
                    "must_be_preserved_in": [reading["id"]],
                }
            )
            objects.append((f"ob-{binding['id']}", span))
    for predicate in spec["predicates"]:
        span = locate(root, predicate["surface"], predicate.get("occurrence", 0))
        obligations.append(
            {
                "obligation_id": f"ob-{predicate['id']}",
                "kind": "PREDICATE",
                "description": predicate.get(
                    "description",
                    f"Predicate {predicate['surface']!r} is part of the certificate.",
                ),
                "source_spans": [span],
                "must_be_preserved_in": _predicate_readings(spec, predicate["id"]),
            }
        )
        objects.append((f"ob-{predicate['id']}", span))
        for role in predicate["roles"]:
            role_span = locate(root, role["surface"], role.get("occurrence", 0))
            obligations.append(
                {
                    "obligation_id": f"ob-{role['id']}",
                    "kind": "ROLE_BINDING",
                    "description": role.get(
                        "description",
                        f"{role['role']} {role['surface']!r} is bound to {predicate['surface']!r}.",
                    ),
                    "source_spans": [role_span],
                    "must_be_preserved_in": _predicate_readings(spec, predicate["id"]),
                }
            )
            objects.append((f"ob-{role['id']}", role_span))
    for extra in spec.get("obligations", []):
        surfaces = extra["surfaces"] if isinstance(extra["surfaces"], list) else [extra["surfaces"]]
        occurrences = extra.get("occurrences", [0] * len(surfaces))
        spans = [
            locate(root, surface, occurrence)
            for surface, occurrence in zip(surfaces, occurrences)
        ]
        obligations.append(
            {
                "obligation_id": extra["id"],
                "kind": extra["kind"],
                "description": extra["description"],
                "source_spans": spans,
                "must_be_preserved_in": list(extra["preserve"]),
            }
        )
        for span in spans:
            objects.append((extra["id"], span))

    certificate = {
        "schema": SCHEMA_ID,
        "certificate_id": spec["certificate_id"],
        "root": {
            "claim_id": spec["claim_id"],
            "text": root,
            "text_sha256": sha256_text(root),
        },
        "source_provenance": spec["source_provenance"],
        "classification": spec["classification"],
        "predicates": predicates,
        "readings": readings,
        "obligations": obligations,
        "completeness": {
            "material_span_ledger": _strict_ledger(root, objects),
            "unassigned_material_spans": [],
            "all_predicates_bound": True,
            "all_roles_bound": True,
            "all_operators_bound": True,
            "all_material_qualifiers_bound": True,
            "all_live_readings_recorded": True,
        },
        "review_status": {
            "state": "FROZEN_PENDING_REVIEW",
            "independent_reviews_required": 2,
            "adjudication_required": False,
        },
    }
    return certificate


def resolve_requirements(spec: dict) -> dict:
    requirements = {
        "min_live_readings": spec.get("requirements", {}).get("min_live_readings"),
        "max_live_readings": spec.get("requirements", {}).get("max_live_readings"),
        "required_roles": list(spec.get("requirements", {}).get("required_roles", [])),
        "required_predicate_surfaces": list(
            spec.get("requirements", {}).get("required_predicate_surfaces", [])
        ),
        "required_bindings": [],
        "modality_descriptions": list(spec.get("requirements", {}).get("modality_descriptions", [])),
    }
    root = spec["text"]
    for binding in spec.get("requirements", {}).get("required_bindings", []):
        resolved = dict(binding)
        if "occurrence" in resolved:
            span = locate(root, resolved["surface"], resolved.pop("occurrence"))
            resolved["start"] = span["start"]
        requirements["required_bindings"].append(resolved)
    requirements = {key: value for key, value in requirements.items() if value is not None}
    return requirements


def _predicate_readings(spec: dict, predicate_id: str) -> list[str]:
    found = []
    for reading in spec["readings"]:
        if reading["status"] not in {"MATERIALLY_LIVE", "WARRANTED"}:
            continue
        for proposition in reading["propositions"]:
            if predicate_id in proposition["predicates"] and reading["id"] not in found:
                found.append(reading["id"])
    if not found:
        raise ValueError(f"predicate {predicate_id} is not used by a live reading")
    return found


def _strict_ledger(root: str, objects: list[tuple[str, dict]]) -> list[dict]:
    ledger = []
    cursor = 0
    for match in WORD_RE.finditer(root):
        if match.start() > cursor:
            ledger.append(_gap(root, cursor, match.start()))
        refs = _covering(objects, match.start(), match.end())
        if not refs:
            raise ValueError(f"uncovered word {match.group(0)!r} in {root!r}")
        ledger.append(
            {
                "span": {
                    "start": match.start(),
                    "end": match.end(),
                    "text": root[match.start() : match.end()],
                },
                "semantic_status": "ACCOUNTED_MATERIAL",
                "object_refs": refs,
            }
        )
        cursor = match.end()
    if cursor < len(root):
        ledger.append(_gap(root, cursor, len(root)))
    return ledger


def lenient_ledger(root: str, objects: list[tuple[str, dict]]) -> list[dict]:
    """Rebuild a ledger that hides dropped spans as non-material."""
    ledger = []
    cursor = 0
    for match in WORD_RE.finditer(root):
        if match.start() > cursor:
            ledger.append(_gap(root, cursor, match.start()))
        refs = _covering(objects, match.start(), match.end())
        ledger.append(
            {
                "span": {
                    "start": match.start(),
                    "end": match.end(),
                    "text": root[match.start() : match.end()],
                },
                "semantic_status": "ACCOUNTED_MATERIAL" if refs else "ACCOUNTED_NON_MATERIAL",
                "object_refs": refs,
            }
        )
        cursor = match.end()
    if cursor < len(root):
        ledger.append(_gap(root, cursor, len(root)))
    return ledger


def _gap(root: str, start: int, end: int) -> dict:
    return {
        "span": {"start": start, "end": end, "text": root[start:end]},
        "semantic_status": "PUNCTUATION_OR_CONNECTIVE",
        "object_refs": [],
    }


def _covering(objects: list[tuple[str, dict]], start: int, end: int) -> list[str]:
    refs = []
    for ref, span in objects:
        if span["start"] <= start and span["end"] >= end and ref not in refs:
            refs.append(ref)
    return refs


def certificate_objects(cert: dict) -> list[tuple[str, dict]]:
    objects = []
    for predicate in cert["predicates"]:
        objects.append((predicate["predicate_id"], predicate["span"]))
        for role in predicate["roles"]:
            objects.append((role["role_id"], role["span"]))
    for reading in cert["readings"]:
        for binding in reading["scope_bindings"]:
            objects.append((binding["binding_id"], binding["span"]))
    for obligation in cert["obligations"]:
        for span in obligation["source_spans"]:
            objects.append((obligation["obligation_id"], span))
    return objects
