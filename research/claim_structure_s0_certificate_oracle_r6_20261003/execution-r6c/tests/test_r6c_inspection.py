import hashlib
import json
from pathlib import Path

from s0r6.build import build_certificate
from s0r6.mutate import apply_mutation
from s0r6.review import prompt_leaks, render_prompt
from s0r6.specs import calibration_specs
from s0r6c.eligibility import score_profile
from s0r6c.inspection import expected_inspection, inspection_match, spans_exact
from s0r6c.run_review import OUTPUT_FORMAT, PROTOCOL, SCHEMA, build_request

RESEARCH = Path(__file__).resolve().parents[2]
FROZEN = {
    "execution/protocol/REVIEW-PROMPT.txt": "bd14da5b075dc7d4d2d73751c5f4833bf059a3c12f95e6c25800d8e8b1d1e1bb",
    "execution/protocol/REVIEW-CHECKLIST.md": "c008878d71466af6c14a03be6a31034dcc04c252a104daa9fbc095191f0fe300",
    "execution/s0r6/validate.py": "2eb2b2765a59e80b0fd8fab8f50145e91e671733c46797bbe0c454e2c5f5059d",
    "execution/s0r6/mutate.py": "a9851915d087d27550c9759c32de2735280007c8593386faaa1457db51d2d107",
    "execution-r6b/protocol/REVIEW-PROMPT.txt": "4703c3d8acd146f7df8470449aec89a4f49424f3e4c2823fdb765509aa7891ad",
    "execution-r6b/protocol/REVIEW-CHECKLIST.md": "c70139e68954b82b42820a8bc71ad264a3b90210787117ed84ab6324bfd2e043",
    "execution-r6b/s0r6b/run_review.py": "13dbee9f00a8e79928786c9bf1b59d4bd23322425c16afe8608b9109f4e712a0",
    "execution-r6c/protocol/REVIEW-CHECKLIST.md": "c70139e68954b82b42820a8bc71ad264a3b90210787117ed84ab6324bfd2e043",
}


def _spec(certificate_id: str) -> dict:
    return next(item for item in calibration_specs() if item["certificate_id"] == certificate_id)


def _payload(certificate: dict) -> dict:
    expected = expected_inspection(certificate)
    return {
        "roles": [
            {"predicate_surface": pred, "role": role, "surface": surface}
            for pred, role, surface in expected["roles"].elements()
        ],
        "live_bindings": [
            {
                "reading_id": reading_id,
                "kind": kind,
                "surface": surface,
                "targets": list(targets),
            }
            for reading_id, kind, surface, targets in expected["live_bindings"].elements()
        ],
        "live_reading_ids": list(expected["live_reading_ids"].elements()),
        "live_operators": [
            {"reading_id": reading_id, "operator": operator}
            for reading_id, operator in expected["live_operators"].elements()
        ],
        "modality_descriptions": list(expected["modality_descriptions"].elements()),
        "spans_exact": expected["spans_exact"],
        "verdict": "ACCEPT_COMPLETE",
        "objections": [],
    }


def test_predecessor_and_r6b_files_stay_byte_identical():
    for relative, digest in FROZEN.items():
        data = (RESEARCH / relative).read_bytes()
        assert hashlib.sha256(data).hexdigest() == digest


def test_exact_copy_matches_and_a_restored_role_does_not():
    certificate = build_certificate(_spec("s0r6-cal-kim"))
    assert spans_exact(certificate) is True
    assert inspection_match(certificate, _payload(certificate)) is True
    mutated = apply_mutation(certificate, "drop_subject")
    assert ("bought", "subject", "Kim") not in expected_inspection(mutated)["roles"]
    restored = _payload(mutated)
    restored["roles"].append(
        {"predicate_surface": "bought", "role": "subject", "surface": "Kim"}
    )
    assert inspection_match(mutated, restored) is False
    altered = apply_mutation(certificate, "alter_span")
    assert spans_exact(altered) is False
    assert inspection_match(altered, _payload(altered)) is True


def test_prompt_hides_mutation_names_and_requests_a_copy():
    certificate = build_certificate(_spec("s0r6-cal-kim"))
    mutated = apply_mutation(certificate, "drop_subject")
    checklist = (PROTOCOL / "REVIEW-CHECKLIST.md").read_text(encoding="utf-8")
    instructions = (PROTOCOL / "REVIEW-PROMPT.txt").read_text(encoding="utf-8")
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    prompt = render_prompt(mutated, schema, checklist, instructions)
    assert prompt_leaks(prompt, mutated) == []
    assert "predicates[].roles" in prompt
    assert "spans_exact" in prompt
    assert "Necessity is not permission" in prompt


def test_request_keeps_frozen_sampling_and_uses_the_inspection_schema():
    profiles = json.loads(
        (RESEARCH / "execution/protocol/REVIEWER-PROFILES.json").read_text(encoding="utf-8")
    )
    body = build_request(profiles["profiles"][1], profiles, "prompt")
    assert body["model"] == "qwen3:14b"
    assert body["think"] is False
    assert body["format"] == OUTPUT_FORMAT
    assert body["options"] == {"temperature": 0, "seed": 7, "num_ctx": 16384}


def test_eligibility_requires_a_matching_copy_on_every_item():
    clean = [
        {"item": "s0r6-cal-kim", "verdict": "ACCEPT_COMPLETE", "inspection_match": True},
        {
            "item": "s0r6-cal-kim--drop_subject",
            "verdict": "REJECT_ROLE_BINDING",
            "inspection_match": True,
        },
    ]
    assert score_profile(clean)["eligible"] is True
    stamped = [
        {"item": "s0r6-cal-kim", "verdict": "ACCEPT_COMPLETE", "inspection_match": True},
        {
            "item": "s0r6-cal-kim--drop_subject",
            "verdict": "REJECT_ROLE_BINDING",
            "inspection_match": False,
        },
    ]
    failed = score_profile(stamped)
    assert failed["eligible"] is False
    assert failed["failures"][0]["reason"] == "inspection_mismatch"
