# ClaimGate V1 repeated-negation conservation successor RC0

**Classification:** bounded semantic-authority successor qualification. This is not merge, release, tag, production, or pipeline-use authorization.

## Trigger

Draft integration successor PR #26 falsified the wiring-only promotion hypothesis on maintained predecessor case `F14` after the public default runtime was bound to the already-reproduced pooled backend.

Exact observed falsifier:

`Unit Brisk did not cache File C and did not cache File D.`

Frozen predecessor gold requires:

1. `Unit Brisk did not cache File C.`
2. `Unit Brisk did not cache File D.`

The current `surface-scope-conservation-v1` instrument interprets the root as local negation and requires only one child to carry `did not`. It therefore blocks an explicitly repeated-negation construction that the frozen predecessor authority labels semantically resolvable.

The failure is localized to the conservation instrument. P4/P5 proposal lanes are not responsible.

## Exact predecessor subject

This experiment starts from ClaimGate PR #26 head:

`53411a8e8f24b2c057d9b5f736c068ab71423233`

Pinned runtime facts at that head:

- default pooled runtime binding commit: `11f0d23a6a67239a1d3e0627ea542265f4eafbbf`;
- `src/proposition_authoring/engine.py` blob: `42ce4798e960a2f48afa7ab90147cac4fdf5799b`;
- `src/proposition_authoring/conservation.py` blob: `dbe69e8bde1d9f485f3f16ba7d50f0bd86dff5a1`;
- `src/proposition_authoring/authority.py` blob: `1c05f7261171ad5176fbbb19bf164bd10db2b78c`;
- predecessor fresh roots blob: `e51ec542898a0f40489e0140bbd0455e1429e0bb`;
- predecessor fresh gold blob: `da169fcc9b0efc096cbb3c68a744da9d7beaa03d`;
- RC4b terminal evidence authority: `809b2534ffb34efa31c13975da55e65770460b99`;
- exact frozen Evidence Bundler consumer: `4e1f6fe00e7c350b28f52bfea14f1f8988847884`.

The predecessor integration candidate `b3278e960707720f5add10935027a7187725d446` remains preserved as falsified by its public-CLI binding. PR #26 remains preserved as falsified by F14.

## Hypothesis

A bounded conservation rule can distinguish **explicitly repeated same-predicate local negation** from **unsafe inferred or propagated negation** without changing any other supported ClaimGate behavior.

For the narrow construction:

`SUBJECT did not VERB X and did not VERB Y`

where the same verb is explicitly repeated in both root conjuncts, a two-child decomposition is conservation-safe only when each child independently retains exactly one explicit `did not VERB` carrier.

This does not authorize general negation parsing, different-verb coordination, arbitrary conjunction depth, or semantic inference beyond the tested construction.

## Allowed semantic change

Only the surface-scope conservation instrument may change semantically.

Because the conservation semantics change, its public diagnostic identity must advance rather than pretending byte/semantic identity with V1.

Allowed maintained runtime files:

- `src/proposition_authoring/conservation.py`;
- `src/proposition_authoring/authority.py` only as needed to use the successor conservation-instrument identity consistently.

The following are frozen for this experiment and must not change:

- `src/proposition_authoring/engine.py`;
- `src/proposition_authoring/coverage_backend.py`;
- `src/proposition_authoring/coverage_proposers.py`;
- `src/proposition_authoring/backend.py`;
- `src/proposition_authoring/ambiguity.py`;
- `src/proposition_authoring/profile.py`;
- `src/proposition_authoring/contract_a.py`;
- released Contract A authority;
- Evidence Bundler behavior;
- frozen smoke expectations.

Tests, workflow apparatus, and durable qualification records may be added or extended.

## Required discriminators

The successor is supported only if every gate below passes on one exact head.

1. **F14 recovery:** the public default runtime returns `DECLARED` with exactly the frozen two negated children.
2. **Repeated-negation conservation:** the exact F14 child set passes the successor conservation instrument.
3. **Negation-loss control:** the same F14 root with a second child that loses explicit negation is rejected.
4. **Propagation control:** a root with only one explicit local negation must still reject a candidate that propagates `did not` into an unrelated second child.
5. **Q18 preservation:** existing local-negation safe case `Gateway Umber did not authenticate token quartz and logged denial event.` remains accepted only with negation local to the first child.
6. **Full frozen predecessor boundary:** all 24 predecessor roots retain the maintained expected boundary: 19 exact `DECLARED`, 5 `ABSTAINED`, no unsafe authority, exact allowed children, valid Contract A for every authoritative result.
7. **RC4b preservation:** all 44 frozen RC4b cases retain their expected authoring state/children, zero unsafe authoritative outcomes, zero Contract A errors, and default runtime remains behaviorally equal to explicit pooled execution under the successor authority.
8. **Public CLI smoke:** frozen `DECLARED`, `NOT_NEEDED`, and `ABSTAINED` fixtures pass twice with deterministic replay.
9. **Released Contract A:** every authoritative smoke output validates under the exact released external Contract A 2.0 validator; preregistered hostile mutations fail closed.
10. **Evidence Bundler RC5 seam:** exact frozen EB consumer accepts valid `DECLARED` and `NOT_NEEDED` handoffs, replays deterministically, and rejects stale-root/stale-child handoffs.
11. **Maintained regression/static gates:** ClaimGate-owned tests, Ruff, compileall, and pip-check pass.

Any other changed semantic outcome on the frozen predecessor or RC4b surfaces is a falsifier, even if the aggregate counts remain acceptable.

## Stop rule

Do not change proposer logic, evaluator logic, ambiguity logic, profiles, Contract A, fixture expectations, Evidence Bundler, or downstream CAL behavior to make the successor green.

Do not broaden the negation rule after seeing a new failure. A new in-domain semantic counterexample requires a separately preregistered successor.

If any required gate is red, preserve the result and stop.

## Positive disposition

Only if all gates pass may the exact subject receive the bounded disposition:

`SUPPORTED_CLAIMGATE_V1_NEGATION_CONSERVATION_SUCCESSOR_FOR_LOCAL_RC5`

That disposition means the exact ClaimGate candidate may be packaged for local RC5 / whole-pipeline smoke use. It does not authorize merge, release, tag, semantic widening, universal natural-language decomposition, or production use.
