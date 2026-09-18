# Gate V1.0.0 → released Contract A 2.0.0 external producer-conformance check

Status: preregistered bounded research check.

## Subject

Exact frozen Gate V1.0.0 compatibility tree:

`c0da10e2e3b9aada5f66af9859cf27964fd3c5fc`

Exact released Contract A 2.0.0 validator authority:

`camerontjs-dot/apparatus-contracts@529c92b49a34d5c610618551a8737f019f9fa332`

## Trigger

CAL Provenance RC1 preserved a Health Canada run in which Gate produced Contract A containing `text/html`, and Evidence Bundler rejected it under released Contract A validation.

The Gate V1.0.0 release-freeze workflow still uses the same `text/html` Health Canada specimen, but its local bundle verifier checks Contract A shape/content hashes rather than the complete released Contract A 2.0.0 vocabulary.

## Question

Does exact frozen Gate V1.0.0 emit a Contract A object from its own Health Canada specimen that the exact released Contract A 2.0.0 validator rejects solely because of the source media representation?

## Primary

Run the unmodified frozen Health Canada RC3 specimen from the exact Gate V1.0.0 tree.

Require:

1. Gate execution completes and emits Contract A;
2. the maintained Gate bundle verifier accepts its own bundle;
3. the released Contract A 2.0.0 validator is applied independently to the emitted Contract A.

## Control

Create a control from the exact same frozen packet changing only both source `media_type` values to:

`text/plain; charset=utf-8`

Run exact same Gate subject and exact released Contract A validator.

## Dispositions

- `FALSIFIED_GATE_V1_RELEASED_CONTRACT_A_PRODUCER_CONFORMANCE`
  - primary is rejected by released Contract A;
  - control is accepted;
  - rejection is attributable to the frozen media-type vocabulary.
- `NOT_REPRODUCED`
  - primary is accepted by the released validator.
- `INCONCLUSIVE_APPARATUS`
  - subject/control cannot be executed or the rejection cannot be isolated to media representation.

## Boundary

This check does not widen Contract A, Evidence Bundler, Gate semantics, CAL, Decision, or Authorization.

If falsified, do not rewrite the frozen V1.0.0 tree in place. Preserve it and require a bounded successor producer-conformance correction before immutable publication if publication is still intended.
