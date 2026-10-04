"""Run one frozen reviewer profile over a directory of certificates.

Usage:
  python -m s0r6.run_review <profile_id> <certificate_dir> <output_dir>

Existing output files are left unchanged. The prompt is built by review.render_prompt.
"""

from __future__ import annotations

import json
import sys
import urllib.request
from pathlib import Path

from s0r6.review import parse_verdict, render_prompt, write_json

EXECUTION = Path(__file__).resolve().parents[1]
PROTOCOL = EXECUTION / "protocol"
SCHEMA = EXECUTION.parent / "CERTIFICATE-SCHEMA.json"


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def review_directory(profile_id: str, certificate_dir: Path, output_dir: Path) -> dict:
    profiles = _load(PROTOCOL / "REVIEWER-PROFILES.json")
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
        body = {
            "model": profile["model"],
            "stream": False,
            "think": profiles["request"]["think"],
            "format": profiles["request"]["format"],
            "options": profiles["request"]["options"],
            "messages": [{"role": "user", "content": prompt}],
        }
        request = urllib.request.Request(
            "http://127.0.0.1:11434/api/chat",
            data=json.dumps(body).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(request, timeout=600) as response:
            payload = json.loads(response.read().decode("utf-8"))
        content = payload.get("message", {}).get("content", "")
        parsed = parse_verdict(content)
        record = {
            "profile_id": profile_id,
            "model": profile["model"],
            "model_digest": profile["model_digest"],
            "item": path.stem,
            "prompt_sha256": __import__("hashlib").sha256(prompt.encode("utf-8")).hexdigest(),
            "raw": content,
            "parsed": parsed,
            "eval_count": payload.get("eval_count"),
            "prompt_eval_count": payload.get("prompt_eval_count"),
        }
        write_json(destination, record)
        results.append({"item": path.stem, "status": parsed["verdict"]})
        print(f"{profile_id} {path.stem} {parsed['verdict']}", flush=True)
    return {"profile_id": profile_id, "results": results}


def main(argv: list[str]) -> None:
    profile_id, certificate_dir, output_dir = argv
    summary = review_directory(profile_id, Path(certificate_dir), Path(output_dir))
    print(json.dumps(summary))


if __name__ == "__main__":
    main(sys.argv[1:])
