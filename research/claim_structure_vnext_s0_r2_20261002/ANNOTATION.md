# S0-R2 prospective annotation rule

This is a research working-oracle rule. It is not a released product contract.
Annotate the exact root and authorized context. Determine what the root asserts;
do not fact check it. The source URL is custody, not additional context.

An atomic assertion is one maximal predication with its arguments and all its
qualifiers attached. Manner, direction, quantity, time and location descriptions
of that predication do not become separate children merely because each can be
tested. Keep the whole qualified predication. This convention fixes annotation
grain; it does not resolve multiple truth-condition readings.

Independently predicated properties, relations or events joined conjunctively
are `ALL_OF`. Recover shared subjects only when their binding is warranted.
Preserve each quantity, unit, comparison group and scope. Coordinated noun
phrases can describe one collective argument; do not split them merely at
"and". Supplementary clauses and parenthetical assertions can add propositions
even without a second finite verb. Do not drop an additional assertion to make
a root atomic. Preserve causal relations rather than replacing them with an
unrelated conjunction of cause and effect.

`AMBIGUOUS` requires at least two materially distinct truth-condition readings.
Write both and identify the different scope, role, reference or quantifier
binding. Different paraphrases, different granularity with the same asserted
content, factual uncertainty and machine uncertainty do not establish semantic
ambiguity. If the rule cannot select annotation grain, use `UNRESOLVED_REVIEW`.

An overt clause-level fronted adjunct scopes over coordinated clauses in this
bounded profile. An adjective inside a coordinated noun phrase is not such an
adjunct. A trailing adjunct may have local or shared scope when grammar leaves
both live. Punctuation and world plausibility alone do not decide the scope.
Attribution over an explicit coordinated complement stays over the whole
complement; a second clause outside that complement is a different reading.

`NON_ALL_OF` means an understood structure that requires disjunction,
conditional, scoped negation, or a mixed/nested operator beyond flat all_of.
Do not assert its branches individually. A conditional antecedent is not an
assertion of that antecedent. Negating a conjunction is not negating every
child. Do not add exclusive-or when only or is expressed.

If unsupported representation and live semantic ambiguity coexist, choose
`AMBIGUOUS` and preserve the representation limitation in obligations. If a
case cannot be judged from the rule, choose `UNRESOLVED_REVIEW` and explain the
missing decision. No target class counts are given to reviewers.

Preserve operators, qualifiers, scope, roles, referents, negation, attribution,
quantities, units, thresholds, temporal and jurisdictional constraints,
modality, and causal/comparative relations. For atomic roots return the whole
root as its sole child. For all_of return complete warranted child assertions.
For non_all_of record the scoped operator and branches in obligations. For
ambiguity return alternatives, with no selected children.

Return one JSON object with id, class, operator, children, scoped_obligations,
alternatives, basis, confidence and unresolved. An alternative contains
operator, children and scope. `unresolved` is true only for `UNRESOLVED_REVIEW`.
Confidence records uncertainty and grants no semantic authority.

> Binds: S0-R2 research reviewers and experiment owner.
> Tier: T0 (advisory semantic protocol).
> Check: none for semantic judgments; run_review.py separately blocks input/model drift and validates JSON shape.
> Escape: preserve UNRESOLVED_REVIEW, FALSIFIED_COLD_REVIEW_ORACLE or FAILED_APPARATUS; do not manufacture gold.
