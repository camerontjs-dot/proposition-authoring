# RC3 Safe Coverage Recovery Preregistration

## Question
Can bounded proposal generation recover useful end-to-end Proposition Authoring coverage while the RC2 semantic authority boundary remains fixed?

## Frozen authority boundary
RC3 inherits the exact RC2 composition: root-scope ambiguity veto, frozen RC1 binding evaluator, `surface-scope-conservation-v1`, fail-closed AND semantics. Proposal count, vote, reranker score and downstream outcomes cannot override a veto.

## New proposal lanes
- P4: simple affirmative shared-subject action conjunction fallback. Development target Q09.
- P5: explicit shared matrix attribution with `that`, repeated onto both child propositions. Development target Q21.

Q18 and RC2 A17/A20 are evaluator false negatives, not proposer targets.

## Arms
1. baseline P1/P2/P3
2. P4 only
3. P5 only
4. pooled P1/P2/P3+P4+P5

## Development evidence only
Previously revealed Q09, Q18, Q21, Q29 may be used before freeze. Fresh RC3 roots must not exist before target/scorer/workflow freeze.

## Positive fresh burden
- zero unsafe authoritative pooled finalizations;
- pooled safe coverage gain >= 6 roots over baseline;
- gains in both P4 and P5 target families;
- >= 90% preservation of baseline safe finalizations;
- deterministic byte-identical replay;
- every pooled authoritative Contract A emission validates with the exact released validator;
- at least one fail-closed fresh case is incorrectly finalized by the weak first-proposal control, demonstrating authority adds real discrimination.

## Hard falsifiers
Any unsafe `DECLARED` or incorrect `NOT_NEEDED`; materially wrong authoritative children on a safe case; authority weakening; proposer/candidate order or duplicate count changing final authority; post-output semantic repair; or any frozen RC2 semantic file change after target freeze.

## Nonclaims
Positive RC3 evidence would authorize only one integrated bounded candidate for RC4 context-free independent reproduction. It would not authorize merge to production semantics, release, Contract A amendment, Evidence Bundler insertion, CAL mutation, or Decision Engine mutation.
