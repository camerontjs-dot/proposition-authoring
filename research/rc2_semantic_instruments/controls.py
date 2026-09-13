from __future__ import annotations

import re
from typing import Any

from proposition_authoring.ambiguity import analyze_root_scope
from proposition_authoring.conservation import audit_candidate

STOP = {"a", "an", "the", "and", "or", "that", "both", "did", "not", "was", "were", "is", "in", "at", "during", "to"}


def _eval_ok(candidate: dict[str, Any], backend: Any) -> bool:
    return backend.evaluate(candidate)["disposition"] == "ACCEPTABLE_WITHIN_PROFILE"


def evaluator_only(candidate: dict[str, Any], backend: Any) -> str:
    if analyze_root_scope(candidate["root_text"]):
        return "BLOCK"
    return "ALLOW" if _eval_ok(candidate, backend) else "BLOCK"


def conservation_only(candidate: dict[str, Any], backend: Any) -> str:
    del backend
    if analyze_root_scope(candidate["root_text"]):
        return "BLOCK"
    children = tuple(x["text"] for x in candidate["children"])
    return "ALLOW" if audit_candidate(candidate["root_text"], children).disposition == "PASS" else "BLOCK"


def permissive_any_pass(candidate: dict[str, Any], backend: Any) -> str:
    if analyze_root_scope(candidate["root_text"]):
        return "BLOCK"
    children = tuple(x["text"] for x in candidate["children"])
    conservation_ok = audit_candidate(candidate["root_text"], children).disposition == "PASS"
    return "ALLOW" if (_eval_ok(candidate, backend) or conservation_ok) else "BLOCK"


def lexical_coverage(candidate: dict[str, Any], backend: Any) -> str:
    del backend
    root_tokens = {x.lower() for x in re.findall(r"[A-Za-z0-9]+", candidate["root_text"]) if x.lower() not in STOP}
    child_tokens = {
        x.lower()
        for child in candidate["children"]
        for x in re.findall(r"[A-Za-z0-9]+", child["text"])
        if x.lower() not in STOP
    }
    return "ALLOW" if child_tokens <= root_tokens else "BLOCK"


CONTROLS = {
    "C0_EVALUATOR_ONLY": evaluator_only,
    "C1_CONSERVATION_ONLY": conservation_only,
    "C2_PERMISSIVE_ANY_PASS": permissive_any_pass,
    "C3_LEXICAL_COVERAGE": lexical_coverage,
}
