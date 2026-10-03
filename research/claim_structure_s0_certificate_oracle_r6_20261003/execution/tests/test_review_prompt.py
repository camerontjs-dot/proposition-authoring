from s0r6.build import build_certificate
from s0r6.mutate import apply_mutation
from s0r6.review import parse_verdict, prompt_leaks, render_prompt, reviewer_view
from s0r6.specs import calibration_specs


def test_reviewer_view_hides_mutation_identity():
    spec = next(item for item in calibration_specs() if item["certificate_id"] == "s0r6-cal-kim")
    certificate = build_certificate(spec)
    mutated = apply_mutation(certificate, "drop_subject")
    viewed = reviewer_view(mutated)
    assert viewed["certificate_id"] == "certificate-under-review"
    assert mutated["certificate_id"].endswith("drop_subject")
    prompt = render_prompt(mutated, {"type": "object"}, "checklist", "instructions")
    assert prompt_leaks(prompt, mutated) == []
    assert "Kim bought a book on Friday." in prompt


def test_parse_verdict_rejects_accept_with_objections_and_garbage():
    assert parse_verdict('{"verdict":"ACCEPT_COMPLETE","objections":[]}')["verdict"] == "ACCEPT_COMPLETE"
    assert parse_verdict('{"verdict":"ACCEPT_COMPLETE","objections":[{"question":1}]}')["verdict"] == "UNPARSABLE"
    assert parse_verdict("not json")["verdict"] == "UNPARSABLE"
    wrapped = parse_verdict('note {"verdict":"REJECT_OMISSION","objections":[]}')
    assert wrapped["verdict"] == "REJECT_OMISSION"
