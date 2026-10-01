# ClaimGate V1 Integration Candidate

**ClaimGate** is the product/system name for the existing `camerontjs-dot/proposition-authoring` apparatus. The repository, Python package, and CLI remain named `proposition-authoring` in this candidate so the already-qualified runtime bytes are not renamed or rewritten during integration.

## Status

`FROZEN_FOR_LOCAL_QUALIFICATION`

This integration candidate packages the already-supported bounded Proposition Authoring subject for local CAL Pipeline testing. It does not widen semantic competence, change the authoring algorithm, alter Contract A, merge research to `main`, tag a release, or claim production readiness.

## Exact semantic subject

- scientific source: `f9d0ae9ba81756c51d7f1d433616d699eb9b6fd3`
- target freeze: `9c76b3d87b4362b79a22c0467a13a48c0a380a16`
- RC4b terminal evidence record: `809b2534ffb34efa31c13975da55e65770460b99`
- RC4b Draft PR: `#22`
- terminal experiment classification: `SUPPORTED_FOR_RC5_CONSUMER_CONFORMANCE`

The target-freeze commit is one evidence-only commit on top of the semantic source. No runtime file differs between the scientific source and target freeze.

## Contract boundary

ClaimGate authoritative output is released Contract A 2.0.0. The integrity-bound wire token remains exactly `contract-a-wire-candidate-rc2`.

Authoritative outcomes:

- `NOT_NEEDED` -> Contract A `not_decomposed`
- `DECLARED` -> Contract A `declared/all_of`
- `ABSTAINED` -> no authoritative Contract A handoff
- `FAILED` -> preserve material failure semantics; emit Contract A `failed` only where the frozen candidate does so faithfully

The released external Contract A validator in `camerontjs-dot/apparatus-contracts` is the qualification authority. ClaimGate's vendored validator is not sufficient by itself for RC5.

## Downstream frozen consumer

Evidence Bundler Draft PR #79:

- tested subject: `8e1e15a96308d20be24b0bd0f0a4d554b0f020cc`
- frozen receipt-only head: `4e1f6fe00e7c350b28f52bfea14f1f8988847884`
- integration profile: `eb-v1-integration-10x3-rc0`

RC5 asks only whether this frozen Evidence Bundler consumer can consume ClaimGate outputs strictly through released Contract A without hidden coupling or semantic rewriting.

## Claim Profile sidecar

`CLAIM_PROFILE_V0.md` records the proposed future ClaimGate characterization surface: domain/industry, claim family, verification-world regime, evidence expectations, and related descriptors.

It is intentionally **shadow-only and non-causal** in V1 qualification. It is not a Contract A field, cannot affect decomposition authority, cannot alter Evidence Bundler retrieval/admission, cannot select CAL semantics, and cannot affect Decision Engine behavior. It exists now only so naturalistic pipeline tests can collect useful observations without changing the frozen candidate.

## Local operator responsibility

The local operator should not develop ClaimGate. They should only:

1. check out this exact frozen integration branch/head;
2. install the pinned candidate in an isolated local worktree/environment;
3. run `LOCAL_QUALIFICATION.md` exactly;
4. preserve outputs/receipts/hashes;
5. report any deviation rather than patching through it.

Any behavior-changing fix creates a successor candidate and requires affected qualification to rerun.
