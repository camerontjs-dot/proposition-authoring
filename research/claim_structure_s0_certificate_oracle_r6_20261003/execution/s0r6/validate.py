"""Mechanical validator for source-bound scope/obligation certificates.

Mechanical acceptance is not semantic correctness. Admission still requires
independent review. These checks are the frozen structural half of the
S0-R6 protocol.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from jsonschema import Draft202012Validator

WORD_RE = re.compile(r"[A-Za-z0-9]+(?:['’][A-Za-z0-9]+)?")
NEGATION_WORDS = {"not", "never", "no", "n't", "n’t"}
MODAL_WORDS = {"must", "may", "might", "should", "would", "could", "can", "ought"}
CONJUNCTION_SURFACES = {"and"}
DISJUNCTION_SURFACES = {"or", "either"}
LIVE_STATUSES = {"MATERIALLY_LIVE", "WARRANTED"}


def sha256_text(text: str) -> str:
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    return f"sha256:{digest}"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _span_errors(span, text: str, label: str) -> list[str]:
    errors = []
    if not isinstance(span, dict):
        return [f"{label}: span is not an object"]
    start, end = span.get("start"), span.get("end")
    surface = span.get("text")
    if not isinstance(start, int) or not isinstance(end, int):
        return [f"{label}: span offsets are not integers"]
    if not isinstance(surface, str) or not surface:
        return [f"{label}: span text is empty"]
    if start < 0 or end <= start or end > len(text):
        errors.append(f"{label}: span [{start}:{end}] is outside the root")
        return errors
    actual = text[start:end]
    if actual != surface:
        errors.append(
            f"{label}: span text {surface!r} does not reproduce root[{start}:{end}]={actual!r}"
        )
    return errors


def _ids(items, key):
    found = []
    errors = []
    for item in items:
        value = item.get(key)
        if not isinstance(value, str) or not value:
            errors.append(f"missing {key}")
            continue
        if value in found:
            errors.append(f"duplicate {key} {value}")
        found.append(value)
    return found, errors


def _word_set(text: str) -> set[str]:
    return {match.group(0).casefold() for match in WORD_RE.finditer(text)}


def _is_negation_word(word: str) -> bool:
    folded = word.casefold()
    return (
        folded in NEGATION_WORDS
        or folded.endswith("n't")
        or folded.endswith("n’t")
        or folded.endswith("’t")
    )


def _covers(span, start: int, end: int) -> bool:
    return span["start"] <= start and span["end"] >= end


def _live_readings(cert) -> list[dict]:
    return [reading for reading in cert["readings"] if reading["status"] in LIVE_STATUSES]


def validate_certificate(
    cert: dict,
    schema: dict,
    requirements: dict | None = None,
    *,
    require_complete: bool = True,
) -> list[str]:
    errors: list[str] = []
    validator = Draft202012Validator(schema)
    for error in sorted(validator.iter_errors(cert), key=lambda item: list(item.path)):
        errors.append(f"schema: {error.message}")
    if errors:
        return errors

    root = cert["root"]["text"]
    expected_hash = sha256_text(root)
    if cert["root"]["text_sha256"] != expected_hash:
        errors.append("root text_sha256 does not match the UTF-8 root text")
    context = cert["root"].get("authorized_context")
    context_hash = cert["root"].get("authorized_context_sha256")
    if context is None and context_hash is not None:
        errors.append("authorized context hash is present without context text")
    if isinstance(context, str):
        if context_hash != sha256_text(context):
            errors.append("authorized context hash does not match the context text")

    predicate_ids, id_errors = _ids(cert["predicates"], "predicate_id")
    errors.extend(id_errors)
    role_ids: list[str] = []
    objects: list[tuple[str, dict]] = []
    predicates_by_id = {}
    for predicate in cert["predicates"]:
        pid = predicate["predicate_id"]
        predicates_by_id[pid] = predicate
        errors.extend(_span_errors(predicate["span"], root, f"predicate {pid}"))
        if predicate["surface"] != predicate["span"]["text"]:
            errors.append(f"predicate {pid}: surface does not equal span text")
        objects.append((pid, predicate["span"]))
        role_list, role_errors = _ids(predicate["roles"], "role_id")
        errors.extend(role_errors)
        for role in predicate["roles"]:
            rid = role["role_id"]
            if rid in role_ids:
                errors.append(f"duplicate role_id {rid}")
            role_ids.append(rid)
            errors.extend(_span_errors(role["span"], root, f"role {rid}"))
            if role["surface"] != role["span"]["text"]:
                errors.append(f"role {rid}: surface does not equal span text")
            objects.append((rid, role["span"]))

    reading_ids, reading_errors = _ids(cert["readings"], "reading_id")
    errors.extend(reading_errors)
    proposition_ids: list[str] = []
    propositions_by_id = {}
    binding_ids: list[str] = []
    for reading in cert["readings"]:
        prop_ids, prop_errors = _ids(reading["propositions"], "proposition_id")
        errors.extend(prop_errors)
        for proposition in reading["propositions"]:
            prop_id = proposition["proposition_id"]
            if prop_id in proposition_ids:
                errors.append(f"duplicate proposition_id {prop_id}")
            proposition_ids.append(prop_id)
            propositions_by_id[prop_id] = proposition
            for predicate_id in proposition["predicate_ids"]:
                if predicate_id not in predicates_by_id:
                    errors.append(
                        f"proposition {prop_id} references missing predicate {predicate_id}"
                    )
            extra_words = _word_set(proposition["text"]) - _word_set(root)
            if extra_words:
                errors.append(
                    f"proposition {prop_id} introduces words absent from the root: {sorted(extra_words)}"
                )
        local_props = {proposition["proposition_id"] for proposition in reading["propositions"]}
        bind_ids, bind_errors = _ids(reading["scope_bindings"], "binding_id")
        errors.extend(bind_errors)
        for binding in reading["scope_bindings"]:
            bid = binding["binding_id"]
            if bid in binding_ids:
                errors.append(f"duplicate binding_id {bid}")
            binding_ids.append(bid)
            errors.extend(_span_errors(binding["span"], root, f"binding {bid}"))
            if binding["surface"] != binding["span"]["text"]:
                errors.append(f"binding {bid}: surface does not equal span text")
            objects.append((bid, binding["span"]))
            for target in binding["targets"]:
                if target not in local_props:
                    errors.append(
                        f"binding {bid} target {target} is not a proposition in {reading['reading_id']}"
                    )

    obligation_ids, obligation_errors = _ids(cert["obligations"], "obligation_id")
    errors.extend(obligation_errors)
    known_refs = set(predicate_ids) | set(role_ids) | set(reading_ids) | set(proposition_ids)
    known_refs |= set(binding_ids) | set(obligation_ids)
    for obligation in cert["obligations"]:
        oid = obligation["obligation_id"]
        for span in obligation["source_spans"]:
            errors.extend(_span_errors(span, root, f"obligation {oid}"))
            objects.append((oid, span))
        for ref in obligation["must_be_preserved_in"]:
            if ref not in reading_ids and ref not in proposition_ids:
                errors.append(f"obligation {oid} preserves missing reference {ref}")
        surface = " ".join(span["text"] for span in obligation["source_spans"]).casefold()
        kind = obligation["kind"]
        if kind == "CONJUNCTION" and not any(token in surface.split() for token in CONJUNCTION_SURFACES):
            errors.append(f"obligation {oid}: CONJUNCTION span is not 'and'")
        if kind == "DISJUNCTION" and not any(token in surface.split() for token in DISJUNCTION_SURFACES):
            errors.append(f"obligation {oid}: DISJUNCTION span is not 'or' or 'either'")

    errors.extend(_classification_errors(cert))
    errors.extend(_operator_surface_errors(cert))
    errors.extend(_ledger_errors(cert, objects, require_complete))
    errors.extend(_lexical_attachment_errors(cert, root))
    if requirements:
        errors.extend(_requirement_errors(cert, requirements))
    if require_complete:
        completeness = cert["completeness"]
        for flag in (
            "all_predicates_bound",
            "all_roles_bound",
            "all_operators_bound",
            "all_material_qualifiers_bound",
            "all_live_readings_recorded",
        ):
            if completeness[flag] is not True:
                errors.append(f"completeness.{flag} is not true")
        if completeness["unassigned_material_spans"]:
            errors.append("complete certificate has unassigned material spans")
    return errors


def _classification_errors(cert: dict) -> list[str]:
    classification = cert["classification"]
    live = _live_readings(cert)
    materially_live = [reading for reading in cert["readings"] if reading["status"] == "MATERIALLY_LIVE"]
    errors = []
    if classification == "AMBIGUOUS":
        if len(materially_live) < 2:
            errors.append("AMBIGUOUS certificate has fewer than two materially live readings")
    elif len(live) != 1:
        errors.append(f"{classification} certificate must have exactly one live or warranted reading")
        return errors
    else:
        reading = live[0]
        operator = reading["operator"]
        propositions = reading["propositions"]
        if classification == "ATOMIC":
            if operator != "ATOMIC" or len(propositions) != 1:
                errors.append("ATOMIC classification requires one ATOMIC reading with one proposition")
        elif classification == "ALL_OF":
            if operator != "ALL_OF" or len(propositions) < 2:
                errors.append("ALL_OF classification requires one ALL_OF reading with at least two propositions")
        elif classification == "NON_ALL_OF":
            if operator not in {"ANY_OF", "IF_THEN", "SCOPED", "OTHER"}:
                errors.append("NON_ALL_OF classification requires a non-conjunctive operator")
            if operator == "ANY_OF" and len(propositions) < 2:
                errors.append("ANY_OF requires at least two propositions")
            if operator == "IF_THEN" and len(propositions) < 2:
                errors.append("IF_THEN requires at least two propositions")
            if operator == "SCOPED" and not reading["scope_bindings"]:
                errors.append("SCOPED reading has no scope binding")
    for predicate in cert["predicates"]:
        if not predicate["roles"]:
            errors.append(f"predicate {predicate['predicate_id']} has no role")
    live_predicate_ids = {
        predicate_id
        for reading in live
        for proposition in reading["propositions"]
        for predicate_id in proposition["predicate_ids"]
    }
    for predicate in cert["predicates"]:
        if predicate["predicate_id"] not in live_predicate_ids:
            errors.append(f"predicate {predicate['predicate_id']} is absent from every live reading")
    return errors


def _operator_surface_errors(cert: dict) -> list[str]:
    root_words = {match.group(0).casefold() for match in WORD_RE.finditer(cert["root"]["text"])}
    live_operators = {reading["operator"] for reading in _live_readings(cert)}
    errors = []
    if "or" in root_words and "ALL_OF" in live_operators:
        errors.append("live ALL_OF reading is incompatible with root coordinator 'or'")
    if "and" in root_words and "or" not in root_words and "ANY_OF" in live_operators:
        errors.append("live ANY_OF reading is incompatible with root coordinator 'and'")
    if "if" in root_words and cert["classification"] != "AMBIGUOUS":
        operators = live_operators
        if operators != {"IF_THEN"}:
            errors.append("root 'if' requires the live operator IF_THEN")
    return errors


def _ledger_errors(cert: dict, objects: list[tuple[str, dict]], require_complete: bool) -> list[str]:
    root = cert["root"]["text"]
    ledger = cert["completeness"]["material_span_ledger"]
    errors = []
    cursor = 0
    unresolved = []
    refs = _reference_index(cert)
    for index, entry in enumerate(ledger):
        errors.extend(_span_errors(entry["span"], root, f"ledger[{index}]"))
        span = entry["span"]
        if not errors and span["start"] != cursor:
            errors.append(f"ledger[{index}] does not continue the partition at {cursor}")
        cursor = span.get("end", cursor)
        for ref in entry["object_refs"]:
            if ref not in refs:
                errors.append(f"ledger[{index}] references missing object {ref}")
        if entry["semantic_status"] == "UNRESOLVED":
            unresolved.append(span)
        if entry["semantic_status"] == "ACCOUNTED_MATERIAL" and not entry["object_refs"]:
            errors.append(f"ledger[{index}] is material but has no object reference")
    if cursor != len(root):
        errors.append("material span ledger does not cover the root")
    unassigned = cert["completeness"]["unassigned_material_spans"]
    if len(unassigned) != len(unresolved):
        errors.append("unassigned material spans do not match unresolved ledger spans")
    else:
        for left, right in zip(unassigned, unresolved):
            if left != right:
                errors.append("unassigned material span differs from the unresolved ledger")
    if require_complete and unresolved:
        errors.append("complete certificate contains unresolved ledger spans")

    for match in WORD_RE.finditer(root):
        start, end = match.span()
        word = match.group(0)
        covering = [
            entry
            for entry in ledger
            if entry["span"]["start"] <= start and entry["span"]["end"] >= end
        ]
        if not covering:
            errors.append(f"word {word!r} is outside the ledger")
            continue
        entry = covering[0]
        if entry["semantic_status"] != "ACCOUNTED_MATERIAL":
            errors.append(f"word {word!r} is not accounted as material")
            continue
        covered = False
        for ref in entry["object_refs"]:
            for span in refs.get(ref, []):
                if _covers(span, start, end):
                    covered = True
        if not covered:
            errors.append(f"word {word!r} is not covered by its ledger object span")
    return errors


def _reference_index(cert: dict) -> dict[str, list[dict]]:
    refs: dict[str, list[dict]] = {}
    for predicate in cert["predicates"]:
        refs.setdefault(predicate["predicate_id"], []).append(predicate["span"])
        for role in predicate["roles"]:
            refs.setdefault(role["role_id"], []).append(role["span"])
    for reading in cert["readings"]:
        refs.setdefault(reading["reading_id"], [])
        for binding in reading["scope_bindings"]:
            refs.setdefault(binding["binding_id"], []).append(binding["span"])
    for obligation in cert["obligations"]:
        refs.setdefault(obligation["obligation_id"], []).extend(obligation["source_spans"])
    return refs


def _binding_covers(cert: dict, kinds: set[str], start: int, end: int) -> bool:
    for reading in _live_readings(cert):
        for binding in reading["scope_bindings"]:
            if binding["kind"] in kinds and _covers(binding["span"], start, end):
                return True
    for obligation in cert["obligations"]:
        if obligation["kind"] in kinds:
            for span in obligation["source_spans"]:
                if _covers(span, start, end):
                    return True
    return False


def _lexical_attachment_errors(cert: dict, root: str) -> list[str]:
    errors = []
    negation_kinds = {"NEGATION"}
    modal_kinds = {"MODALITY"}
    conjunction_kinds = {"CONJUNCTION"}
    disjunction_kinds = {"DISJUNCTION"}
    condition_kinds = {"CONDITION"}
    for match in WORD_RE.finditer(root):
        word = match.group(0)
        folded = word.casefold()
        start, end = match.span()
        if _is_negation_word(word) and not _binding_covers(cert, negation_kinds, start, end):
            errors.append(f"negation token {word!r} is not bound")
        if folded in MODAL_WORDS and not _binding_covers(cert, modal_kinds, start, end):
            errors.append(f"modality token {word!r} is not bound")
        if folded in CONJUNCTION_SURFACES and not _binding_covers(cert, conjunction_kinds, start, end):
            errors.append(f"conjunction token {word!r} is not bound")
        if folded in DISJUNCTION_SURFACES and not _binding_covers(cert, disjunction_kinds, start, end):
            errors.append(f"disjunction token {word!r} is not bound")
        if folded == "if" and not _binding_covers(cert, condition_kinds, start, end):
            errors.append(f"condition token {word!r} is not bound")
    return errors


def _requirement_errors(cert: dict, requirements: dict) -> list[str]:
    errors = []
    live = _live_readings(cert)
    materially_live = [reading for reading in live if reading["status"] == "MATERIALLY_LIVE"]
    minimum = requirements.get("min_live_readings")
    maximum = requirements.get("max_live_readings")
    if minimum is not None and len(materially_live) < minimum:
        errors.append(
            f"external basis requires at least {minimum} materially live readings, found {len(materially_live)}"
        )
    if maximum is not None and len(materially_live) > maximum:
        errors.append(
            f"external basis allows at most {maximum} materially live readings, found {len(materially_live)}"
        )
    for spec in requirements.get("required_roles", []):
        if not _has_role(cert, spec):
            errors.append(
                "missing required role "
                f"{spec['predicate_surface']}/{spec['role']}/{spec['surface']}"
            )
    for surface in requirements.get("required_predicate_surfaces", []):
        if not any(predicate["surface"] == surface for predicate in cert["predicates"]):
            errors.append(f"missing required predicate surface {surface!r}")
    for spec in requirements.get("required_bindings", []):
        matches = _bindings(
            cert,
            spec["kind"],
            spec["surface"],
            reading_id=spec.get("reading_id"),
            start=spec.get("start"),
        )
        if not matches:
            where = f" in {spec['reading_id']}" if spec.get("reading_id") else ""
            errors.append(f"missing required {spec['kind']} binding {spec['surface']!r}{where}")
            continue
        for binding, reading in matches:
            targets = [
                proposition
                for proposition in reading["propositions"]
                if proposition["proposition_id"] in binding["targets"]
            ]
            joined = " ".join(proposition["text"] for proposition in targets)
            for needle in spec.get("target_must_contain_all", []):
                if not _text_has(joined, needle):
                    errors.append(
                        f"{spec['kind']} binding {spec['surface']!r} does not reach {needle!r}"
                    )
            for needle in spec.get("target_must_not_contain", []):
                if any(_text_has(proposition["text"], needle) for proposition in targets):
                    errors.append(
                        f"{spec['kind']} binding {spec['surface']!r} reaches forbidden {needle!r}"
                    )
    for spec in requirements.get("modality_descriptions", []):
        descriptions = [
            obligation["description"]
            for obligation in cert["obligations"]
            if any(span["text"] == spec["surface"] for span in obligation["source_spans"])
        ]
        if not descriptions:
            errors.append(f"missing modality description for {spec['surface']!r}")
            continue
        blob = " ".join(descriptions).casefold()
        if spec["must_contain"].casefold() not in blob:
            errors.append(f"modality {spec['surface']!r} does not state {spec['must_contain']!r}")
        for forbidden in spec.get("must_not_contain", []):
            if forbidden.casefold() in blob:
                errors.append(f"modality {spec['surface']!r} states forbidden {forbidden!r}")
    return errors


def _text_has(text: str, needle: str) -> bool:
    text_words = [match.group(0).casefold() for match in WORD_RE.finditer(text)]
    needle_words = [match.group(0).casefold() for match in WORD_RE.finditer(needle)]
    if not needle_words:
        return False
    width = len(needle_words)
    return any(
        text_words[index : index + width] == needle_words
        for index in range(len(text_words) - width + 1)
    )


def _has_role(cert: dict, spec: dict) -> bool:
    for predicate in cert["predicates"]:
        if predicate["surface"] != spec["predicate_surface"]:
            continue
        for role in predicate["roles"]:
            if role["role"] == spec["role"] and role["surface"] == spec["surface"]:
                return True
    return False


def _bindings(cert: dict, kind: str, surface: str, *, reading_id: str | None = None, start: int | None = None):
    found = []
    for reading in _live_readings(cert):
        if reading_id is not None and reading["reading_id"] != reading_id:
            continue
        for binding in reading["scope_bindings"]:
            if binding["kind"] != kind or binding["surface"] != surface:
                continue
            if start is not None and binding["span"]["start"] != start:
                continue
            found.append((binding, reading))
    return found
