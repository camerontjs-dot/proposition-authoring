# ClaimGate V1 default pooled runtime successor RC0

**Classification:** Draft integration qualification / bounded runtime binding.

## Trigger

The exact frozen integration candidate `b3278e960707720f5add10935027a7187725d446` was falsified during its prescribed RC5 smoke: the declared fixture returned `ABSTAINED` through the installed public CLI instead of the frozen expected `DECLARED` result.

The mismatch is localized to runtime binding, not yet to the RC4b pooled semantics:

- public CLI calls default `AuthoringEngine()`;
- default `AuthoringEngine()` instantiates `FrozenPredecessorBackend()`;
- decisive RC4b reproduction at `809b2534ffb34efa31c13975da55e65770460b99` explicitly instantiated `AuthoringEngine(CoverageBackend("pooled", vendor_dir=...))`.

## Candidate hypothesis

The smallest justified successor is to change only the default backend selected by `AuthoringEngine()` so that the public CLI uses the exact existing `CoverageBackend("pooled")` semantic apparatus already exercised by RC4b.

No proposer, evaluator, authority rule, profile competence, Contract A projection, ambiguity rule, or semantic-family behavior may change in RC0.

## Exact predecessor identities

- falsified integration head: `b3278e960707720f5add10935027a7187725d446`
- RC4b terminal record: `809b2534ffb34efa31c13975da55e65770460b99`
- RC4b decisive subject configuration: `AuthoringEngine(CoverageBackend("pooled", vendor_dir=...))`
- Evidence Bundler frozen downstream head: `4e1f6fe00e7c350b28f52bfea14f1f8988847884`
- Contract A public authority: released 2.0.0 / `contract-a-wire-candidate-rc2`

## Required discriminators

1. Runtime diff from `b3278e960...` is limited to default-backend binding plus tests/qualification records/workflow.
2. On the exact immutable RC4b fresh-case surface from `809b253...`, default `AuthoringEngine()` must produce the same canonical state, reason, children, Contract A and receipt as explicit `AuthoringEngine(CoverageBackend("pooled", vendor_dir=...))`.
3. The three frozen integration fixtures must pass through the actual installed `proposition-authoring author` CLI with the exact frozen expectations from PR #23.
4. Authoritative Contract A outputs must pass the released external Contract A 2.0 validator.
5. Exact frozen EB PR #79 must consume the declared and not-needed authoritative outputs without proposition identity repair or mutation.
6. Stale-root, stale-child, handoff-hash, operator and child-removal tamper controls must fail closed at Contract A and the applicable EB boundary.
7. CLI replay of declared and not-needed fixtures into fresh directories must be byte-identical.
8. Maintained ClaimGate tests/static checks remain green.

## Stop rule

Any semantic difference between default runtime behavior and the exact explicit pooled RC4b subject falsifies this successor. Do not alter `CoverageBackend`, coverage proposers, authority semantics, competence sets, fixture expectations, or downstream EB to turn RC0 green.

A green result supports a new exact ClaimGate integration candidate for whole-pipeline prototype qualification. It does not authorize merge, release, semantic widening, production use, or pipeline prototype freeze by itself.
