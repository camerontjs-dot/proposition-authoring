from __future__ import annotations

from typing import Any, Iterable

from .canonical import bound_object_hash, sha256_text
from .model import AuthoringRequest

SCHEMA_TOKEN = "contract-a-wire-candidate-rc2"


def _source_rows(request: AuthoringRequest) -> list[dict[str, str]]:
    return [
        {
            "source_id": row.source_id,
            "media_type": row.media_type,
            "content": row.content,
            "content_sha256": sha256_text(row.content),
        }
        for row in request.sources
    ]


def _base(request: AuthoringRequest) -> dict[str, Any]:
    return {
        "schema": SCHEMA_TOKEN,
        "handoff_id": request.handoff_id,
        "producer": {
            "producer_id": request.producer_id,
            "producer_version": request.producer_version,
        },
        "work": {"work_id": request.work_id},
        "root_proposition": {
            "proposition_id": request.root_id,
            "text": request.root_text,
            "text_sha256": sha256_text(request.root_text),
        },
        "sources": _source_rows(request),
    }


def seal(value: dict[str, Any]) -> dict[str, Any]:
    out = dict(value)
    out["handoff_sha256"] = bound_object_hash(out, "handoff_sha256")
    return out


def emit_not_decomposed(request: AuthoringRequest) -> dict[str, Any]:
    out = _base(request)
    out["decomposition"] = {"state": "not_decomposed"}
    return seal(out)


def emit_failed(request: AuthoringRequest) -> dict[str, Any]:
    out = _base(request)
    out["decomposition"] = {"state": "failed"}
    return seal(out)


def emit_declared(
    request: AuthoringRequest,
    *,
    decomposition_id: str,
    child_texts: Iterable[str],
) -> dict[str, Any]:
    texts = tuple(child_texts)
    if len(texts) < 2:
        raise ValueError("declared all_of requires at least two children")
    out = _base(request)
    children = []
    for index, text in enumerate(texts, start=1):
        text_hash = sha256_text(text)
        children.append(
            {
                "proposition_id": f"{request.root_id}::pa::{text_hash[7:19]}",
                "text": text,
                "text_sha256": text_hash,
                "sequence": index,
            }
        )
    out["decomposition"] = {
        "state": "declared",
        "decomposition_id": decomposition_id,
        "operator": "all_of",
        "children": children,
    }
    return seal(out)
