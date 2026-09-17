from __future__ import annotations

import re

# Narrow research-only recognizer for atomic comparative surface forms. It does not
# decompose, interpret evidence, or infer omitted arguments. Its only output is
# whether the complete root matches one bounded one-comparison grammar.
_ATOMIC_COMPARATIVE = re.compile(
    r"^(?P<left>[A-Za-z0-9][A-Za-z0-9 ._/-]*?)\s+had\s+"
    r"(?:(?:a|an)\s+)?"
    r"(?P<comparator>higher|lower|greater|fewer)\s+"
    r"(?P<measure>[A-Za-z][A-Za-z -]*?)\s+than\s+"
    r"(?P<right>[A-Za-z0-9][A-Za-z0-9 ._/-]*?)\.?$",
    re.IGNORECASE,
)

_FORBIDDEN = re.compile(
    r",|;|\b(?:and|or|but|while|whereas|not|according\s+to)\b",
    re.IGNORECASE,
)


def is_bounded_atomic_comparative(root_text: str, context_text: str = "") -> bool:
    """Return True only for one explicitly bounded comparative root.

    Context-bearing roots remain delegated to the predecessor semantic parser. This
    lane intentionally proves less rather than treating a surface match as authority
    when external context may affect scope or reference.
    """

    text = " ".join(root_text.strip().split())
    if not text or context_text.strip():
        return False
    if _FORBIDDEN.search(text):
        return False
    if len(re.findall(r"\bthan\b", text, flags=re.IGNORECASE)) != 1:
        return False
    match = _ATOMIC_COMPARATIVE.fullmatch(text)
    if match is None:
        return False
    return all(match.group(name).strip() for name in ("left", "measure", "right"))
