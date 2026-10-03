"""Run one frozen reviewer profile with the r6c inspection procedure.

Usage:
  python -m s0r6c.run_review <profile_id> <certificate_dir> <output_dir>

Profiles, temperature, seed, context length, and think flag come from the
frozen R6 profile file. The response format is the inspection object below.
Existing output files are left unchanged.
"""

from __future__ import annotations

import hashlib
import json
import sys
import urllib.request
from pathlib import Path

R6C = Path(__file__).resolve().parents[1]
RESEARCH = R6C.parent
EXECUTION = RESEARCH / "execution"
if str(EXECUTION) not in sys.path:
    sys.path.insert(0, str(EXECUTION))

from s0r6.review import parse_verdict, render_prompt, write_json
from s0r6c.inspection import inspection_match

PROTOCOL = R6C / "protocol"
FROZEN_PROTOCOL = EXECUTION / "protocol"
SCHEMA = RESEARCH / "CERTIFICATE-SCHEMA.json"

OUTPUT_FORMAT = {
    "type": "object",
    "properties": {
        "roles": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "predicate_surface": {"type": "string"},
                    "role": {"type": "string"},
                    "surface": {"type": "string"},
                },
                "required": ["predicate_surface", "role", "surface"],
            },
        },
        "live_bindings": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "reading_id": {"type": "string"},
                    "kind": {"type": "string"},
                    "surface": {"type": "string"},
                    "targets": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["reading_id", "kind", "surface", "targets"],
            },
        },
        "live_reading_ids": {"type": "array", "items": {"type": "string"}},
        "live_operators": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "reading_id": {"type": "string"},
                    "operator": {"type": "string"},
                },
                "required": ["reading_id", "operator"],
            },
        },
        "modality_descriptions": {"type": "array", "items": {"type": "string"}},
        "spans_exact": {"type": "boolean"},
        "verdict": {"type": "string"},
        "objections": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "question": {"type": "integer"},
                    "severity": {"type": "string"},
                    "detail": {"type": "string"},
                },
                "required": ["question", "severity", "detail"],
            },
        },
    },
    "required": [
        "roles",
        "live_bindings",
        "live_reading_ids",
        "live_operators",
        "modality_descriptions",
        "spans_exact",
        "verdict",
        "objections",
    ],
}


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def build_request(profile: dict, profiles_doc: dict, prompt: str) -> dict:
    request_doc = profiles_doc["request"]
    return {
        "model": profile["model"],
        "stream": False,
        "think": request_doc["think"],
        "format": OUTPUT_FORMAT,
        "options": request_doc["options"],
        "messages": [{"role": "user", "content": prompt}],
    }


def review_directory(profile_id: str, certificate_dir: Path, output_dir: Path) -> dict:
    profiles = _load(FROZEN_PROTOCOL / "REVIEWER-PROFILES.json")
    profile = next(item for item in profiles["profiles"] if item["profile_id"] == profile_id)
    schema = _load(SCHEMA)
    checklist = (PROTOCOL / "REVIEW-CHECKLIST.md").read_text(encoding="utf-8")
    instructions = (PROTOCOL / "REVIEW-PROMPT.txt").read_text(encoding="utf-8")
    output_dir.mkdir(parents=True, exist_ok=True)
    results = []
    for path in sorted(certificate_dir.glob("*.json")):
        destination = output_dir / f"{path.stem}.json"
        if destination.exists():
            results.append({"item": path.stem, "status": "skipped"})
            continue
        certificate = _load(path)
        prompt = render_prompt(certificate, schema, checklist, instructions)
        body = build_request(profile, profiles, prompt)
        request = urllib.request.Request(
            "http://127.0.0.1:11434/api/chat",
            data=json.dumps(body).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(request, timeout=600) as response:
            payload = json.loads(response.read().decode("utf-8"))
        content = payload.get("message", {}).get("content", "")
        parsed = parse_verdict(content)
        try:
            inspected = json.loads(content)
        except json.JSONDecodeError:
            start = content.find("{")
            end = content.rfind("}")
            try:
                inspected = json.loads(content[start : end + 1]) if start >= 0 and end > start else {}
            except json.JSONDecodeError:
                inspected = {}
        matched = inspection_match(certificate, inspected)
        record = {
            "successor": "r6c",
            "profile_id": profile_id,
            "model": profile["model"],
            "model_digest": profile["model_digest"],
            "item": path.stem,
            "prompt_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
            "checklist_sha256": hashlib.sha256(checklist.encode("utf-8")).hexdigest(),
            "instructions_sha256": hashlib.sha256(instructions.encode("utf-8")).hexdigest(),
            "inspection_match": matched,
            "raw": content,
            "parsed": parsed,
            "eval_count": payload.get("eval_count"),
            "prompt_eval_count": payload.get("prompt_eval_count"),
        }
        write_json(destination, record)
        results.append(
            {
                "item": path.stem,
                "status": parsed["verdict"],
                "inspection_match": matched,
            }
        )
        print(
            f"{profile_id} {path.stem} {parsed['verdict']} inspection_match={matched}",
            flush=True,
        )
    return {"profile_id": profile_id, "results": results}


def main(argv: list[str]) -> None:
    profile_id, certificate_dir, output_dir = argv
    summary = review_directory(profile_id, Path(certificate_dir), Path(output_dir))
    print(json.dumps(summary))


if __name__ == "__main__":
    main(sys.argv[1:])
