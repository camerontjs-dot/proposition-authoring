# Frozen discovery scoring rubric

Evaluator: `agent_llm`, using the frozen working gold after proposals are cached.
This evaluator never supplies runtime authority. Hide lane, model, proposer and
confidence identities; assign opaque candidate IDs. Retain first judgments.

For each structure, mark `correct` only if the declared operator and all leaves
plus scoped obligations reconstruct the materially asserted root. Every role,
reference, qualifier, negation, modality, attribution and operator must survive.
A correct paraphrase is allowed. A candidate with the right operator but a
missing or invented proposition is wrong. A non-all_of candidate must retain its
operator; it cannot assert its branches as conjunctions. An atomic candidate
must carry one proposition, not merely echo an unparsed composite.

For ambiguous roots, a single interpretation may be a `live_alternative` without
being uniquely correct. Correct candidate-set recall requires all material
gold alternatives represented or explicit unresolved alternatives preserving
those differences. A model's word `AMBIGUOUS` alone is insufficient. Uncertain
scoring is `unresolved`, remains in the denominator and prevents positive
qualification. Report invented/omitted assertion counts and parallel error
flags: operator, scope, role/reference, qualifier, propositionhood. Do not
convert scores into votes.

Semantic pooling is an evaluation operation only: classify equivalent candidate
IDs into clusters from their meaning, ignoring lane, order and duplicate count.
Discovery union is not majority selection. Runtime exact normalization may
remove byte/surface-equivalent duplicates; broader semantic equivalence that
is unqualified remains separate candidates. Report the uncollapsed burden.

Aggregate by frozen root class and material kind: correct candidate recall,
wrong candidate rate, omitted/invented proposition counts, error family counts,
candidate count per root and pooled unique clusters. Sensitivity is a separate
frozen prompt ordering variant and exact regeneration on IDs T05, T08, T13, T23;
it never replaces the first main response. Model sensitivity across different
models is NOT_RUN in this bounded first discovery comparison.
