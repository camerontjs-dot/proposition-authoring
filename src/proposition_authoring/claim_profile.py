from __future__ import annotations

import re

from .canonical import bound_object_hash, sha256_text
from .model import AuthoringRequest
from .shadow_models import ClaimProfileV0, TaskMetadata, UNKNOWN

_COMPARATIVE = re.compile(r"\b(more|less|higher|lower|greater|fewer|than|compared|versus|vs\.?|exceed(?:s|ed)?)\b", re.I)
_CAUSAL = re.compile(r"\b(because|caus(?:e|ed|es)|led to|result(?:ed|s)? in|due to)\b", re.I)
_ATTRIBUTIONAL = re.compile(r"\b(reported|stated|claimed|said|asserted|concluded|observed|confirmed|indicated|showed|found)\b", re.I)
_NUMERIC = re.compile(r"(?:\b\d+(?:\.\d+)?\b|%)")
_TEMPORAL = re.compile(r"\b(?:19|20)\d{2}\b|\b(as of|before|after|during|since|between|from|until|through)\b", re.I)
_DEFINITIONAL = re.compile(r"\b(means|defined as|refers to)\b", re.I)
_EXISTENCE = re.compile(r"\b(exists?|there (?:is|are)|contains?|includes?)\b", re.I)
_STATUS = re.compile(r"\b(active|inactive|approved|compliant|ready|failed|passed|rejected|revoked|expired|open|closed)\b", re.I)
_COMPLIANCE = re.compile(r"\b(compliant|compliance|regulation|regulated|requirement|standard)\b", re.I)
_YEAR = re.compile(r"\b(?:19|20)\d{2}\b")


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
        forms.update({"database_record", "registry_entry", "authoritative_declaration"})
    if "existence" in family_set:
        forms.update({"database_record", "registry_entry", "document_text"})
    if "definitional" in family_set:
        forms.add("document_text")
    return tuple(sorted(forms)) if forms else (UNKNOWN,)


def _temporal_scope(text: str, task: TaskMetadata) -> str:
    if task.temporal_scope != UNKNOWN:
        return task.temporal_scope
    years = sorted(set(_YEAR.findall(text)))
    if len(years) == 1:
        return years[0]
    if len(years) > 1:
        return "years:" + ",".join(years)
    return UNKNOWN


def build_claim_profile(request: AuthoringRequest, task: TaskMetadata | None = None) -> dict:
    task = task or TaskMetadata()
    families = _families(request.root_text)
    profile = ClaimProfileV0(
        root_id=request.root_id,
        claim_families=families,
        expected_evidence_forms=_expected_forms(families),
        domain=task.domain,
        verification_world=task.verification_world,
        temporal_scope=_temporal_scope(request.root_text, task),
        jurisdiction=task.jurisdiction,
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
