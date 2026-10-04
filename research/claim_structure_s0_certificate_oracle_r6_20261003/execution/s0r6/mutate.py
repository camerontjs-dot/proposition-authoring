"""Hostile certificate mutations.

Each function returns a new certificate or None when the mutation is not
applicable. The admitted original is never edited. A mutation rebuilds the
ledger and sets the completeness flags true, so a rejection has to come from
the missing role, operator, reading, span, or external requirement.
"""

from __future__ import annotations

import copy

from s0r6.build import certificate_objects, lenient_ledger

MUTATION_NAMES = (
    "drop_subject",
    "drop_object",
    "drop_qualifier",
    "reattach_qualifier",
    "reattach_attribution",
    "drop_negation",
    "change_modality",
    "or_to_and",
    "drop_live_reading",
    "invent_proposition",
    "alter_span",
    "delete_predicate",
)

QUALIFIER_KINDS = {
    "TEMPORAL",
    "LOCATION",
    "CONDITION",
    "EXCEPTION",
    "QUANTIFIER",
    "JURISDICTION",
    "OTHER",
}
LIVE = {"MATERIALLY_LIVE", "WARRANTED"}


def apply_mutation(cert: dict, name: str) -> dict | None:
    mutated = copy.deepcopy(cert)
    changed = _MUTATIONS[name](mutated)
    if changed is None:
        return None
    _seal(changed)
    changed["certificate_id"] = f"{cert['certificate_id']}--{name}"
    return changed


def applicable_mutations(cert: dict) -> list[str]:
    return [name for name in MUTATION_NAMES if apply_mutation(cert, name) is not None]


def _seal(cert: dict) -> None:
    cert["completeness"]["material_span_ledger"] = lenient_ledger(
        cert["root"]["text"], certificate_objects(cert)
    )
    cert["completeness"]["unassigned_material_spans"] = []
    for flag in (
        "all_predicates_bound",
        "all_roles_bound",
        "all_operators_bound",
        "all_material_qualifiers_bound",
        "all_live_readings_recorded",
    ):
        cert["completeness"][flag] = True


def _drop_role(cert: dict, role_name: str) -> dict | None:
    for predicate in cert["predicates"]:
        for index, role in enumerate(predicate["roles"]):
            if role["role"] == role_name:
                del predicate["roles"][index]
                return cert
    return None


def _drop_subject(cert: dict) -> dict | None:
    return _drop_role(cert, "subject")


def _drop_object(cert: dict) -> dict | None:
    return _drop_role(cert, "object")


def _drop_qualifier(cert: dict) -> dict | None:
    for reading in cert["readings"]:
        if reading["status"] not in LIVE:
            continue
        for index, binding in enumerate(reading["scope_bindings"]):
            if binding["kind"] not in QUALIFIER_KINDS:
                continue
            span = binding["span"]
            del reading["scope_bindings"][index]
            cert["obligations"] = [
                obligation
                for obligation in cert["obligations"]
                if not obligation["source_spans"] or any(item != span for item in obligation["source_spans"])
            ]
            return cert
    return None


def _reattach_qualifier(cert: dict) -> dict | None:
    for reading in cert["readings"]:
        if reading["status"] not in LIVE:
            continue
        propositions = reading["propositions"]
        if len(propositions) < 2:
            continue
        ids = [proposition["proposition_id"] for proposition in propositions]
        for binding in reading["scope_bindings"]:
            if binding["kind"] not in QUALIFIER_KINDS:
                continue
            current = list(binding["targets"])
            alternatives = [proposition_id for proposition_id in ids if proposition_id not in current]
            if alternatives:
                binding["targets"] = [alternatives[0]]
                return cert
            if len(current) > 1:
                binding["targets"] = [current[-1]]
                return cert
    return None


def _reattach_attribution(cert: dict) -> dict | None:
    for reading in cert["readings"]:
        if reading["status"] not in LIVE:
            continue
        propositions = reading["propositions"]
        if len(propositions) < 2:
            continue
        by_id = {proposition["proposition_id"]: proposition for proposition in propositions}
        for binding in reading["scope_bindings"]:
            if binding["kind"] != "ATTRIBUTION":
                continue
            current_words = set()
            for proposition_id in binding["targets"]:
                current_words.update(_words(by_id[proposition_id]["text"]))
            for proposition in propositions:
                if proposition["proposition_id"] in binding["targets"] and len(binding["targets"]) == 1:
                    continue
                if _words(proposition["text"]) < current_words:
                    binding["targets"] = [proposition["proposition_id"]]
                    return cert
    return None


def _drop_negation(cert: dict) -> dict | None:
    removed = False
    for reading in cert["readings"]:
        kept = []
        for binding in reading["scope_bindings"]:
            if binding["kind"] == "NEGATION":
                removed = True
            else:
                kept.append(binding)
        reading["scope_bindings"] = kept
    cert["obligations"] = [
        obligation
        for obligation in cert["obligations"]
        if obligation["kind"] != "NEGATION"
    ]
    return cert if removed else None


def _change_modality(cert: dict) -> dict | None:
    changed = False
    for obligation in cert["obligations"]:
        if obligation["kind"] != "MODALITY":
            continue
        folded = obligation["description"].casefold()
        if "permission" in folded and "necessity" not in folded:
            obligation["description"] = "The modal is necessity."
        else:
            obligation["description"] = "The modal is permission."
        changed = True
    return cert if changed else None


def _or_to_and(cert: dict) -> dict | None:
    changed = False
    for reading in cert["readings"]:
        if reading["status"] not in LIVE:
            continue
        if reading["operator"] == "ANY_OF":
            reading["operator"] = "ALL_OF"
            changed = True
        elif reading["operator"] == "ALL_OF":
            reading["operator"] = "ANY_OF"
            changed = True
    return cert if changed else None


def _drop_live_reading(cert: dict) -> dict | None:
    live_indexes = [
        index for index, reading in enumerate(cert["readings"]) if reading["status"] == "MATERIALLY_LIVE"
    ]
    if len(live_indexes) < 2:
        return None
    del cert["readings"][live_indexes[0]]
    return cert


def _invent_proposition(cert: dict) -> dict | None:
    for reading in cert["readings"]:
        if reading["status"] not in LIVE:
            continue
        predicate_ids = list(reading["propositions"][0]["predicate_ids"])
        reading["propositions"].append(
            {
                "proposition_id": f"{reading['reading_id']}-invented",
                "text": "a parade",
                "predicate_ids": predicate_ids,
            }
        )
        return cert
    return None


def _alter_span(cert: dict) -> dict | None:
    predicate = cert["predicates"][0]
    predicate["span"]["text"] = "NOT-THE-SOURCE"
    return cert


def _delete_predicate(cert: dict) -> dict | None:
    if not cert["predicates"]:
        return None
    removed = cert["predicates"].pop(0)
    remaining = [predicate["predicate_id"] for predicate in cert["predicates"]]
    replacement = remaining[0] if remaining else "deleted-predicate"
    for reading in cert["readings"]:
        for proposition in reading["propositions"]:
            proposition["predicate_ids"] = [
                predicate_id
                for predicate_id in proposition["predicate_ids"]
                if predicate_id != removed["predicate_id"]
            ] or [replacement]
    return cert


def _words(text: str) -> set[str]:
    return {part.casefold() for part in text.split()}


_MUTATIONS = {
    "drop_subject": _drop_subject,
    "drop_object": _drop_object,
    "drop_qualifier": _drop_qualifier,
    "reattach_qualifier": _reattach_qualifier,
    "reattach_attribution": _reattach_attribution,
    "drop_negation": _drop_negation,
    "change_modality": _change_modality,
    "or_to_and": _or_to_and,
    "drop_live_reading": _drop_live_reading,
    "invent_proposition": _invent_proposition,
    "alter_span": _alter_span,
    "delete_predicate": _delete_predicate,
}
