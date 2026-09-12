# Proposition Authoring V0 Convergence Plan

## Class

Research / convergence build. Not a promotion or production-insertion task.

## Claim under review

A standalone Proposition Authoring V0 can integrate the already-supported **plural proposal + common fail-closed semantic authority** architecture into one deterministic upstream producer that either emits Contract A 2.0.0 exactly or refuses to author an authoritative decomposition.

## Exact predecessor authorities

- Evidence Bundler protected main at decision time: `c26fbd4bfc8ba5c2604a784af158594b59fcae37`.
- Multi-proposer positive evidence: EB PR #65 decisive head `b25fa4743e16f40186d29bec3757c378733b7791`.
- Multi-proposer proposal/resolution freeze: `89d3917d4a4fb65851858e3d79711ac391988fd4`.
- Proposer Git blob: `b2684f1752a1eb841dd6ee85b1e81ae523b03810`.
- Resolver predecessor Git blob: `ca2fbf63855f21551c2e1ebb46019768753746e4`.
- Frozen RC1 authority commit: `26539c53781148543e980fe1f07b25f1ad9c2005`.
- RC1 evaluator Git blob: `e675b55559af17d50b65cd6af01ac23b0881bb43`.
- RC1 evaluator SHA-256: `1091169da8e960cdf93242ee4c629c7a1a814009c8f80554f4a190f5b3fe989d`.
- Contract A canonical release: `contract-a-v2.0.0`.
- Contract A wire-spec blob: `2e7c37fca9aa6bdd1090fb527a663bdbe606ebcb`.
- Contract A schema blob: `ff5cddfeacf4511136a3dd3b47db1a794b631cd9`.
- Contract A validator blob: `42e5f5b3bf38d677445e9d01ea130ba604e53409`.
- Architecture EDR: `camerontjs-dot/apparatus-contracts#90`.

## V0 responsibility

Input one authoritative root proposition plus exact authorized source/context representations.

Output exactly one of:

- `NOT_NEEDED` + valid Contract A `not_decomposed`;
- `DECLARED` + valid Contract A `declared/all_of`;
- `ABSTAINED` + authoring receipt only, no Contract A authority emitted;
- `FAILED` + failure receipt and, where faithfully representable, Contract A `failed`.

V0 never emits Contract A `unknown` for semantic abstention.

## Architectural invariants

1. Proposal generation is plural and non-authoritative.
2. Every proposal and rejection remains in the candidate ledger.
3. The semantic authority evaluates candidates independently of proposer identity.
4. Vote count cannot promote a candidate.
5. Exactly one surviving semantic cluster is required for `DECLARED`.
6. Multiple materially different surviving clusters fail closed.
7. No surviving decomposition does not imply `NOT_NEEDED`; `NOT_NEEDED` requires a bounded single-proposition root parse.
8. Retrieval, CAL, Decision Engine, and downstream outcome signals are prohibited as authoring inputs.
9. Every emitted Contract A object must validate against released Contract A 2.0.0.
10. Authoring receipt and Contract A identity are deterministic under exact replay.

## New V0 hypotheses requiring qualification

These are convergence choices, not already-supported scientific conclusions:

- root single-frame parsing is sufficient for the bounded V0 `NOT_NEEDED` decision;
- when one semantic cluster contains multiple surface realizations, lexicographically canonical child-text tuple selection is a safe deterministic representative rule;
- deterministic child proposition IDs derived from exact child text hashes preserve the required Contract A lineage semantics;
- material runtime failure can be represented as Contract A `failed` without conflating semantic abstention.

Each must be separately attacked in the V0 qualification corpus.

## Qualification before pipeline insertion

Require, at minimum:

- fresh naturalistic + adversarial roots authored after V0 freeze;
- explicit single-proposition / NOT_NEEDED controls;
- multiple equivalent-surface realization cases;
- multiple-material-reading ambiguity cases;
- threshold/quantifier, scope, negation, modality, direction, attribution, reference and ellipsis mutations;
- exact Contract A validation for every emitted handoff;
- mutation/metamorphic tests for proposer order, candidate order, child-order invariance where semantically irrelevant, and representative stability;
- zero unsafe authoritative emissions;
- exact replay;
- weak controls that force `not_decomposed`, select majority vote, or pick first candidate and must fail;
- independent/context-free implementation or consumer conformance before production promotion.

One unsafe authoritative decomposition blocks promotion.

## Reranker boundary

Reranking is intentionally excluded from V0 convergence. The learned reranker evidence remains a subordinate-measurement research lane and is not required to establish the core apparatus.
