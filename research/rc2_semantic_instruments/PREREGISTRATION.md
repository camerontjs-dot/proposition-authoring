# RC2 Independent Semantic Instruments — Preregistration

## Question

Can fail-closed composition of the frozen RC1 candidate evaluator with an independently implemented root/candidate surface-conservation instrument reduce unsafe semantic authority without majority voting or proposer expansion?

## Fixed predecessor

RC1 target freeze: `bd4fca4494b1ffce4a13118fad5a1268990e42db`. Exact RC1 runtime blobs are imported onto clean `main` and remain unchanged unless explicitly listed as RC2 scientific changes.

## Development-only evidence

Q18, Q29, and RC1 R22 are revealed predecessor evidence. They may be used before freeze only. No RC1 fresh case can count as RC2 decisive evidence.

## Target rule

1. Root ambiguity veto runs first.
2. Frozen RC1 evaluator must return `ACCEPTABLE_WITHIN_PROFILE`.
3. Independent conservation instrument must return `PASS`.
4. Any failure or indeterminate result blocks candidate authority.
5. Counts, votes and scores never grant authority.

The independent conservation module may inspect only root/candidate surface strings. It must not import/call the frozen evaluator, parser, backend, or downstream pipeline.

## Weak controls

- evaluator-only: root ambiguity veto + frozen evaluator, no independent conservation;
- conservation-only: root ambiguity veto + surface conservation, no frozen evaluator;
- permissive-any-pass: root ambiguity veto + authority if either semantic instrument passes;
- lexical-coverage: authority if every non-stopword child token occurs in the root, ignoring attachment.

## Fresh surface

Authored only after target/harness freeze. Candidate-level root + child-set cases, including safe conservative candidates, scope-loss mutations, word-preserving attachment mutations, ambiguous roots, explicit clear counterparts, shared qualifiers, local negation, threshold/quantifier and correlative scope.

## Hard falsifiers

- any fresh unsafe or ambiguous candidate is `ALLOW`;
- any fresh candidate with materially wrong semantic attachment is `ALLOW`;
- vote/count/score overrides a veto;
- purported independent instrument shares the frozen parser/evaluator implementation path;
- candidate/order mutation changes authority;
- scientific code or gold is repaired after decisive output.

## Positive burden

- zero unsafe/ambiguous `ALLOW` decisions;
- at least 80% of preregistered safe candidates `ALLOW`;
- safe accepts across at least four semantic families;
- weak controls meaningfully separate;
- exact replay;
- all target-allowed Contract A projections validate under the exact released validator;
- maintained CI green.

Positive disposition: `SUPPORTED_FOR_RC3_COVERAGE_TESTING`. Otherwise `FALSIFIED` on hard safety failure, else `INCONCLUSIVE`.
