from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal

Disposition = Literal["PASS", "FAIL", "INDETERMINATE"]
REPORTING = "reported|stated|confirmed|noted|claimed|observed|found|said"
MATRIX_RE = re.compile(rf"^(?P<matrix>.+?\b(?:{REPORTING}))\s+(?P<body>.+)$", re.IGNORECASE)
LEADING_RE = re.compile(r"^(?P<prefix>(?:during|at|in|under|after|before|when|while|if|unless)\b[^,]*,\s*)(?P<body>.+\band\b.+)$", re.IGNORECASE)
LOCAL_NEG_RE = re.compile(r"^(?P<subject>.+?)\s+did\s+not\s+(?P<verb>[A-Za-z][A-Za-z-]*)\b.*?\band\b.+$", re.IGNORECASE)
GENERIC_BOTH_RE = re.compile(r"^(?P<subject>.+?)\s+both\s+(?P<body>.+\band\b.+)$", re.IGNORECASE)
TRAILING_RE = re.compile(r"^.+\band\b.+\s+(?:during|at|in|under|after|before|when|while|if|unless)\b[^,]*[.]?$", re.IGNORECASE)
THRESHOLD_RE = re.compile(r"\b(?:at\s+least|at\s+most|more\s+than|less\s+than|below|above)\s+\d+(?:\.\d+)?(?:\s+[A-Za-z%]+)?\b", re.IGNORECASE)


def norm(text: str) -> str:
    return " ".join(text.strip().rstrip(".").lower().split())


@dataclass(frozen=True)
class ConservationMeasurement:
    disposition: Disposition
    findings: tuple[str, ...]
    families: tuple[str, ...]

    def as_dict(self) -> dict[str, object]:
        return {
            "instrument": "surface-scope-conservation-v1",
            "disposition": self.disposition,
            "findings": list(self.findings),
            "families": list(self.families),
        }


def audit_candidate(root_text: str, child_texts: tuple[str, ...] | list[str]) -> ConservationMeasurement:
    root = norm(root_text)
    children = tuple(norm(x) for x in child_texts)
    findings: list[str] = []
    families: list[str] = []
    if len(children) < 2:
        return ConservationMeasurement("INDETERMINATE", ("NON_DECOMPOSITION_CANDIDATE",), ())

    matrix = MATRIX_RE.match(root)
    if matrix and " and " in matrix.group("body"):
        anchor = norm(matrix.group("matrix"))
        body = norm(matrix.group("body"))
        families.append("MATRIX_ATTRIBUTION")
        marked_that = body.startswith("that ")
        marked_both = body.startswith("both ")
        if not (marked_that or marked_both):
            findings.append("UNMARKED_MATRIX_ATTRIBUTION_SCOPE")
        else:
            if any(not child.startswith(anchor + " ") for child in children):
                findings.append("SHARED_MATRIX_ATTRIBUTION_LOST")
            if marked_both and any(re.search(r"\bboth\b", child) for child in children):
                findings.append("CORRELATIVE_BOTH_STRANDED")

    leading = LEADING_RE.match(root)
    if leading:
        prefix = norm(leading.group("prefix").rstrip(", "))
        families.append("LEADING_SHARED_ADJUNCT")
        if any(not child.startswith(prefix + ",") and not child.startswith(prefix + " ") for child in children):
            findings.append("SHARED_LEADING_ADJUNCT_LOST")

    local_neg = LOCAL_NEG_RE.match(root)
    if local_neg:
        verb = local_neg.group("verb").lower()
        families.append("LOCAL_NEGATION")
        carriers = [c for c in children if re.search(rf"\b{re.escape(verb)}\b", c)]
        if len(carriers) != 1 or " did not " not in f" {carriers[0]} ":
            findings.append("LOCAL_NEGATION_BINDING_LOST")
        elif sum(" did not " in f" {c} " for c in children) != 1:
            findings.append("LOCAL_NEGATION_OVERDISTRIBUTED")

    generic_both = GENERIC_BOTH_RE.match(root)
    if generic_both and not matrix:
        subject = norm(generic_both.group("subject"))
        families.append("CORRELATIVE_BOTH")
        if any(not child.startswith(subject + " ") for child in children):
            findings.append("CORRELATIVE_SHARED_SUBJECT_LOST")
        if any(re.search(r"\bboth\b", child) for child in children):
            findings.append("CORRELATIVE_BOTH_STRANDED")

    phrases = tuple(norm(m.group(0)) for m in THRESHOLD_RE.finditer(root))
    if phrases:
        families.append("THRESHOLD_QUANTIFIER")
        for phrase in phrases:
            if not any(phrase in child for child in children):
                findings.append(f"CRITICAL_THRESHOLD_PHRASE_LOST:{phrase}")

    if TRAILING_RE.match(root) and not leading:
        families.append("TRAILING_ADJUNCT")
        findings.append("TRAILING_ADJUNCT_SCOPE_UNRESOLVED")

    if any(x.startswith("UNMARKED_") or x.endswith("_UNRESOLVED") for x in findings):
        disposition: Disposition = "INDETERMINATE"
    elif findings:
        disposition = "FAIL"
    else:
        disposition = "PASS"
    return ConservationMeasurement(disposition, tuple(sorted(set(findings))), tuple(sorted(set(families))))
