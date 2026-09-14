from __future__ import annotations

import re

# Conservative V0 profile gate. This does not prove decomposition is required.
# It only prevents a bounded root parser's single-frame result from being promoted
# to Contract A `not_decomposed` when the surface still carries an obvious
# composition/coordination hazard that the parser could have swallowed.
_COMPOSITION_HAZARD = re.compile(
    r"\band/or\b|\b(?:and|or|but|while|whereas)\b|;",
    re.IGNORECASE,
)


def not_needed_profile_allows(root_text: str) -> bool:
    return _COMPOSITION_HAZARD.search(root_text) is None
