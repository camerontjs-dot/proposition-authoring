# Independent review protocol

## Objective

Determine whether a frozen source-bound certificate is complete and faithful enough to serve as an evaluation object.

Reviewers do **not** generate a class from scratch.

They receive:

- exact root text and authorized context;
- public/published analysis basis;
- frozen certificate;
- certificate schema;
- review checklist.

They do not receive:

- prior reviewer verdicts;
- model/proposer outputs under future S1/S2 tests;
- expected downstream ClaimGate result;
- programme development transcript.

## Review questions

Each reviewer answers independently:

1. Are all predicates in the root represented?
2. Does every predicate have its materially required subject/object/other role binding?
3. Are negation, modality, attribution and qualifiers bound to the correct target(s)?
4. Are conjunction/disjunction/conditional operators represented correctly?
5. For an ambiguous example, are all externally supported materially live readings represented?
6. Does any reading invent a proposition or obligation not supported by the source?
7. Does any reading omit a material proposition or obligation?
8. Are source spans exact and reconstructable?
9. Does the completeness ledger account for every material semantic span?
10. Is the top-level classification justified by the certificate rather than by unsupported intuition?

Allowed per-certificate verdicts:

- `ACCEPT_COMPLETE`
- `REJECT_OMISSION`
- `REJECT_INVENTION`
- `REJECT_SCOPE`
- `REJECT_ROLE_BINDING`
- `REJECT_OPERATOR`
- `REJECT_SOURCE_BINDING`
- `INCONCLUSIVE_REVIEW`

## Consolidation

Two independent reviews are required.

Agreement does not itself make the certificate true.

If either reviewer identifies a material defect, the certificate is not admitted without a separately recorded adjudication that resolves the exact objection using inspectable source/analysis evidence.

No majority vote.

The adjudicator must respond to every material objection.

## Completeness burden

A certificate cannot be marked complete merely because all required JSON fields are present.

Admission requires:

- no unassigned material spans;
- every predicate bound;
- every materially required role bound;
- every operator bound;
- every material qualifier bound;
- every materially live reading recorded or explicitly rejected by external analysis basis;
- hostile omission/operator/role mutations rejected by reviewers or mechanical checks.

## Reviewer qualification check

Before reviewing decisive certificates, each reviewer must pass a small frozen calibration set containing obvious:

- role omission;
- qualifier omission;
- attribution misattachment;
- negation loss;
- conjunction/disjunction swap;
- extra invented proposition.

A reviewer who accepts a hard calibration mutation cannot review decisive cases under that profile.

This reviewer check is itself an experiment object and must be frozen before decisive review.
