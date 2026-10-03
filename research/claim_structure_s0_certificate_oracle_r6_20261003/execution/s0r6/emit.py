"""Write the frozen certificate packet."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from s0r6.build import build_certificate, resolve_requirements
from s0r6.mutate import apply_mutation
from s0r6.specs import GUM_TEXT, all_specs, calibration_specs, decisive_specs
from s0r6.validate import sha256_text

EXECUTION = Path(__file__).resolve().parents[1]
PACKET = EXECUTION / "packet"
HARD = {
    "s0r6-cal-kim": ["drop_subject", "drop_object", "drop_qualifier", "alter_span", "invent_proposition"],
    "s0r6-cal-or": ["or_to_and"],
    "s0r6-cal-amb": ["drop_live_reading", "drop_negation"],
    "s0r6-cal-attr": ["reattach_attribution"],
    "s0r6-cal-must": ["change_modality"],
}


def _write(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _digest(payload) -> str:
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def emit() -> dict:
    certificates = {}
    requirements = {}
    corpus = []
    for spec in all_specs():
        certificate = build_certificate(spec)
        requirement = resolve_requirements(spec)
        certificates[spec["certificate_id"]] = certificate
        requirements[spec["certificate_id"]] = requirement
        destination = "decisive" if spec["packet"] == "decisive" else "calibration/known-good"
        _write(PACKET / destination / f"{spec['certificate_id']}.json", certificate)
        if spec["packet"] == "decisive":
            corpus.append(
                {
                    "certificate_id": spec["certificate_id"],
                    "claim_id": spec["claim_id"],
                    "families": spec["families"],
                    "classification": spec["classification"],
                    "root_sha256": certificate["root"]["text_sha256"],
                    "source_locator": certificate["source_provenance"]["root_source"]["locator"],
                    "source_location": certificate["source_provenance"]["root_source"]["location"],
                }
            )
    _write(PACKET / "requirements.json", requirements)
    _write(
        PACKET / "CORPUS.json",
        {
            "decisive_count": len(decisive_specs()),
            "calibration_count": len(calibration_specs()),
            "family_note": (
                "A root may cover more than one family. "
                "temporal_location_scope is L01 (both PPs on the verb) and L02 (verb-level versus nominal PP). "
                "AM01 is the coordination modifier shared-versus-local analogue, not a place-name sentence. "
                "D02's parenthetical not-both is negation on a disjunction and is also tagged negation_scope."
            ),
            "items": corpus,
        },
    )
    controls = []
    for spec in calibration_specs():
        certificate = certificates[spec["certificate_id"]]
        controls.append(
            {
                "item_id": spec["certificate_id"],
                "kind": "known_good",
                "expected_mechanical": "pass",
            }
        )
        for name in HARD[spec["certificate_id"]]:
            mutated = apply_mutation(certificate, name)
            _write(PACKET / "calibration/mutations" / f"{mutated['certificate_id']}.json", mutated)
            controls.append(
                {
                    "item_id": mutated["certificate_id"],
                    "kind": "hard_mutation",
                    "mutation": name,
                    "expected_mechanical": "fail",
                }
            )
    _write(PACKET / "calibration/CONTROLS.json", {"items": controls})
    hashes = {
        certificate_id: _digest(certificate)
        for certificate_id, certificate in sorted(certificates.items())
    }
    _write(PACKET / "CERTIFICATE-HASHES.json", hashes)
    excerpt = EXECUTION / "sources/excerpts/gum_essay_system-51.conllu"
    excerpt.parent.mkdir(parents=True, exist_ok=True)
    source = EXECUTION / "sources/en_gum-ud-test.conllu"
    if source.exists():
        raw = source.read_text(encoding="utf-8")
        marker = "# text = " + GUM_TEXT
        start = raw.rfind("# sent_id", 0, raw.find(marker))
        end = raw.find("\n\n", raw.find(marker))
        excerpt.write_text(raw[start:end].strip() + "\n", encoding="utf-8")
    return {
        "decisive": len(decisive_specs()),
        "calibration": len(calibration_specs()),
        "mutations": sum(len(names) for names in HARD.values()),
        "gum_root_sha256": sha256_text(GUM_TEXT),
    }


if __name__ == "__main__":
    print(json.dumps(emit(), indent=2))
