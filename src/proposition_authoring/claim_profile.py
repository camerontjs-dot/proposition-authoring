from __future__ import annotations

import re

from .canonical import bound_object_hash, sha256_text
from .model import AuthoringRequest
from .shadow_models import UNKNOWN, ClaimProfileV0, ObservationBasis, TaskMetadata

_COMPARATIVE = re.compile(
    r"\b(more|less|higher|lower|greater|fewer|than|compared|versus|vs\.?|exceed(?:s|ed)?)\b",
    re.IGNORECASE,
)
_CAUSAL = re.compile(
    r"\b(because|caus(?:e|ed|es)|led to|result(?:ed|s)? in|due to)\b",
    re.IGNORECASE,
)
_ATTRIBUTIONAL = re.compile(
    r"\b(reported|stated|claimed|said|asserted|concluded|observed|confirmed|indicated|showed|found)\b",
    re.IGNORECASE,
)
_NUMERIC = re.compile(r"(?:\b\d+(?:\.\d+)?\b|%)")
_TEMPORAL = re.compile(
    r"\b(?:19|20)\d{2}\b|\b(as of|before|after|during|since|between|from|until|through)\b",
    re.IGNORECASE,
)
_DEFINITIONAL = re.compile(r"\b(means|defined as|refers to)\b", re.IGNORECASE)
_EXISTENCE = re.compile(r"\b(exists?|there (?:is|are)|contains?|includes?)\b", re.IGNORECASE)
_STATUS = re.compile(
    r"\b(active|inactive|approved|compliant|ready|failed|passed|rejected|revoked|expired|open|closed)\b",
    re.IGNORECASE,
)
_COMPLIANCE = re.compile(
    r"\b(compliant|compliance|regulation|regulated|requirement|standard)\b",
    re.IGNORECASE,
)
_YEAR = re.compile(r"\b(?:19|20)\d{2}\b")
_NEGATION = re.compile(
    r"\b(no|not|never|neither|nor|without|didn['’]?t|doesn['’]?t|isn['’]?t|wasn['’]?t)\b",
    re.IGNORECASE,
)
_MODALITY = re.compile(
    r"\b(may|might|could|can|should|would|likely|unlikely|possibly|probably|must)\b",
    re.IGNORECASE,
)
_COORDINATION = re.compile(r"(?:[,;]|\b(?:and|or|but|while|whereas)\b)", re.IGNORECASE)
_SIMPLE_COMPARATIVE = re.compile(
    r"^\s*(?P<left>.+?)\s+had\s+(?:an?\s+)?(?:higher|lower|greater|fewer)\s+.+?\s+than\s+(?P<right>.+?)\.?\s*$",
    re.IGNORECASE,
)


def _basis(kind: str, detail: str, source_ref: str = UNKNOWN) -> dict[str, str]:
    return ObservationBasis(kind, detail, source_ref).as_dict()


def _basis_rows(
    mapping: dict[str, list[dict[str, str]]],
) -> tuple[tuple[str, tuple[dict[str, str], ...]], ...]:
    return tuple((key, tuple(mapping[key])) for key in sorted(mapping))


def _families(text: str) -> tuple[str, ...]:
    found: set[str] = set()
    checks = (
        ("comparative", _COMPARATIVE),
        ("causal", _CAUSAL),
        ("attributional", _ATTRIBUTIONAL),
        ("numeric", _NUMERIC),
        ("temporal", _TEMPORAL),
        ("definitional", _DEFINITIONAL),
        ("existence", _EXISTENCE),
        ("status_state", _STATUS),
        ("compliance", _COMPLIANCE),
    )
    for name, pattern in checks:
        if pattern.search(text):
            found.add(name)
    return tuple(sorted(found)) if found else (UNKNOWN,)


def _expected_forms(families: tuple[str, ...]) -> tuple[str, ...]:
    forms: set[str] = set()
    family_set = set(families)
    if family_set & {"comparative", "numeric"}:
        forms.update({"measurement", "document_text"})
    if "causal" in family_set:
        forms.update({"measurement", "event_record", "document_text"})
    if "attributional" in family_set:
        forms.update({"authoritative_declaration", "document_text"})
    if family_set & {"status_state", "compliance"}:
        forms.update(
            {
                "authoritative_declaration",
                "database_record",
                "document_text",
                "registry_entry",
            }
        )
    if "existence" in family_set:
        forms.update({"database_record", "registry_entry", "document_text"})
    if "definitional" in family_set:
        forms.add("document_text")
    return tuple(sorted(forms)) if forms else (UNKNOWN,)


def _temporal_scope(text: str, task: TaskMetadata) -> tuple[str, dict[str, str]]:
    if task.temporal_scope != UNKNOWN:
        return task.temporal_scope, _basis(
            "task_declaration", "explicit task temporal_scope"
        )
    years = sorted(set(_YEAR.findall(text)))
    if len(years) == 1:
        return years[0], _basis(
            "mechanical_text_pattern", "single explicit year in root text"
        )
    if len(years) > 1:
        return "years:" + ",".join(years), _basis(
            "mechanical_text_pattern", "multiple explicit years in root text"
        )
    return UNKNOWN, _basis("no_basis", "no explicit temporal scope recovered")


def _surface_shape(text: str) -> str:
    if not text.strip():
        return UNKNOWN
    if _COORDINATION.search(text):
        return "compound_or_scope_bearing_surface"
    return "single_clause_surface"


def _relation_targets(text: str) -> tuple[tuple[str, ...], tuple[str, ...]]:
    match = _SIMPLE_COMPARATIVE.fullmatch(text)
    if not match:
        return (), ()
    left = match.group("left").strip()
    right = match.group("right").strip().rstrip(".")
    right = re.sub(r"\s+in\s+(?:19|20)\d{2}$", "", right, flags=re.IGNORECASE)
    if not left or not right:
        return (), ()
    return (left, right), (left, right)


def _declared_basis(value: str, label: str) -> dict[str, str]:
    if value == UNKNOWN:
        return _basis("no_basis", f"{label} not declared")
    return _basis("task_declaration", f"task {label}")


def build_claim_profile(
    request: AuthoringRequest, task: TaskMetadata | None = None
) -> dict:
    task = task or TaskMetadata()
    text = request.root_text
    families = _families(text)
    expected = _expected_forms(families)
    temporal_scope, temporal_basis = _temporal_scope(text, task)
    entities, relation_targets = _relation_targets(text)
    structure = _surface_shape(text)
    context_dependence = (
        "context_supplied"
        if request.context_source_id is not None
        else "no_context_supplied"
    )
    scope_ambiguity = (
        "possible_surface_scope"
        if _COORDINATION.search(text)
        else "none_mechanically_observed"
    )
    negation = "present" if _NEGATION.search(text) else "absent"
    modality = "present" if _MODALITY.search(text) else "absent"
    attribution = "present" if _ATTRIBUTIONAL.search(text) else "absent"

    basis: dict[str, list[dict[str, str]]] = {
        "claim_families": [
            _basis("mechanical_text_pattern", "bounded family detectors over root text")
        ],
        "expected_evidence_forms": [
            _basis("claim_family_mapping", "V0 family-to-form mapping")
        ],
        "claim_structure_shape": [
            _basis(
                "mechanical_surface_shape",
                "coordination and punctuation surface check",
            )
        ],
        "entities": [
            _basis(
                "bounded_relation_parse" if entities else "no_basis",
                (
                    "bounded comparative left/right extraction"
                    if entities
                    else "no bounded relation extraction"
                ),
            )
        ],
        "relation_targets": [
            _basis(
                "bounded_relation_parse" if relation_targets else "no_basis",
                (
                    "bounded comparative relation targets"
                    if relation_targets
                    else "no bounded relation extraction"
                ),
            )
        ],
        "domain": [_declared_basis(task.domain, "domain")],
        "verification_world": [
            _declared_basis(task.verification_world, "verification world")
        ],
        "temporal_scope": [temporal_basis],
        "jurisdiction": [_declared_basis(task.jurisdiction, "jurisdiction")],
        "context_dependence": [
            _basis("request_structure", "presence or absence of context_source_id")
        ],
        "scope_ambiguity": [
            _basis(
                "mechanical_surface_shape", "bounded coordination/punctuation screen"
            )
        ],
        "negation": [_basis("mechanical_text_pattern", "bounded negation detector")],
        "modality": [_basis("mechanical_text_pattern", "bounded modality detector")],
        "attribution": [
            _basis("mechanical_text_pattern", "bounded attribution detector")
        ],
    }

    profile = ClaimProfileV0(
        root_id=request.root_id,
        claim_families=families,
        expected_evidence_forms=expected,
        claim_structure_shape=structure,
        entities=entities,
        relation_targets=relation_targets,
        domain=task.domain,
        verification_world=task.verification_world,
        temporal_scope=temporal_scope,
        jurisdiction=task.jurisdiction,
        context_dependence=context_dependence,
        scope_ambiguity=scope_ambiguity,
        negation=negation,
        modality=modality,
        attribution=attribution,
        field_basis=_basis_rows(basis),
        notes=("shadow-only; non-authoritative; non-causal",),
    ).as_dict()
    profile["profile_sha256"] = bound_object_hash(profile, "profile_sha256")
    return profile


def build_claim_profile_receipt(request: AuthoringRequest, profile: dict) -> dict:
    receipt = {
        "schema": "claim-profile-receipt-v0",
        "root_id": request.root_id,
        "root_text_sha256": sha256_text(request.root_text),
        "context_source_id": request.context_source_id,
        "source_content_sha256": {
            source.source_id: sha256_text(source.content)
            for source in sorted(request.sources, key=lambda row: row.source_id)
        },
        "profile_sha256": profile["profile_sha256"],
        "authority_conferring": False,
        "nonclaims": [
            "does not alter ClaimGate authoring state",
            "does not establish proposition structure",
            "does not steer retrieval",
            "does not judge support or refutation",
        ],
    }
    receipt["receipt_sha256"] = bound_object_hash(receipt, "receipt_sha256")
    return receipt
