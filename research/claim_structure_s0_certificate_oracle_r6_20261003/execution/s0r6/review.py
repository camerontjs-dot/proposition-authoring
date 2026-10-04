"""Independent certificate review runner.

The prompt builder is part of the frozen procedure. It shows the root, the
analysis basis, the certificate, the schema, and the checklist. It does not
show filenames, mutation names, other reviewers, or the desired disposition.
"""

from __future__ import annotations

import json
from pathlib import Path

VERDICTS = {
    "ACCEPT_COMPLETE",
    "REJECT_OMISSION",
    "REJECT_INVENTION",
    "REJECT_SCOPE",
    "REJECT_ROLE_BINDING",
    "REJECT_OPERATOR",
    "REJECT_SOURCE_BINDING",
    "INCONCLUSIVE_REVIEW",
}


def reviewer_view(certificate: dict) -> dict:
    viewed = json.loads(json.dumps(certificate))
    viewed["certificate_id"] = "certificate-under-review"
    return viewed


def render_prompt(certificate: dict, schema: dict, checklist: str, instructions: str) -> str:
    viewed = reviewer_view(certificate)
    return "\n\n".join(
        [
            instructions.strip(),
            "REVIEW CHECKLIST",
            checklist.strip(),
            "CERTIFICATE SCHEMA",
            json.dumps(schema, indent=2, ensure_ascii=False),
            "CERTIFICATE",
            json.dumps(viewed, indent=2, ensure_ascii=False),
        ]
    )


def parse_verdict(raw: str) -> dict:
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        start = raw.find("{")
        end = raw.rfind("}")
        if start < 0 or end <= start:
            return {"verdict": "UNPARSABLE", "objections": [], "parse_error": "no json object"}
        try:
            payload = json.loads(raw[start : end + 1])
        except json.JSONDecodeError as exc:
            return {"verdict": "UNPARSABLE", "objections": [], "parse_error": str(exc)}
    if not isinstance(payload, dict):
        return {"verdict": "UNPARSABLE", "objections": [], "parse_error": "json is not an object"}
    verdict = payload.get("verdict")
    objections = payload.get("objections", [])
    if verdict not in VERDICTS or not isinstance(objections, list):
        return {"verdict": "UNPARSABLE", "objections": [], "parse_error": "verdict or objections invalid"}
    if verdict == "ACCEPT_COMPLETE" and objections:
        return {
            "verdict": "UNPARSABLE",
            "objections": objections,
            "parse_error": "ACCEPT_COMPLETE included objections",
        }
    return {"verdict": verdict, "objections": objections}


def prompt_leaks(prompt: str, certificate: dict) -> list[str]:
    leaks = []
    certificate_id = certificate["certificate_id"]
    if certificate_id != "certificate-under-review" and certificate_id in prompt:
        leaks.append("certificate id")
    for banned in ("drop_subject", "drop_object", "FALSIFIED", "SUPPORTED_CERTIFICATE", "ClaimGate"):
        if banned in prompt:
            leaks.append(banned)
    return leaks


def write_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
