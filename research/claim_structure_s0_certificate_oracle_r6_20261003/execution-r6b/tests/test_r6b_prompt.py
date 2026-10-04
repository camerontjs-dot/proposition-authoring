import hashlib
import json
from pathlib import Path

from s0r6.build import build_certificate
from s0r6.mutate import apply_mutation
from s0r6.review import prompt_leaks, render_prompt
from s0r6.specs import calibration_specs
from s0r6b.eligibility import score_profile
from s0r6b.run_review import PROTOCOL, SCHEMA, build_request

RESEARCH = Path(__file__).resolve().parents[2]
FROZEN = {
    "execution/protocol/REVIEW-PROMPT.txt": "bd14da5b075dc7d4d2d73751c5f4833bf059a3c12f95e6c25800d8e8b1d1e1bb",
    "execution/protocol/REVIEW-CHECKLIST.md": "c008878d71466af6c14a03be6a31034dcc04c252a104daa9fbc095191f0fe300",
    "execution/protocol/REVIEWER-PROFILES.json": "7f45379d66d9aa1ade4cb1bf0bc6d2dd6b7f042383eaa8254331522cd1dcebdb",
    "CERTIFICATE-SCHEMA.json": "a8c08d65413af8203bb40da4fa3f0bcd9f3fcb5038811a53181d5e656ba25e2c",
    "execution/s0r6/run_review.py": "035f75f2935f6c6359a55ee2ee34abd096c0479497c263cff4f717cbcbc06864",
    "execution/s0r6/validate.py": "2eb2b2765a59e80b0fd8fab8f50145e91e671733c46797bbe0c454e2c5f5059d",
    "execution/s0r6/mutate.py": "a9851915d087d27550c9759c32de2735280007c8593386faaa1457db51d2d107",
}


def test_predecessor_files_stay_byte_identical():
    for relative, digest in FROZEN.items():
        data = (RESEARCH / relative).read_bytes()
        assert hashlib.sha256(data).hexdigest() == digest


def test_r6b_prompt_states_field_rules_and_hides_mutation_names():
    spec = next(item for item in calibration_specs() if item["certificate_id"] == "s0r6-cal-kim")
    certificate = build_certificate(spec)
    mutated = apply_mutation(certificate, "drop_subject")
    checklist = (PROTOCOL / "REVIEW-CHECKLIST.md").read_text(encoding="utf-8")
    instructions = (PROTOCOL / "REVIEW-PROMPT.txt").read_text(encoding="utf-8")
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    prompt = render_prompt(mutated, schema, checklist, instructions)
    assert prompt_leaks(prompt, mutated) == []
    assert "predicates[].roles" in prompt
    assert "ACCOUNTED_NON_MATERIAL" in prompt
    assert "Necessity is not permission" in prompt
    assert "MATERIALLY_LIVE" in prompt
    assert "do not prove completeness" in prompt
    assert "Kim bought a book on Friday." in prompt


def test_request_uses_the_frozen_profile_options():
    profiles = json.loads(
        (RESEARCH / "execution/protocol/REVIEWER-PROFILES.json").read_text(encoding="utf-8")
    )
    profile = profiles["profiles"][1]
    body = build_request(profile, profiles, "prompt")
    assert body["model"] == "qwen3:14b"
    assert body["stream"] is False
    assert body["think"] is False
    assert body["format"] == "json"
    assert body["options"] == {"temperature": 0, "seed": 7, "num_ctx": 16384}


def test_eligibility_requires_known_goods_and_rejects_accepts_of_mutations():
    records = [
        {"item": "s0r6-cal-kim", "verdict": "ACCEPT_COMPLETE"},
        {"item": "s0r6-cal-kim--drop_subject", "verdict": "REJECT_ROLE_BINDING"},
    ]
    assert score_profile(records)["eligible"] is True
    failed = score_profile(
        [
            {"item": "s0r6-cal-kim", "verdict": "REJECT_SOURCE_BINDING"},
            {"item": "s0r6-cal-kim--drop_subject", "verdict": "ACCEPT_COMPLETE"},
        ]
    )
    assert failed["eligible"] is False
    assert {item["reason"] for item in failed["failures"]} == {
        "known_good_not_accepted",
        "hard_mutation_accepted",
    }
