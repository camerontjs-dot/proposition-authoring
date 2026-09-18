from __future__ import annotations

from collections import defaultdict

from .canonical import bound_object_hash, sha256_text
from .model import AuthoringRequest
from .shadow_models import (
    UNKNOWN,
    EvidenceWorldProfileV0,
    ObservationBasis,
    SourceMetadata,
    TaskMetadata,
)

_MEDIA_TO_FORM = {
    "application/pdf": "document_text",
    "text/plain": "document_text",
    "text/markdown": "document_text",
    "text/html": "document_text",
    "text/csv": "database_record",
    "application/json": "database_record",
    "application/xml": "database_record",
}
_MEDIA_TO_DOCUMENT_TYPE = {
    "application/pdf": "pdf_document",
    "text/plain": "text_document",
    "text/markdown": "markdown_document",
    "text/html": "html_document",
    "text/csv": "tabular_record",
    "application/json": "structured_record",
    "application/xml": "structured_record",
}


def _basis(kind: str, detail: str, source_ref: str = UNKNOWN) -> dict[str, str]:
    return ObservationBasis(kind, detail, source_ref).as_dict()


def _basis_rows(
    mapping: dict[str, list[dict[str, str]]],
) -> tuple[tuple[str, tuple[dict[str, str], ...]], ...]:
    return tuple((key, tuple(mapping[key])) for key in sorted(mapping))


def _metadata_index(rows: tuple[SourceMetadata, ...]) -> dict[str, SourceMetadata]:
    return {row.source_id: row for row in rows}


def _normalized_media_type(media_type: str) -> str:
    return media_type.split(";", 1)[0].strip().lower()


def _effective_form(media_type: str, declared: str) -> tuple[str, str]:
    if declared != UNKNOWN:
        return declared, "source_metadata"
    normalized = _normalized_media_type(media_type)
    value = _MEDIA_TO_FORM.get(normalized, UNKNOWN)
    return value, "media_type_mapping" if value != UNKNOWN else "no_basis"


def _effective_document_type(media_type: str, declared: str) -> tuple[str, str]:
    if declared != UNKNOWN:
        return declared, "source_metadata"
    normalized = _normalized_media_type(media_type)
    value = _MEDIA_TO_DOCUMENT_TYPE.get(normalized, UNKNOWN)
    return value, "media_type_mapping" if value != UNKNOWN else "no_basis"


def _duplicate_groups(inventory: list[dict]) -> tuple[tuple[str, ...], ...]:
    by_hash: dict[str, list[str]] = defaultdict(list)
    for row in inventory:
        by_hash[row["content_sha256"]].append(row["source_id"])
    return tuple(
        sorted(
            tuple(sorted(source_ids))
            for source_ids in by_hash.values()
            if len(source_ids) > 1
        )
    )


def _metadata_basis(
    value: str,
    label: str,
    source_id: str,
) -> dict[str, str]:
    if value == UNKNOWN:
        return _basis("no_basis", f"{label} not declared", source_id)
    return _basis("source_metadata", f"declared {label}", source_id)


def _task_basis(value: str, label: str) -> dict[str, str]:
    if value == UNKNOWN:
        return _basis("no_basis", f"{label} not declared")
    return _basis("task_declaration", f"task {label}")


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
    issuers: set[str] = set()
    document_types: set[str] = set()
    currency_states: set[str] = set()
    conflicts: set[tuple[str, str]] = set()
    supersessions: set[tuple[str, str]] = set()

    for source in sorted(request.sources, key=lambda row: row.source_id):
        meta = by_id.get(source.source_id, SourceMetadata(source_id=source.source_id))
        evidence_form, form_basis = _effective_form(source.media_type, meta.evidence_form)
        document_type, document_basis = _effective_document_type(
            source.media_type, meta.document_type
        )
        content_hash = sha256_text(source.content)
        source_basis = {
            "provenance": [
                _metadata_basis(meta.provenance, "source provenance", source.source_id)
            ],
            "issuer": [_metadata_basis(meta.issuer, "issuer", source.source_id)],
            "source_role": [
                _metadata_basis(meta.source_role, "source role", source.source_id)
            ],
            "authority_basis": [
                _metadata_basis(meta.authority_basis, "authority basis", source.source_id)
            ],
            "document_type": [
                _basis(
                    document_basis,
                    "document type from declaration/media type",
                    source.source_id,
                )
            ],
            "evidence_form": [
                _basis(
                    form_basis,
                    "evidence form from declaration/media type",
                    source.source_id,
                )
            ],
            "temporal_coverage": [
                _metadata_basis(
                    meta.temporal_coverage, "temporal coverage", source.source_id
                )
            ],
            "jurisdictional_coverage": [
                _metadata_basis(
                    meta.jurisdictional_coverage,
                    "jurisdictional coverage",
                    source.source_id,
                )
            ],
            "version": [_metadata_basis(meta.version, "version", source.source_id)],
            "currency_state": [
                _metadata_basis(meta.currency_state, "currency state", source.source_id)
            ],
        }
        inventory.append(
            {
                "source_id": source.source_id,
                "media_type": source.media_type,
                "content_sha256": content_hash,
                "provenance": meta.provenance,
                "issuer": meta.issuer,
                "source_role": meta.source_role,
                "authority_basis": meta.authority_basis,
                "document_type": document_type,
                "evidence_form": evidence_form,
                "temporal_coverage": meta.temporal_coverage,
                "jurisdictional_coverage": meta.jurisdictional_coverage,
                "version": meta.version,
                "currency_state": meta.currency_state,
                "supersedes": sorted(set(meta.supersedes)),
                "conflicts_with": sorted(set(meta.conflicts_with)),
                "field_basis": source_basis,
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
        if meta.issuer != UNKNOWN:
            issuers.add(meta.issuer)
        if document_type != UNKNOWN:
            document_types.add(document_type)
        if meta.currency_state != UNKNOWN:
            currency_states.add(meta.currency_state)
        for other in meta.conflicts_with:
            conflicts.add(tuple(sorted((source.source_id, other))))
        for predecessor in meta.supersedes:
            supersessions.add((source.source_id, predecessor))

    duplicate_groups = _duplicate_groups(inventory)
    basis: dict[str, list[dict[str, str]]] = {
        "source_inventory": [
            _basis("supplied_source", "exact supplied pre-retrieval source universe")
        ],
        "evidence_forms": [
            _basis(
                "inventory_aggregation",
                "set of mechanically/declaratively characterized source forms",
            )
        ],
        "source_roles": [
            _basis("inventory_aggregation", "declared source roles")
        ],
        "temporal_coverage": [
            _basis("inventory_aggregation", "declared temporal coverage values")
        ],
        "jurisdictional_coverage": [
            _basis("inventory_aggregation", "declared jurisdictional coverage values")
        ],
        "issuers": [_basis("inventory_aggregation", "declared issuers")],
        "document_types": [
            _basis(
                "inventory_aggregation", "declared/mechanical document types"
            )
        ],
        "currency_states": [
            _basis("inventory_aggregation", "declared currency states")
        ],
        "duplicate_source_groups": [
            _basis("content_hash", "identical supplied source content hashes")
        ],
        "conflict_observations": [
            _basis("source_metadata", "declared conflict links only")
        ],
        "supersession_observations": [
            _basis("source_metadata", "declared supersession links only")
        ],
        "verification_world": [
            _task_basis(task.verification_world, "verification world")
        ],
        "corpus_scope": [_task_basis(task.corpus_scope, "corpus scope")],
        "completeness_state": [
            _task_basis(task.completeness_state, "completeness state")
        ],
        "known_gaps": [
            _basis(
                "task_declaration" if task.known_gaps else "no_basis",
                "declared known gaps" if task.known_gaps else "no known gaps declared",
            )
        ],
    }

    profile = EvidenceWorldProfileV0(
        source_inventory=tuple(inventory),
        evidence_forms=tuple(sorted(forms)),
        source_roles=tuple(sorted(roles)),
        temporal_coverage=tuple(sorted(temporal)),
        jurisdictional_coverage=tuple(sorted(jurisdictions)),
        issuers=tuple(sorted(issuers)),
        document_types=tuple(sorted(document_types)),
        currency_states=tuple(sorted(currency_states)),
        duplicate_source_groups=duplicate_groups,
        conflict_observations=tuple(sorted(conflicts)),
        supersession_observations=tuple(sorted(supersessions)),
        verification_world=task.verification_world,
        corpus_scope=task.corpus_scope,
        completeness_state=task.completeness_state,
        known_gaps=tuple(sorted(set(task.known_gaps))),
        field_basis=_basis_rows(basis),
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
            "does not prescribe Evidence Bundler queries or source routing",
        ],
    }
    receipt["receipt_sha256"] = bound_object_hash(receipt, "receipt_sha256")
    return receipt
