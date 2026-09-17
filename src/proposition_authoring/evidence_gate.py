from __future__ import annotations

from .canonical import bound_object_hash, sha256_text
from .model import AuthoringRequest
from .shadow_models import UNKNOWN, EvidenceWorldProfileV0, SourceMetadata, TaskMetadata

_MEDIA_TO_FORM = {
    "application/pdf": "document_text",
    "text/plain": "document_text",
    "text/markdown": "document_text",
    "text/html": "document_text",
    "text/csv": "database_record",
    "application/json": "database_record",
    "application/xml": "database_record",
}


def _metadata_index(rows: tuple[SourceMetadata, ...]) -> dict[str, SourceMetadata]:
    return {row.source_id: row for row in rows}


def _effective_form(media_type: str, declared: str) -> str:
    if declared != UNKNOWN:
        return declared
    normalized = media_type.split(";", 1)[0].strip().lower()
    return _MEDIA_TO_FORM.get(normalized, UNKNOWN)


def build_evidence_world_profile(
    request: AuthoringRequest,
    *,
    task: TaskMetadata | None = None,
    source_metadata: tuple[SourceMetadata, ...] = (),
) -> dict:
    task = task or TaskMetadata()
    by_id = _metadata_index(source_metadata)
    inventory: list[dict] = []
    forms: set[str] = set()
    roles: set[str] = set()
    temporal: set[str] = set()
    jurisdictions: set[str] = set()

    for source in sorted(request.sources, key=lambda row: row.source_id):
        meta = by_id.get(source.source_id, SourceMetadata(source_id=source.source_id))
        evidence_form = _effective_form(source.media_type, meta.evidence_form)
        inventory.append(
            {
                "source_id": source.source_id,
                "media_type": source.media_type,
                "content_sha256": sha256_text(source.content),
                "provenance": meta.provenance,
                "source_role": meta.source_role,
                "evidence_form": evidence_form,
                "temporal_coverage": meta.temporal_coverage,
                "jurisdictional_coverage": meta.jurisdictional_coverage,
            }
        )
        if evidence_form != UNKNOWN:
            forms.add(evidence_form)
        if meta.source_role != UNKNOWN:
            roles.add(meta.source_role)
        if meta.temporal_coverage != UNKNOWN:
            temporal.add(meta.temporal_coverage)
        if meta.jurisdictional_coverage != UNKNOWN:
            jurisdictions.add(meta.jurisdictional_coverage)

    profile = EvidenceWorldProfileV0(
        source_inventory=tuple(inventory),
        evidence_forms=tuple(sorted(forms)),
        source_roles=tuple(sorted(roles)),
        temporal_coverage=tuple(sorted(temporal)),
        jurisdictional_coverage=tuple(sorted(jurisdictions)),
        verification_world=task.verification_world,
        corpus_scope=task.corpus_scope,
        completeness_state=task.completeness_state,
        known_gaps=tuple(sorted(set(task.known_gaps))),
    ).as_dict()
    profile["profile_sha256"] = bound_object_hash(profile, "profile_sha256")
    return profile


def build_evidence_world_receipt(request: AuthoringRequest, profile: dict) -> dict:
    receipt = {
        "schema": "evidence-world-receipt-v0",
        "root_id": request.root_id,
        "source_ids": sorted(source.source_id for source in request.sources),
        "source_content_sha256": {
            source.source_id: sha256_text(source.content)
            for source in sorted(request.sources, key=lambda row: row.source_id)
        },
        "profile_sha256": profile["profile_sha256"],
        "authority_conferring": False,
        "nonclaims": [
            "does not retrieve evidence",
            "does not rank or retain candidates",
            "does not admit Contract B evidence",
            "does not judge support or refutation",
        ],
    }
    receipt["receipt_sha256"] = bound_object_hash(receipt, "receipt_sha256")
    return receipt
