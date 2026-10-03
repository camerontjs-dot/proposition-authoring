"""Compare a reviewer's copied fields with the certificate.

Order does not matter. The comparison does not judge meaning. A copy that
adds a role the certificate does not contain is a mismatch.
"""

from __future__ import annotations

from collections import Counter


def _span_exact(root: str, span: dict) -> bool:
    return span["text"] == root[span["start"] : span["end"]]


def iter_source_spans(certificate: dict):
    for predicate in certificate["predicates"]:
        yield predicate["span"]
        for role in predicate["roles"]:
            yield role["span"]
    for reading in certificate["readings"]:
        for binding in reading["scope_bindings"]:
            yield binding["span"]
    for obligation in certificate["obligations"]:
        for span in obligation["source_spans"]:
            yield span
    for row in certificate["completeness"]["material_span_ledger"]:
        yield row["span"]


def spans_exact(certificate: dict) -> bool:
    root = certificate["root"]["text"]
    return all(_span_exact(root, span) for span in iter_source_spans(certificate))


def expected_inspection(certificate: dict) -> dict:
    roles = []
    for predicate in certificate["predicates"]:
        for role in predicate["roles"]:
            roles.append((predicate["surface"], role["role"], role["surface"]))
    bindings = []
    reading_ids = []
    operators = []
    for reading in certificate["readings"]:
        if reading["status"] != "MATERIALLY_LIVE":
            continue
        reading_ids.append(reading["reading_id"])
        operators.append((reading["reading_id"], reading["operator"]))
        for binding in reading["scope_bindings"]:
            bindings.append(
                (
                    reading["reading_id"],
                    binding["kind"],
                    binding["surface"],
                    tuple(sorted(binding["targets"])),
                )
            )
    descriptions = [
        obligation["description"]
        for obligation in certificate["obligations"]
        if obligation["kind"] == "MODALITY"
    ]
    return {
        "roles": Counter(roles),
        "live_bindings": Counter(bindings),
        "live_reading_ids": Counter(reading_ids),
        "live_operators": Counter(operators),
        "modality_descriptions": Counter(descriptions),
        "spans_exact": spans_exact(certificate),
    }


def _as_counter(items, key) -> Counter | None:
    if not isinstance(items, list):
        return None
    values = []
    for item in items:
        if not isinstance(item, dict):
            return None
        try:
            values.append(key(item))
        except (KeyError, TypeError):
            return None
    return Counter(values)


def observed_inspection(payload: dict) -> dict | None:
    if not isinstance(payload, dict) or not isinstance(payload.get("spans_exact"), bool):
        return None
    roles = _as_counter(
        payload.get("roles"),
        lambda item: (item["predicate_surface"], item["role"], item["surface"]),
    )
    bindings = _as_counter(
        payload.get("live_bindings"),
        lambda item: (
            item["reading_id"],
            item["kind"],
            item["surface"],
            tuple(sorted(item["targets"])),
        ),
    )
    reading_ids = payload.get("live_reading_ids")
    operators = _as_counter(
        payload.get("live_operators"),
        lambda item: (item["reading_id"], item["operator"]),
    )
    descriptions = payload.get("modality_descriptions")
    if (
        roles is None
        or bindings is None
        or operators is None
        or not isinstance(reading_ids, list)
        or not all(isinstance(item, str) for item in reading_ids)
        or not isinstance(descriptions, list)
        or not all(isinstance(item, str) for item in descriptions)
    ):
        return None
    for item in payload.get("live_bindings", []):
        if not isinstance(item.get("targets"), list) or not all(
            isinstance(target, str) for target in item["targets"]
        ):
            return None
    return {
        "roles": roles,
        "live_bindings": bindings,
        "live_reading_ids": Counter(reading_ids),
        "live_operators": operators,
        "modality_descriptions": Counter(descriptions),
        "spans_exact": payload["spans_exact"],
    }


def inspection_match(certificate: dict, payload: dict) -> bool:
    observed = observed_inspection(payload)
    if observed is None:
        return False
    return observed == expected_inspection(certificate)
