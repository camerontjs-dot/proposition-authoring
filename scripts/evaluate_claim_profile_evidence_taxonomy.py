from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from proposition_authoring.claim_profile import build_claim_profile
from proposition_authoring.evidence_gate import build_evidence_world_profile
from proposition_authoring.model import AuthoringRequest, SourceRepresentation
from proposition_authoring.preflight import compare_profiles
from proposition_authoring.shadow_models import SourceMetadata

ROOT = Path(__file__).resolve().parents[1]
GOLD = ROOT / "research" / "claim_profile_evidence_taxonomy_v0" / "gold_cases.json"
OUT = ROOT / "artifacts" / "claim-profile-evidence-taxonomy-v0"


def _case_request(case: dict[str, Any]) -> tuple[AuthoringRequest, tuple[SourceMetadata, ...]]:
    sources: list[SourceRepresentation] = []
    metadata: list[SourceMetadata] = []
    for index, form in enumerate(case["evidence_forms"], start=1):
        source_id = f"{case['case_id']}-S{index:02d}"
        sources.append(
            SourceRepresentation(
                source_id=source_id,
                media_type="text/plain",
                content=f"Frozen form-level gold fixture for {case['case_id']} / {form}.",
            )
        )
        metadata.append(
            SourceMetadata(
                source_id=source_id,
                provenance="frozen research gold fixture",
                source_role="taxonomy_gold",
                evidence_form=form,
            )
        )
    request = AuthoringRequest(
        handoff_id=f"taxonomy::{case['case_id']}",
        producer_id="claim-profile-taxonomy-gold-v0",
        producer_version="v0",
        work_id=case["case_id"],
        root_id=case["case_id"],
        root_text=case["claim"],
        sources=tuple(sources),
    )
    return request, tuple(metadata)


def _evidence_form_state(compatibility: dict[str, Any]) -> str:
    for observation in compatibility["observations"]:
        if observation["field"] == "evidence_forms":
            return observation["state"]
    raise RuntimeError("missing evidence_forms observation")


def main() -> None:
    gold = json.loads(GOLD.read_text(encoding="utf-8"))
    OUT.mkdir(parents=True, exist_ok=True)

    rows: list[dict[str, Any]] = []
    family_counts: dict[str, Counter[str]] = defaultdict(Counter)

    for case in gold["cases"]:
        request, metadata = _case_request(case)
        claim_profile = build_claim_profile(request)
        evidence_profile = build_evidence_world_profile(request, source_metadata=metadata)
        compatibility = compare_profiles(claim_profile, evidence_profile)
        actual = _evidence_form_state(compatibility)
        family_detected = case["family"] in claim_profile["claim_families"]
        compatibility_agrees = actual == case["expected_compatibility"]
        status = "AGREE" if family_detected and compatibility_agrees else "DISAGREE"
        family_counts[case["family"]][status] += 1
        rows.append(
            {
                "case_id": case["case_id"],
                "family_gold": case["family"],
                "claim_families_observed": claim_profile["claim_families"],
                "family_detected": family_detected,
                "evidence_forms_gold": case["evidence_forms"],
                "expected_compatibility_gold": case["expected_compatibility"],
                "observed_expected_forms": claim_profile["expected_evidence_forms"],
                "observed_compatibility": actual,
                "compatibility_agrees": compatibility_agrees,
                "status": status,
                "rationale": case["rationale"],
                "claim_profile_sha256": claim_profile["profile_sha256"],
                "evidence_profile_sha256": evidence_profile["profile_sha256"],
                "compatibility_sha256": compatibility["compatibility_sha256"],
            }
        )

    disagreements = [row for row in rows if row["status"] == "DISAGREE"]
    report = {
        "schema": "claim-profile-evidence-taxonomy-evaluation-v0",
        "gold_schema": gold["schema"],
        "case_count": len(rows),
        "agreement_count": len(rows) - len(disagreements),
        "disagreement_count": len(disagreements),
        "per_family": {
            family: dict(sorted(counts.items()))
            for family, counts in sorted(family_counts.items())
        },
        "disposition": (
            "BASELINE_AGREES_WITH_FROZEN_GOLD"
            if not disagreements
            else "BASELINE_DISAGREES_WITH_FROZEN_GOLD"
        ),
        "nonclaims": [
            "workflow success means the evaluator executed, not that the taxonomy passed",
            "gold compatibility is form-level only and does not establish factual support",
            "results do not authorize retrieval routing or downstream semantic effects",
        ],
        "cases": rows,
    }
    (OUT / "REPORT.json").write_text(
        json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False))


if __name__ == "__main__":
    main()
