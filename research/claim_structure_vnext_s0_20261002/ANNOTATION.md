# S0 annotation guideline

Profile: research evaluation, public-safe, stage-local, replace only in a new
experiment. Evaluator: `agent_llm`, blinded to implementation and proposer outputs.
This is a working semantic oracle, not human or deterministic semantic truth.

Annotate only the exact root and supplied authorized context. Source locators
establish custody; they supply no additional interpretive context. Do not fact
check whether a root is true. Determine what it asserts.

Use `ATOMIC` for one independently evaluable relation or property with all its
qualifiers preserved. A comparison is one relation; do not turn its arguments
into separately asserted facts. Units in two systems can express one quantity.
Negation of one property remains one proposition. Additional independently
asserted properties or events require a composite.

Use `ALL_OF` for unambiguous independently asserted conjuncts. Preserve roles,
reference, negation, quantifiers, modality, attribution, units, quantities,
thresholds, dates, temporal and jurisdictional scope. An attribution over an
explicit coordinated complement must remain attached to every child. Do not
assert the reported events as unattributed facts. Distinguish qualification
from a separately asserted proposition, explaining any close call.

Use `AMBIGUOUS` when at least two materially different interpretations remain
live. Supply both. Do not decide from plausibility or word frequency. Examples
of families are reference, modifier attachment, matrix scope and quantifier
scope. An explicit leading shared modifier has shared scope in this controlled
profile. Repeated scope removes a local/shared ambiguity. Punctuation alone
does not settle matrix or trailing-adjunct scope.

Use `NON_ALL_OF` for a sufficiently understood disjunction, conditional, scoped
negation of a composite, or mixed structure requiring an operator beyond flat
all_of. Represent the operator, without asserting its branches individually.
If both material ambiguity and unsupported representation apply, record both
and retain ambiguity as the class. Never flatten an alternative to all_of.

Use `UNRESOLVED_REVIEW` if the guideline cannot adjudicate a case. Preserve it;
it blocks a positive qualification claim. Do not force a balanced class count.
The proposed class counts are a design aim, not an oracle input.

Return JSONL, one row per ID in original order:
`id`, `class`, `operator`, `children` (list of strings), `scoped_obligations`
(list of strings), `alternatives` (list of materially different structures),
`basis`, `confidence` (`high`, `moderate`, `low`), `unresolved` (boolean).

The review may see only this guideline and targeted.jsonl. It must not read
source code, programme history, memory, proposer responses, mutation answers or
neighboring research records. Record any exposure as a deviation. Do not tune
or reroll a completed review because it disagrees with an intended label.

Review is frozen before any new proposer or verifier decisive execution.
Runtime instruments cannot read gold. Later evaluation labels candidate
correctness separately from runtime authority. Gold-informed coverage labels
are evaluation observations, not online authority.
